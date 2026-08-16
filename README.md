<div align="center">

# readme-gen

**Automate project documentation by analyzing local or GitHub repositories.**

![Typer](https://img.shields.io/badge/Typer-4C566A)

</div>

## 🌟 Highlights

- Analyzes both local directories and remote GitHub repositories.
- Automatically detects technical stacks, including languages, package managers, and dependencies.
- Identifies project infrastructure such as CLI commands, environment variables, and API routes.
- Uses Gemini AI to generate descriptive taglines, summaries, and architectural overviews.
- Supports a --no-ai mode for purely deterministic, metadata-driven generation.
- Extends project analysis through modular detectors for assets, workflows, and usage examples.

## ℹ️ Overview

readme-gen is a Python-based CLI tool that scans software repositories to extract technical metadata and generate structured documentation. It identifies project traits such as languages, dependencies, and directory structures, and can optionally use Gemini AI to synthesize this data into concise summaries and highlights. The tool is designed to help developers quickly create factual, high-quality README files that accurately reflect their project's current state.

## ⬇️ Installation

```bash
pip install readme-gen
```

## 🚀 Usage

Users interact with the tool through the readme-gen CLI. Running the command with a local file path or a GitHub repository URL initiates the scanning and analysis process. Configuration options allow users to specify output paths, overwrite existing files with --force, or skip AI analysis with the --no-ai flag. A GEMINI_API_KEY environment variable is required for AI-powered content generation.

### CLI

```bash
readme-gen
```

### Project Commands

| Purpose | Command         |
| ------- | --------------- |
| Test    | `uv run pytest` |

## ⚡ Examples

### Example 1

```bash
readme-gen
```

### Example 2

```bash
git clone https://github.com/olashin1/readme_gen.git
cd readme_gen
```

### Example 3

```bash
uv tool install .
```

## 🛠️ Tech Stack

| Category               | Technologies |
| ---------------------- | ------------ |
| **Languages**          | Python       |
| **AI**                 | Gemini       |
| **CLI**                | Typer        |
| **Package Management** | uv           |

## ⚙️ Environment Variables

The application reads the following variable names. Values are not included in this README.

| Variable         | Detected in                           |
| ---------------- | ------------------------------------- |
| `GEMINI_API_KEY` | `.env`, `src/readme_gen/ai/client.py` |
| `GITHUB_TOKEN`   | `src/readme_gen/github/client.py`     |

## 🏗️ Architecture

The tool follows a modular pipeline: a scanner component uses specialized detectors to gather raw facts from the repository; an analyzer layer optionally processes this metadata through the Gemini-3-flash-preview model for synthesis; and a generator component renders the final output into Markdown. Data consistency is maintained through a central Pydantic-based project model.

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

```bash
git clone https://github.com/olashin1/readme_gen.git
cd readme_gen
uv sync
```

</details>
