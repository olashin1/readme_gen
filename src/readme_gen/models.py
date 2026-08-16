from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel, Field


class ProjectAnalysis(BaseModel):
    tagline: str = Field(
        description=(
            "A concise one-sentence tagline suitable for display directly "
            "beneath the project title in a GitHub README."
        )
    )

    summary: str = Field(
        description=(
            "A concise overview explaining what the project does, what "
            "problem it solves, and who it is useful for."
        )
    )

    highlights: list[str] = Field(
        description=(
            "Four to six concise, compelling project highlights suitable "
            "for a GitHub landing-page README. Focus on the project's most "
            "important user-facing strengths rather than exhaustive "
            "implementation details."
        )
    )

    usage_summary: str = Field(
        description=(
            "A short explanation of how a user typically interacts with or "
            "runs the project."
        )
    )

    architecture: str = Field(
        description=(
            "A high-level explanation of the project's architecture and "
            "major components without excessive implementation detail."
        )
    )


@dataclass
class RepositoryMetadata:
    """
    Provider-neutral metadata about the repository hosting the project.

    This model intentionally does not depend on GitHub-specific classes so
    the scanner, AI layer, and README generator remain independent from the
    implementation used to retrieve remote repository information.
    """

    owner: str | None = None
    name: str | None = None
    url: str | None = None

    description: str | None = None
    homepage: str | None = None

    topics: list[str] = field(default_factory=list)

    default_branch: str | None = None

    primary_language: str | None = None
    language_bytes: dict[str, int] = field(default_factory=dict)

    license_name: str | None = None
    license_spdx_id: str | None = None

    issues_url: str | None = None
    actions_url: str | None = None

    stars: int | None = None
    forks: int | None = None

    archived: bool = False


@dataclass(frozen=True, slots=True)
class WorkflowInfo:
    """
    Information about a detected GitHub Actions workflow.

    Attributes:
        name:
            Human-facing workflow name.

        path:
            Repository-relative path to the workflow file.

        purpose:
            Broad purpose inferred from the workflow, such as testing,
            linting, publishing, security, documentation, or general CI.
    """

    name: str
    path: str
    purpose: str


@dataclass
class ProjectInfo:
    name: str
    root: Path

    description: str | None = None
    repository_url: str | None = None
    license: str | None = None
    project_type: str | None = None

    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    package_managers: list[str] = field(default_factory=list)

    dependencies: list[str] = field(default_factory=list)
    dev_dependencies: list[str] = field(default_factory=list)

    cli_commands: dict[str, str] = field(default_factory=dict)
    package_scripts: dict[str, str] = field(default_factory=dict)

    source_dirs: list[str] = field(default_factory=list)
    test_dirs: list[str] = field(default_factory=list)
    important_files: list[str] = field(default_factory=list)
    context_files: list[str] = field(default_factory=list)
    directory_tree: list[str] = field(default_factory=list)

    workflows: list[WorkflowInfo] = field(default_factory=list)

    repository: RepositoryMetadata | None = None
    analysis: ProjectAnalysis | None = None