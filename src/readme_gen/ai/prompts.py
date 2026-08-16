from pathlib import Path

from readme_gen.models import ProjectInfo


def build_project_prompt(project: ProjectInfo) -> str:
    context = build_context(project)

    repository_context = build_repository_context(project)

    return f"""
You are analyzing a software repository to produce content for a polished GitHub README landing page.

Your goal is to help a developer who has just opened the repository understand the project quickly.

Important rules:
- Only make claims supported by the supplied repository metadata or file contents.
- Do not invent features, commands, flags, integrations, workflows, compatibility claims, or usage patterns.
- Distinguish between what this specific project currently does and what its tools or frameworks are generally capable of doing.
- If something is uncertain, omit it rather than guessing.
- Keep the content concise and easy to skim.
- Write for a technical audience without assuming deep familiarity with the project.
- Prefer clear, direct language over promotional hype.
- Avoid vague marketing phrases such as "revolutionary", "cutting-edge", "powerful", or "next-generation".
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
   - Return 4 to 6 concise bullet-style statements.
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

Project metadata:

Name: {project.name}
Existing description: {project.description or "None"}
Project type: {project.project_type or "Unknown"}
Languages: {", ".join(project.languages) or "Unknown"}
Frameworks: {", ".join(project.frameworks) or "None"}
Package managers: {", ".join(project.package_managers) or "Unknown"}

Repository metadata:

{repository_context}

CLI commands:
{format_mapping(project.cli_commands)}

Package scripts:
{format_mapping(project.package_scripts)}

Dependencies:
{format_list(project.dependencies)}

Dev dependencies:
{format_list(project.dev_dependencies)}

Detected GitHub Actions workflows:
{format_workflows(project)}

Repository structure:

{chr(10).join(project.directory_tree)}

Selected repository context:

{context}
""".strip()


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

        contents = read_context_file(path)

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
) -> str | None:
    try:
        contents = path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return None

    if len(contents) > max_chars:
        contents = (
            contents[:max_chars]
            + "\n\n[FILE TRUNCATED]"
        )

    return contents


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