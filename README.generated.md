# readme-gen

A CLI tool that analyzes a project and generates a README.

## Tech Stack

**Languages:** Python
**Package Managers:** uv

## Installation

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd readme-gen
uv sync
```

## Usage

### readme-gen

```bash
uv run readme-gen
```

## Project Structure

```text
readme_gen/
├── .pytest_cache
│   ├── v
│   │   └── cache
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   └── README.md
├── src
│   └── readme_gen
│       ├── detectors
│       ├── __init__.py
│       ├── cli.py
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
