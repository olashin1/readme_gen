from __future__ import annotations

from pathlib import PurePosixPath
from urllib.parse import quote

from readme_gen.models import ProjectInfo, WorkflowInfo


MAX_BADGES = 4


TECH_LOGOS = {
    "Python": "python",
    "JavaScript": "javascript",
    "TypeScript": "typescript",
    "Java": "openjdk",
    "C++": "cplusplus",
    "C": "c",
    "C#": "dotnet",
    "Go": "go",
    "Rust": "rust",
    "Ruby": "ruby",
    "PHP": "php",
    "Swift": "swift",
    "Kotlin": "kotlin",
    "React": "react",
    "Vue": "vuedotjs",
    "Angular": "angular",
    "Svelte": "svelte",
    "FastAPI": "fastapi",
    "Flask": "flask",
    "Django": "django",
    "Node.js": "nodedotjs",
}


TECH_COLORS = {
    "Python": "3776AB",
    "JavaScript": "F7DF1E",
    "TypeScript": "3178C6",
    "Java": "ED8B00",
    "C++": "00599C",
    "C": "A8B9CC",
    "C#": "512BD4",
    "Go": "00ADD8",
    "Rust": "000000",
    "Ruby": "CC342D",
    "PHP": "777BB4",
    "Swift": "F05138",
    "Kotlin": "7F52FF",
    "React": "61DAFB",
    "Vue": "4FC08D",
    "Angular": "DD0031",
    "Svelte": "FF3E00",
    "FastAPI": "009688",
    "Flask": "000000",
    "Django": "092E20",
    "Node.js": "5FA04E",
}


WORKFLOW_PURPOSE_PRIORITY = {
    "testing": 0,
    "linting": 1,
    "build": 2,
    "security": 3,
    "documentation": 4,
    "publishing": 5,
    "ci": 6,
}


def generate_badges(
    project: ProjectInfo,
) -> list[str]:
    """
    Generate a concise set of useful GitHub README badges.

    Project-specific signals such as CI status are preferred over generic
    repository statistics like open issue counts.
    """
    badges: list[str] = []

    technology_badge = _generate_primary_technology_badge(
        project
    )

    if technology_badge:
        badges.append(technology_badge)

    license_badge = _generate_license_badge(
        project
    )

    if license_badge:
        badges.append(license_badge)

    workflow_badge = _generate_workflow_badge(
        project
    )

    if workflow_badge:
        badges.append(workflow_badge)

    stars_badge = _generate_stars_badge(
        project
    )

    if stars_badge:
        badges.append(stars_badge)

    if len(badges) < MAX_BADGES:
        issues_badge = _generate_issues_badge(
            project
        )

        if issues_badge:
            badges.append(issues_badge)

    return badges[:MAX_BADGES]


def _generate_primary_technology_badge(
    project: ProjectInfo,
) -> str | None:
    technology = _get_primary_technology(
        project
    )

    if not technology:
        return None

    color = TECH_COLORS.get(
        technology,
        "4C566A",
    )

    logo = TECH_LOGOS.get(
        technology
    )

    label = _escape_shields_text(
        technology
    )

    image_url = (
        "https://img.shields.io/badge/"
        f"{label}-{color}"
    )

    if logo:
        image_url += (
            f"?logo={quote(logo, safe='')}"
            "&logoColor=white"
        )

    return (
        f"![{technology}]"
        f"({image_url})"
    )


def _generate_license_badge(
    project: ProjectInfo,
) -> str | None:
    license_name = _get_license_name(
        project
    )

    if not license_name:
        return None

    encoded_license = _escape_shields_text(
        license_name
    )

    return (
        "![License]"
        "(https://img.shields.io/badge/"
        f"license-{encoded_license}-blue)"
    )


def _generate_workflow_badge(
    project: ProjectInfo,
) -> str | None:
    """
    Generate a GitHub Actions status badge for the most useful workflow.

    Workflow badges require a GitHub repository URL because the badge and
    target URLs are hosted by GitHub.
    """
    repository = project.repository

    if not repository:
        return None

    if not repository.url:
        return None

    workflow = _select_primary_workflow(
        project.workflows
    )

    if workflow is None:
        return None

    workflow_file = PurePosixPath(
        workflow.path
    ).name

    if not workflow_file:
        return None

    encoded_workflow_file = quote(
        workflow_file,
        safe="",
    )

    workflow_url = (
        f"{repository.url}/actions/workflows/"
        f"{encoded_workflow_file}"
    )

    badge_url = (
        f"{workflow_url}/badge.svg"
    )

    alt_text = workflow.name or "CI"

    return (
        f"[![{alt_text}]({badge_url})]"
        f"({workflow_url})"
    )


def _select_primary_workflow(
    workflows: list[WorkflowInfo],
) -> WorkflowInfo | None:
    """
    Select the workflow that provides the most useful README status signal.

    Test status is generally the most useful signal, followed by code quality
    and build status. Publishing workflows rank lower because release status
    says less about the health of the current codebase.
    """
    if not workflows:
        return None

    return min(
        workflows,
        key=lambda workflow: (
            WORKFLOW_PURPOSE_PRIORITY.get(
                workflow.purpose,
                100,
            ),
            workflow.name.lower(),
            workflow.path.lower(),
        ),
    )


def _generate_stars_badge(
    project: ProjectInfo,
) -> str | None:
    repository = project.repository

    if not repository:
        return None

    if not repository.owner or not repository.name:
        return None

    image_url = (
        "https://img.shields.io/github/stars/"
        f"{quote(repository.owner, safe='')}/"
        f"{quote(repository.name, safe='')}"
        "?style=flat"
    )

    if repository.url:
        return (
            f"[![GitHub Stars]({image_url})]"
            f"({repository.url}/stargazers)"
        )

    return f"![GitHub Stars]({image_url})"


def _generate_issues_badge(
    project: ProjectInfo,
) -> str | None:
    repository = project.repository

    if not repository:
        return None

    if not repository.owner or not repository.name:
        return None

    if not repository.issues_url:
        return None

    image_url = (
        "https://img.shields.io/github/issues/"
        f"{quote(repository.owner, safe='')}/"
        f"{quote(repository.name, safe='')}"
    )

    return (
        f"[![GitHub Issues]({image_url})]"
        f"({repository.issues_url})"
    )


def _get_primary_technology(
    project: ProjectInfo,
) -> str | None:
    if project.frameworks:
        return project.frameworks[0]

    if (
        project.repository
        and project.repository.primary_language
    ):
        return project.repository.primary_language

    if project.languages:
        return project.languages[0]

    return None


def _get_license_name(
    project: ProjectInfo,
) -> str | None:
    """
    Return the most useful human-facing license identifier.

    GitHub SPDX metadata is preferred because local scanners may only know
    that a file named LICENSE.txt exists.
    """
    repository = project.repository

    if repository:
        if repository.license_spdx_id:
            return repository.license_spdx_id

        if repository.license_name:
            return repository.license_name

    if project.license:
        return project.license

    return None


def _escape_shields_text(
    value: str,
) -> str:
    """
    Escape text for shields.io static badge path syntax.

    Shields uses a double hyphen to represent a literal hyphen and an
    underscore to represent a space.
    """
    return (
        value
        .replace("-", "--")
        .replace("_", "__")
        .replace(" ", "_")
    )