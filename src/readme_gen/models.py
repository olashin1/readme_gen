from dataclasses import dataclass, field
from enum import StrEnum
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
            "Up to six concise, repository-supported project highlights. "
            "Return fewer or none when the supplied facts do not establish "
            "user-facing capabilities."
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


class Confidence(StrEnum):
    """How strongly repository evidence supports a detected fact."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True, slots=True)
class Evidence:
    source: str
    kind: str
    confidence: Confidence = Confidence.HIGH


@dataclass(frozen=True, slots=True)
class TechnologyInfo:
    name: str
    category: str
    role: str | None = None
    evidence: tuple[Evidence, ...] = ()


@dataclass(frozen=True, slots=True)
class ProjectCommand:
    kind: str
    command: str
    source: str
    name: str | None = None


@dataclass(frozen=True, slots=True)
class EnvironmentVariable:
    name: str
    sources: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ApiRoute:
    method: str
    path: str
    source: str
    handler: str | None = None


@dataclass(frozen=True, slots=True)
class ProjectAsset:
    path: str
    kind: str


@dataclass
class RepositoryMetadata:
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
    name: str
    path: str
    purpose: str


@dataclass(frozen=True, slots=True)
class PackageInfo:
    ecosystem: str
    name: str
    version: str | None
    manifest: str
    install_command: str


@dataclass(frozen=True, slots=True)
class UsageExample:
    """
    A concise usage example detected directly from the repository.

    Attributes:
        language:
            Markdown code-fence language.

        code:
            Example code or command content.

        source:
            Repository-relative file that provided the example.

        title:
            Optional short label describing the example.
    """

    language: str
    code: str
    source: str
    title: str | None = None


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
    libraries: list[str] = field(default_factory=list)
    package_managers: list[str] = field(default_factory=list)

    technologies: list[TechnologyInfo] = field(default_factory=list)
    technology_roles: dict[str, list[str]] = field(default_factory=dict)
    databases: list[str] = field(default_factory=list)
    external_services: list[str] = field(default_factory=list)
    frontend: list[str] = field(default_factory=list)
    backend: list[str] = field(default_factory=list)

    dependencies: list[str] = field(default_factory=list)
    dev_dependencies: list[str] = field(default_factory=list)

    cli_commands: dict[str, str] = field(default_factory=dict)
    package_scripts: dict[str, str] = field(default_factory=dict)
    commands: list[ProjectCommand] = field(default_factory=list)
    environment_variables: list[EnvironmentVariable] = field(
        default_factory=list
    )
    api_routes: list[ApiRoute] = field(default_factory=list)
    assets: list[ProjectAsset] = field(default_factory=list)

    # Optional repository-derived statements. Detectors should leave these
    # empty instead of inferring capabilities from filenames alone.
    features: list[str] = field(default_factory=list)
    architecture_components: list[str] = field(default_factory=list)

    source_dirs: list[str] = field(default_factory=list)
    test_dirs: list[str] = field(default_factory=list)
    important_files: list[str] = field(default_factory=list)
    context_files: list[str] = field(default_factory=list)
    directory_tree: list[str] = field(default_factory=list)

    workflows: list[WorkflowInfo] = field(default_factory=list)
    packages: list[PackageInfo] = field(default_factory=list)
    usage_examples: list[UsageExample] = field(default_factory=list)

    repository: RepositoryMetadata | None = None
    analysis: ProjectAnalysis | None = None
