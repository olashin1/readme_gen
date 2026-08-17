from __future__ import annotations

import re
from pathlib import PurePosixPath

from readme_gen.formatting.badges import generate_badges
from readme_gen.formatting.structure import build_structure_preview
from readme_gen.models import PackageInfo, ProjectInfo


def render_header(
    project: ProjectInfo,
) -> str:
    title = get_display_name(project)
    tagline = get_tagline(project)
    badges = generate_badges(project)
    links = get_repository_links(project)

    lines = [
        '<div align="center">',
        "",
        f"# {title}",
    ]

    if tagline:
        lines.extend(
            [
                "",
                f"**{tagline}**",
            ]
        )

    if badges:
        lines.extend(
            [
                "",
                " ".join(badges),
            ]
        )

    if links:
        lines.extend(
            [
                "",
                " • ".join(links),
            ]
        )

    lines.extend(
        [
            "",
            "</div>",
        ]
    )

    return "\n".join(lines)


def render_highlights(
    project: ProjectInfo,
) -> str:
    if not project.analysis:
        return ""

    highlights = [
        highlight.strip()
        for highlight in project.analysis.highlights
        if highlight.strip()
    ]

    if not highlights:
        return ""

    lines = [
        "## Highlights",
        "",
    ]

    lines.extend(
        f"- {highlight}"
        for highlight in highlights
    )

    return "\n".join(lines)


def render_overview(
    project: ProjectInfo,
) -> str:
    if not project.analysis:
        return ""

    summary = project.analysis.summary.strip()

    if not summary:
        return ""

    return "\n".join(
        [
            "## Overview",
            "",
            summary,
        ]
    )


def render_usage(
    project: ProjectInfo,
) -> str:
    usage_summary = get_usage_intro(
        project
    )

    cli_commands = list(
        project.cli_commands.keys()
    )

    script_commands = get_useful_script_commands(
        project
    )

    detected_commands = [
        command
        for command in project.commands
        if command.kind in {"development", "run", "script", "task", "usage"}
        and command.command not in cli_commands
    ]

    if not (
        usage_summary
        or cli_commands
        or script_commands
        or detected_commands
    ):
        return ""

    lines = [
        "## Usage",
    ]

    if usage_summary:
        lines.extend(
            [
                "",
                usage_summary,
            ]
        )

    if cli_commands:
        lines.extend(
            [
                "",
                "### CLI",
            ]
        )

        for command in cli_commands:
            lines.extend(
                [
                    "",
                    "```bash",
                    command,
                    "```",
                ]
            )

    if script_commands:
        lines.extend(
            [
                "",
                "### Common Scripts",
                "",
                "```bash",
                *script_commands,
                "```",
            ]
        )

    if detected_commands:
        lines.extend(
            [
                "",
                "### Project Commands",
                "",
                "| Purpose | Command |",
                "| --- | --- |",
            ]
        )
        for command in detected_commands[:12]:
            purpose = (command.name or command.kind).replace("-", " ").title()
            lines.append(
                f"| {purpose} | `{command.command}` |"
            )

    return "\n".join(lines)


def render_installation(
    project: ProjectInfo,
) -> str:
    package = get_primary_package(
        project
    )

    if package is not None:
        return "\n".join(
            [
                "## Installation",
                "",
                "```bash",
                package.install_command,
                "```",
            ]
        )

    commands = get_detected_install_commands(project) or detect_install_commands(project)

    if not commands:
        return ""

    setup_commands = get_clone_commands(
        project,
        commands,
    )

    if not setup_commands:
        return ""

    return "\n".join(
        [
            "## Installation",
            "",
            "```bash",
            *setup_commands,
            "```",
        ]
    )


