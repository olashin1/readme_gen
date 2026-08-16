from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

from readme_gen.models import PackageInfo


def detect_packages(
    root: Path,
) -> list[PackageInfo]:
    """
    Detect user-installable packages declared by the repository.

    This first implementation focuses on Python packages declared through
    PEP 621 metadata in pyproject.toml. Additional ecosystems can be added
    behind the same interface later.
    """
    packages: list[PackageInfo] = []

    python_package = detect_python_package(
        root
    )

    if python_package is not None:
        packages.append(
            python_package
        )

    npm_package = detect_npm_package(root)
    if npm_package is not None:
        packages.append(npm_package)

    cargo_package = detect_cargo_package(root)
    if cargo_package is not None:
        packages.append(cargo_package)

    return packages


def detect_python_package(
    root: Path,
) -> PackageInfo | None:
    """
    Detect a verified PyPI distribution from pyproject.toml.

    PEP 621 package metadata describes a local distribution, but does not
    prove that the distribution has been published. Require an explicit PyPI
    project URL before offering a public ``pip install <name>`` command.
    """
    manifest_path = (
        root / "pyproject.toml"
    )

    if not manifest_path.is_file():
        return None

    try:
        with manifest_path.open(
            "rb"
        ) as manifest_file:
            data = tomllib.load(
                manifest_file
            )

    except (
        OSError,
        tomllib.TOMLDecodeError,
    ):
        return None

    project = data.get(
        "project"
    )

    if not isinstance(
        project,
        dict,
    ):
        return None

    name = project.get(
        "name"
    )

    if not isinstance(
        name,
        str,
    ):
        return None

    name = name.strip()

    if not name:
        return None

    if not _has_pypi_project_url(project, name):
        return None

    version = project.get(
        "version"
    )

    if not isinstance(
        version,
        str,
    ):
        version = None
    else:
        version = (
            version.strip()
            or None
        )

    return PackageInfo(
        ecosystem="pypi",
        name=name,
        version=version,
        manifest="pyproject.toml",
        install_command=(
            f"pip install {name}"
        ),
    )


def _has_pypi_project_url(project: dict, name: str) -> bool:
    urls = project.get("urls")
    if not isinstance(urls, dict):
        return False

    normalized_name = re.sub(r"[-_.]+", "-", name).lower()
    for value in urls.values():
        if not isinstance(value, str):
            continue
        parsed = urlsplit(value.strip())
        if parsed.scheme != "https" or parsed.hostname not in {
            "pypi.org",
            "pypi.python.org",
        }:
            continue
        path_parts = [part for part in parsed.path.split("/") if part]
        if len(path_parts) < 2 or path_parts[0].lower() not in {"project", "pypi"}:
            continue
        url_name = re.sub(r"[-_.]+", "-", path_parts[1]).lower()
        if url_name == normalized_name:
            return True

    return False


def detect_npm_package(root: Path) -> PackageInfo | None:
    manifest_path = root / "package.json"
    if not manifest_path.is_file():
        return None
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    name = data.get("name")
    if not isinstance(name, str) or not name.strip() or data.get("private") is True:
        return None
    if not any(key in data for key in ("bin", "exports", "main", "module", "types", "typings")):
        return None
    version = data.get("version") if isinstance(data.get("version"), str) else None
    install = "npm install --global" if "bin" in data else "npm install"
    return PackageInfo(
        ecosystem="npm",
        name=name.strip(),
        version=version,
        manifest="package.json",
        install_command=f"{install} {name.strip()}",
    )


def detect_cargo_package(root: Path) -> PackageInfo | None:
    manifest_path = root / "Cargo.toml"
    if not manifest_path.is_file():
        return None
    try:
        with manifest_path.open("rb") as file:
            data = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        return None
    package = data.get("package", {})
    name = package.get("name")
    if not isinstance(name, str) or not name.strip():
        return None
    version = package.get("version") if isinstance(package.get("version"), str) else None
    has_binary = (root / "src" / "main.rs").is_file() or bool(data.get("bin"))
    command = "cargo install" if has_binary else "cargo add"
    return PackageInfo(
        ecosystem="crates.io",
        name=name.strip(),
        version=version,
        manifest="Cargo.toml",
        install_command=f"{command} {name.strip()}",
    )
