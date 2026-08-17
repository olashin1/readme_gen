from pathlib import Path
from textwrap import dedent

from readme_gen.ai.prompts import build_project_prompt
from readme_gen.generator import generate_readme
from readme_gen.models import ProjectInfo
from readme_gen.scanner import scan_project


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).strip(), encoding="utf-8")


def test_detects_react_vite_stack_roles_and_commands(tmp_path: Path) -> None:
    write(
        tmp_path / "frontend" / "package.json",
        """
        {
          "name": "watchwise-web",
          "dependencies": {
            "react": "^19.0.0",
            "axios": "^1.0.0",
            "@supabase/supabase-js": "^2.0.0"
          },
          "devDependencies": {
            "vite": "^7.0.0",
            "tailwindcss": "^4.0.0",
            "typescript": "^5.0.0"
          },
          "scripts": {
            "dev": "vite",
            "build": "vite build",
            "test": "vitest"
          }
        }
        """,
    )
    write(tmp_path / "frontend" / "package-lock.json", "{}")
    write(
        tmp_path / "frontend" / "src" / "App.tsx",
        "import axios from 'axios';\nexport default function App() { return null; }",
    )

    project = scan_project(tmp_path)

    assert {"React", "Tailwind CSS"}.issubset(project.frameworks)
    assert "Axios" in project.libraries
    assert "axios" in project.dependencies
    assert project.technology_roles["Frontend"] == ["React"]
    assert project.technology_roles["Build"] == ["Vite"]
    assert project.technology_roles["Styling"] == ["Tailwind CSS"]
    assert "Supabase" in project.external_services
    assert "npm --prefix frontend run dev" in {
        command.command for command in project.commands
    }

    react = next(item for item in project.technologies if item.name == "React")
    assert any(evidence.confidence.value == "high" for evidence in react.evidence)


def test_detects_fastapi_environment_routes_and_run_command(tmp_path: Path) -> None:
    write(
        tmp_path / "pyproject.toml",
        """
        [project]
        name = "movie-api"
        version = "0.1.0"
        dependencies = ["fastapi>=0.115", "uvicorn>=0.30", "google-genai>=2"]
        """,
    )
    write(tmp_path / "uv.lock", "version = 1")
    write(
        tmp_path / ".env.example",
        """
        GEMINI_API_KEY=replace-me
        TMDB_API_KEY=replace-me
        """,
    )
    write(
        tmp_path / "src" / "movie_api" / "main.py",
        """
        import os
        from fastapi import FastAPI

        app = FastAPI()
        token = os.getenv("INTERNAL_API_TOKEN")

        @app.get("/movies/{movie_id}")
        async def movie_detail(movie_id: int):
            return {"id": movie_id}

        @app.post("/recommendations")
        def recommend():
            return []
        """,
    )

    project = scan_project(tmp_path)

    assert project.project_type == "backend"
    assert "FastAPI" in project.backend
    assert {variable.name for variable in project.environment_variables} == {
        "GEMINI_API_KEY",
        "INTERNAL_API_TOKEN",
        "TMDB_API_KEY",
    }
    assert {(route.method, route.path, route.handler) for route in project.api_routes} == {
        ("GET", "/movies/{movie_id}", "movie_detail"),
        ("POST", "/recommendations", "recommend"),
    }
    assert "uv run uvicorn movie_api.main:app --reload" in {
        command.command for command in project.commands
    }
    assert project.technology_roles["AI"] == ["Gemini"]
    assert project.technology_roles["Movie data"] == ["TMDB"]


def test_detects_python_test_command_from_declared_dependency(tmp_path: Path) -> None:
    write(
        tmp_path / "pyproject.toml",
        """
        [project]
        name = "tested-package"
        version = "1.0.0"

        [dependency-groups]
        dev = ["pytest>=9", "ruff>=0.12"]
        """,
    )
    write(tmp_path / "uv.lock", "version = 1")

    project = scan_project(tmp_path)
    commands = {command.command for command in project.commands}

    assert "uv run pytest" in commands
    assert "uv run ruff check ." in commands


def test_detects_full_stack_project_across_nested_manifests(tmp_path: Path) -> None:
    write(
        tmp_path / "frontend" / "package.json",
        '{"dependencies": {"react": "^19"}, "devDependencies": {"vite": "^7"}}',
    )
    write(tmp_path / "backend" / "requirements.txt", "fastapi==0.115\nuvicorn==0.30")
    write(
        tmp_path / "backend" / "main.py",
        "from fastapi import FastAPI\napp = FastAPI()",
    )

    project = scan_project(tmp_path)

    assert project.project_type == "full-stack"
    assert project.frontend == ["React"]
    assert project.backend == ["FastAPI"]
    assert "npm --prefix frontend install" in {
        command.command for command in project.commands
    }
    assert "python -m pip install -r backend/requirements.txt" in {
        command.command for command in project.commands
    }