def render_development(
    project: ProjectInfo,
) -> str:
    if not project.packages and not project.commands:
        return ""

    install_commands = get_detected_install_commands(project) or detect_install_commands(project)

    if not install_commands:
        return ""

    commands = get_clone_commands(
        project,
        install_commands,
    )

    if not commands:
        return ""

    return "\n".join(
        [
            "## Development",
            "",
            "<details>",
            "<summary>Local development setup</summary>",
            "",
            "```bash",
            *commands,
            "```",
            "",
            "</details>",
        ]
    )


def render_tech_stack(
    project: ProjectInfo,
) -> str:
    rows: list[tuple[str, str]] = []

    if project.languages:
        rows.append(
            (
                "Languages",
                ", ".join(project.languages),
            )
        )

    if project.technology_roles:
        role_labels = {
            "Build": "Build System",
            "CLI": "CLI Framework",
            "Containers": "Deployment",
        }
        for role, technologies in project.technology_roles.items():
            rows.append(
                (
                    role_labels.get(role, role),
                    ", ".join(technologies),
                )
            )

    elif project.frameworks:
        rows.append(
            (
                "Frameworks",
                ", ".join(project.frameworks),
            )
        )

    if project.libraries and not project.technology_roles:
        rows.append(("Libraries", ", ".join(project.libraries)))

    if project.databases and "Database" not in project.technology_roles:
        rows.append(("Database", ", ".join(project.databases)))

    if project.external_services and not project.technology_roles:
        rows.append(("External Services", ", ".join(project.external_services)))

    if project.package_managers:
        rows.append(
            (
                "Package Management",
                ", ".join(
                    project.package_managers
                ),
            )
        )

    if not rows:
        return ""

    lines = [
        "## Tech Stack",
        "",
        "| Category | Technologies |",
        "| --- | --- |",
    ]

    for category, technologies in rows:
        lines.append(
            f"| **{category}** | {technologies} |"
        )

    return "\n".join(lines)


def render_environment_variables(
    project: ProjectInfo,
) -> str:
    if not project.environment_variables:
        return ""

    lines = [
        "## Environment Variables",
        "",
        "The application reads the following variable names. Values are not included in this README.",
        "",
        "| Variable | Detected in |",
        "| --- | --- |",
    ]
    for variable in project.environment_variables:
        sources = ", ".join(f"`{source}`" for source in variable.sources)
        lines.append(f"| `{variable.name}` | {sources} |")
    return "\n".join(lines)


def render_api_routes(
    project: ProjectInfo,
) -> str:
    return render_interfaces(project)


def render_interfaces(
    project: ProjectInfo,
) -> str:
    routes = [
        interface
        for interface in project.interfaces
        if interface.kind == "http" and interface.method and interface.path
    ]
    if not routes:
        return ""

    lines = [
        "## API Endpoints",
        "",
        "| Method | Path | Handler |",
        "| --- | --- | --- |",
    ]
    for route in routes:
        handler = f"`{route.name}`" if route.name else "\u2014"
        lines.append(f"| `{route.method}` | `{route.path}` | {handler} |")
    return "\n".join(lines)


def render_building(
    project: ProjectInfo,
) -> str:
    commands = [
        command.command
        for command in project.commands
        if command.kind == "build"
    ]
    if not commands:
        return ""
    return "\n".join(
        [
            "## Building",
            "",
            "```bash",
            *commands,
            "```",
        ]
    )


def render_testing(
    project: ProjectInfo,
) -> str:
    commands = [
        command.command
        for command in project.commands
        if command.kind in {"test", "lint"}
    ]
    if not commands:
        return ""
    return "\n".join(
        [
            "## Testing",
            "",
            "```bash",
            *commands,
            "```",
        ]
    )


def render_examples(
    project: ProjectInfo,
) -> str:
    examples = [
        example
        for example in project.usage_examples
        if not _contains_unverified_pypi_install(project, example.code)
    ]

    if not examples:
        return ""

    heading = "Quick Start" if project.project_type == "library" else "Examples"
    lines = [f"## {heading}"]
    for index, example in enumerate(examples, start=1):
        if len(examples) > 1:
            lines.extend(["", f"### Example {index}"])
        lines.extend(
            [
                "",
                f"```{example.language}",
                example.code,
                "```",
            ]
        )
    return "\n".join(lines)


