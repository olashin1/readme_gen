from pathlib import Path

from readme_gen.generator import generate_readme
from readme_gen.models import (
    ProjectAnalysis,
    ProjectInfo,
    RepositoryMetadata,
)


def make_project(
    root: Path,
) -> ProjectInfo:
    return ProjectInfo(
        name="readme-gen",
        root=root,
        description=(
            "Generate polished README files "
            "from software repositories."
        ),
        repository_url=(
            "https://github.com/example/readme-gen"
        ),
        license="MIT",
        project_type="cli",
        languages=[
            "Python",
        ],
        frameworks=[
            "Typer",
        ],
        package_managers=[
            "uv",
        ],
        cli_commands={
            "readme-gen": "readme_gen.main:app",
        },
        important_files=[
            "pyproject.toml",
            "LICENSE",
        ],
        source_dirs=[
            "src",
        ],
        test_dirs=[
            "tests",
        ],
        directory_tree=[
            "readme-gen/",
            "├── src",
            "│   └── readme_gen",
            "│       ├── main.py",
            "│       └── scanner.py",
            "├── tests",
            "└── pyproject.toml",
        ],
        repository=RepositoryMetadata(
            owner="example",
            name="readme-gen",
            url=(
                "https://github.com/"
                "example/readme-gen"
            ),
            description=(
                "Generate polished README files "
                "from software repositories."
            ),
            homepage=(
                "https://example.com/readme-gen"
            ),
            topics=[
                "python",
                "cli",
                "documentation",
            ],
            default_branch="main",
            primary_language="Python",
            license_name="MIT License",
            license_spdx_id="MIT",
            issues_url=(
                "https://github.com/"
                "example/readme-gen/issues"
            ),
            stars=100,
            forks=10,
        ),
        analysis=ProjectAnalysis(
            summary=(
                "readme-gen analyzes software "
                "repositories and produces "
                "structured README documentation."
            ),
            features=[
                "Automatic repository scanning",
                "AI-assisted project analysis",
                "GitHub-aware README generation",
            ],
            intended_users=(
                "Software developers"
            ),
            usage_summary=(
                "Pass a local project path or "
                "GitHub repository URL."
            ),
            architecture=(
                "Repository sources feed a common "
                "scanner before structured analysis "
                "and deterministic Markdown rendering."
            ),
        ),
    )


def create_project_files(
    root: Path,
) -> None:
    src_package = (
        root
        / "src"
        / "readme_gen"
    )

    tests_dir = root / "tests"

    workflows_dir = (
        root
        / ".github"
        / "workflows"
    )

    src_package.mkdir(
        parents=True
    )

    tests_dir.mkdir(
        parents=True
    )

    workflows_dir.mkdir(
        parents=True
    )

    (
        src_package / "main.py"
    ).write_text(
        "print('hello')\n",
        encoding="utf-8",
    )

    (
        tests_dir / "test_main.py"
    ).write_text(
        "def test_main(): pass\n",
        encoding="utf-8",
    )

    (
        workflows_dir / "tests.yml"
    ).write_text(
        "name: tests\n",
        encoding="utf-8",
    )

    (
        root / "pyproject.toml"
    ).write_text(
        "[project]\nname = 'readme-gen'\n",
        encoding="utf-8",
    )

    (
        root / "LICENSE"
    ).write_text(
        "MIT\n",
        encoding="utf-8",
    )

    (
        root / "README.md"
    ).write_text(
        "# readme-gen\n",
        encoding="utf-8",
    )


def test_generator_renders_centered_header(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert '<div align="center">' in readme
    assert "# readme-gen" in readme
    assert "</div>" in readme


def test_generator_renders_tagline(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert (
        "**Generate polished README files "
        "from software repositories.**"
        in readme
    )


def test_generator_renders_github_links(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert (
        "[Repository]"
        "(https://github.com/example/readme-gen)"
        in readme
    )

    assert (
        "[Website]"
        "(https://example.com/readme-gen)"
        in readme
    )

    assert (
        "[Issues]"
        "(https://github.com/"
        "example/readme-gen/issues)"
        in readme
    )


def test_generator_renders_feature_section(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert "## 🚀 Features" in readme

    assert (
        "- Automatic repository scanning"
        in readme
    )


def test_generator_renders_tech_stack_table(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert "## 🛠️ Tech Stack" in readme

    assert (
        "| **Languages** | Python |"
        in readme
    )

    assert (
        "| **Frameworks** | Typer |"
        in readme
    )


def test_generator_renders_quick_start(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert "## ⚡ Quick Start" in readme

    assert (
        "git clone "
        "https://github.com/example/readme-gen"
        in readme
    )

    assert "cd readme-gen" in readme
    assert "uv sync" in readme


def test_generator_does_not_invent_cli_path_argument(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert "readme-gen" in readme
    assert "readme-gen [PATH]" not in readme


def test_generator_renders_architecture(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert "## 🏗️ Architecture" in readme

    assert (
        "Repository sources feed a common scanner"
        in readme
    )


def test_generator_renders_license_link(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert "## 📄 License" in readme

    assert (
        "[MIT]"
        "(https://github.com/example/readme-gen/"
        "blob/main/LICENSE)"
        in readme
    )


def test_generator_renders_semantic_project_structure(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    project = make_project(
        tmp_path
    )

    readme = generate_readme(
        project
    )

    assert "## 📁 Project Structure" in readme

    assert "readme-gen/" in readme

    assert (
        "├── src/  # Source code"
        in readme
    )

    assert (
        "│   └── readme_gen/"
        in readme
    )

    assert (
        "├── tests/  # Test suite"
        in readme
    )

    assert (
        "├── .github/  # GitHub configuration"
        in readme
    )

    assert (
        "│   └── workflows/  # CI/CD workflows"
        in readme
    )

    assert (
        "├── pyproject.toml"
        in readme
    )

    assert (
        "├── LICENSE  # License"
        in readme
        or
        "└── LICENSE  # License"
        in readme
    )


def test_generator_uses_project_name_not_repository_slug(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    project = make_project(
        tmp_path
    )

    project.name = "Readme Gen"

    project.repository = RepositoryMetadata(
        owner="example",
        name="readme-gen",
        url=(
            "https://github.com/"
            "example/readme-gen"
        ),
    )

    readme = generate_readme(
        project
    )

    assert "# Readme Gen" in readme
    assert "# readme-gen" not in readme


def test_generator_prefers_spdx_license_over_filename(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    project = make_project(
        tmp_path
    )

    project.license = "LICENSE.txt"

    project.important_files = [
        "LICENSE",
    ]

    readme = generate_readme(
        project
    )

    assert (
        "licensed under the [MIT]"
        in readme
    )

    assert (
        "licensed under the [LICENSE.txt]"
        not in readme
    )