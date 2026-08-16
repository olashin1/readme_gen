from readme_gen.models import Interface, ProjectInfo


def normalize_interfaces(project: ProjectInfo) -> list[Interface]:
    """Convert framework-specific and package facts to generic interfaces."""
    interfaces = [
        Interface(
            kind="http",
            method=route.method,
            path=route.path,
            name=route.handler,
            source=route.source,
        )
        for route in project.api_routes
    ]

    for command in project.commands:
        is_cli_run = bool(project.technology_roles.get("CLI")) and command.kind == "run"
        if command.kind != "usage" and not is_cli_run:
            continue
        interfaces.append(
            Interface(
                kind="cli",
                name=command.name or project.name,
                target=command.command,
                source=command.source,
            )
        )

    for package in project.packages:
        interfaces.append(
            Interface(
                kind="package",
                name=package.name,
                target=package.ecosystem,
                source=package.manifest,
            )
        )

    unique: dict[tuple[object, ...], Interface] = {}
    for interface in interfaces:
        key = (
            interface.kind,
            interface.method,
            interface.path,
            interface.name,
            interface.target,
        )
        unique.setdefault(key, interface)
    return list(unique.values())