def _contains_unverified_pypi_install(
    project: ProjectInfo,
    code: str,
) -> bool:
    verified_names = {
        re.sub(r"[-_.]+", "-", package.name).lower()
        for package in project.packages
        if package.ecosystem == "pypi"
    }
    project_name = re.sub(r"[-_.]+", "-", project.name).lower()
    if project_name in verified_names:
        return False

    for line in code.splitlines():
        match = re.match(
            r"^\s*(?:\$\s*)?(?:(?:python|python3)\s+-m\s+)?pip\s+install\s+([^\s]+)",
            line,
        )
        if not match:
            continue
        package_name = re.split(
            r"[<>=!~;\[]",
            match.group(1).strip("'\""),
            maxsplit=1,
        )[0]
        if re.sub(r"[-_.]+", "-", package_name).lower() == project_name:
            return True

    return False


def render_screenshots(
    project: ProjectInfo,
) -> str:
    screenshots = [asset for asset in project.assets if asset.kind == "screenshot"]
    if not screenshots:
        return ""

    lines = ["## Screenshots"]
    for index, asset in enumerate(screenshots[:4], start=1):
        label = "Project screenshot" if len(screenshots) == 1 else f"Project screenshot {index}"
        lines.extend(["", f"![{label}]({asset.path})"])
    return "\n".join(lines)


def render_architecture(
    project: ProjectInfo,
) -> str:
    if not project.analysis:
        return ""

    architecture = (
        project.analysis.architecture.strip()
    )

    if not architecture:
        return ""

    return "\n".join(
        [
            "## Architecture",
            "",
            architecture,
        ]
    )


def render_structure(
    project: ProjectInfo,
) -> str:
    structure = build_structure_preview(
        project
    )

    if not structure:
        return ""

    return "\n".join(
        [
            "## Project Structure",
            "",
            "```text",
            *structure,
            "```",
        ]
    )


def render_repository_info(
    project: ProjectInfo,
) -> str:
    repository = project.repository

    if not repository:
        return ""

    rows: list[tuple[str, str]] = []

    if repository.default_branch:
        rows.append(
            (
                "Default branch",
                f"`{repository.default_branch}`",
            )
        )

    if repository.topics:
        rows.append(
            (
                "Topics",
                ", ".join(
                    f"`{topic}`"
                    for topic in repository.topics
                ),
            )
        )

    if not rows:
        return ""

    lines = [
        "## Repository",
        "",
        "| | |",
        "| --- | --- |",
    ]

    for label, value in rows:
        lines.append(
            f"| **{label}** | {value} |"
        )

    return "\n".join(lines)


def render_license(
    project: ProjectInfo,
) -> str:
    license_name = get_license_name(
        project
    )

    if not license_name:
        return ""

    license_link = get_license_link(
        project
    )

    if license_link:
        body = (
            f"This project is licensed under the "
            f"[{license_name}]({license_link}) license."
        )
    else:
        body = (
            f"This project is licensed under the "
            f"**{license_name}** license."
        )

    return "\n".join(
        [
            "## License",
            "",
            body,
        ]
    )


def get_primary_package(
    project: ProjectInfo,
) -> PackageInfo | None:
    if not project.packages:
        return None

    return project.packages[0]


def get_display_name(
    project: ProjectInfo,
) -> str:
    if project.name:
        return project.name

    if (
        project.repository
        and project.repository.name
    ):
        return project.repository.name

    return project.root.name


def get_tagline(
    project: ProjectInfo,
) -> str | None:
    if project.analysis:
        tagline = project.analysis.tagline.strip()

        if tagline:
            return tagline

    if project.description:
        return project.description.strip()

    if (
        project.repository
        and project.repository.description
    ):
        return project.repository.description.strip()

    return None


