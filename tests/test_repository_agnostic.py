import json
from pathlib import Path
from textwrap import dedent

from typer.testing import CliRunner

from readme_gen.generator import generate_readme
from readme_gen.main import app
from readme_gen.scanner import scan_project


runner = CliRunner()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).strip(), encoding="utf-8")


def command_values(project) -> set[str]:
    return {command.command for command in project.commands}


def test_cpp_cmake_project_uses_native_sections_and_ignores_build_output(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "CMakeLists.txt",
        """
        cmake_minimum_required(VERSION 3.20)
        project(sensor_reader LANGUAGES CXX)
        add_executable(sensor-reader src/main.cpp)
        enable_testing()
        add_test(NAME smoke COMMAND sensor-reader --version)
        """,
    )
    write(tmp_path / "src" / "main.cpp", "int main() { return 0; }")
    for directory in ("build", "target", "vendor", "node_modules"):
        write(tmp_path / directory / "generated.py", "print('not authored')")

    project = scan_project(tmp_path)
    readme = generate_readme(project)

    assert project.project_type == "application"
    assert project.languages == ["C++"]
    assert project.build_tools == ["CMake"]
    assert "cmake -S . -B build" in command_values(project)
    assert "cmake --build build" in command_values(project)
    assert "ctest --test-dir build" in command_values(project)
    assert {interface.name for interface in project.interfaces} >= {"sensor-reader"}
    assert "building" in project.section_plan
    assert "testing" in project.section_plan
    assert "## \ud83d\udd28 Building" in readme
    assert "## \u2705 Testing" in readme
    assert "| **Build System** | CMake |" in readme
    assert "## \u2b07\ufe0f Installation" not in readme
    assert "Python" not in project.languages
    assert not any(
        directory in "\n".join(project.directory_tree)
        for directory in ("node_modules", "target", "vendor")
    )


def test_rust_cli_has_cargo_commands_package_and_cli_role(tmp_path: Path) -> None:
    write(
        tmp_path / "Cargo.toml",
        """
        [package]
        name = "log-sift"
        version = "0.3.0"

        [dependencies]
        clap = "4"
        """,
    )
    write(tmp_path / "src" / "main.rs", "fn main() { println!(\"log-sift\"); }")
    write(tmp_path / "target" / "generated.py", "print('ignore')")

    project = scan_project(tmp_path)
    readme = generate_readme(project)

    assert project.project_type == "cli"
    assert project.languages == ["Rust"]
    assert project.technology_roles["CLI"] == ["Clap"]
    assert {"cargo build", "cargo test", "cargo run"}.issubset(
        command_values(project)
    )
    assert project.packages[0].install_command == "cargo install log-sift"
    assert any(interface.kind == "cli" for interface in project.interfaces)
    assert "cargo install log-sift" in readme
    assert "## \ud83d\udd28 Building" in readme
    assert "## \u2705 Testing" in readme
    assert "| **CLI Framework** | Clap |" in readme


def test_python_library_keeps_library_specific_plan(tmp_path: Path) -> None:
    write(
        tmp_path / "pyproject.toml",
        """
        [project]
        name = "units-core"
        version = "1.2.0"
        description = "Unit conversion primitives."
        dependencies = []

        [dependency-groups]
        dev = ["pytest>=9"]
        """,
    )
    write(tmp_path / "src" / "units_core" / "__init__.py", "VERSION = '1.2.0'")

    project = scan_project(tmp_path)
    readme = generate_readme(project)

    assert project.project_type == "library"
    assert project.packages[0].install_command == "pip install units-core"
    assert "installation" in project.section_plan
    assert "testing" in project.section_plan
    assert "interfaces" not in project.section_plan
    assert "pip install units-core" in readme
    assert "python -m pytest" in readme
    assert "API Endpoints" not in readme


def test_node_cli_uses_manifest_bin_and_scripts(tmp_path: Path) -> None:
    write(
        tmp_path / "package.json",
        """
        {
          "name": "note-tool",
          "version": "2.0.0",
          "bin": {"note": "./bin/note.js"},
          "dependencies": {"commander": "^13"},
          "scripts": {"test": "node --test", "build": "node build.js"}
        }
        """,
    )
    write(tmp_path / "bin" / "note.js", "#!/usr/bin/env node\nconsole.log('note')")

    project = scan_project(tmp_path)
    readme = generate_readme(project)

    assert project.project_type == "cli"
    assert project.languages == ["JavaScript"]
    assert project.cli_commands == {"note": "./bin/note.js"}
    assert "npm run build" in command_values(project)
    assert "npm run test" in command_values(project)
    assert any(interface.kind == "cli" and interface.name == "note" for interface in project.interfaces)
    assert "npm install --global note-tool" in readme
    assert "npm run test" in readme


