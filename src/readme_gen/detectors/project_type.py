from readme_gen.models import ProjectInfo


FRONTEND_FRAMEWORKS = {
    "React",
    "Next.js",
    "Vue",
    "Angular",
    "Svelte",
}

BACKEND_FRAMEWORKS = {
    "FastAPI",
    "Flask",
    "Django",
    "Express",
    "Fastify",
}


def detect_project_type(project: ProjectInfo) -> str:
    frameworks = set(project.frameworks)

    has_frontend = bool(
        frameworks.intersection(FRONTEND_FRAMEWORKS)
    )

    has_backend = bool(
        frameworks.intersection(BACKEND_FRAMEWORKS)
    )

    has_cli = bool(
        project.cli_commands
        or project.technology_roles.get("CLI")
        or any(interface.kind == "cli" for interface in project.interfaces)
    )

    if has_frontend and has_backend:
        return "full-stack"

    if has_cli:
        return "cli"

    if has_frontend:
        return "frontend"

    if has_backend:
        return "backend"

    if any(interface.kind == "executable" for interface in project.interfaces):
        return "application"

    if is_library(project):
        return "library"

    return "application"


def is_library(project: ProjectInfo) -> bool:
    if project.packages:
        return True

    if not project.source_dirs:
        return False

    if project.cli_commands:
        return False

    if project.package_scripts:
        return False

    return True
