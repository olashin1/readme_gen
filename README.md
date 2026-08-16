<div align="center">

# readme-gen

**A CLI tool that automatically analyzes software repositories to generate polished, structured GitHub README documentation.**

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

**Install once. Generate READMEs from any project.**

</div>

## 🌟 Highlights

- Automatic scanning of local paths and public GitHub URLs to detect project metadata.
- Integrated AI analysis via Google Gemini for generating descriptive project overviews and taglines.
- Detection of programming languages, frameworks, dependencies, and package managers across ecosystems.
- Automated GitHub Actions workflow discovery and dynamic status badge generation.
- Intelligent extraction of usage examples and code snippets from existing documentation.
- Deterministic Markdown rendering focused on GitHub-ready landing pages with table-based tech stacks.
- Installable as a system-wide CLI command, allowing `readme-gen` to be run from any project directory.

## ℹ️ Overview

`readme-gen` automates the creation of high-quality project documentation by scanning local or remote codebases to identify their technology stack, project structure, and usage patterns.

It resolves repository metadata from GitHub and uses Google Gemini to produce context-aware project summaries, highlights, and architecture descriptions. The resulting content is combined with deterministic Markdown formatting to create a polished GitHub landing-page README.

Once installed as a CLI tool, `readme-gen` can be called directly from any project directory:

```bash
readme-gen
```

The current directory is analyzed automatically and the generated documentation is written to `README.md`.

## ⬇️ Installation

### Install as a CLI tool

Clone the repository:

```bash
git clone https://github.com/olashin1/readme_gen.git
cd readme_gen
```

Install `readme-gen` with `uv`:

```bash
uv tool install .
```

Once installed, the `readme-gen` command is available from anywhere on your system.

Verify the installation:

```bash
readme-gen --help
```

### Editable installation

If you are developing `readme-gen` itself, install it in editable mode:

```bash
uv tool install --editable .
```

Changes to the local source code will then be reflected by the installed command without requiring a normal reinstall.

## 🚀 Usage

### Generate a README for the current project

Navigate into any software project:

```bash
cd path/to/my-project
```

Then run:

```bash
readme-gen
```

`readme-gen` analyzes the current directory and generates:

```text
README.md
```

This means the typical workflow is simply:

```bash
cd my-project
readme-gen
```

### Analyze another local project

You can also provide a project path explicitly:

```bash
readme-gen path/to/project
```

The generated `README.md` will be written inside that project.

### Analyze a GitHub repository

Public GitHub repositories can be analyzed directly:

```bash
readme-gen https://github.com/owner/repository
```

When analyzing a remote repository, the resulting `README.md` is written to the directory where the command was executed.

### Replace an existing README

`readme-gen` will not overwrite an existing `README.md` by default.

If a README already exists, use:

```bash
readme-gen --force
```

to explicitly replace it.

### Generate without AI analysis

Gemini analysis can be disabled with:

```bash
readme-gen --no-ai
```

The project will still be scanned and a README will be generated using the metadata detected locally.

### Custom output path

Use `--output` or `-o` to choose a different output file:

```bash
readme-gen --output PROJECT.md
```

## 🛠️ Tech Stack

| Category               | Technologies |
| ---------------------- | ------------ |
| **Languages**          | Python       |
| **Package Management** | uv           |

## 🏗️ Architecture

The system follows a pipeline architecture where a resolver identifies the repository source, a scanner extracts structured metadata using specialized detectors, and an AI module provides qualitative analysis. These inputs are aggregated into a standardized project model, which a formatting engine renders into final Markdown using deterministic templates.

At a high level:

```text
Local Path / GitHub URL
          │
          ▼
 Repository Resolver
          │
          ▼
     Project Scanner
          │
          ├── Languages
          ├── Frameworks
          ├── Packages
          ├── Workflows
          ├── Structure
          └── Metadata
          │
          ▼
    Gemini Analysis
          │
          ▼
 Deterministic Formatter
          │
          ▼
       README.md
```

## 📁 Project Structure

```text
readme-gen/
├── src/  # Source code
│   └── readme_gen/
├── tests/  # Test suite
├── pyproject.toml  # Python project configuration
└── README.md  # Project documentation
```

## 🧑‍💻 Development

<details>
<summary>Local development setup</summary>

Clone the repository:

```bash
git clone https://github.com/olashin1/readme_gen.git
cd readme_gen
```

Install the project dependencies:

```bash
uv sync
```

Install the CLI in editable mode:

```bash
uv tool install --editable .
```

You can now modify `readme-gen` while testing the command from any other project directory.

</details>