def get_repository_links(
    project: ProjectInfo,
) -> list[str]:
    repository = project.repository

    if not repository:
        return []

    links: list[str] = []

    if repository.url:
        links.append(
            f"[Repository]({repository.url})"
        )

    if repository.homepage:
        links.append(
            f"[Website]({repository.homepage})"
        )

    if repository.issues_url:
        links.append(
            f"[Issues]({repository.issues_url})"
        )

    return links


def get_clone_commands(
    project: ProjectInfo,
    install_commands: list[str],
) -> list[str]:
    repository_url = get_repository_url(
        project
    )

    repository_name = get_repository_name(
        project
    )

    commands: list[str] = []

    if repository_url:
        commands.extend(
            [
                f"git clone {repository_url}",
                f"cd {repository_name}",
            ]
        )

    commands.extend(
        install_commands
    )

    return commands


def get_repository_url(
    project: ProjectInfo,
) -> str | None:
    if (
        project.repository
        and project.repository.url
    ):
        return project.repository.url

    return project.repository_url


def get_repository_name(
    project: ProjectInfo,
) -> str:
    if (
        project.repository
        and project.repository.name
    ):
        return project.repository.name

    return project.root.name


def detect_install_commands(
    project: ProjectInfo,
) -> list[str]:
    commands: list[str] = []

    managers = set(
        project.package_managers
    )

    if "uv" in managers:
        commands.append("uv sync")

    elif "Poetry" in managers:
        commands.append("poetry install")

    elif "Pipenv" in managers:
        commands.append("pipenv install")

    elif "pip" in managers:
        commands.append(
            "pip install -r requirements.txt"
        )

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


def get_detected_install_commands(
    project: ProjectInfo,
) -> list[str]:
    return [
        command.command
        for command in project.commands
        if command.kind == "install"
    ]


def get_usage_intro(
    project: ProjectInfo,
) -> str:
    if not project.analysis:
        return ""

    return (
        project.analysis
        .usage_summary
        .strip()
    )


def get_useful_script_commands(
    project: ProjectInfo,
) -> list[str]:
    if any(command.kind != "install" for command in project.commands):
        return []

    commands: list[str] = []

    preferred_names = (
        "dev",
        "start",
        "build",
        "test",
        "lint",
    )

    for script_name in preferred_names:
        if script_name not in project.package_scripts:
            continue

        commands.append(
            get_package_script_command(
                project,
                script_name,
            )
        )

    return commands


def get_package_script_command(
    project: ProjectInfo,
    script_name: str,
) -> str:
    managers = set(
        project.package_managers
    )

    if "npm" in managers:
        return f"npm run {script_name}"

    if "pnpm" in managers:
        return f"pnpm {script_name}"

    if "Yarn" in managers:
        return f"yarn {script_name}"

    if "Bun" in managers:
        return f"bun run {script_name}"

    return script_name


def get_license_name(
    project: ProjectInfo,
) -> str | None:
    repository = project.repository

    if repository:
        if repository.license_spdx_id:
            return repository.license_spdx_id

        if repository.license_name:
            return repository.license_name

    if project.license:
        return project.license

    return None


def get_license_link(
    project: ProjectInfo,
) -> str | None:
    repository = project.repository

    if not repository or not repository.url:
        return None

    license_file = find_license_file(
        project
    )

    if not license_file:
        return None

    branch = (
        repository.default_branch
        or "main"
    )

    return (
        f"{repository.url}/blob/"
        f"{branch}/{license_file}"
    )


def find_license_file(
    project: ProjectInfo,
) -> str | None:
    for file_name in project.important_files:
        path = PurePosixPath(
            file_name.replace("\\", "/")
        )

        if path.name.upper().startswith(
            "LICENSE"
        ):
            return str(path)

    return None
