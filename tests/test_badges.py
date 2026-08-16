from pathlib import Path

from readme_gen.formatting.badges import (
    _select_primary_workflow,
    generate_badges,
)
from readme_gen.models import (
    ProjectInfo,
    RepositoryMetadata,
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
        "[![Tests]"
        "(https://github.com/example/demo/"
        "actions/workflows/tests.yaml/badge.svg)]"
        "(https://github.com/example/demo/"
        "actions/workflows/tests.yaml)"
    )

    assert expected in badges


def test_testing_workflow_is_preferred() -> None:
    workflows = [
        WorkflowInfo(
            name="Publish",
            path=".github/workflows/publish.yaml",
            purpose="publishing",
        ),
        WorkflowInfo(
            name="Security",
            path=".github/workflows/security.yaml",
            purpose="security",
        ),
        WorkflowInfo(
            name="Tests",
            path=".github/workflows/tests.yaml",
            purpose="testing",
        ),
    ]

    selected = _select_primary_workflow(
        workflows
    )

    assert selected is not None
    assert selected.name == "Tests"


def test_linting_is_preferred_over_publishing() -> None:
    workflows = [
        WorkflowInfo(
            name="Release",
            path=".github/workflows/release.yaml",
            purpose="publishing",
        ),
        WorkflowInfo(
            name="Lint",
            path=".github/workflows/lint.yaml",
            purpose="linting",
        ),
    ]

    selected = _select_primary_workflow(
        workflows
    )

    assert selected is not None
    assert selected.name == "Lint"


def test_workflow_selection_returns_none_when_empty() -> None:
    assert (
        _select_primary_workflow([])
        is None
    )


def test_workflow_badge_replaces_issue_badge_when_header_is_full() -> None:
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

    assert len(badges) == 4

    assert any(
        "actions/workflows/tests.yaml/badge.svg"
        in badge
        for badge in badges
    )

    assert any(
        "github/stars/example/demo"
        in badge
        for badge in badges
    )

    assert not any(
        "github/issues/example/demo"
        in badge
        for badge in badges
    )


def test_issue_badge_is_used_as_fallback_without_workflow() -> None:
    project = make_project()

    badges = generate_badges(
        project
    )

    assert any(
        "github/issues/example/demo"
        in badge
        for badge in badges
    )


def test_workflow_badge_requires_repository_url() -> None:
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

    assert not any(
        "actions/workflows" in badge
        for badge in badges
    )