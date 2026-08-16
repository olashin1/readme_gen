<div align="center">

# readme-gen

**A CLI tool that analyzes a project and generates a README.**

![Typer](https://img.shields.io/badge/Typer-4C566A)

</div>

## 🛠️ Tech Stack

| Category               | Technologies |
| ---------------------- | ------------ |
| **Languages**          | Python       |
| **AI**                 | Gemini       |
| **CLI Framework**      | Typer        |
| **Package Management** | uv           |

## ⬇️ Installation

```bash
pip install readme-gen
```

## 🚀 Usage

### CLI

```bash
readme-gen
```

## ⚡ Examples

### Example 1

```bash
pip install readme-gen
```

### Example 2

```bash
readme-gen
```

### Example 3

```bash
readme-gen . --debug-metadata
```

## ⚙️ Environment Variables

The application reads the following variable names. Values are not included in this README.

| Variable         | Detected in                           |
| ---------------- | ------------------------------------- |
| `GEMINI_API_KEY` | `.env`, `src/readme_gen/ai/client.py` |
| `GITHUB_TOKEN`   | `src/readme_gen/github/client.py`     |

## ✅ Testing

```bash
uv run pytest
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

```bash
git clone https://github.com/olashin1/readme_gen.git
cd readme_gen
uv sync
```

</details>
