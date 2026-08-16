from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from readme_gen.detectors.path_filters import is_test_file


def detect_dependencies(
    root: Path,
    files: list[Path],
) -> tuple[list[str], list[str]]:
    """Collect declared dependency names across supported manifests."""
    runtime: list[str] = []
    development: list[str] = []

    for path in files:
        if is_test_file(root, path):
            continue
        if path.name == "package.json":
            data = _read_json(path)
            _extend_keys(runtime, data.get("dependencies"))
            _extend_keys(runtime, data.get("peerDependencies"))
            _extend_keys(development, data.get("devDependencies"))
        elif path.name == "pyproject.toml":
            data = _read_toml(path)
            project = data.get("project", {})
            _extend_python(runtime, project.get("dependencies", []))
            for values in project.get("optional-dependencies", {}).values():
                _extend_python(development, values)
            for values in data.get("dependency-groups", {}).values():
                _extend_python(development, values)
            poetry = data.get("tool", {}).get("poetry", {})
            _extend_keys(runtime, poetry.get("dependencies"))
            for group in poetry.get("group", {}).values():
                _extend_keys(development, group.get("dependencies"))
        elif path.name in {"Pipfile"}:
            data = _read_toml(path)
            _extend_keys(runtime, data.get("packages"))
            _extend_keys(development, data.get("dev-packages"))
        elif path.name.startswith("requirements") and path.suffix == ".txt":
            values = _requirements(path)
            target = development if any(word in path.name.lower() for word in ("dev", "test")) else runtime
            _extend_python(target, values)
        elif path.name == "Cargo.toml":
            data = _read_toml(path)
            _extend_keys(runtime, data.get("dependencies"))
            _extend_keys(development, data.get("dev-dependencies"))

    return _unique(runtime), _unique(development)


def _read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _read_toml(path: Path) -> dict:
    try:
        with path.open("rb") as file:
            data = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return data


def _requirements(path: Path) -> list[str]:
    try:
        return [
            line.strip()
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip() and not line.lstrip().startswith(("#", "-"))
        ]
    except OSError:
        return []


def _extend_keys(target: list[str], values: object) -> None:
    if isinstance(values, dict):
        target.extend(str(value) for value in values)


def _extend_python(target: list[str], values: object) -> None:
    if not isinstance(values, list):
        return
    for value in values:
        if not isinstance(value, str):
            continue
        name = value.strip().split(";", 1)[0].split("[", 1)[0]
        name = re.split(r"[<>=!~\s]", name, maxsplit=1)[0]
        if name:
            target.append(name)


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value.lower() != "python"))