def test_unknown_repository_omits_unsupported_claims_and_sections(
    tmp_path: Path,
) -> None:
    write(tmp_path / "notes.txt", "Repository notes only.")

    project = scan_project(tmp_path)
    readme = generate_readme(project)

    assert project.project_type == "application"
    assert project.commands == []
    assert project.interfaces == []
    assert project.technologies == []
    assert project.section_plan == ["header", "structure"]
    for unsupported in (
        "Installation",
        "Building",
        "Testing",
        "API Endpoints",
        "Environment Variables",
        "Architecture",
        "robust",
        "comprehensive",
    ):
        assert unsupported not in readme


def test_go_maven_and_dotnet_commands_are_evidence_based(tmp_path: Path) -> None:
    go_root = tmp_path / "go-service"
    write(go_root / "go.mod", "module example.com/go-service\n\ngo 1.24")
    write(go_root / "main.go", "package main\nfunc main() {}")
    write(go_root / "main_test.go", "package main\nfunc TestMain() {}")
    write(go_root / "Dockerfile", "FROM golang:1.24")
    go_project = scan_project(go_root)
    assert {"go build ./...", "go test ./...", "go run ."}.issubset(
        command_values(go_project)
    )
    assert go_project.build_tools == ["Go Modules"]
    assert go_project.deployment_files == ["Dockerfile"]

    java_root = tmp_path / "java-service"
    write(
        java_root / "pom.xml",
        """
        <project>
          <modelVersion>4.0.0</modelVersion>
          <groupId>example</groupId><artifactId>demo</artifactId><version>1</version>
          <dependencies>
            <dependency><groupId>org.junit.jupiter</groupId><artifactId>junit-jupiter</artifactId><scope>test</scope></dependency>
          </dependencies>
        </project>
        """,
    )
    write(java_root / "src" / "Main.java", "class Main {}")
    java_project = scan_project(java_root)
    assert {"mvn package", "mvn test"}.issubset(command_values(java_project))
    assert java_project.build_tools == ["Maven"]

    gradle_root = tmp_path / "gradle-service"
    write(
        gradle_root / "build.gradle.kts",
        'plugins { java }\ndependencies { testImplementation("org.junit.jupiter:junit-jupiter:5.11") }',
    )
    write(gradle_root / "src" / "Main.java", "class Main {}")
    gradle_project = scan_project(gradle_root)
    assert {"gradle build", "gradle test"}.issubset(command_values(gradle_project))
    assert gradle_project.build_tools == ["Gradle"]

    dotnet_root = tmp_path / "dotnet-app"
    write(
        dotnet_root / "Demo.csproj",
        """
        <Project Sdk="Microsoft.NET.Sdk">
          <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net9.0</TargetFramework></PropertyGroup>
        </Project>
        """,
    )
    write(dotnet_root / "Program.cs", "System.Console.WriteLine(\"demo\");")
    write(dotnet_root / "bin" / "generated.py", "print('ignore')")
    write(dotnet_root / "obj" / "generated.py", "print('ignore')")
    dotnet_project = scan_project(dotnet_root)
    assert {
        "dotnet restore Demo.csproj",
        "dotnet build Demo.csproj",
        "dotnet run --project Demo.csproj",
    }.issubset(command_values(dotnet_project))
    assert dotnet_project.build_tools == ["dotnet"]
    assert dotnet_project.languages == ["C#"]
    assert "bin" not in "\n".join(dotnet_project.directory_tree)
    assert "obj" not in "\n".join(dotnet_project.directory_tree)


def test_debug_metadata_is_safe_and_does_not_generate_readme(tmp_path: Path) -> None:
    write(tmp_path / ".env.example", "SERVICE_TOKEN=never-print-this")
    write(tmp_path / "main.py", "import os\ntoken = os.getenv('SERVICE_TOKEN')")
    write(
        tmp_path / "package.json",
        '{"name": "debug-demo", "scripts": {"deploy": "tool --token hidden-script-token"}}',
    )

    result = runner.invoke(app, [str(tmp_path), "--debug-metadata"])

    assert result.exit_code == 0
    assert '"environment_variables"' in result.stdout
    assert '"SERVICE_TOKEN"' in result.stdout
    assert '"section_plan"' in result.stdout
    assert "never-print-this" not in result.stdout
    assert "hidden-script-token" not in result.stdout
    assert "Analyzing project with Gemini" not in result.stdout
    assert not (tmp_path / "README.md").exists()

    json_start = result.stdout.index("{")
    metadata = json.loads(result.stdout[json_start:])
    assert metadata["environment_variables"][0]["name"] == "SERVICE_TOKEN"
