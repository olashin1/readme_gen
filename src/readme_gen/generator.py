from readme_gen.models import ProjectInfo


def generate_readme(project: ProjectInfo) -> str:
    sections = [
        generate_header(project),
        generate_overview(project),
        generate_features(project),
        generate_tech_stack(project),
        generate_installation(project),
        generate_usage(project),
        generate_architecture(project),
        generate_structure(project),
        generate_license(project),
    ]

    return "\n\n".join(
        section
        for section in sections
        if section
    ).strip() + "\n"


def generate_header(project: ProjectInfo) -> str:
    lines = [f"# {project.name}"]

    if project.description:
        lines.extend(
            [
                "",
                project.description,
            ]
        )

    return "\n".join(lines)


def generate_overview(project: ProjectInfo) -> str:
    if not project.analysis:
        return ""

    if not project.analysis.summary:
        return ""

    return "\n".join(
        [
            "## Overview",
            "",
            project.analysis.summary,
        ]
    )


def generate_features(project: ProjectInfo) -> str:
    if not project.analysis:
        return ""

    if not project.analysis.features:
        return ""

    lines = [
        "## Features",
        "",
    ]

    for feature in project.analysis.features:
        lines.append(f"- {feature}")

    return "\n".join(lines)


def generate_tech_stack(project: ProjectInfo) -> str:
    if not (
        project.languages
        or project.frameworks
        or project.package_managers
    ):
        return ""

    lines = [
        "## Tech Stack",
        "",
    ]

    if project.languages:
        lines.append(
            f"**Languages:** {', '.join(project.languages)}"
        )

    if project.frameworks:
        lines.append(
            f"**Frameworks:** {', '.join(project.frameworks)}"
        )

    if project.package_managers:
        lines.append(
            f"**Package Managers:** "
            f"{', '.join(project.package_managers)}"
        )

    return "\n".join(lines)


def generate_installation(project: ProjectInfo) -> str:
    commands = detect_install_commands(project)

    if not commands:
        return ""

    repo_name = project.root.name

    lines = [
        "## Installation",
        "",
        "Clone the repository and install dependencies:",
        "",
        "```bash",
        f"git clone {project.repository_url or '<repository-url>'}",
        f"cd {repo_name}",
    ]

    lines.extend(commands)
    lines.append("```")

    return "\n".join(lines)


def detect_install_commands(project: ProjectInfo) -> list[str]:
    commands: list[str] = []

    managers = set(project.package_managers)

    if "uv" in managers:
        commands.append("uv sync")

    elif "Poetry" in managers:
        commands.append("poetry install")

    elif "Pipenv" in managers:
        commands.append("pipenv install")

    elif "pip" in managers:
        commands.append("pip install -r requirements.txt")

    if "npm" in managers:
        commands.append("npm install")

    elif "pnpm" in managers:
        commands.append("pnpm install")

    elif "Yarn" in managers:
        commands.append("yarn install")

    elif "Bun" in managers:
        commands.append("bun install")

    if "Cargo" in managers:
        commands.append("cargo build")

    if "Go Modules" in managers:
        commands.append("go mod download")

    return commands


def generate_usage(project: ProjectInfo) -> str:
    sections: list[str] = []

    usage_intro = generate_usage_intro(project)

    if usage_intro:
        sections.append(usage_intro)

    cli_section = generate_cli_usage(project)

    if cli_section:
        sections.append(cli_section)

    package_script_section = generate_package_script_usage(project)

    if package_script_section:
        sections.append(package_script_section)

    if not sections:
        return ""

    return "\n\n".join(
        [
            "## Usage",
            *sections,
        ]
    )


def generate_usage_intro(project: ProjectInfo) -> str:
    if not project.analysis:
        return ""

    return project.analysis.usage_summary.strip()


def generate_cli_usage(project: ProjectInfo) -> str:
    if not project.cli_commands:
        return ""

    lines = [
        "### CLI",
        "",
    ]

    for command_name in project.cli_commands:
        lines.extend(
            [
                "```bash",
                f"{command_name} [PATH]",
                "```",
                "",
            ]
        )

    return "\n".join(lines).rstrip()


def generate_package_script_usage(project: ProjectInfo) -> str:
    if not project.package_scripts:
        return ""

    lines = [
        "### Scripts",
        "",
    ]

    for script_name in project.package_scripts:
        command = get_package_script_command(
            project,
            script_name,
        )

        lines.extend(
            [
                f"**{script_name}**",
                "",
                "```bash",
                command,
                "```",
                "",
            ]
        )

    return "\n".join(lines).rstrip()


def get_package_script_command(
    project: ProjectInfo,
    script_name: str,
) -> str:
    managers = set(project.package_managers)

    if "npm" in managers:
        return f"npm run {script_name}"

    if "pnpm" in managers:
        return f"pnpm {script_name}"

    if "Yarn" in managers:
        return f"yarn {script_name}"

    if "Bun" in managers:
        return f"bun run {script_name}"

    return script_name


def generate_architecture(project: ProjectInfo) -> str:
    if not project.analysis:
        return ""

    if not project.analysis.architecture:
        return ""

    return "\n".join(
        [
            "## Architecture",
            "",
            project.analysis.architecture,
        ]
    )


def generate_structure(project: ProjectInfo) -> str:
    if not project.directory_tree:
        return ""

    lines = [
        "## Project Structure",
        "",
        "```text",
        *project.directory_tree,
        "```",
    ]

    return "\n".join(lines)


def generate_license(project: ProjectInfo) -> str:
    if not project.license:
        return ""

    return "\n".join(
        [
            "## License",
            "",
            f"This project is licensed under {project.license}.",
        ]
    )