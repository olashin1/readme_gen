from __future__ import annotations

from collections.abc import Callable

from readme_gen.formatting.sections import (
    render_api_routes,
    render_architecture,
    render_building,
    render_development,
    render_environment_variables,
    render_examples,
    render_header,
    render_highlights,
    render_installation,
    render_interfaces,
    render_license,
    render_overview,
    render_repository_info,
    render_screenshots,
    render_structure,
    render_tech_stack,
    render_testing,
    render_usage,
)
from readme_gen.models import ProjectInfo
from readme_gen.planning import plan_readme_sections


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
    render_screenshots,
    render_usage,
    render_installation,
    render_interfaces,
    render_tech_stack,
    render_testing,
    render_environment_variables,
    render_api_routes,
    render_examples,
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
    render_examples,
    render_tech_stack,
    render_environment_variables,
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
    render_examples,
    render_usage,
    render_architecture,
    render_tech_stack,
    render_environment_variables,
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
    render_screenshots,
    render_tech_stack,
    render_installation,
    render_usage,
    render_examples,
    render_environment_variables,
    render_api_routes,
    render_architecture,
    render_structure,
    render_repository_info,
    render_development,
    render_license,
)


BACKEND_LAYOUT: tuple[
    SectionRenderer,
    ...,
] = (
    render_header,
    render_highlights,
    render_overview,
    render_tech_stack,
    render_api_routes,
    render_environment_variables,
    render_installation,
    render_usage,
    render_examples,
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
    renderers: dict[str, SectionRenderer] = {
        "header": render_header,
        "highlights": render_highlights,
        "overview": render_overview,
        "screenshots": render_screenshots,
        "tech_stack": render_tech_stack,
        "installation": render_installation,
        "building": render_building,
        "usage": render_usage,
        "examples": render_examples,
        "interfaces": render_interfaces,
        "environment": render_environment_variables,
        "testing": render_testing,
        "architecture": render_architecture,
        "structure": render_structure,
        "repository": render_repository_info,
        "development": render_development,
        "license": render_license,
    }
    plan = project.section_plan or plan_readme_sections(project)
    return tuple(
        renderers[section]
        for section in plan
        if section in renderers
    )
