from __future__ import annotations

from pathlib import Path

from readme_gen.detectors.structure import IGNORED_DIRS
from readme_gen.models import ProjectInfo


MAX_SOURCE_CHILDREN = 8
MAX_GENERAL_DIRECTORIES = 5


DIRECTORY_DESCRIPTIONS = {
    "src": "Source code",
    "tests": "Test suite",
    "test": "Test suite",
    "docs": "Documentation",
    "doc": "Documentation",
    "examples": "Examples",
    "example": "Examples",
    ".github": "GitHub configuration",
    "scripts": "Development scripts",
    "tools": "Development tools",
    "assets": "Static assets",
    "public": "Public assets",
    "config": "Configuration",
    "configs": "Configuration",
}


IMPORTANT_FILE_DESCRIPTIONS = {
    "pyproject.toml": "Python project configuration",
    "package.json": "JavaScript project configuration",
    "Cargo.toml": "Rust project configuration",
    "go.mod": "Go module definition",
    "CMakeLists.txt": "CMake build configuration",
    "Dockerfile": "Container definition",
    "docker-compose.yml": "Container services",
    "docker-compose.yaml": "Container services",
    "compose.yml": "Container services",
    "compose.yaml": "Container services",
    "README.md": "Project documentation",
    "README.rst": "Project documentation",
}


def build_structure_preview(
    project: ProjectInfo,
) -> list[str]:
    """
    Build a concise, semantic repository tree for README presentation.

    Unlike the scanner's full directory tree, this representation focuses on
    the parts of the repository that help a reader understand its structure.
    """
    root_name = get_structure_root_name(project)

    entries = collect_top_level_entries(project)

    lines = [
        f"{root_name}/",
    ]

    if not entries:
        return lines

    for index, entry in enumerate(entries):
        is_last = index == len(entries) - 1

        connector = (
            "└──"
            if is_last
            else "├──"
        )

        lines.append(
            format_entry(
                connector,
                entry,
            )
        )

        if entry.is_dir():
            child_lines = build_directory_children(
                project=project,
                directory=entry,
                parent_is_last=is_last,
            )

            lines.extend(child_lines)

    return lines


def get_structure_root_name(
    project: ProjectInfo,
) -> str:
    """
    Return a stable display name instead of a temporary GitHub archive name.
    """
    if project.repository and project.repository.name:
        return project.repository.name

    return project.name


def collect_top_level_entries(
    project: ProjectInfo,
) -> list[Path]:
    """
    Select the most useful top-level repository entries for the README tree.
    """
    root = project.root

    if not root.exists():
        return []

    entries_by_name = {
        path.name: path
        for path in root.iterdir()
    }

    selected: list[Path] = []
    seen: set[str] = set()

    def add(name: str) -> None:
        path = entries_by_name.get(name)

        if path is None:
            return

        if name in seen:
            return

        selected.append(path)
        seen.add(name)

    # Source code should appear first.
    for source_dir in project.source_dirs:
        top_level = Path(source_dir).parts[0]

        if top_level:
            add(top_level)

    # Tests are generally the next most structurally meaningful directory.
    for test_dir in project.test_dirs:
        top_level = Path(test_dir).parts[0]

        if top_level:
            add(top_level)

    # Common useful repository directories.
    for name in (
        "docs",
        "examples",
        "scripts",
        "tools",
        "assets",
        "public",
        "config",
        "configs",
        ".github",
    ):
        add(name)

    # Add a few other visible top-level directories when they have not already
    # been represented.
    general_directories = [
        path
        for path in sorted(
            root.iterdir(),
            key=lambda item: item.name.lower(),
        )
        if path.is_dir()
        and not path.name.startswith(".")
        and path.name not in seen
        and path.name not in IGNORED_DIRS
    ]

    for path in general_directories[
        :MAX_GENERAL_DIRECTORIES
    ]:
        selected.append(path)
        seen.add(path.name)

    # Important configuration files belong at the end.
    important_names = {
        Path(file_name).name
        for file_name in project.important_files
    }

    preferred_files = [
        "pyproject.toml",
        "package.json",
        "Cargo.toml",
        "go.mod",
        "CMakeLists.txt",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",
        "LICENSE",
        "LICENSE.txt",
        "LICENSE.md",
        "README.md",
        "README.rst",
    ]

    for name in preferred_files:
        if (
            name in important_names
            or name in entries_by_name
        ):
            add(name)

    return selected


def build_directory_children(
    project: ProjectInfo,
    directory: Path,
    parent_is_last: bool,
) -> list[str]:
    """
    Render a small amount of useful second-level structure.

    Source directories and GitHub workflow directories receive special
    treatment. Other directories remain summarized at the top level.
    """
    if directory.name in project.source_dirs:
        return build_source_children(
            directory,
            parent_is_last,
        )

    if directory.name == "src":
        return build_source_children(
            directory,
            parent_is_last,
        )

    if directory.name == ".github":
        workflows = directory / "workflows"

        if workflows.is_dir():
            prefix = (
                "    "
                if parent_is_last
                else "│   "
            )

            return [
                (
                    f"{prefix}└── workflows/"
                    "  # CI/CD workflows"
                )
            ]

    return []


def build_source_children(
    directory: Path,
    parent_is_last: bool,
) -> list[str]:
    """
    Show the primary packages/modules immediately beneath a source directory.
    """
    try:
        children = [
            path
            for path in sorted(
                directory.iterdir(),
                key=lambda item: item.name.lower(),
            )
            if (
                path.is_dir()
                and not path.name.startswith(".")
                and path.name != "__pycache__"
            )
        ]
    except OSError:
        return []

    children = children[
        :MAX_SOURCE_CHILDREN
    ]

    if not children:
        return []

    prefix = (
        "    "
        if parent_is_last
        else "│   "
    )

    lines: list[str] = []

    for index, child in enumerate(children):
        is_last = (
            index == len(children) - 1
        )

        connector = (
            "└──"
            if is_last
            else "├──"
        )

        lines.append(
            f"{prefix}{connector} {child.name}/"
        )

    return lines


def format_entry(
    connector: str,
    entry: Path,
) -> str:
    """
    Format a tree entry with an optional concise description.
    """
    display_name = entry.name

    if entry.is_dir():
        display_name += "/"

    description = get_entry_description(
        entry
    )

    if description:
        return (
            f"{connector} {display_name}"
            f"  # {description}"
        )

    return f"{connector} {display_name}"


def get_entry_description(
    entry: Path,
) -> str | None:
    if entry.is_dir():
        return DIRECTORY_DESCRIPTIONS.get(
            entry.name
        )

    if entry.name.upper().startswith(
        "LICENSE"
    ):
        return "License"

    return IMPORTANT_FILE_DESCRIPTIONS.get(
        entry.name
    )
