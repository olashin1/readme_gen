import os
from pathlib import Path

from readme_gen.detectors.context import detect_context_files
from readme_gen.detectors.assets import detect_assets
from readme_gen.detectors.commands import detect_commands
from readme_gen.detectors.components import (
    detect_components,
    detect_deployment_files,
)
from readme_gen.detectors.dependencies import detect_dependencies
from readme_gen.detectors.environment import detect_environment_variables
from readme_gen.detectors.entrypoints import detect_executable_interfaces
from readme_gen.detectors.languages import detect_languages
from readme_gen.detectors.metadata import detect_metadata
from readme_gen.detectors.package_managers import detect_package_managers
from readme_gen.detectors.packages import detect_packages
from readme_gen.detectors.project_type import detect_project_type
from readme_gen.detectors.routes import detect_api_routes
from readme_gen.detectors.structure import (
    IGNORED_DIRS,
    build_directory_tree,
    detect_structure,
    is_ignored_directory,
)
from readme_gen.detectors.technologies import (
    detect_technologies,
    group_technology_roles,
)
from readme_gen.detectors.usage_examples import detect_usage_examples
from readme_gen.detectors.workflows import detect_workflows
from readme_gen.models import ProjectInfo
from readme_gen.normalization import normalize_interfaces
from readme_gen.planning import plan_readme_sections


def get_project_files(root: Path) -> list[Path]:
    files: list[Path] = []

    for current, directory_names, file_names in os.walk(root):
        directory_names[:] = sorted(
            name
            for name in directory_names
            if name not in IGNORED_DIRS
            and not is_ignored_directory(Path(current) / name)
        )
        current_path = Path(current)
        files.extend(
            current_path / name
            for name in sorted(file_names)
            if name != ".DS_Store"
        )

    return files


def scan_project(root: Path) -> ProjectInfo:
    root = root.resolve()

    project = ProjectInfo(
        name=root.name,
        root=root,
    )

    files = get_project_files(root)

    project.languages = detect_languages(files)

    project.package_managers = (
        detect_package_managers(
            root,
            files,
        )
    )

    detect_metadata(
        root,
        project,
    )

    dependencies, dev_dependencies = detect_dependencies(root, files)
    project.dependencies = list(dict.fromkeys(project.dependencies + dependencies))
    project.dev_dependencies = list(dict.fromkeys(project.dev_dependencies + dev_dependencies))

    (
        project.source_dirs,
        project.test_dirs,
        project.important_files,
    ) = detect_structure(
        root,
        files,
    )

    project.context_files = (
        detect_context_files(
            root,
            files,
        )
    )

    project.workflows = detect_workflows(
        root
    )

    project.packages = detect_packages(
        root
    )

    project.usage_examples = detect_usage_examples(
        root
    )

    project.environment_variables = (
        detect_environment_variables(
            root,
            files,
        )
    )

    project.api_routes = detect_api_routes(
        root,
        files,
    )

    project.assets = detect_assets(
        root,
        files,
    )

    project.technologies = detect_technologies(
        root,
        files,
    )

    project.frameworks = _technology_names(
        project,
        "framework",
    )
    project.libraries = _technology_names(
        project,
        "library",
    )
    project.databases = _technology_names(
        project,
        "database",
    )
    project.external_services = _technology_names(
        project,
        "service",
    )
    project.build_tools = _technology_names(
        project,
        "build tool",
    )
    project.technology_roles = group_technology_roles(
        project.technologies
    )
    project.frontend = project.technology_roles.get(
        "Frontend",
        [],
    )
    project.backend = project.technology_roles.get(
        "Backend",
        [],
    )

    project.components = detect_components(
        root,
        files,
        project,
    )
    project.deployment_files = detect_deployment_files(
        root,
        files,
    )

    project.directory_tree = (
        build_directory_tree(
            root
        )
    )

    project.commands = detect_commands(
        root,
        files,
        project,
    )

    project.interfaces = [
        *normalize_interfaces(project),
        *detect_executable_interfaces(root, files),
    ]

    project.project_type = (
        detect_project_type(
            project
        )
    )

    project.section_plan = plan_readme_sections(project)

    return project


def _technology_names(
    project: ProjectInfo,
    category: str,
) -> list[str]:
    names: list[str] = []
    for technology in project.technologies:
        if technology.category != category:
            continue
        if technology.name not in names:
            names.append(technology.name)
    return names
