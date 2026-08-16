from pathlib import Path

from readme_gen.models import ProjectInfo

import json


PACKAGE_MANAGER_FILES = {
    "uv.lock": "uv",
    "poetry.lock": "Poetry",
    "Pipfile": "Pipenv",
    "requirements.txt": "pip",
    "package-lock.json": "npm",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "Yarn",
    "bun.lock": "Bun",
    "Cargo.lock": "Cargo",
    "go.mod": "Go Modules",
}


def detect_package_managers(root: Path) -> list[str]:
    detected = []

    for filename, manager in PACKAGE_MANAGER_FILES.items():
        if (root / filename).exists():
            detected.append(manager)

    return detected

def detect_package_json(root: Path, project: ProjectInfo) -> None:
    package_json = root / "package.json"

    if not package_json.exists():
        return

    try:
        data = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return

    if data.get("name"):
        project.name = data["name"]

    if data.get("description"):
        project.description = data["description"]

    dependencies = data.get("dependencies", {})
    dev_dependencies = data.get("devDependencies", {})

    project.dependencies.extend(dependencies.keys())
    project.dev_dependencies.extend(dev_dependencies.keys())

    project.package_scripts.update(data.get("scripts", {}))
    
    repository = data.get("repository")

    if isinstance(repository, str):
        project.repository_url = repository

    elif isinstance(repository, dict):
        project.repository_url = repository.get("url")

    if data.get("license"):
        project.license = data["license"]

def detect_license(root: Path, project: ProjectInfo) -> None:
    if project.license:
        return

    license_files = [
        "LICENSE",
        "LICENSE.md",
        "LICENSE.txt",
    ]

    for filename in license_files:
        if (root / filename).exists():
            project.license = filename
            return