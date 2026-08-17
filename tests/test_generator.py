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
            tagline=(
                "Turn software repositories into "
                "polished GitHub landing pages."
            ),
            summary=(
                "readme-gen analyzes software "
                "repositories and produces concise, "
                "structured README documentation."
            ),
            highlights=[
                "Automatic repository scanning",
                "AI-assisted project understanding",
                "Local and GitHub repository support",
                "Deterministic GitHub-focused Markdown",
            ],
            usage_summary=(
                "Pass a local project path or GitHub "
                "repository URL to generate a README."
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
        "name: Tests\n",
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


def test_generator_renders_selected_badges_beneath_tagline(
    tmp_path: Path,
) -> None:
    create_project_files(tmp_path)

    readme = generate_readme(make_project(tmp_path))

    tagline_position = readme.index("**Turn software repositories")
    language_position = readme.index("![Python]")
    package_manager_position = readme.index("![uv]")
    license_position = readme.index("![License]")
    header_end = readme.index("</div>")

    assert (
        tagline_position
        < language_position
        < package_manager_position
        < license_position
        < header_end
    )


def test_generator_prefers_ai_tagline(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert (
        "**Turn software repositories into "
        "polished GitHub landing pages.**"
        in readme
    )

    assert (
        "**Generate polished README files "
        "from software repositories.**"
        not in readme
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


def test_generator_renders_highlights(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert "## Highlights" in readme

    assert (
        "- Automatic repository scanning"
        in readme
    )

    assert (
        "- Local and GitHub repository support"
        in readme
    )

    assert "## Features" not in readme


def test_highlights_appear_before_overview(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    highlights_position = readme.index(
        "## Highlights"
    )

    overview_position = readme.index(
        "## Overview"
    )

    assert (
        highlights_position
        < overview_position
    )


def test_generator_renders_overview(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert "## Overview" in readme

    assert (
        "readme-gen analyzes software repositories"
        in readme
    )


def test_generator_renders_usage(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert "## Usage" in readme

    assert (
        "Pass a local project path or GitHub "
        "repository URL"
        in readme
    )

    assert "### CLI" in readme
    assert "readme-gen" in readme


def test_generator_does_not_invent_cli_path_argument(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert "readme-gen [PATH]" not in readme


def test_generator_renders_installation(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert "## Installation" in readme

    assert (
        "git clone "
        "https://github.com/example/readme-gen"
        in readme
    )

    assert "cd readme-gen" in readme
    assert "uv sync" in readme


def test_generator_renders_tech_stack_table(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert "## Tech Stack" in readme

    assert (
        "| **Languages** | Python |"
        in readme
    )

    assert (
        "| **Frameworks** | Typer |"
        in readme
    )


def test_generator_renders_architecture(
    tmp_path: Path,
) -> None:
    create_project_files(
        tmp_path
    )

    readme = generate_readme(
        make_project(tmp_path)
    )

    assert "## Architecture" in readme

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

    assert "## License" in readme

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

    assert "## Project Structure" in readme

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

    assert "pyproject.toml" in readme
    assert "LICENSE  # License" in readme


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
