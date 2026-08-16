<div align="center">

# readme-gen

**Automated repository analysis and AI-assisted README generation for GitHub projects.**

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

</div>

## 🌟 Highlights

- Support for analyzing both local directory paths and remote GitHub repository URLs.
- AI-assisted project understanding using Gemini to generate summaries and taglines.
- Automated detection of tech stacks, license information, and GitHub Actions workflows.
- Generation of dynamic GitHub badges for licenses, stars, and CI/CD status.
- Semantic project structure visualization with intelligent directory labeling.
- Extraction and normalization of usage examples from existing documentation.

## ℹ️ Overview

readme-gen is a CLI tool that automates the creation of documentation by scanning software repositories to extract technical metadata. It analyzes project structures to identify programming languages, frameworks, package managers, and CI/CD workflows from both local paths and GitHub URLs. By combining automated scanning with AI-driven analysis, the tool generates structured Markdown READMEs complete with technical tables, directory trees, and project highlights.

## ⬇️ Installation

```bash
pip install readme-gen
```

## 🚀 Usage

Users interact with the tool through the readme-gen CLI by passing a source path or URL. The tool scans the project, optionally performs an AI analysis using an API key, and writes a structured Markdown file to a specified output location. Command-line options allow for disabling AI features or customizing the output filename.

### CLI

```bash
readme-gen
```

## 🛠️ Tech Stack

| Category               | Technologies |
| ---------------------- | ------------ |
| **Languages**          | Python       |
| **Package Management** | uv           |

## 🏗️ Architecture

The system utilizes a modular pipeline where repository resolvers fetch source code, a scanner component extracts structured data via specialized detectors, and an AI analyzer provides high-level context. This metadata is then processed by a formatting engine that renders deterministic Markdown for GitHub display.

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
