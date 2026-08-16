from __future__ import annotations

import json
import re
import tomllib
from collections import defaultdict
from pathlib import Path

from readme_gen.detectors.path_filters import is_test_file
from readme_gen.models import Confidence, Evidence, TechnologyInfo


MAX_SOURCE_SIZE = 256_000
MAX_SOURCE_FILES = 400


# normalized dependency -> (display name, category, role)
DEPENDENCY_TECHNOLOGIES: dict[str, tuple[str, str, str]] = {
    "react": ("React", "framework", "Frontend"),
    "react-dom": ("React", "framework", "Frontend"),
    "next": ("Next.js", "framework", "Frontend"),
    "vue": ("Vue", "framework", "Frontend"),
    "@angular/core": ("Angular", "framework", "Frontend"),
    "svelte": ("Svelte", "framework", "Frontend"),
    "vite": ("Vite", "build tool", "Build"),
    "tailwindcss": ("Tailwind CSS", "framework", "Styling"),
    "@tailwindcss/vite": ("Tailwind CSS", "framework", "Styling"),
    "express": ("Express", "framework", "Backend"),
    "fastify": ("Fastify", "framework", "Backend"),
    "fastapi": ("FastAPI", "framework", "Backend"),
    "flask": ("Flask", "framework", "Backend"),
    "django": ("Django", "framework", "Backend"),
    "typer": ("Typer", "framework", "CLI"),
    "click": ("Click", "framework", "CLI"),
    "axios": ("Axios", "library", "HTTP client"),
    "@supabase/supabase-js": ("Supabase", "service", "Backend service"),
    "supabase": ("Supabase", "service", "Backend service"),
    "psycopg": ("PostgreSQL", "database", "Database"),
    "psycopg2": ("PostgreSQL", "database", "Database"),
    "asyncpg": ("PostgreSQL", "database", "Database"),
    "pg": ("PostgreSQL", "database", "Database"),
    "mysql": ("MySQL", "database", "Database"),
    "mysqlclient": ("MySQL", "database", "Database"),
    "mysql-connector-python": ("MySQL", "database", "Database"),
    "pymongo": ("MongoDB", "database", "Database"),
    "mongoose": ("MongoDB", "database", "Database"),
    "mongodb": ("MongoDB", "database", "Database"),
    "redis": ("Redis", "database", "Cache"),
    "ioredis": ("Redis", "database", "Cache"),
    "google-genai": ("Gemini", "service", "AI"),
    "google-generativeai": ("Gemini", "service", "AI"),
    "@google/generative-ai": ("Gemini", "service", "AI"),
}


IMPORT_TECHNOLOGIES: dict[str, tuple[str, str, str]] = {
    "fastapi": DEPENDENCY_TECHNOLOGIES["fastapi"],
    "flask": DEPENDENCY_TECHNOLOGIES["flask"],
    "django": DEPENDENCY_TECHNOLOGIES["django"],
    "typer": DEPENDENCY_TECHNOLOGIES["typer"],
    "axios": DEPENDENCY_TECHNOLOGIES["axios"],
    "@supabase/supabase-js": DEPENDENCY_TECHNOLOGIES["@supabase/supabase-js"],
    "supabase": DEPENDENCY_TECHNOLOGIES["supabase"],
    "psycopg": DEPENDENCY_TECHNOLOGIES["psycopg"],
    "psycopg2": DEPENDENCY_TECHNOLOGIES["psycopg2"],
    "asyncpg": DEPENDENCY_TECHNOLOGIES["asyncpg"],
    "pymongo": DEPENDENCY_TECHNOLOGIES["pymongo"],
    "redis": DEPENDENCY_TECHNOLOGIES["redis"],
    "google.genai": DEPENDENCY_TECHNOLOGIES["google-genai"],
    "google.generativeai": DEPENDENCY_TECHNOLOGIES["google-generativeai"],
}


