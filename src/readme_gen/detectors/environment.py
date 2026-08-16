from __future__ import annotations

import ast
import re
from collections import defaultdict
from pathlib import Path

from readme_gen.detectors.path_filters import is_test_file
from readme_gen.models import EnvironmentVariable


MAX_FILE_SIZE = 256_000
SOURCE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx"}
IGNORED_VITE_VARIABLES = {"BASE_URL", "DEV", "MODE", "PROD", "SSR"}


def detect_environment_variables(
    root: Path,
    files: list[Path],
) -> list[EnvironmentVariable]:
    """Collect environment variable names without retaining their values."""
    found: defaultdict[str, set[str]] = defaultdict(set)

    for path in files:
        if is_test_file(root, path):
            continue
        relative_path = path.relative_to(root).as_posix()

        if path.name.startswith(".env"):
            content = _read_small_text(path)
            if content is not None:
                for name in re.findall(
                    r"(?m)^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=",
                    content,
                ):
                    found[name].add(relative_path)
            continue

        if path.suffix.lower() not in SOURCE_SUFFIXES:
            continue

        content = _read_small_text(path)
        if content is None:
            continue

        names = _python_environment_names(content) if path.suffix.lower() == ".py" else _javascript_environment_names(content)
        for name in names:
            found[name].add(relative_path)

    return [
        EnvironmentVariable(
            name=name,
            sources=tuple(sorted(sources)),
        )
        for name, sources in sorted(found.items())
    ]


def _python_environment_names(content: str) -> set[str]:
    names = set(
        re.findall(
            r"\bos\.(?:getenv|environ\.get)\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]",
            content,
        )
    )
    names.update(
        re.findall(
            r"\bos\.environ\[\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s*\]",
            content,
        )
    )
    names.update(
        re.findall(
            r"\b(?:alias|validation_alias)\s*=\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]",
            content,
        )
    )

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return names

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if not any(_base_name(base).endswith("BaseSettings") for base in node.bases):
            continue

        prefix = _settings_prefix(node)
        for statement in node.body:
            field_name: str | None = None
            if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
                field_name = statement.target.id
            elif isinstance(statement, ast.Assign) and len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):
                field_name = statement.targets[0].id

            if not field_name or field_name in {"Config", "model_config"} or field_name.startswith("_"):
                continue
            if field_name.isupper():
                names.add(field_name)
            elif prefix:
                names.add(f"{prefix}{field_name}".upper())

    return names


def _javascript_environment_names(content: str) -> set[str]:
    names = set(
        re.findall(
            r"\bprocess\.env\.([A-Za-z_][A-Za-z0-9_]*)",
            content,
        )
    )
    names.update(
        re.findall(
            r"\bprocess\.env\[['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\]",
            content,
        )
    )
    names.update(
        re.findall(
            r"\b(?:Deno|Bun)\.env\.get\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]",
            content,
        )
    )
    vite_names = set(
        re.findall(
            r"\bimport\.meta\.env\.([A-Za-z_][A-Za-z0-9_]*)",
            content,
        )
    )
    names.update(vite_names - IGNORED_VITE_VARIABLES)
    return names


def _base_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_base_name(node.value)}.{node.attr}"
    return ""


def _settings_prefix(node: ast.ClassDef) -> str:
    for statement in node.body:
        value: ast.expr | None = None
        if isinstance(statement, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "model_config"
            for target in statement.targets
        ):
            value = statement.value
        if isinstance(value, ast.Call):
            for keyword in value.keywords:
                if keyword.arg == "env_prefix" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                    return keyword.value.value
    return ""


def _read_small_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
