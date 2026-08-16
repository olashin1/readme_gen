from __future__ import annotations

import ast
import json
import re
import tomllib
from pathlib import Path

from readme_gen.detectors.path_filters import is_test_file
from readme_gen.models import ProjectCommand, ProjectInfo


SCRIPT_KINDS = {
    "build": "build",
    "check": "test",
    "dev": "development",
    "develop": "development",
    "lint": "lint",
    "preview": "run",
    "serve": "run",
    "start": "run",
    "test": "test",
    "typecheck": "test",
}


def detect_commands(
    root: Path,
    files: list[Path],
    project: ProjectInfo,
) -> list[ProjectCommand]:
    """Derive executable setup and project commands from configuration."""
    files = [path for path in files if not is_test_file(root, path)]
    commands: list[ProjectCommand] = []

    for path in files:
        relative = path.relative_to(root).as_posix()

        if path.name == "package.json":
            commands.extend(_package_json_commands(root, path))
        elif path.name == "requirements.txt":
            commands.append(
                ProjectCommand(
                    kind="install",
                    command=f"python -m pip install -r {relative}",
                    source=relative,
                )
            )
        elif path.name == "Makefile":
            commands.extend(_make_commands(root, path))

    commands.extend(_python_install_commands(root, files))
    commands.extend(_python_tool_commands(root, files))
    commands.extend(_fastapi_commands(root, files, project))
    commands.extend(_container_commands(root, files))
    commands.extend(_compiled_project_commands(root, files))

    for name in sorted(project.cli_commands):
        commands.append(
            ProjectCommand(
                kind="usage",
                name=name,
                command=name,
                source="pyproject.toml",
            )
        )

    unique: dict[str, ProjectCommand] = {}
    for command in commands:
        unique.setdefault(command.command, command)
    return list(unique.values())


def _package_json_commands(root: Path, path: Path) -> list[ProjectCommand]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    source = path.relative_to(root).as_posix()
    directory = path.parent.relative_to(root).as_posix()
    directory = "" if directory == "." else directory
    manager = _javascript_manager(path.parent, root, data)
    commands = [
        ProjectCommand(
            kind="install",
            command=_javascript_command(manager, directory, None),
            source=source,
        )
    ]
    scripts = data.get("scripts", {})
    if not isinstance(scripts, dict):
        return commands
    for name in sorted(scripts):
        commands.append(
            ProjectCommand(
                kind=SCRIPT_KINDS.get(name, "script"),
                name=name,
                command=_javascript_command(manager, directory, name),
                source=source,
            )
        )
    return commands


def _javascript_manager(directory: Path, root: Path, data: dict) -> str:
    declared = data.get("packageManager")
    if isinstance(declared, str) and declared:
        return declared.split("@", 1)[0]
    candidates = (
        ("pnpm-lock.yaml", "pnpm"),
        ("yarn.lock", "yarn"),
        ("bun.lock", "bun"),
        ("bun.lockb", "bun"),
        ("package-lock.json", "npm"),
    )
    for current in (directory, root):
        for filename, manager in candidates:
            if (current / filename).is_file():
                return manager
    return "npm"


def _javascript_command(manager: str, directory: str, script: str | None) -> str:
    if manager == "pnpm":
        prefix = f"pnpm --dir {directory}" if directory else "pnpm"
        return f"{prefix} {script}" if script else f"{prefix} install"
    if manager == "yarn":
        prefix = f"yarn --cwd {directory}" if directory else "yarn"
        return f"{prefix} {script}" if script else f"{prefix} install"
    if manager == "bun":
        prefix = f"bun --cwd {directory}" if directory else "bun"
        return f"{prefix} run {script}" if script else f"{prefix} install"
    prefix = f"npm --prefix {directory}" if directory else "npm"
    return f"{prefix} run {script}" if script else f"{prefix} install"


def _python_install_commands(root: Path, files: list[Path]) -> list[ProjectCommand]:
    commands: list[ProjectCommand] = []
    pyprojects = [path for path in files if path.name == "pyproject.toml"]
    for path in pyprojects:
        source = path.relative_to(root).as_posix()
        directory = path.parent.relative_to(root).as_posix()
        directory = "" if directory == "." else directory
        if (path.parent / "uv.lock").is_file():
            command = "uv sync" if not directory else f"uv sync --project {directory}"
        elif (path.parent / "poetry.lock").is_file():
            command = "poetry install" if not directory else f"poetry -C {directory} install"
        elif (path.parent / "Pipfile").is_file():
            command = "pipenv install" if not directory else f"(cd {directory} && pipenv install)"
        else:
            target = "." if not directory else directory
            command = f"python -m pip install -e {target}"
        commands.append(ProjectCommand(kind="install", command=command, source=source))
    return commands


