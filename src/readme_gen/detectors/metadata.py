import json
import tomllib
from pathlib import Path

from readme_gen.models import ProjectInfo


def detect_metadata(root: Path, project: ProjectInfo) -> None:
    detect_pyproject(root, project)
    detect_package_json(root, project)
    detect_license(root, project)

def detect_pyproject(root: Path, project: ProjectInfo) -> None:
    pyproject = root / "pyproject.toml"

    if not pyproject.exists():
        return

    try:
        with pyproject.open("rb") as file:
            data = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        return

    project_data = data.get("project", {})

    if project_data.get("name"):
        project.name = project_data["name"]

    if project_data.get("description"):
        project.description = project_data["description"]

    project.dependencies.extend(
        parse_python_dependency(dep)
        for dep in project_data.get("dependencies", [])
    )

    scripts = project_data.get("scripts", {})

    for name, command in scripts.items():
        project.scripts[name] = command
        project.entry_points.append(name)

def parse_python_dependency(dependency: str) -> str:
    dependency = dependency.split(";")[0]
    dependency = dependency.split("[")[0]

    for operator in ("==", ">=", "<=", "~=", "!=", ">", "<"):
        dependency = dependency.split(operator)[0]

    return dependency.strip()

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

    project.scripts.update(data.get("scripts", {}))

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