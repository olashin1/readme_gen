import json
import re
from pathlib import Path

from readme_gen.models import ProjectInfo


def build_project_prompt(project: ProjectInfo) -> str:
    context = build_context(project)
    metadata = json.dumps(
        build_metadata_payload(project),
        indent=2,
        ensure_ascii=False,
    )

    return f"""
You are composing factual prose for a polished GitHub README.

Your goal is to help a developer who has just opened the repository understand the project quickly.

Important rules:
- Treat the structured metadata as the authoritative source of repository facts.
- Only make claims supported by the supplied metadata or selected file excerpts.
- Do not invent features, commands, flags, integrations, workflows, compatibility claims, or usage patterns.
- Never turn a low-confidence clue or filename into a definite feature claim.
- Distinguish between what this specific project currently does and what its tools or frameworks are generally capable of doing.
- If something is uncertain, omit it rather than guessing.
- Keep the content concise and easy to skim.
- Write for a technical audience without assuming deep familiarity with the project.
- Prefer clear, direct language over promotional hype.
- Avoid vague phrases such as "comprehensive solution", "robust application", "seamless experience", "powerful platform", "revolutionary", "cutting-edge", and "next-generation".
- Prefer short sentences, concrete nouns, and terminology found in the metadata.
- Do not write exhaustive API documentation.
- Focus on what would be useful on the main GitHub repository page.
- Do not mention that you are analyzing a repository.
- Do not refer to the README generation process.

Return structured content with the following fields:

1. tagline
   - One short sentence suitable for display directly beneath the project title.
   - Explain what the project is or what it helps users do.
   - Keep it concise.
   - Do not simply repeat the project name.

2. summary
   - One concise paragraph explaining what the project does.
   - Mention the main problem or use case when supported by the repository.
   - Give enough context for a first-time visitor to understand the project.
   - Avoid implementation-level details unless they are central to the project's identity.

3. highlights
   - Return no more than 6 concise bullet-style statements.
   - Return an empty list if user-facing features are not supported.
   - Treat these as the most important reasons someone would care about the project.
   - Prioritize user-facing capabilities and distinctive strengths.
   - Do not create a long exhaustive feature list.
   - Avoid repeating the summary.
   - Avoid listing low-level dependencies as highlights unless they are directly meaningful to users.

4. usage_summary
   - Briefly explain how someone typically interacts with or runs the project.
   - Focus on the normal user workflow.
   - Mention visible CLI commands, scripts, frameworks, or usage patterns only when supported by the supplied information.
   - Do not invent exact command syntax or arguments that are not shown.

5. architecture
   - Give a concise, high-level explanation of how the major parts of the project fit together.
   - Focus on the important architectural relationships.
   - Avoid excessive implementation detail.
   - Keep this useful for someone trying to understand the codebase at a glance.

Structured repository metadata (JSON):

```json
{metadata}
```

Selected repository excerpts for understanding purpose only. Do not use an
excerpt to contradict or replace structured facts:

{context}
""".strip()


def build_metadata_payload(project: ProjectInfo) -> dict[str, object]:
    repository = project.repository
    payload: dict[str, object] = {
        "name": project.name,
        "description": project.description,
        "project_type": project.project_type,
        "languages": project.languages,
        "package_managers": project.package_managers,
        "dependencies": project.dependencies,
        "development_dependencies": project.dev_dependencies,
        "cli_entry_points": project.cli_commands,
        "package_scripts": project.package_scripts,
        "technologies": [
            {
                "name": technology.name,
                "category": technology.category,
                "role": technology.role,
                "evidence": [
                    {
                        "source": evidence.source,
                        "kind": evidence.kind,
                        "confidence": evidence.confidence.value,
                    }
                    for evidence in technology.evidence
                ],
            }
            for technology in project.technologies
        ],
        "technology_roles": project.technology_roles,
        "commands": [
            {
                "kind": command.kind,
                "name": command.name,
                "command": command.command,
                "source": command.source,
            }
            for command in project.commands
        ],
        "environment_variables": [
            {
                "name": variable.name,
                "sources": list(variable.sources),
            }
            for variable in project.environment_variables
        ],
        "api_routes": [
            {
                "method": route.method,
                "path": route.path,
                "handler": route.handler,
                "source": route.source,
            }
            for route in project.api_routes
        ],
        "assets": [
            {"path": asset.path, "kind": asset.kind}
            for asset in project.assets
        ],
        "features": project.features,
        "source_directories": project.source_dirs,
        "test_directories": project.test_dirs,
        "project_structure": project.directory_tree,
        "workflows": [
            {
                "name": workflow.name,
                "purpose": workflow.purpose,
                "path": workflow.path,
            }
            for workflow in project.workflows
        ],
    }
    if repository is not None:
        payload["repository"] = {
            "url": repository.url,
            "owner": repository.owner,
            "name": repository.name,
            "description": repository.description,
            "homepage": repository.homepage,
            "topics": repository.topics,
            "default_branch": repository.default_branch,
            "primary_language": repository.primary_language,
            "license": repository.license_spdx_id or repository.license_name,
        }
    return payload


def build_repository_context(
    project: ProjectInfo,
) -> str:
    repository = project.repository

    if repository is None:
        return "None"

    lines = [
        f"Repository URL: {repository.url or 'None'}",
        f"Owner: {repository.owner or 'Unknown'}",
        f"Repository name: {repository.name or 'Unknown'}",
        f"Description: {repository.description or 'None'}",
        f"Homepage: {repository.homepage or 'None'}",
        f"Default branch: {repository.default_branch or 'Unknown'}",
        f"Primary language: {repository.primary_language or 'Unknown'}",
        f"License: {repository.license_spdx_id or repository.license_name or 'Unknown'}",
    ]

    if repository.topics:
        lines.append(
            f"Topics: {', '.join(repository.topics)}"
        )
    else:
        lines.append("Topics: None")

    return "\n".join(lines)


def build_context(project: ProjectInfo) -> str:
    sections: list[str] = []

    for relative_path in project.context_files:
        path = project.root / relative_path

        contents = read_context_file(
            path,
            redact_environment=path.name.startswith(".env"),
        )

        if contents is None:
            continue

        sections.append(
            "\n".join(
                [
                    f"FILE: {relative_path}",
                    "-----",
                    contents,
                ]
            )
        )

    return "\n\n".join(sections)


def read_context_file(
    path: Path,
    max_chars: int = 12_000,
    redact_environment: bool = False,
) -> str | None:
    try:
        contents = path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return None

    if redact_environment:
        contents = redact_environment_values(contents)

    if len(contents) > max_chars:
        contents = (
            contents[:max_chars]
            + "\n\n[FILE TRUNCATED]"
        )

    return contents


def redact_environment_values(contents: str) -> str:
    lines: list[str] = []
    pattern = re.compile(
        r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=",
    )
    for line in contents.splitlines():
        match = pattern.match(line)
        if match:
            lines.append(f"{match.group(1)}=<redacted>")
    return "\n".join(lines)


def format_mapping(values: dict[str, str]) -> str:
    if not values:
        return "None"

    return "\n".join(
        f"- {key}: {value}"
        for key, value in values.items()
    )


def format_list(values: list[str]) -> str:
    if not values:
        return "None"

    return "\n".join(
        f"- {value}"
        for value in values
    )


def format_workflows(project: ProjectInfo) -> str:
    if not project.workflows:
        return "None"

    return "\n".join(
        (
            f"- {workflow.name} "
            f"({workflow.purpose}): "
            f"{workflow.path}"
        )
        for workflow in project.workflows
    )