def _python_tool_commands(root: Path, files: list[Path]) -> list[ProjectCommand]:
    commands: list[ProjectCommand] = []
    for path in files:
        if path.name not in {"pyproject.toml", "requirements.txt", "requirements-dev.txt"}:
            continue
        dependencies = _python_dependencies(path)
        source = path.relative_to(root).as_posix()
        if path.name == "pyproject.toml":
            if (path.parent / "uv.lock").is_file():
                prefix = "uv run "
            elif (path.parent / "poetry.lock").is_file():
                prefix = "poetry run "
            elif (path.parent / "Pipfile").is_file():
                prefix = "pipenv run "
            else:
                prefix = ""
        else:
            prefix = ""

        if "pytest" in dependencies:
            command = f"{prefix}pytest" if prefix else "python -m pytest"
            commands.append(ProjectCommand("test", command, source, "test"))
        if "ruff" in dependencies:
            commands.append(ProjectCommand("lint", f"{prefix}ruff check .", source, "lint"))
        if "mypy" in dependencies:
            command = f"{prefix}mypy ." if prefix else "python -m mypy ."
            commands.append(ProjectCommand("test", command, source, "type check"))
    return commands


def _python_dependencies(path: Path) -> set[str]:
    if path.name.startswith("requirements"):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return set()
        return {
            _normalize_python_dependency(line)
            for line in lines
            if line.strip() and not line.lstrip().startswith(("#", "-"))
        }
    try:
        with path.open("rb") as file:
            data = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        return set()
    values = list(data.get("project", {}).get("dependencies", []))
    for group in data.get("dependency-groups", {}).values():
        if isinstance(group, list):
            values.extend(item for item in group if isinstance(item, str))
    optional = data.get("project", {}).get("optional-dependencies", {})
    for group in optional.values():
        if isinstance(group, list):
            values.extend(item for item in group if isinstance(item, str))
    poetry = data.get("tool", {}).get("poetry", {})
    values.extend(poetry.get("dependencies", {}).keys())
    for group in poetry.get("group", {}).values():
        values.extend(group.get("dependencies", {}).keys())
    return {_normalize_python_dependency(value) for value in values}


def _normalize_python_dependency(value: str) -> str:
    name = str(value).strip().lower().split(";", 1)[0].split("[", 1)[0]
    return re.split(r"[<>=!~\s]", name, maxsplit=1)[0].replace("_", "-")


def _fastapi_commands(
    root: Path,
    files: list[Path],
    project: ProjectInfo,
) -> list[ProjectCommand]:
    if "FastAPI" not in project.frameworks:
        return []
    for path in files:
        if path.suffix.lower() != ".py":
            continue
        if is_test_file(root, path):
            continue
        try:
            if path.stat().st_size > 256_000:
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue
        app_name: str | None = None
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            value = node.value
            if not isinstance(value, ast.Call) or _ast_name(value.func) != "FastAPI":
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            target = targets[0] if targets else None
            if isinstance(target, ast.Name):
                app_name = target.id
                break
        if not app_name:
            continue
        runner = _python_tool_runner(path.parent, root, "uvicorn")
        relative = path.relative_to(root)
        parts = list(relative.with_suffix("").parts)
        if parts and parts[0] == "src":
            parts = parts[1:]
        module = ".".join(parts)
        return [
            ProjectCommand(
                kind="development",
                name="api",
                command=f"{runner} {module}:{app_name} --reload",
                source=relative.as_posix(),
            )
        ]
    return []


def _python_tool_runner(directory: Path, root: Path, tool: str) -> str:
    current = directory
    while True:
        if (current / "uv.lock").is_file():
            return f"uv run {tool}"
        if (current / "poetry.lock").is_file():
            return f"poetry run {tool}"
        if (current / "Pipfile").is_file():
            return f"pipenv run {tool}"
        if current == root or current.parent == current:
            break
        current = current.parent
    return f"python -m {tool}"


def _ast_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _make_commands(root: Path, path: Path) -> list[ProjectCommand]:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    source = path.relative_to(root).as_posix()
    directory = path.parent.relative_to(root).as_posix()
    prefix = "make" if directory == "." else f"make -C {directory}"
    commands: list[ProjectCommand] = []
    for target in re.findall(r"(?m)^([A-Za-z][A-Za-z0-9_.-]*):(?:\s|$)", content):
        if target.startswith("."):
            continue
        commands.append(
            ProjectCommand(
                kind=SCRIPT_KINDS.get(target, "task"),
                name=target,
                command=f"{prefix} {target}",
                source=source,
            )
        )
    return commands


def _container_commands(root: Path, files: list[Path]) -> list[ProjectCommand]:
    for path in files:
        if path.name in {"compose.yml", "compose.yaml", "docker-compose.yml", "docker-compose.yaml"}:
            relative = path.relative_to(root).as_posix()
            file_option = "" if path.parent == root else f" -f {relative}"
            return [
                ProjectCommand(
                    kind="development",
                    name="containers",
                    command=f"docker compose{file_option} up --build",
                    source=relative,
                )
            ]
    return []


