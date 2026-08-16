from __future__ import annotations

from collections.abc import Callable

from readme_gen.formatting.sections import (
    render_architecture,
    render_development,
    render_header,
    render_highlights,
    render_installation,
    render_license,
    render_overview,
    render_repository_info,
    render_structure,
    render_tech_stack,
    render_usage,
)
from readme_gen.models import ProjectInfo


SectionRenderer = Callable[
    [ProjectInfo],
    str,
]


DEFAULT_LAYOUT: tuple[
    SectionRenderer,
    ...,
] = (
    render_header,
    render_highlights,
    render_overview,
    render_usage,
    render_installation,
    render_tech_stack,
    render_architecture,
    render_structure,
    render_repository_info,
    render_development,
    render_license,
)


CLI_LAYOUT: tuple[
    SectionRenderer,
    ...,
] = (
    render_header,
    render_highlights,
    render_overview,
    render_installation,
    render_usage,
    render_tech_stack,
    render_architecture,
    render_structure,
    render_repository_info,
    render_development,
    render_license,
)


LIBRARY_LAYOUT: tuple[
    SectionRenderer,
    ...,
] = (
    render_header,
    render_highlights,
    render_overview,
    render_installation,
    render_usage,
    render_architecture,
    render_tech_stack,
    render_structure,
    render_repository_info,
    render_development,
    render_license,
)


APPLICATION_LAYOUT: tuple[
    SectionRenderer,
    ...,
] = (
    render_header,
    render_highlights,
    render_overview,
    render_usage,
    render_installation,
    render_tech_stack,
    render_architecture,
    render_structure,
    render_repository_info,
    render_development,
    render_license,
)


def render_readme(
    project: ProjectInfo,
) -> str:
    layout = choose_layout(
        project
    )

    sections = [
        renderer(project)
        for renderer in layout
    ]

    rendered = "\n\n".join(
        section
        for section in sections
        if section
    )

    return rendered.strip() + "\n"


def choose_layout(
    project: ProjectInfo,
) -> tuple[SectionRenderer, ...]:
    project_type = (
        project.project_type
        or ""
    ).lower()

    if project_type == "cli":
        return CLI_LAYOUT

    if project_type == "library":
        return LIBRARY_LAYOUT

    if project_type in {
        "frontend",
        "backend",
        "full-stack",
    }:
        return APPLICATION_LAYOUT

    return DEFAULT_LAYOUT