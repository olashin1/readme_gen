from readme_gen.models import ProjectInfo


def generate_readme(project: ProjectInfo) -> str:
    sections = [
        generate_header(project),
        generate_tech_stack(project),
        generate_installation(project),
        generate_usage(project),
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
        lines.append("")
        lines.append(project.description)

    return "\n".join(lines)


def generate_tech_stack(project: ProjectInfo) -> str:
    if not (
        project.languages
        or project.frameworks
        or project.package_managers
    ):
        return ""

    lines = ["## Tech Stack", ""]

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

    lines = [
        "## Installation",
        "",
        "Clone the repository and install dependencies:",
        "",
        "```bash",
        f"git clone {project.repository_url or '<repository-url>'}",
        f"cd {project.name}",
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
    if not project.scripts:
        return ""

    lines = [
        "## Usage",
        "",
    ]

    for name in project.scripts:
        command = get_script_command(
            project,
            name,
        )

        if command:
            lines.extend(
                [
                    f"### {name}",
                    "",
                    "```bash",
                    command,
                    "```",
                    "",
                ]
            )

    return "\n".join(lines).rstrip()


def get_script_command(
    project: ProjectInfo,
    script_name: str,
) -> str | None:
    managers = set(project.package_managers)

    if "uv" in managers:
        return f"uv run {script_name}"

    if "npm" in managers:
        return f"npm run {script_name}"

    if "pnpm" in managers:
        return f"pnpm {script_name}"

    if "Yarn" in managers:
        return f"yarn {script_name}"

    if "Bun" in managers:
        return f"bun run {script_name}"

    return script_name


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