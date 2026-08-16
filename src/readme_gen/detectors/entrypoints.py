from __future__ import annotations

import re
import tomllib
from pathlib import Path

from readme_gen.detectors.path_filters import is_test_file
from readme_gen.models import Interface


def detect_executable_interfaces(
    root: Path,
    files: list[Path],
) -> list[Interface]:
    interfaces: list[Interface] = []

    for path in files:
        if is_test_file(root, path):
            continue
        source = path.relative_to(root).as_posix()
        if path.name == "CMakeLists.txt":
            content = _read_text(path)
            for name in re.findall(
                r"\badd_executable\s*\(\s*([A-Za-z0-9_.+-]+)",
                content,
                re.IGNORECASE,
            ):
                interfaces.append(
                    Interface(kind="executable", name=name, source=source)
                )
        elif path.name == "Cargo.toml":
            name = _cargo_binary_name(path)
            if name:
                interfaces.append(
                    Interface(kind="executable", name=name, source=source)
                )
        elif path.suffix.lower() == ".csproj":
            content = _read_text(path)
            if re.search(
                r"<OutputType>\s*(?:Exe|WinExe)\s*</OutputType>",
                content,
                re.IGNORECASE,
            ) or "Microsoft.NET.Sdk.Web" in content:
                interfaces.append(
                    Interface(kind="executable", name=path.stem, source=source)
                )
        elif path.name == "main.go" and re.search(
            r"(?m)^\s*package\s+main\b",
            _read_text(path),
        ):
            interfaces.append(
                Interface(
                    kind="executable",
                    name=path.parent.name,
                    source=source,
                )
            )
        elif path.suffix.lower() == ".py" and re.search(
            r"if\s+__name__\s*==\s*['\"]__main__['\"]",
            _read_text(path),
        ):
            interfaces.append(
                Interface(kind="executable", name=path.stem, source=source)
            )
        elif path.suffix.lower() == ".java" and re.search(
            r"\bpublic\s+static\s+void\s+main\s*\(",
            _read_text(path),
        ):
            interfaces.append(
                Interface(kind="executable", name=path.stem, source=source)
            )
        elif path.suffix.lower() in {".c", ".cc", ".cpp", ".cxx"} and re.search(
            r"\b(?:int|auto)\s+main\s*\(",
            _read_text(path),
        ):
            interfaces.append(
                Interface(kind="executable", name=path.stem, source=source)
            )

    unique: dict[tuple[str, str | None], Interface] = {}
    for interface in interfaces:
        unique.setdefault((interface.kind, interface.name), interface)
    return list(unique.values())


def _cargo_binary_name(path: Path) -> str | None:
    try:
        with path.open("rb") as file:
            data = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        return None
    binaries = data.get("bin")
    if isinstance(binaries, list) and binaries:
        name = binaries[0].get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    if (path.parent / "src" / "main.rs").is_file():
        name = data.get("package", {}).get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return None


def _read_text(path: Path) -> str:
    try:
        if path.stat().st_size > 512_000:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
