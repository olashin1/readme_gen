from __future__ import annotations

from collections.abc import Callable

from readme_gen.formatting.sections import (
    render_architecture,
    render_features,
    render_header,
    render_license,
    render_overview,
    render_quick_start,
    render_repository_info,
    render_structure,
    render_tech_stack,
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
    render_overview,
    render_features,
    render_quick_start,
    render_tech_stack,
    render_architecture,
    render_structure,
    render_repository_info,
    render_license,
)


CLI_LAYOUT: tuple[
    SectionRenderer,
    ...,
] = (
    render_header,
    render_overview,
    render_features,
    render_quick_start,
    render_tech_stack,
    render_architecture,
    render_structure,
    render_repository_info,
    render_license,
)


LIBRARY_LAYOUT: tuple[
    SectionRenderer,
    ...,
] = (
    render_header,
    render_overview,
    render_features,
    render_quick_start,
    render_architecture,
    render_tech_stack,
    render_structure,
    render_repository_info,
    render_license,
)


APPLICATION_LAYOUT: tuple[
    SectionRenderer,
    ...,
] = (
    render_header,
    render_overview,
    render_features,
    render_tech_stack,
    render_quick_start,
    render_architecture,
    render_structure,
    render_repository_info,
    render_license,
)


def render_readme(
    project: ProjectInfo,
) -> str:
    """
    Render a complete GitHub-oriented README.

    The project's detected type determines the section ordering while each
    section remains responsible for its own Markdown representation.
    """
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
    """
    Select an appropriate README layout for the detected project type.
    """
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