def detect_technologies(
    root: Path,
    files: list[Path],
) -> list[TechnologyInfo]:
    """Detect technologies from manifests, configuration, and imports."""
    found: dict[tuple[str, str], dict[str, object]] = {}

    def add(
        technology: tuple[str, str, str],
        source: Path,
        kind: str,
        confidence: Confidence,
        role: str | None = None,
    ) -> None:
        name, category, default_role = technology
        selected_role = role or default_role
        key = (name, selected_role)
        record = found.setdefault(
            key,
            {
                "name": name,
                "category": category,
                "role": selected_role,
                "evidence": [],
            },
        )
        evidence = Evidence(
            source=source.relative_to(root).as_posix(),
            kind=kind,
            confidence=confidence,
        )
        evidence_list = record["evidence"]
        if isinstance(evidence_list, list) and evidence not in evidence_list:
            evidence_list.append(evidence)

    for path in files:
        if is_test_file(root, path):
            continue
        for dependency in _manifest_dependencies(path):
            technology = DEPENDENCY_TECHNOLOGIES.get(
                _normalize_dependency(dependency)
            )
            if technology:
                add(
                    technology,
                    path,
                    "package dependency",
                    Confidence.HIGH,
                )

        lower_name = path.name.lower()
        if lower_name.startswith("vite.config"):
            add(
                DEPENDENCY_TECHNOLOGIES["vite"],
                path,
                "framework configuration",
                Confidence.HIGH,
            )
        if lower_name.startswith("tailwind.config"):
            add(
                DEPENDENCY_TECHNOLOGIES["tailwindcss"],
                path,
                "framework configuration",
                Confidence.HIGH,
            )
        if lower_name == "dockerfile" or lower_name.startswith("docker-compose") or lower_name in {"compose.yml", "compose.yaml"}:
            add(
                ("Docker", "infrastructure", "Containers"),
                path,
                "configuration file",
                Confidence.HIGH,
            )
            if lower_name != "dockerfile":
                compose_content = (_read_small_text(path) or "").lower()
                for token, dependency in (
                    ("postgres", "psycopg"),
                    ("mysql", "mysql"),
                    ("mongo", "pymongo"),
                    ("redis", "redis"),
                ):
                    if token in compose_content:
                        add(
                            DEPENDENCY_TECHNOLOGIES[dependency],
                            path,
                            "container configuration",
                            Confidence.HIGH,
                        )
        if path.name == "CMakeLists.txt":
            add(
                ("CMake", "build tool", "Build"),
                path,
                "build configuration",
                Confidence.HIGH,
            )
        if path.name.startswith(".env"):
            content = _read_small_text(path)
            variable_names = set(
                re.findall(
                    r"(?m)^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=",
                    content or "",
                )
            )
            for variable_name in variable_names:
                upper_name = variable_name.upper()
                if "SUPABASE" in upper_name:
                    add(
                        DEPENDENCY_TECHNOLOGIES["supabase"],
                        path,
                        "environment variable",
                        Confidence.MEDIUM,
                    )
                if "TMDB" in upper_name:
                    add(
                        ("TMDB", "service", "Movie data"),
                        path,
                        "environment variable",
                        Confidence.MEDIUM,
                    )
                if "GEMINI" in upper_name:
                    add(
                        DEPENDENCY_TECHNOLOGIES["google-genai"],
                        path,
                        "environment variable",
                        Confidence.MEDIUM,
                    )
                if "REDIS" in upper_name:
                    add(
                        DEPENDENCY_TECHNOLOGIES["redis"],
                        path,
                        "environment variable",
                        Confidence.MEDIUM,
                    )
                if "MONGO" in upper_name:
                    add(
                        DEPENDENCY_TECHNOLOGIES["pymongo"],
                        path,
                        "environment variable",
                        Confidence.MEDIUM,
                    )

    source_count = 0
    for path in files:
        if is_test_file(root, path):
            continue
        if path.suffix.lower() not in {".py", ".js", ".jsx", ".ts", ".tsx"}:
            continue
        if source_count >= MAX_SOURCE_FILES:
            break
        source_count += 1
        content = _read_small_text(path)
        if content is None:
            continue

        imports = _extract_imports(content, path.suffix.lower())
        for imported_name in imports:
            technology = IMPORT_TECHNOLOGIES.get(imported_name)
            if technology:
                add(
                    technology,
                    path,
                    "source import",
                    Confidence.MEDIUM,
                )

        lowered = content.lower()
        environment_names = _source_environment_names(
            content,
            path.suffix.lower(),
        )
        if any("TMDB" in name.upper() for name in environment_names):
            add(
                ("TMDB", "service", "Movie data"),
                path,
                "environment access",
                Confidence.MEDIUM,
            )
        if any("SUPABASE" in name.upper() for name in environment_names):
            add(
                DEPENDENCY_TECHNOLOGIES["supabase"],
                path,
                "environment access",
                Confidence.MEDIUM,
            )
        if any("GEMINI" in name.upper() for name in environment_names):
            add(
                DEPENDENCY_TECHNOLOGIES["google-genai"],
                path,
                "environment access",
                Confidence.MEDIUM,
            )
        if any("supabase" in imported for imported in imports) and re.search(r"\.auth\b", lowered):
            add(
                ("Supabase", "service", "Authentication"),
                path,
                "source usage",
                Confidence.MEDIUM,
            )
        if any(imported.split(".", 1)[0] == "sqlite3" for imported in imports):
            add(
                ("SQLite", "database", "Database"),
                path,
                "source import",
                Confidence.MEDIUM,
            )

    return [
        TechnologyInfo(
            name=str(record["name"]),
            category=str(record["category"]),
            role=str(record["role"]),
            evidence=tuple(record["evidence"]),
        )
        for _, record in sorted(
            found.items(),
            key=lambda item: (item[1]["role"], item[1]["name"]),
        )
    ]


