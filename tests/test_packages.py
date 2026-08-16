from pathlib import Path

from readme_gen.detectors.packages import (
    detect_packages,
    detect_python_package,
)


def test_detect_python_package(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "pyproject.toml"
    ).write_text(
        """
[project]
name = "Flask"
version = "3.1.0"
description = "A web framework"
""".strip(),
        encoding="utf-8",
    )

    package = detect_python_package(
        tmp_path
    )

    assert package is not None
    assert package.ecosystem == "pypi"
    assert package.name == "Flask"
    assert package.version == "3.1.0"
    assert package.manifest == "pyproject.toml"
    assert package.install_command == "pip install Flask"


def test_detect_python_package_without_version(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "pyproject.toml"
    ).write_text(
        """
[project]
name = "demo-package"
dynamic = ["version"]
""".strip(),
        encoding="utf-8",
    )

    package = detect_python_package(
        tmp_path
    )

    assert package is not None
    assert package.name == "demo-package"
    assert package.version is None


def test_detect_python_package_returns_none_without_manifest(
    tmp_path: Path,
) -> None:
    assert (
        detect_python_package(
            tmp_path
        )
        is None
    )


def test_detect_python_package_returns_none_without_project_table(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "pyproject.toml"
    ).write_text(
        """
[tool.ruff]
line-length = 88
""".strip(),
        encoding="utf-8",
    )

    assert (
        detect_python_package(
            tmp_path
        )
        is None
    )


def test_detect_python_package_returns_none_without_name(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "pyproject.toml"
    ).write_text(
        """
[project]
version = "1.0.0"
""".strip(),
        encoding="utf-8",
    )

    assert (
        detect_python_package(
            tmp_path
        )
        is None
    )


def test_detect_python_package_handles_invalid_toml(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "pyproject.toml"
    ).write_text(
        """
[project
name = "broken"
""".strip(),
        encoding="utf-8",
    )

    assert (
        detect_python_package(
            tmp_path
        )
        is None
    )


def test_detect_packages_returns_python_package(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "pyproject.toml"
    ).write_text(
        """
[project]
name = "demo"
version = "0.1.0"
""".strip(),
        encoding="utf-8",
    )

    packages = detect_packages(
        tmp_path
    )

    assert len(packages) == 1
    assert packages[0].name == "demo"


def test_detect_packages_returns_empty_for_non_package(
    tmp_path: Path,
) -> None:
    assert detect_packages(
        tmp_path
    ) == []