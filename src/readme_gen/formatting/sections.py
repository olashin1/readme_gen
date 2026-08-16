from __future__ import annotations

from pathlib import PurePosixPath

from readme_gen.formatting.badges import generate_badges
from readme_gen.formatting.structure import build_structure_preview
from readme_gen.models import ProjectInfo


def render_header(
    project: ProjectInfo,
) -> str:
    """
    Render the GitHub-facing project hero/header.
    """
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


def render_overview(
    project: ProjectInfo,
) -> str:
    summary = None

    if project.analysis:
        summary = project.analysis.summary.strip()

    if not summary:
        return ""

    return "\n".join(
        [
            "## ✨ Overview",
            "",
            summary,
        ]
    )


def render_features(
    project: ProjectInfo,
) -> str:
    if not project.analysis:
        return ""

    features = [
        feature.strip()
        for feature in project.analysis.features
        if feature.strip()
    ]

    if not features:
        return ""

    lines = [
        "## 🚀 Features",
        "",
    ]

    lines.extend(
        f"- {feature}"
        for feature in features
    )

    return "\n".join(lines)


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

    if project.frameworks:
        rows.append(
            (
                "Frameworks",
                ", ".join(project.frameworks),
            )
        )

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
        "## 🛠️ Tech Stack",
        "",
        "| Category | Technologies |",
        "| --- | --- |",
    ]

    for category, technologies in rows:
        lines.append(
            f"| **{category}** | {technologies} |"
        )

    return "\n".join(lines)


def render_quick_start(
    project: ProjectInfo,
) -> str:
    install_commands = detect_install_commands(
        project
    )

    cli_commands = list(
        project.cli_commands.keys()
    )

    script_commands = get_useful_script_commands(
        project
    )

    if not (
        install_commands
        or cli_commands
        or script_commands
    ):
        return ""

    lines = [
        "## ⚡ Quick Start",
    ]

    clone_lines = get_clone_commands(
        project,
        install_commands,
    )

    if clone_lines:
        lines.extend(
            [
                "",
                "### Installation",
                "",
                "```bash",
                *clone_lines,
                "```",
            ]
        )

    usage_intro = get_usage_intro(
        project
    )

    if (
        usage_intro
        or cli_commands
        or script_commands
    ):
        lines.extend(
            [
                "",
                "### Usage",
            ]
        )

    if usage_intro:
        lines.extend(
            [
                "",
                usage_intro,
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
                "#### Common scripts",
                "",
                "```bash",
                *script_commands,
                "```",
            ]
        )

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
            "## 🏗️ Architecture",
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
            "## 📁 Project Structure",
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
        "## 🔗 Repository",
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
            "## 📄 License",
            "",
            body,
        ]
    )


def get_display_name(
    project: ProjectInfo,
) -> str:
    """
    Return the best human-facing project name.

    Scanner/project metadata is preferred over the repository slug because
    repository names may be lowercase or otherwise machine-oriented.
    """
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
    if project.description:
        return project.description.strip()

    if (
        project.repository
        and project.repository.description
    ):
        return (
            project.repository.description.strip()
        )

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
    if not install_commands:
        return []

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
        commands.append(
            "poetry install"
        )

    elif "Pipenv" in managers:
        commands.append(
            "pipenv install"
        )

    elif "pip" in managers:
        commands.append(
            "pip install -r requirements.txt"
        )

    if "npm" in managers:
        commands.append(
            "npm install"
        )

    elif "pnpm" in managers:
        commands.append(
            "pnpm install"
        )

    elif "Yarn" in managers:
        commands.append(
            "yarn install"
        )

    elif "Bun" in managers:
        commands.append(
            "bun install"
        )

    if "Cargo" in managers:
        commands.append(
            "cargo build"
        )

    if "Go Modules" in managers:
        commands.append(
            "go mod download"
        )

    return commands


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
        return (
            f"npm run {script_name}"
        )

    if "pnpm" in managers:
        return (
            f"pnpm {script_name}"
        )

    if "Yarn" in managers:
        return (
            f"yarn {script_name}"
        )

    if "Bun" in managers:
        return (
            f"bun run {script_name}"
        )

    return script_name


def get_license_name(
    project: ProjectInfo,
) -> str | None:
    """
    Return the best human-facing license name.

    A real SPDX/license name from repository metadata is preferred over a
    scanner value that merely identifies a license filename.
    """
    repository = project.repository

    if repository:
        if repository.license_spdx_id:
            return repository.license_spdx_id

        if repository.license_name:
            return repository.license_name

    if project.license and not looks_like_license_filename(
        project.license
    ):
        return project.license

    return project.license


def get_license_link(
    project: ProjectInfo,
) -> str | None:
    repository = project.repository

    if not repository:
        return None

    if not repository.url:
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


def looks_like_license_filename(
    value: str,
) -> bool:
    """
    Return True when a detected license value looks like a filename rather
    than a license identifier.
    """
    normalized = value.strip().lower()

    return normalized.startswith(
        (
            "license.",
            "licence.",
            "copying.",
        )
    )