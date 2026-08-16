from pathlib import Path

from readme_gen.detectors.badges import detect_badges
from readme_gen.scanner import scan_project


def test_scan_python_project(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
name = "demo-project"
version = "0.1.0"
description = "Demo project"
dependencies = [
    "typer>=0.12.0",
    "fastapi>=0.100.0",
]

[project.scripts]
demo = "demo.main:app"
""".strip(),
        encoding="utf-8",
    )

    src = tmp_path / "src"
    src.mkdir()

    package = src / "demo"
    package.mkdir()

    main_file = package / "main.py"
    main_file.write_text(
        "print('hello')",
        encoding="utf-8",
    )

    tests = tmp_path / "tests"
    tests.mkdir()

    project = scan_project(tmp_path)

    assert project.name == "demo-project"
    assert project.description == "Demo project"

    assert "Python" in project.languages
    assert "FastAPI" in project.frameworks
    assert "uv" not in project.package_managers

    assert "typer" in project.dependencies
    assert "fastapi" in project.dependencies

    assert project.cli_commands["demo"] == "demo.main:app"

    assert "src" in project.source_dirs
    assert "tests" in project.test_dirs

    assert "pyproject.toml" in project.important_files
    assert project.project_type == "cli"
    assert "pyproject.toml" in project.context_files
    assert "src/demo/main.py" in project.context_files

    assert project.packages == []
    assert any(
        command.command == "python -m pip install -e ."
        for command in project.commands
    )


def test_scan_react_project(tmp_path: Path):
    package_json = tmp_path / "package.json"

    package_json.write_text(
        """
{
  "name": "react-demo",
  "description": "React test project",
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "vite": "^7.0.0",
    "typescript": "^5.0.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  }
}
""".strip(),
        encoding="utf-8",
    )

    package_lock = tmp_path / "package-lock.json"
    package_lock.write_text(
        "{}",
        encoding="utf-8",
    )

    src = tmp_path / "src"
    src.mkdir()

    app_file = src / "App.tsx"
    app_file.write_text(
        "export default function App() {}",
        encoding="utf-8",
    )

    project = scan_project(tmp_path)

    assert project.name == "react-demo"
    assert project.description == "React test project"

    assert "TypeScript" in project.languages
    assert "React" in project.frameworks
    assert "npm" in project.package_managers

    assert "react" in project.dependencies
    assert "react-dom" in project.dependencies

    assert "vite" in project.dev_dependencies
    assert "typescript" in project.dev_dependencies

    assert project.package_scripts["dev"] == "vite"
    assert project.package_scripts["build"] == "vite build"

    assert project.project_type == "frontend"
    assert "package.json" in project.context_files
    assert "src/App.tsx" in project.context_files

    assert project.packages == []


def test_ignored_directories_are_not_scanned(tmp_path: Path):
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()

    fake_python_file = node_modules / "fake.py"
    fake_python_file.write_text(
        "print('should be ignored')",
        encoding="utf-8",
    )

    project = scan_project(tmp_path)

    assert "Python" not in project.languages


def test_scan_project_detects_github_workflows(
    tmp_path: Path,
):
    workflow_directory = (
        tmp_path
        / ".github"
        / "workflows"
    )

    workflow_directory.mkdir(
        parents=True,
    )

    tests_workflow = (
        workflow_directory
        / "tests.yaml"
    )

    tests_workflow.write_text(
        """
name: Tests

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
      - run: pytest
""".strip(),
        encoding="utf-8",
    )

    publish_workflow = (
        workflow_directory
        / "publish.yml"
    )

    publish_workflow.write_text(
        """
name: Publish

on:
  release:
    types:
      - published

jobs:
  publish:
    runs-on: ubuntu-latest

    steps:
      - run: uv publish
""".strip(),
        encoding="utf-8",
    )

    project = scan_project(tmp_path)

    assert len(project.workflows) == 2

    assert [
        workflow.path
        for workflow in project.workflows
    ] == [
        ".github/workflows/publish.yml",
        ".github/workflows/tests.yaml",
    ]

    tests_info = next(
        workflow
        for workflow in project.workflows
        if workflow.name == "Tests"
    )

    publish_info = next(
        workflow
        for workflow in project.workflows
        if workflow.name == "Publish"
    )

    assert tests_info.purpose == "testing"
    assert publish_info.purpose == "publishing"


def test_scan_project_detects_test_framework_from_dependency_group(
    tmp_path: Path,
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "demo"
version = "0.1.0"

[dependency-groups]
dev = ["pytest>=9"]
""".strip(),
        encoding="utf-8",
    )

    project = scan_project(tmp_path)

    testing = [
        technology
        for technology in project.technologies
        if technology.category == "testing"
    ]
    assert [technology.name for technology in testing] == ["pytest"]
    assert any(
        badge.name == "pytest"
        for badge in detect_badges(project)
    )
