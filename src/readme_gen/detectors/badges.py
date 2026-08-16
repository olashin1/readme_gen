from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from urllib.parse import quote

from readme_gen.models import BadgeInfo, Confidence, ProjectInfo, TechnologyInfo


MAX_BADGES = 6


@dataclass(frozen=True, slots=True)
class BadgeStyle:
    color: str
    logo: str | None = None


LANGUAGE_STYLES = {
    "Python": BadgeStyle("3776AB", "python"),
    "JavaScript": BadgeStyle("F7DF1E", "javascript"),
    "TypeScript": BadgeStyle("3178C6", "typescript"),
    "Java": BadgeStyle("ED8B00", "openjdk"),
    "C++": BadgeStyle("00599C", "cplusplus"),
    "C": BadgeStyle("A8B9CC", "c"),
    "C#": BadgeStyle("512BD4", "dotnet"),
    "Go": BadgeStyle("00ADD8", "go"),
    "Rust": BadgeStyle("000000", "rust"),
    "Ruby": BadgeStyle("CC342D", "ruby"),
    "PHP": BadgeStyle("777BB4", "php"),
    "Swift": BadgeStyle("F05138", "swift"),
    "Kotlin": BadgeStyle("7F52FF", "kotlin"),
}

PACKAGE_MANAGER_STYLES = {
    "uv": BadgeStyle("DE5FE9", "uv"),
    "npm": BadgeStyle("CB3837", "npm"),
    "pnpm": BadgeStyle("F69220", "pnpm"),
    "Yarn": BadgeStyle("2C8EBB", "yarn"),
    "Bun": BadgeStyle("000000", "bun"),
    "Poetry": BadgeStyle("60A5FA", "poetry"),
    "Pipenv": BadgeStyle("2C3E50", "pypi"),
    "pip": BadgeStyle("3775A9", "pypi"),
    "Cargo": BadgeStyle("000000", "rust"),
    "Go Modules": BadgeStyle("00ADD8", "go"),
    "Maven": BadgeStyle("C71A36", "apachemaven"),
    "Gradle": BadgeStyle("02303A", "gradle"),
    "dotnet": BadgeStyle("512BD4", "dotnet"),
}

# Deliberately curated: minor libraries remain in the Tech Stack section.
TECHNOLOGY_STYLES: dict[str, tuple[str, BadgeStyle]] = {
    "Gemini": ("service", BadgeStyle("8E75B2", "googlegemini")),
    "Supabase": ("service", BadgeStyle("3FCF8E", "supabase")),
    "React": ("framework", BadgeStyle("61DAFB", "react")),
    "Next.js": ("framework", BadgeStyle("000000", "nextdotjs")),
    "Vue": ("framework", BadgeStyle("4FC08D", "vuedotjs")),
    "Angular": ("framework", BadgeStyle("DD0031", "angular")),
    "Svelte": ("framework", BadgeStyle("FF3E00", "svelte")),
    "FastAPI": ("framework", BadgeStyle("009688", "fastapi")),
    "Flask": ("framework", BadgeStyle("000000", "flask")),
    "Django": ("framework", BadgeStyle("092E20", "django")),
    "pytest": ("testing", BadgeStyle("0A9EDC", "pytest")),
    "Vitest": ("testing", BadgeStyle("6E9F18", "vitest")),
    "Jest": ("testing", BadgeStyle("C21325", "jest")),
    "JUnit": ("testing", BadgeStyle("25A162", "junit5")),
    "xUnit": ("testing", BadgeStyle("512BD4", "dotnet")),
    "Catch2": ("testing", BadgeStyle("D34F4F")),
    "GoogleTest": ("testing", BadgeStyle("4285F4", "google")),
}

CATEGORY_PRIORITY = {
    "language": 10,
    "package-manager": 20,
    "service": 30,
    "framework": 31,
    "testing": 40,
    "ci": 50,
    "license": 60,
}