def group_technology_roles(
    technologies: list[TechnologyInfo],
) -> dict[str, list[str]]:
    grouped: defaultdict[str, list[str]] = defaultdict(list)
    for technology in technologies:
        if not technology.role:
            continue
        if technology.name not in grouped[technology.role]:
            grouped[technology.role].append(technology.name)
    return dict(sorted(grouped.items()))


def _manifest_dependencies(path: Path) -> list[str]:
    if path.name == "package.json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        dependencies: list[str] = []
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            values = data.get(key, {})
            if isinstance(values, dict):
                dependencies.extend(values)
        return dependencies

    if path.name in {"pyproject.toml", "Pipfile", "Cargo.toml"}:
        try:
            with path.open("rb") as file:
                data = tomllib.load(file)
        except (OSError, tomllib.TOMLDecodeError):
            return []
        if path.name == "pyproject.toml":
            dependencies = list(data.get("project", {}).get("dependencies", []))
            optional = data.get("project", {}).get("optional-dependencies", {})
            for values in optional.values():
                dependencies.extend(values)
            poetry = data.get("tool", {}).get("poetry", {})
            dependencies.extend(poetry.get("dependencies", {}).keys())
            dependencies.extend(poetry.get("group", {}).get("dev", {}).get("dependencies", {}).keys())
            return dependencies
        table = "packages" if path.name == "Pipfile" else "dependencies"
        dependencies = list(data.get(table, {}).keys())
        if path.name == "Pipfile":
            dependencies.extend(data.get("dev-packages", {}).keys())
        return dependencies

    if path.name in {"requirements.txt", "requirements-dev.txt"}:
        content = _read_small_text(path)
        if content is None:
            return []
        return [
            line.strip()
            for line in content.splitlines()
            if line.strip() and not line.lstrip().startswith(("#", "-"))
        ]

    if path.name in {"go.mod", "pom.xml", "build.gradle", "build.gradle.kts"}:
        content = _read_small_text(path)
        if content is None:
            return []
        # Substring matching is enough here because the technology map only
        # contains well-known package identifiers.
        return [
            package
            for package in DEPENDENCY_TECHNOLOGIES
            if package in content.lower()
        ]

    return []


def _normalize_dependency(dependency: str) -> str:
    value = str(dependency).strip().lower()
    value = value.split(";", 1)[0]
    value = value.split("[", 1)[0]
    value = re.split(r"[<>=!~\s]", value, maxsplit=1)[0]
    return value.replace("_", "-")


def _extract_imports(content: str, suffix: str) -> set[str]:
    imports: set[str] = set()
    if suffix == ".py":
        try:
            import ast

            tree = ast.parse(content)
        except SyntaxError:
            return imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
    else:
        patterns = (
            r"\bfrom\s+['\"]([^'\"]+)['\"]",
            r"\brequire\(\s*['\"]([^'\"]+)['\"]\s*\)",
            r"\bimport\(\s*['\"]([^'\"]+)['\"]\s*\)",
        )
        for pattern in patterns:
            imports.update(re.findall(pattern, content))
    return imports


def _source_environment_names(content: str, suffix: str) -> set[str]:
    if suffix != ".py":
        return set(
            re.findall(
                r"(?:process\.env\.|import\.meta\.env\.)([A-Za-z_][A-Za-z0-9_]*)",
                content,
            )
        )
    try:
        import ast

        tree = ast.parse(content)
    except SyntaxError:
        return set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        function = ""
        if isinstance(node.func, ast.Attribute):
            function = node.func.attr
        if function not in {"getenv", "get"}:
            continue
        first_argument = node.args[0]
        if isinstance(first_argument, ast.Constant) and isinstance(first_argument.value, str):
            names.add(first_argument.value)
    return names


def _read_small_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_SOURCE_SIZE:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
