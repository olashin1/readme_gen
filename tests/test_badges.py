from pathlib import Path

from readme_gen.detectors.badges import detect_badges
from readme_gen.formatting.badges import generate_badges, render_badge
from readme_gen.models import (
    BadgeInfo,
    Confidence,
    Evidence,
    ProjectInfo,
    RepositoryMetadata,
    TechnologyInfo,
    WorkflowInfo,
)


def make_project() -> ProjectInfo:
    return ProjectInfo(
        name="demo",
        root=Path("/projects/demo"),
        languages=[
            "Python",
        ],
        license="LICENSE.txt",
        repository=RepositoryMetadata(
            owner="example",
            name="demo",
            url="https://github.com/example/demo",
            primary_language="Python",
            license_name="BSD 3-Clause License",
            license_spdx_id="BSD-3-Clause",
            issues_url=(
                "https://github.com/example/demo/issues"
            ),
            stars=100,
        ),
    )


def test_generate_badges_includes_technology() -> None:
    project = make_project()

    badges = generate_badges(
        project
    )

    assert any(
        "Python-3776AB" in badge
        for badge in badges
    )


def test_generate_badges_prefers_spdx_license() -> None:
    project = make_project()

    badges = generate_badges(
        project
    )

    license_badge = next(
        badge
        for badge in badges
        if "![License]" in badge
    )

    assert "BSD--3--Clause" in license_badge
    assert "LICENSE.txt" not in license_badge


def test_generate_badges_includes_testing_workflow() -> None:
    project = make_project()

    project.workflows = [
        WorkflowInfo(
            name="Tests",
            path=".github/workflows/tests.yaml",
            purpose="testing",
        )
    ]

    badges = generate_badges(
        project
    )

    expected = (
        "[![GitHub Actions]"
        "(https://img.shields.io/badge/"
        "GitHub_Actions-2088FF?logo=githubactions&logoColor=white)]"
        "(https://github.com/example/demo/actions)"
    )

    assert expected in badges


def test_workflow_badge_does_not_claim_a_passing_build() -> None:
    project = make_project()

    project.workflows = [
        WorkflowInfo(
            name="Tests",
            path=".github/workflows/tests.yaml",
            purpose="testing",
        )
    ]

    badges = generate_badges(
        project
    )

    assert len(badges) == 3

    assert any(
        "GitHub_Actions-2088FF"
        in badge
        for badge in badges
    )

    assert not any(
        "badge.svg"
        in badge
        for badge in badges
    )


def test_repository_statistics_are_not_used_as_fallback_badges() -> None:
    project = make_project()

    badges = generate_badges(
        project
    )

    assert not any("github/issues" in badge for badge in badges)
    assert not any("github/stars" in badge for badge in badges)


def test_workflow_badge_can_render_without_repository_url() -> None:
    project = make_project()

    project.repository = RepositoryMetadata(
        owner="example",
        name="demo",
    )

    project.workflows = [
        WorkflowInfo(
            name="Tests",
            path=".github/workflows/tests.yaml",
            purpose="testing",
        )
    ]

    badges = generate_badges(
        project
    )

    assert any(
        "GitHub_Actions-2088FF" in badge
        for badge in badges
    )


def test_badge_selection_uses_evidence_and_expected_categories() -> None:
    project = make_project()
    project.package_managers = ["uv"]
    project.technologies = [
        TechnologyInfo(
            name="Gemini",
            category="service",
            evidence=(Evidence("pyproject.toml", "package dependency"),),
        ),
        TechnologyInfo(
            name="pytest",
            category="testing",
            evidence=(Evidence("pyproject.toml", "package dependency"),),
        ),
    ]
    project.workflows = [WorkflowInfo("Tests", ".github/workflows/tests.yml", "testing")]

    badges = detect_badges(project)

    assert [badge.name for badge in badges] == [
        "Python",
        "uv",
        "Gemini",
        "pytest",
        "GitHub Actions",
        "License",
    ]


def test_badge_selection_deduplicates_categories_and_respects_limit() -> None:
    project = make_project()
    project.package_managers = ["npm", "pnpm"]
    project.frameworks = ["React", "FastAPI"]
    project.external_services = ["Gemini", "Supabase"]
    project.technologies = [
        TechnologyInfo(name="pytest", category="testing"),
    ]
    project.workflows = [WorkflowInfo("CI", ".github/workflows/ci.yml", "ci")]

    badges = detect_badges(project, limit=4)

    assert len(badges) == 4
    assert [badge.category for badge in badges] == [
        "language",
        "package-manager",
        "service",
        "framework",
    ]
    assert [badge.name for badge in badges] == ["Python", "npm", "Gemini", "FastAPI"]


def test_low_confidence_test_framework_is_not_badged() -> None:
    project = make_project()
    project.technologies = [
        TechnologyInfo(
            name="pytest",
            category="testing",
            evidence=(
                Evidence(
                    "src/demo.py",
                    "source import",
                    Confidence.MEDIUM,
                ),
            ),
        )
    ]

    assert "pytest" not in [badge.name for badge in detect_badges(project)]


def test_rendered_badges_use_internal_badge_information() -> None:
    badge = BadgeInfo(
        name="Example",
        image_url="https://img.shields.io/badge/Example-blue",
        link_target="https://example.com",
        category="service",
        priority=30,
    )

    assert render_badge(badge) == (
        "[![Example](https://img.shields.io/badge/Example-blue)]"
        "(https://example.com)"
    )