def detect_badges(project: ProjectInfo, limit: int = MAX_BADGES) -> list[BadgeInfo]:
    """Select a small deterministic badge set from normalized scan evidence."""
    candidates = [
        *_language_candidates(project),
        *_package_manager_candidates(project),
        *_technology_candidates(project),
        *_ci_candidates(project),
        *_license_candidates(project),
    ]
    selected: list[BadgeInfo] = []
    seen_names: set[str] = set()
    seen_categories: set[str] = set()

    for badge in sorted(candidates, key=lambda item: (item.priority, item.name.lower())):
        normalized_name = badge.name.casefold()
        if normalized_name in seen_names or badge.category in seen_categories:
            continue
        selected.append(badge)
        seen_names.add(normalized_name)
        seen_categories.add(badge.category)
        if len(selected) >= limit:
            break

    return selected


def _language_candidates(project: ProjectInfo) -> list[BadgeInfo]:
    language = (
        project.repository.primary_language
        if project.repository and project.repository.primary_language
        else project.languages[0] if project.languages else None
    )
    if not language:
        return []
    style = LANGUAGE_STYLES.get(language, BadgeStyle("4C566A"))
    return [_static_badge(language, "language", style)]


def _package_manager_candidates(project: ProjectInfo) -> list[BadgeInfo]:
    return [
        _static_badge(
            name,
            "package-manager",
            PACKAGE_MANAGER_STYLES.get(name, BadgeStyle("4C566A")),
            priority_offset=index,
        )
        for index, name in enumerate(project.package_managers)
    ]


def _technology_candidates(project: ProjectInfo) -> list[BadgeInfo]:
    candidates: list[BadgeInfo] = []
    technologies = list(project.technologies)
    known = {(item.name, item.category) for item in technologies}

    # Compatibility for callers that populate the older normalized lists.
    technologies.extend(
        TechnologyInfo(name=name, category="framework")
        for name in project.frameworks
        if (name, "framework") not in known
    )
    technologies.extend(
        TechnologyInfo(name=name, category="service")
        for name in project.external_services
        if (name, "service") not in known
    )

    for technology in technologies:
        configured = TECHNOLOGY_STYLES.get(technology.name)
        if not configured:
            continue
        category, style = configured
        if category == "testing" and not _is_confident(technology):
            continue
        candidates.append(_static_badge(technology.name, category, style))
    return candidates


def _is_confident(technology: TechnologyInfo) -> bool:
    return not technology.evidence or any(
        evidence.confidence == Confidence.HIGH for evidence in technology.evidence
    )


def _ci_candidates(project: ProjectInfo) -> list[BadgeInfo]:
    if not project.workflows:
        return []
    link_target = None
    if project.repository:
        link_target = project.repository.actions_url
        if not link_target and project.repository.url:
            link_target = f"{project.repository.url}/actions"
    return [
        _static_badge(
            "GitHub Actions",
            "ci",
            BadgeStyle("2088FF", "githubactions"),
            link_target=link_target,
        )
    ]


def _license_candidates(project: ProjectInfo) -> list[BadgeInfo]:
    license_name = None
    if project.repository:
        license_name = project.repository.license_spdx_id or project.repository.license_name
    license_name = license_name or project.license
    if not license_name:
        return []

    link_target = None
    message = license_name
    filename = PurePosixPath(license_name).name
    if filename.upper().startswith(("LICENSE", "COPYING")):
        message = "detected"
        link_target = license_name

    return [
        _static_badge(
            "License",
            "license",
            BadgeStyle("007EC6"),
            message=message,
            link_target=link_target,
        )
    ]


def _static_badge(
    name: str,
    category: str,
    style: BadgeStyle,
    *,
    message: str | None = None,
    link_target: str | None = None,
    priority_offset: int = 0,
) -> BadgeInfo:
    label = _escape_shields_text(name)
    value = _escape_shields_text(message) if message else None
    path = f"{label}-{value}-{style.color}" if value else f"{label}-{style.color}"
    image_url = f"https://img.shields.io/badge/{quote(path, safe='-_')}"
    if style.logo:
        image_url += f"?logo={quote(style.logo, safe='')}&logoColor=white"
    return BadgeInfo(
        name=name,
        image_url=image_url,
        link_target=link_target,
        category=category,
        priority=CATEGORY_PRIORITY[category] + priority_offset,
    )


def _escape_shields_text(value: str | None) -> str:
    return (value or "").replace("-", "--").replace("_", "__").replace(" ", "_")
