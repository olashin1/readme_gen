from pathlib import Path

from readme_gen.models import ProjectInfo


def build_project_prompt(project: ProjectInfo) -> str:
    context = build_context(project)

    return f"""
You are analyzing a software repository to produce accurate README content.

Important rules:
- Only make claims supported by the supplied repository metadata or file contents.
- Distinguish between what this specific project currently uses and what the tool itself is capable of supporting.
- Do not invent features.
- Do not claim commands, flags, integrations, or workflows unless they are visible in the supplied information.
- Keep descriptions concise and technical.
- Avoid marketing language.
- If something is uncertain, omit it rather than guessing.

Analyze the project and return:
- a concise project overview
- the main concrete features implemented by this repository
- the intended users
- a practical usage summary
- a concise architecture summary

Project metadata:

Name: {project.name}
Existing description: {project.description or "None"}
Project type: {project.project_type or "Unknown"}
Languages: {", ".join(project.languages) or "Unknown"}
Frameworks: {", ".join(project.frameworks) or "None"}
Package managers: {", ".join(project.package_managers) or "Unknown"}

CLI commands:
{format_mapping(project.cli_commands)}

Package scripts:
{format_mapping(project.package_scripts)}

Dependencies:
{format_list(project.dependencies)}

Dev dependencies:
{format_list(project.dev_dependencies)}

Repository structure:

{chr(10).join(project.directory_tree)}

Selected repository context:

{context}
""".strip()


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