def _compiled_project_commands(root: Path, files: list[Path]) -> list[ProjectCommand]:
    commands: list[ProjectCommand] = []

    for manifest in (path for path in files if path.name == "Cargo.toml"):
        source = manifest.relative_to(root).as_posix()
        option = "" if manifest.parent == root else f" --manifest-path {source}"
        commands.extend([
            ProjectCommand("build", f"cargo build{option}", source),
            ProjectCommand("test", f"cargo test{option}", source),
        ])
        if (manifest.parent / "src" / "main.rs").is_file() or _cargo_declares_binary(manifest):
            commands.append(
                ProjectCommand("run", f"cargo run{option}", source, "run")
            )

    for manifest in (path for path in files if path.name == "CMakeLists.txt"):
        source = manifest.relative_to(root).as_posix()
        directory = manifest.parent.relative_to(root).as_posix()
        source_directory = "." if directory == "." else directory
        build_directory = "build" if directory == "." else f"{directory}/build"
        commands.extend([
            ProjectCommand("build", f"cmake -S {source_directory} -B {build_directory}", source),
            ProjectCommand("build", f"cmake --build {build_directory}", source),
        ])
        content = _read_text(manifest)
        if re.search(r"\b(?:enable_testing|include\s*\(\s*CTest|add_test)\b", content, re.IGNORECASE):
            commands.append(
                ProjectCommand("test", f"ctest --test-dir {build_directory}", source, "test")
            )

    for manifest in (path for path in files if path.name == "go.mod"):
        source = manifest.relative_to(root).as_posix()
        directory = manifest.parent.relative_to(root).as_posix()
        prefix = "" if directory == "." else f"(cd {directory} && "
        suffix = "" if directory == "." else ")"
        commands.append(
            ProjectCommand("build", f"{prefix}go build ./...{suffix}", source)
        )
        if any(
            path.name.endswith("_test.go") and manifest.parent in path.parents
            for path in files
        ):
            commands.append(
                ProjectCommand("test", f"{prefix}go test ./...{suffix}", source, "test")
            )
        run_target = _go_run_target(manifest.parent, files)
        if run_target:
            commands.append(
                ProjectCommand("run", f"{prefix}go run {run_target}{suffix}", source, "run")
            )

    for manifest in (path for path in files if path.name == "pom.xml"):
        source = manifest.relative_to(root).as_posix()
        wrapper = manifest.parent / "mvnw"
        if wrapper.is_file():
            executable = f"./{wrapper.relative_to(root).as_posix()}"
        else:
            executable = "mvn"
        file_option = "" if manifest.parent == root else f" -f {source}"
        commands.extend([
            ProjectCommand("build", f"{executable}{file_option} package", source),
            ProjectCommand("test", f"{executable}{file_option} test", source, "test"),
        ])

    for manifest in (
        path
        for path in files
        if path.name in {"build.gradle", "build.gradle.kts"}
    ):
        source = manifest.relative_to(root).as_posix()
        wrapper = manifest.parent / "gradlew"
        executable = f"./{wrapper.relative_to(root).as_posix()}" if wrapper.is_file() else "gradle"
        directory = manifest.parent.relative_to(root).as_posix()
        project_option = "" if directory == "." else f" -p {directory}"
        commands.extend([
            ProjectCommand("build", f"{executable}{project_option} build", source),
            ProjectCommand("test", f"{executable}{project_option} test", source, "test"),
        ])

    for manifest in (path for path in files if path.suffix.lower() == ".csproj"):
        source = manifest.relative_to(root).as_posix()
        commands.extend([
            ProjectCommand("install", f"dotnet restore {source}", source),
            ProjectCommand("build", f"dotnet build {source}", source),
        ])
        content = _read_text(manifest)
        if "Microsoft.NET.Test.Sdk" in content or "test" in manifest.stem.lower():
            commands.append(
                ProjectCommand("test", f"dotnet test {source}", source, "test")
            )
        if re.search(r"<OutputType>\s*(?:Exe|WinExe)\s*</OutputType>", content, re.IGNORECASE) or "Microsoft.NET.Sdk.Web" in content:
            commands.append(
                ProjectCommand("run", f"dotnet run --project {source}", source, "run")
            )

    return commands


def _cargo_declares_binary(manifest: Path) -> bool:
    try:
        with manifest.open("rb") as file:
            return bool(tomllib.load(file).get("bin"))
    except (OSError, tomllib.TOMLDecodeError):
        return False


def _go_run_target(directory: Path, files: list[Path]) -> str | None:
    root_main = directory / "main.go"
    if root_main in files and re.search(r"(?m)^\s*package\s+main\b", _read_text(root_main)):
        return "."
    command_root = directory / "cmd"
    candidates: list[Path] = []
    for path in files:
        if path.name != "main.go" or command_root not in path.parents:
            continue
        if re.search(r"(?m)^\s*package\s+main\b", _read_text(path)):
            candidates.append(path.parent)
    if len(candidates) == 1:
        return f"./{candidates[0].relative_to(directory).as_posix()}"
    return None


def _read_text(path: Path) -> str:
    try:
        if path.stat().st_size > 512_000:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
