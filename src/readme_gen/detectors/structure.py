from pathlib import Path

from readme_gen.detectors.path_filters import is_test_file


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
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "CMakeLists.txt",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "tailwind.config.js",
    "tailwind.config.ts",
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
    ".cache",
    ".nox",
    ".tox",
    ".next",
    ".idea",
    ".vscode",
    ".gradle",
    "dist",
    "build",
    "target",
    "vendor",
    "out",
    "coverage",
    "htmlcov",
}

IGNORED_FILES = {
    ".env",
    ".DS_Store",
    "README.generated.md",
    ".coverage",
}

MAX_TREE_CHILDREN = 30
MAX_TREE_LINES = 200


def is_ignored_directory(path: Path) -> bool:
    if path.name in IGNORED_DIRS:
        return True
    if path.name not in {"bin", "obj"}:
        return False
    return any(path.parent.glob("*.csproj"))


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
        if is_test_file(root, file):
            continue
        if file.name in IMPORTANT_FILE_NAMES or file.suffix.lower() == ".csproj":
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
    if depth >= max_depth or len(lines) >= MAX_TREE_LINES:
        return

    items = [
        item
        for item in current.iterdir()
        if not (item.is_dir() and is_ignored_directory(item))
        and item.name not in IGNORED_FILES
    ]

    items.sort(
        key=lambda item: (
            item.is_file(),
            item.name.lower(),
        )
    )

    items = items[:MAX_TREE_CHILDREN]

    for index, item in enumerate(items):
        if len(lines) >= MAX_TREE_LINES:
            return
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
