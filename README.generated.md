# readme-gen

A CLI tool that analyzes a project and generates a README.

## Overview

A Python-based CLI tool designed to automate the creation of project documentation by analyzing source code, directory structures, and metadata to generate a structured README.md file.

## Features

- Automated project scanning for languages, frameworks, and package managers.
- AI-powered analysis using Google Gemini to generate project summaries, feature lists, and architectural overviews.
- Directory tree generation with support for configurable ignored paths (e.g., .git, node_modules, .venv).
- Heuristic-based detection of installation and usage commands for various ecosystems including Python (uv, poetry, pip), JavaScript (npm, yarn, pnpm, bun), and others.
- Configurable Markdown output via CLI arguments.
- Support for non-AI generation mode to produce basic documentation without LLM calls.

## Tech Stack

**Languages:** Python
**Package Managers:** uv

## Installation

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd readme_gen
uv sync
```

## Usage

Run the tool via the command 'readme-gen [PATH]'. Use the '--output' or '-o' flag to specify a destination file (defaults to README.generated.md). The '--no-ai' flag disables Gemini analysis. Requires a GEMINI_API_KEY environment variable for AI-assisted content.

### CLI

```bash
readme-gen [PATH]
```

## Architecture

The tool is structured into three main layers: a scanner that extracts metadata and file structures from the local filesystem, an AI analyzer that sends filtered repository context to the Gemini API, and a generator that formats both extracted and analyzed data into a Markdown template using Pydantic models for data integrity.

## Project Structure

```text
readme_gen/
├── src
│   └── readme_gen
│       ├── ai
│       ├── detectors
│       ├── __init__.py
│       ├── generator.py
│       ├── main.py
│       ├── models.py
│       └── scanner.py
├── tests
│   ├── test_generator.py
│   └── test_scanner.py
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```
