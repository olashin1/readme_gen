from pathlib import Path

from readme_gen.detectors.path_filters import is_test_file


HIGH_PRIORITY_FILES = {
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env.example",
}

ENTRY_FILE_NAMES = {
    "main.py",
    "app.py",
    "server.py",
    "cli.py",
    "index.js",
    "index.ts",
    "main.js",
    "main.ts",
    "main.tsx",
    "App.jsx",
    "App.tsx",
}

SOURCE_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".cc",
    ".cxx",
    ".c",
    ".cs",
    ".go",
    ".rs",
}


def detect_context_files(
    root: Path,
    files: list[Path],
    max_files: int = 12,
) -> list[str]:
    files = [path for path in files if not is_test_file(root, path)]
    selected: list[Path] = []

    # Package/configuration files first.
    for file in files:
        if file.name in HIGH_PRIORITY_FILES:
            selected.append(file)

    # Likely application entry points.
    for file in files:
        if file.name in ENTRY_FILE_NAMES:
            selected.append(file)

    # Add a few source files if we still don't have much context.
    for file in files:
        if len(selected) >= max_files:
            break

        if file.suffix.lower() not in SOURCE_SUFFIXES:
            continue

        if file in selected:
            continue

        selected.append(file)

    # Remove duplicates while preserving order.
    unique: list[Path] = []

    for file in selected:
        if file not in unique:
            unique.append(file)

    return [
        file.relative_to(root).as_posix()
        for file in unique[:max_files]
    ]
