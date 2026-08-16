from pathlib import Path

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

    assert project.scripts["demo"] == "demo.main:app"

    assert "src" in project.source_dirs
    assert "tests" in project.test_dirs

    assert "pyproject.toml" in project.important_files


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

    assert project.scripts["dev"] == "vite"
    assert project.scripts["build"] == "vite build"


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