def test_tree_ignores_generated_directories_and_limits_children(tmp_path: Path) -> None:
    for directory in ("node_modules", ".venv", ".cache", "coverage", "dist"):
        write(tmp_path / directory / "noise.py", "print('noise')")
    for index in range(40):
        write(tmp_path / "src" / f"module_{index:02}.py", "pass")
    write(tmp_path / "pyproject.toml", "[project]\nname = 'tree-demo'\nversion = '1'")

    project = scan_project(tmp_path)
    tree = "\n".join(project.directory_tree)

    assert "node_modules" not in tree
    assert ".venv" not in tree
    assert ".cache" not in tree
    assert "coverage" not in tree
    assert len(project.directory_tree) <= 200
    assert "Python" in project.languages


def test_readme_sections_are_conditional_and_fact_driven(tmp_path: Path) -> None:
    write(
        tmp_path / "app.py",
        """
        import os
        from fastapi import FastAPI
        app = FastAPI()
        key = os.getenv("SERVICE_KEY")

        @app.get("/health")
        def health():
            return {"ok": True}
        """,
    )
    write(
        tmp_path / "requirements.txt",
        "fastapi==0.115\nuvicorn==0.30",
    )

    backend_readme = generate_readme(scan_project(tmp_path))

    assert "API Endpoints" in backend_readme
    assert "Environment Variables" in backend_readme
    assert "`GET` | `/health`" in backend_readme
    assert "`SERVICE_KEY`" in backend_readme
    assert "Screenshots" not in backend_readme

    library = ProjectInfo(
        name="plain-library",
        root=tmp_path / "missing",
        project_type="library",
        languages=["Python"],
    )
    library_readme = generate_readme(library)

    assert "API Endpoints" not in library_readme
    assert "Environment Variables" not in library_readme
    assert "Usage" not in library_readme


def test_prompt_redacts_environment_values(tmp_path: Path) -> None:
    write(tmp_path / ".env.example", "API_KEY=do-not-send-this-value")
    write(tmp_path / "main.py", 'SERVICE_TOKEN = "hardcoded-token-value"')
    write(
        tmp_path / "package.json",
        '{"name": "safe-prompt", "scripts": {"deploy": "tool --token package-script-secret"}}',
    )
    project = scan_project(tmp_path)

    prompt = build_project_prompt(project)

    assert "API_KEY" in prompt
    assert "do-not-send-this-value" not in prompt
    assert "hardcoded-token-value" not in prompt
    assert "package-script-secret" not in prompt
    assert "API_KEY=<redacted>" in prompt


def test_prompt_explicitly_forbids_emojis(tmp_path: Path) -> None:
    project = scan_project(tmp_path)

    prompt = build_project_prompt(project)

    assert "Do not use or reproduce emojis" in prompt


def test_detected_screenshot_is_rendered_without_inventing_a_path(tmp_path: Path) -> None:
    write(tmp_path / "public" / "screenshots" / "dashboard.png", "image bytes")
    project = scan_project(tmp_path)

    readme = generate_readme(project)

    assert [asset.path for asset in project.assets] == [
        "public/screenshots/dashboard.png"
    ]
    assert "## Screenshots" in readme
    assert "![Project screenshot](public/screenshots/dashboard.png)" in readme


def test_semantic_detectors_ignore_test_fixture_code(tmp_path: Path) -> None:
    write(tmp_path / "src" / "demo.py", "print('demo')")
    write(
        tmp_path / "tests" / "test_fixture.py",
        """
        from fastapi import FastAPI
        app = FastAPI()
        token = os.getenv("FIXTURE_SECRET")

        @app.get("/fixture-only")
        def fixture_route():
            return None
        """,
    )
    write(
        tmp_path / "tests" / "fixtures" / "package.json",
        '{"dependencies": {"react": "latest"}, "scripts": {"dev": "vite"}}',
    )
    write(
        tmp_path / "tests" / "fixtures" / ".env.example",
        "FIXTURE_ONLY_KEY=ignored",
    )

    project = scan_project(tmp_path)

    assert "FastAPI" not in project.frameworks
    assert project.api_routes == []
    assert project.environment_variables == []
    assert "React" not in project.frameworks
    assert "npm" not in project.package_managers
    assert not any("uvicorn" in command.command for command in project.commands)
