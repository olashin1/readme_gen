<div align="center">

# readme-gen

**A CLI tool that analyzes a project and generates a README.**

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![uv](https://img.shields.io/badge/uv-DE5FE9?logo=uv&logoColor=white) ![Gemini](https://img.shields.io/badge/Gemini-8E75B2?logo=googlegemini&logoColor=white) ![pytest](https://img.shields.io/badge/pytest-0A9EDC?logo=pytest&logoColor=white)

</div>

## Tech Stack

| Category               | Technologies |
| ---------------------- | ------------ |
| **Languages**          | Python       |
| **AI**                 | Gemini       |
| **CLI Framework**      | Typer        |
| **Testing**            | pytest       |
| **Package Management** | uv           |

## Installation

```bash
git clone https://github.com/olashin1/readme_gen.git
cd readme_gen
uv sync
```

## Usage

### CLI

```bash
readme-gen
```

## Examples

### Example 1

```bash
git clone https://github.com/olashin1/readme_gen.git
cd readme_gen
uv sync
```

### Example 2

```bash
readme-gen
```

## Environment Variables

The application reads the following variable names. Values are not included in this README.

| Variable         | Detected in                           |
| ---------------- | ------------------------------------- |
| `GEMINI_API_KEY` | `.env`, `src/readme_gen/ai/client.py` |
| `GITHUB_TOKEN`   | `src/readme_gen/github/client.py`     |

## Testing

```bash
uv run pytest
```

## Project Structure

```text
readme-gen/
├── src/  # Source code
│   └── readme_gen/
├── tests/  # Test suite
├── readme-examples/
├── pyproject.toml  # Python project configuration
└── README.md  # Project documentation
```
