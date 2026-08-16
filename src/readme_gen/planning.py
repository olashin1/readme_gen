from readme_gen.models import ProjectInfo


def plan_readme_sections(project: ProjectInfo) -> list[str]:
    """Plan README sections from capabilities before LLM composition."""
    sections = ["header"]

    has_description = bool(
        project.description
        or (project.repository and project.repository.description)
        or project.context_files
    )
    if project.features or has_description:
        sections.extend(["highlights", "overview"])

    if any(asset.kind == "screenshot" for asset in project.assets):
        sections.append("screenshots")

    if project.languages or project.technology_roles or project.package_managers:
        sections.append("tech_stack")

    install_commands = [command for command in project.commands if command.kind == "install"]
    build_commands = [command for command in project.commands if command.kind == "build"]
    test_commands = [
        command
        for command in project.commands
        if command.kind in {"test", "lint"}
    ]
    usage_commands = [
        command
        for command in project.commands
        if command.kind in {"development", "run", "script", "task", "usage"}
    ]

    install_managers = {"Bun", "Pipenv", "Poetry", "Yarn", "npm", "pip", "pnpm", "uv"}
    if (
        project.packages
        or install_commands
        or install_managers.intersection(project.package_managers)
    ):
        sections.append("installation")
    if build_commands:
        sections.append("building")
    if usage_commands or project.cli_commands:
        sections.append("usage")
    if project.usage_examples:
        sections.append("examples")
    if any(interface.kind == "http" for interface in project.interfaces):
        sections.append("interfaces")
    if project.environment_variables:
        sections.append("environment")
    if test_commands:
        sections.append("testing")

    if (
        project.architecture_components
        or project.project_type == "full-stack"
        or len(project.components) > 1
        or (project.analysis and project.analysis.architecture.strip())
    ):
        sections.append("architecture")
    if len(project.directory_tree) > 1:
        sections.append("structure")
    if project.repository:
        sections.append("repository")
    if project.packages and install_commands:
        sections.append("development")
    if project.license or (
        project.repository
        and (project.repository.license_spdx_id or project.repository.license_name)
    ):
        sections.append("license")
    return sections
