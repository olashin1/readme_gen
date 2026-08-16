from pathlib import Path

from readme_gen.detectors.frameworks import detect_frameworks
from readme_gen.detectors.languages import detect_languages
from readme_gen.detectors.metadata import detect_metadata
from readme_gen.detectors.package_managers import detect_package_managers
from readme_gen.detectors.structure import (
    build_directory_tree,
    detect_structure,
)
from readme_gen.models import ProjectInfo


IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".idea",
    ".vscode",
}


def get_project_files(root: Path) -> list[Path]:
    files: list[Path] = []

    for path in root.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue

        if path.is_file():
            files.append(path)

    return files


def scan_project(root: Path) -> ProjectInfo:
    root = root.resolve()

    project = ProjectInfo(
        name=root.name,
        root=root,
    )

    files = get_project_files(root)

    project.languages = detect_languages(files)
    project.frameworks = detect_frameworks(root)
    project.package_managers = detect_package_managers(root)

    detect_metadata(root, project)

    (
        project.source_dirs,
        project.test_dirs,
        project.important_files,
    ) = detect_structure(root, files)

    project.directory_tree = build_directory_tree(root)

    return project