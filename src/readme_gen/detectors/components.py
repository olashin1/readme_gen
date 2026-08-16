from __future__ import annotations

import json
import tomllib
from collections import defaultdict
from pathlib import Path

from readme_gen.detectors.languages import detect_languages
from readme_gen.detectors.path_filters import is_test_file
from readme_gen.models import ProjectComponent, ProjectInfo


MANIFEST_ECOSYSTEMS = {
    "package.json": "JavaScript/Node.js",
    "pyproject.toml": "Python",
    "requirements.txt": "Python",
    "Cargo.toml": "Rust",
    "go.mod": "Go",
    "pom.xml": "Java/Maven",
    "build.gradle": "Java/Gradle",
    "build.gradle.kts": "JVM/Gradle",
    "CMakeLists.txt": "C/C++",
}


def detect_components(
    root: Path,
    files: list[Path],
    project: ProjectInfo,
) -> list[ProjectComponent]:
    """Group manifests into repository components without assuming a stack."""
    grouped: defaultdict[Path, set[str]] = defaultdict(set)
    for path in files:
        if is_test_file(root, path):
            continue
        ecosystem = _manifest_ecosystem(path)
        if ecosystem:
            grouped[path.parent].add(ecosystem)

    components: list[ProjectComponent] = []
    for directory, ecosystems in sorted(
        grouped.items(),
        key=lambda item: item[0].relative_to(root).as_posix(),
    ):
        relative = directory.relative_to(root).as_posix()
        relative = "." if relative == "." else relative
        scoped_files = [
            path
            for path in files
            if path == directory or directory in path.parents
            if not is_test_file(root, path)
        ]
        components.append(
            ProjectComponent(
                name=_component_name(directory, root, project.name),
                path=relative,
                ecosystems=tuple(sorted(ecosystems)),
                languages=tuple(detect_languages(scoped_files)),
            )
        )

    if components:
        return components

    for source_dir in project.source_dirs:
        directory = root / source_dir
        scoped_files = [path for path in files if directory in path.parents]
        components.append(
            ProjectComponent(
                name=directory.name,
                path=source_dir,
                languages=tuple(detect_languages(scoped_files)),
            )
        )
    return components


def detect_deployment_files(root: Path, files: list[Path]) -> list[str]:
    detected: list[str] = []
    exact_names = {
        "Dockerfile",
        "compose.yml",
        "compose.yaml",
        "docker-compose.yml",
        "docker-compose.yaml",
        "fly.toml",
        "netlify.toml",
        "render.yaml",
        "vercel.json",
    }
    for path in files:
        if is_test_file(root, path):
            continue
        relative = path.relative_to(root).as_posix()
        parts = {part.lower() for part in path.relative_to(root).parts}
        is_kubernetes_config = (
            ("k8s" in parts or "kubernetes" in parts)
            and (path.suffix.lower() in {".json", ".yaml", ".yml"} or path.name == "Chart.yaml")
        )
        if path.name in exact_names or path.name.lower().startswith("dockerfile") or is_kubernetes_config:
            detected.append(relative)
    return sorted(dict.fromkeys(detected))


def _manifest_ecosystem(path: Path) -> str | None:
    if path.suffix.lower() == ".csproj":
        return ".NET"
    return MANIFEST_ECOSYSTEMS.get(path.name)


def _component_name(directory: Path, root: Path, fallback: str) -> str:
    package_json = directory / "package.json"
    if package_json.is_file():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            if isinstance(data.get("name"), str) and data["name"].strip():
                return data["name"].strip()
        except (OSError, json.JSONDecodeError):
            pass

    for filename, tables in (
        ("pyproject.toml", ("project",)),
        ("Cargo.toml", ("package",)),
    ):
        manifest = directory / filename
        if not manifest.is_file():
            continue
        try:
            with manifest.open("rb") as file:
                data = tomllib.load(file)
            value = data
            for table in tables:
                value = value.get(table, {})
            name = value.get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()
        except (OSError, tomllib.TOMLDecodeError):
            pass

    return fallback if directory == root else directory.name
