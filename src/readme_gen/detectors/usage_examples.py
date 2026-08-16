from __future__ import annotations

import re
from pathlib import Path

from readme_gen.models import UsageExample


MAX_EXAMPLES = 3
MAX_FILE_SIZE = 256_000
MAX_CODE_CHARS = 1_500

README_NAMES = (
    "README.md",
    "README.markdown",
)

DOC_CANDIDATE_NAMES = (
    "quickstart.md",
    "quick-start.md",
    "getting-started.md",
    "getting_started.md",
    "usage.md",
)


def detect_usage_examples(
    root: Path,
) -> list[UsageExample]:
    """
    Detect concise usage examples directly from repository documentation.

    README examples are preferred, followed by common quick-start and usage
    documentation files. Only fenced code blocks are considered so the
    detector does not invent or reconstruct examples.
    """
    candidates = get_candidate_files(
        root
    )

    examples: list[UsageExample] = []

    for path in candidates:
        for example in extract_examples_from_markdown(
            root=root,
            path=path,
        ):
            examples.append(example)

            if len(examples) >= MAX_EXAMPLES:
                return examples

    return examples


def get_candidate_files(
    root: Path,
) -> list[Path]:
    """
    Return documentation files in priority order.
    """
    candidates: list[Path] = []

    for name in README_NAMES:
        path = root / name

        if path.is_file():
            candidates.append(path)

    docs_directory = root / "docs"

    if docs_directory.is_dir():
        for name in DOC_CANDIDATE_NAMES:
            path = docs_directory / name

            if path.is_file():
                candidates.append(path)

    for name in DOC_CANDIDATE_NAMES:
        path = root / name

        if path.is_file():
            candidates.append(path)

    return candidates


def extract_examples_from_markdown(
    root: Path,
    path: Path,
) -> list[UsageExample]:
    """
    Extract fenced code blocks from a Markdown file.
    """
    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            return []

        content = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    except OSError:
        return []

    examples: list[UsageExample] = []

    pattern = re.compile(
        r"```([a-zA-Z0-9_+\-]*)[ \t]*\n(.*?)```",
        re.DOTALL,
    )

    for match in pattern.finditer(content):
        language = match.group(1).strip().lower()
        code = match.group(2).strip()

        if not is_useful_example(
            language=language,
            code=code,
        ):
            continue

        if len(code) > MAX_CODE_CHARS:
            continue

        relative_path = (
            path
            .relative_to(root)
            .as_posix()
        )

        examples.append(
            UsageExample(
                language=normalize_language(
                    language
                ),
                code=code,
                source=relative_path,
            )
        )

    return examples


def is_useful_example(
    language: str,
    code: str,
) -> bool:
    """
    Filter out blocks that are unlikely to demonstrate project usage.
    """
    if not code:
        return False

    normalized_language = (
        language.lower()
    )

    ignored_languages = {
        "text",
        "plaintext",
        "json",
        "yaml",
        "yml",
        "toml",
        "ini",
        "diff",
    }

    if normalized_language in ignored_languages:
        return False

    lines = [
        line
        for line in code.splitlines()
        if line.strip()
    ]

    if not lines:
        return False

    if len(lines) > 40:
        return False

    return True


def normalize_language(
    language: str,
) -> str:
    aliases = {
        "py": "python",
        "sh": "bash",
        "shell": "bash",
        "console": "bash",
        "js": "javascript",
        "ts": "typescript",
    }

    if not language:
        return "text"

    return aliases.get(
        language,
        language,
    )