import json
import tomllib

from pathlib import Path


JAVASCRIPT_FRAMEWORKS = {
    "react": "React",
    "next": "Next.js",
    "vue": "Vue",
    "@angular/core": "Angular",
    "svelte": "Svelte",
    "express": "Express",
    "fastify": "Fastify",
}

PYTHON_FRAMEWORKS = {
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
}


def detect_frameworks(root: Path) -> list[str]:
    frameworks = []

    frameworks.extend(detect_javascript_frameworks(root))
    frameworks.extend(detect_python_frameworks(root))

    return frameworks


def detect_javascript_frameworks(root: Path) -> list[str]:
    package_json = root / "package.json"

    if not package_json.exists():
        return []

    try:
        data = json.loads(package_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    dependencies = {
        **data.get("dependencies", {}),
        **data.get("devDependencies", {}),
    }

    return [
        display_name
        for package, display_name in JAVASCRIPT_FRAMEWORKS.items()
        if package in dependencies
    ]


def detect_python_frameworks(root: Path) -> list[str]:
    pyproject = root / "pyproject.toml"

    if not pyproject.exists():
        return []

    try:
        with pyproject.open("rb") as file:
            data = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        return []

    dependencies = data.get("project", {}).get("dependencies", [])

    detected = []

    for dependency in dependencies:
        package_name = dependency.split("[")[0]
        package_name = package_name.split(">=")[0]
        package_name = package_name.split("==")[0]
        package_name = package_name.strip().lower()

        if package_name in PYTHON_FRAMEWORKS:
            detected.append(PYTHON_FRAMEWORKS[package_name])

    return detected