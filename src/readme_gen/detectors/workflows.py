from __future__ import annotations

import re
from pathlib import Path

from readme_gen.models import WorkflowInfo


WORKFLOW_DIRECTORY = Path(".github") / "workflows"

WORKFLOW_SUFFIXES = {
    ".yml",
    ".yaml",
}

MAX_WORKFLOW_FILE_SIZE = 512_000


PURPOSE_PATTERNS: tuple[
    tuple[str, tuple[str, ...]],
    ...,
] = (
    (
        "testing",
        (
            "test",
            "tests",
            "testing",
            "pytest",
            "unittest",
            "coverage",
            "tox",
            "nox",
        ),
    ),
    (
        "linting",
        (
            "lint",
            "linting",
            "pre-commit",
            "precommit",
            "ruff",
            "flake8",
            "eslint",
            "pylint",
            "mypy",
            "typecheck",
            "type-check",
            "format",
            "formatting",
        ),
    ),
    (
        "publishing",
        (
            "publish",
            "publishing",
            "release",
            "deploy",
            "deployment",
            "pypi",
            "npm publish",
            "cargo publish",
            "docker push",
        ),
    ),
    (
        "security",
        (
            "security",
            "codeql",
            "dependabot",
            "sast",
            "scan",
            "scanning",
            "zizmor",
            "trivy",
        ),
    ),
    (
        "documentation",
        (
            "docs",
            "documentation",
            "mkdocs",
            "sphinx",
            "readthedocs",
        ),
    ),
    (
        "build",
        (
            "build",
            "compile",
            "cmake",
            "cargo build",
        ),
    ),
)


def detect_workflows(
    root: Path,
) -> list[WorkflowInfo]:
    """
    Detect GitHub Actions workflows in a repository.

    Workflow files are discovered under:

        .github/workflows/

    Each workflow is assigned a broad purpose using its filename, declared
    workflow name, and a limited amount of workflow content.

    The detector intentionally avoids requiring a YAML dependency because
    README generation only needs lightweight workflow metadata rather than a
    complete GitHub Actions parser.
    """
    workflow_directory = (
        root / WORKFLOW_DIRECTORY
    )

    if not workflow_directory.is_dir():
        return []

    workflow_files = sorted(
        (
            path
            for path in workflow_directory.iterdir()
            if (
                path.is_file()
                and path.suffix.lower()
                in WORKFLOW_SUFFIXES
            )
        ),
        key=lambda path: path.name.lower(),
    )

    workflows: list[WorkflowInfo] = []

    for workflow_path in workflow_files:
        workflow = parse_workflow(
            root=root,
            workflow_path=workflow_path,
        )

        if workflow is not None:
            workflows.append(workflow)

    return workflows


def parse_workflow(
    root: Path,
    workflow_path: Path,
) -> WorkflowInfo | None:
    """
    Extract the small amount of workflow information needed by readme-gen.

    Files that cannot be safely read are ignored rather than causing the
    entire repository scan to fail.
    """
    try:
        if (
            workflow_path.stat().st_size
            > MAX_WORKFLOW_FILE_SIZE
        ):
            return None

        content = workflow_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    except OSError:
        return None

    relative_path = (
        workflow_path
        .relative_to(root)
        .as_posix()
    )

    name = extract_workflow_name(
        content
    )

    if not name:
        name = humanize_workflow_filename(
            workflow_path.stem
        )

    purpose = detect_workflow_purpose(
        filename=workflow_path.stem,
        name=name,
        content=content,
    )

    return WorkflowInfo(
        name=name,
        path=relative_path,
        purpose=purpose,
    )


def extract_workflow_name(
    content: str,
) -> str | None:
    """
    Extract the workflow-level `name:` field without fully parsing YAML.

    Only an unindented top-level name is considered so job names and step
    names are not mistaken for the workflow name.
    """
    match = re.search(
        r"(?m)^name:\s*(.+?)\s*$",
        content,
    )

    if not match:
        return None

    name = match.group(1).strip()

    if (
        len(name) >= 2
        and name[0] == name[-1]
        and name[0] in {'"', "'"}
    ):
        name = name[1:-1].strip()

    return name or None


def detect_workflow_purpose(
    filename: str,
    name: str,
    content: str,
) -> str:
    """
    Infer the broad purpose of a workflow.

    Workflow identity receives more weight than arbitrary step contents:
    filename and workflow name are checked first, followed by file content.
    """
    identity = (
        f"{filename} {name}"
    ).lower()

    identity_match = match_purpose(
        identity
    )

    if identity_match:
        return identity_match

    content_match = match_purpose(
        content.lower()
    )

    if content_match:
        return content_match

    return "ci"


def match_purpose(
    value: str,
) -> str | None:
    """
    Match text against the known workflow-purpose vocabulary.
    """
    normalized = normalize_text(
        value
    )

    for purpose, patterns in PURPOSE_PATTERNS:
        for pattern in patterns:
            if normalize_text(pattern) in normalized:
                return purpose

    return None


def normalize_text(
    value: str,
) -> str:
    """
    Normalize text for lightweight keyword matching.
    """
    return re.sub(
        r"[^a-z0-9]+",
        " ",
        value.lower(),
    ).strip()


def humanize_workflow_filename(
    filename: str,
) -> str:
    """
    Convert a workflow filename into a readable fallback name.

    Examples:
        tests -> Tests
        pre-commit -> Pre Commit
        release_package -> Release Package
    """
    words = re.split(
        r"[-_.\s]+",
        filename,
    )

    return " ".join(
        word.capitalize()
        for word in words
        if word
    )