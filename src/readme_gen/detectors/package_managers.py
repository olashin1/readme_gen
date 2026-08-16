import json
from pathlib import Path

from readme_gen.detectors.path_filters import is_test_file

PACKAGE_MANAGER_FILES = {
    "uv.lock": "uv",
    "poetry.lock": "Poetry",
    "Pipfile": "Pipenv",
    "requirements.txt": "pip",
    "package-lock.json": "npm",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "Yarn",
    "bun.lock": "Bun",
    "bun.lockb": "Bun",
    "Cargo.lock": "Cargo",
    "Cargo.toml": "Cargo",
    "go.mod": "Go Modules",
    "pom.xml": "Maven",
    "build.gradle": "Gradle",
    "build.gradle.kts": "Gradle",
}


def detect_package_managers(
    root: Path,
    files: list[Path] | None = None,
) -> list[str]:
    detected: list[str] = []

    candidates = files or [path for path in root.rglob("*") if path.is_file()]
    candidates = [path for path in candidates if not is_test_file(root, path)]

    names = {path.name for path in candidates}
    for filename, manager in PACKAGE_MANAGER_FILES.items():
        if filename in names:
            detected.append(manager)

    if "package.json" in names and not {"npm", "pnpm", "Yarn", "Bun"}.intersection(detected):
        declared_manager = _declared_javascript_manager(candidates)
        detected.append(declared_manager or "npm")

    if "pyproject.toml" in names and not {"uv", "Poetry", "Pipenv", "pip"}.intersection(detected):
        detected.append("pip")

    if any(path.suffix.lower() == ".csproj" for path in candidates):
        detected.append("dotnet")

    return list(dict.fromkeys(detected))


def _declared_javascript_manager(files: list[Path]) -> str | None:
    display_names = {
        "bun": "Bun",
        "npm": "npm",
        "pnpm": "pnpm",
        "yarn": "Yarn",
    }
    for path in files:
        if path.name != "package.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        declared = data.get("packageManager")
        if isinstance(declared, str):
            name = declared.split("@", 1)[0].lower()
            if name in display_names:
                return display_names[name]
    return None
