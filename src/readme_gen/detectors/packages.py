from __future__ import annotations

import tomllib
from pathlib import Path

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

    return packages


def detect_python_package(
    root: Path,
) -> PackageInfo | None:
    """
    Detect a Python package from pyproject.toml.

    Only the standardized [project] table is used. Tool-specific metadata
    such as Poetry configuration can be added separately later.
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