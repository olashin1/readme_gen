from pathlib import Path


SOURCE_DIR_NAMES = {
    "src",
    "app",
    "lib",
    "frontend",
    "backend",
    "client",
    "server",
}

TEST_DIR_NAMES = {
    "tests",
    "test",
    "__tests__",
}

IMPORTANT_FILE_NAMES = {
    "pyproject.toml",
    "package.json",
    "vite.config.ts",
    "vite.config.js",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Dockerfile",
    ".env.example",
    "Makefile",
    "README.md",
}

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".next",
    ".idea",
    ".vscode",
    "dist",
    "build",
    "coverage",
}

IGNORED_FILES = {
    ".env",
    "README.generated.md",
    ".coverage",
}


def detect_structure(
    root: Path,
    files: list[Path],
) -> tuple[list[str], list[str], list[str]]:
    source_dirs: list[str] = []
    test_dirs: list[str] = []
    important_files: list[str] = []

    for item in root.iterdir():
        if not item.is_dir():
            continue

        if item.name in SOURCE_DIR_NAMES:
            source_dirs.append(item.name)

        if item.name in TEST_DIR_NAMES:
            test_dirs.append(item.name)

    for file in files:
        if file.name in IMPORTANT_FILE_NAMES:
            important_files.append(
                file.relative_to(root).as_posix()
            )

    return (
        sorted(source_dirs),
        sorted(test_dirs),
        sorted(important_files),
    )


def build_directory_tree(
    root: Path,
    max_depth: int = 3,
) -> list[str]:
    lines = [f"{root.name}/"]

    _walk_tree(
        current=root,
        lines=lines,
        prefix="",
        depth=0,
        max_depth=max_depth,
    )

    return lines


def _walk_tree(
    current: Path,
    lines: list[str],
    prefix: str,
    depth: int,
    max_depth: int,
) -> None:
    if depth >= max_depth:
        return

    items = [
        item
        for item in current.iterdir()
        if item.name not in IGNORED_DIRS
        and item.name not in IGNORED_FILES
    ]

    items.sort(
        key=lambda item: (
            item.is_file(),
            item.name.lower(),
        )
    )

    for index, item in enumerate(items):
        is_last = index == len(items) - 1

        branch = "└── " if is_last else "├── "
        lines.append(f"{prefix}{branch}{item.name}")

        if item.is_dir():
            child_prefix = (
                prefix + ("    " if is_last else "│   ")
            )

            _walk_tree(
                current=item,
                lines=lines,
                prefix=child_prefix,
                depth=depth + 1,
                max_depth=max_depth,
            )