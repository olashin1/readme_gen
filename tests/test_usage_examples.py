from pathlib import Path

from readme_gen.detectors.usage_examples import (
    detect_usage_examples,
    extract_examples_from_markdown,
)


def test_detect_usage_example_from_readme(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "README.md"
    ).write_text(
        """
# Demo

## Usage

```python
from demo import Demo

app = Demo()
app.run()
```
""".strip(),
        encoding="utf-8",
    )

    examples = detect_usage_examples(
        tmp_path
    )

    assert len(examples) == 1

    example = examples[0]

    assert example.language == "python"
    assert "from demo import Demo" in example.code
    assert example.source == "README.md"


def test_normalizes_python_fence(
    tmp_path: Path,
) -> None:
    readme = tmp_path / "README.md"

    readme.write_text(
        """
```py
print("hello")
```
""".strip(),
        encoding="utf-8",
    )

    examples = extract_examples_from_markdown(
        root=tmp_path,
        path=readme,
    )

    assert examples[0].language == "python"


def test_normalizes_shell_fence(
    tmp_path: Path,
) -> None:
    readme = tmp_path / "README.md"

    readme.write_text(
        """
```sh
demo --help
```
""".strip(),
        encoding="utf-8",
    )

    examples = extract_examples_from_markdown(
        root=tmp_path,
        path=readme,
    )

    assert examples[0].language == "bash"


def test_ignores_configuration_blocks(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "README.md"
    ).write_text(
        """
```toml
[project]
name = "demo"
```

```python
import demo
```
""".strip(),
        encoding="utf-8",
    )

    examples = detect_usage_examples(
        tmp_path
    )

    assert len(examples) == 1
    assert examples[0].language == "python"


def test_ignores_empty_blocks(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "README.md"
    ).write_text(
        """
```python
```
""".strip(),
        encoding="utf-8",
    )

    assert detect_usage_examples(
        tmp_path
    ) == []


def test_detects_quickstart_documentation(
    tmp_path: Path,
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()

    (
        docs / "quickstart.md"
    ).write_text(
        """
# Quickstart

```python
from demo import create_app

app = create_app()
```
""".strip(),
        encoding="utf-8",
    )

    examples = detect_usage_examples(
        tmp_path
    )

    assert len(examples) == 1
    assert examples[0].source == "docs/quickstart.md"


def test_readme_is_preferred_over_docs(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "README.md"
    ).write_text(
        """
```python
print("readme")
```
""".strip(),
        encoding="utf-8",
    )

    docs = tmp_path / "docs"
    docs.mkdir()

    (
        docs / "usage.md"
    ).write_text(
        """
```python
print("docs")
```
""".strip(),
        encoding="utf-8",
    )

    examples = detect_usage_examples(
        tmp_path
    )

    assert examples[0].source == "README.md"


def test_limits_number_of_examples(
    tmp_path: Path,
) -> None:
    (
        tmp_path / "README.md"
    ).write_text(
        """
```python
print("one")
```

```python
print("two")
```

```python
print("three")
```

```python
print("four")
```
""".strip(),
        encoding="utf-8",
    )

    examples = detect_usage_examples(
        tmp_path
    )

    assert len(examples) == 3