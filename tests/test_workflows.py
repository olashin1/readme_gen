from pathlib import Path

from readme_gen.detectors.workflows import (
    detect_workflow_purpose,
    detect_workflows,
    extract_workflow_name,
    humanize_workflow_filename,
)


def create_workflow(
    root: Path,
    filename: str,
    content: str,
) -> Path:
    workflow_directory = (
        root
        / ".github"
        / "workflows"
    )

    workflow_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    workflow_path = (
        workflow_directory
        / filename
    )

    workflow_path.write_text(
        content,
        encoding="utf-8",
    )

    return workflow_path


def test_detect_workflows_returns_empty_without_directory(
    tmp_path: Path,
) -> None:
    assert detect_workflows(
        tmp_path
    ) == []


def test_detect_workflows_finds_yaml_files(
    tmp_path: Path,
) -> None:
    create_workflow(
        tmp_path,
        "tests.yaml",
        """
name: Tests

on:
  push:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest
""".strip(),
    )

    workflows = detect_workflows(
        tmp_path
    )

    assert len(workflows) == 1

    workflow = workflows[0]

    assert workflow.name == "Tests"

    assert (
        workflow.path
        == ".github/workflows/tests.yaml"
    )

    assert workflow.purpose == "testing"


def test_detect_workflows_supports_yml_extension(
    tmp_path: Path,
) -> None:
    create_workflow(
        tmp_path,
        "lint.yml",
        """
name: Lint

on:
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ruff check .
""".strip(),
    )

    workflows = detect_workflows(
        tmp_path
    )

    assert len(workflows) == 1
    assert workflows[0].purpose == "linting"


def test_detect_workflows_ignores_non_yaml_files(
    tmp_path: Path,
) -> None:
    workflow_directory = (
        tmp_path
        / ".github"
        / "workflows"
    )

    workflow_directory.mkdir(
        parents=True,
    )

    (
        workflow_directory
        / "notes.txt"
    ).write_text(
        "not a workflow",
        encoding="utf-8",
    )

    assert detect_workflows(
        tmp_path
    ) == []


def test_extract_workflow_name() -> None:
    content = """
name: Test Suite

on:
  push:
""".strip()

    assert (
        extract_workflow_name(content)
        == "Test Suite"
    )


def test_extract_workflow_name_removes_quotes() -> None:
    content = """
name: "Python Tests"

on:
  push:
""".strip()

    assert (
        extract_workflow_name(content)
        == "Python Tests"
    )


def test_extract_workflow_name_ignores_nested_names() -> None:
    content = """
on:
  push:

jobs:
  test:
    name: Python Tests
    runs-on: ubuntu-latest
""".strip()

    assert extract_workflow_name(
        content
    ) is None


def test_filename_is_used_when_name_is_missing(
    tmp_path: Path,
) -> None:
    create_workflow(
        tmp_path,
        "pre-commit.yaml",
        """
on:
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
""".strip(),
    )

    workflows = detect_workflows(
        tmp_path
    )

    assert len(workflows) == 1

    assert (
        workflows[0].name
        == "Pre Commit"
    )

    assert (
        workflows[0].purpose
        == "linting"
    )


def test_testing_workflow_detection() -> None:
    purpose = detect_workflow_purpose(
        filename="ci",
        name="Python Tests",
        content="run: pytest",
    )

    assert purpose == "testing"


def test_publishing_workflow_detection() -> None:
    purpose = detect_workflow_purpose(
        filename="publish",
        name="Publish Package",
        content="run: uv publish",
    )

    assert purpose == "publishing"


def test_security_workflow_detection() -> None:
    purpose = detect_workflow_purpose(
        filename="zizmor",
        name="Zizmor",
        content="run: zizmor .",
    )

    assert purpose == "security"


def test_documentation_workflow_detection() -> None:
    purpose = detect_workflow_purpose(
        filename="docs",
        name="Documentation",
        content="run: mkdocs build",
    )

    assert purpose == "documentation"


def test_unknown_workflow_defaults_to_ci() -> None:
    purpose = detect_workflow_purpose(
        filename="automation",
        name="Automation",
        content="echo hello",
    )

    assert purpose == "ci"


def test_ubuntu_latest_does_not_match_test() -> None:
    purpose = detect_workflow_purpose(
        filename="automation",
        name="Automation",
        content="""
jobs:
  task:
    runs-on: ubuntu-latest
    steps:
      - run: echo hello
""".strip(),
    )

    assert purpose == "ci"


def test_issue_lock_workflow_does_not_match_testing(
    tmp_path: Path,
) -> None:
    create_workflow(
        tmp_path,
        "lock.yaml",
        """
name: Lock inactive closed issues

on:
  schedule:
    - cron: "0 0 * * *"

jobs:
  lock:
    runs-on: ubuntu-latest
    steps:
      - uses: dessant/lock-threads@v5
""".strip(),
    )

    workflows = detect_workflows(
        tmp_path
    )

    assert len(workflows) == 1

    workflow = workflows[0]

    assert (
        workflow.name
        == "Lock inactive closed issues"
    )

    assert workflow.purpose == "ci"


def test_full_test_token_still_matches_testing() -> None:
    purpose = detect_workflow_purpose(
        filename="ci",
        name="Continuous Integration",
        content="""
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: python -m pytest
""".strip(),
    )

    assert purpose == "testing"


def test_humanize_workflow_filename() -> None:
    assert (
        humanize_workflow_filename(
            "release-package"
        )
        == "Release Package"
    )


def test_workflows_are_sorted_by_filename(
    tmp_path: Path,
) -> None:
    create_workflow(
        tmp_path,
        "tests.yaml",
        "name: Tests",
    )

    create_workflow(
        tmp_path,
        "publish.yaml",
        "name: Publish",
    )

    create_workflow(
        tmp_path,
        "lint.yaml",
        "name: Lint",
    )

    workflows = detect_workflows(
        tmp_path
    )

    assert [
        workflow.path
        for workflow in workflows
    ] == [
        ".github/workflows/lint.yaml",
        ".github/workflows/publish.yaml",
        ".github/workflows/tests.yaml",
    ]