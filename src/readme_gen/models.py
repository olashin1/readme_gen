from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel


class ProjectAnalysis(BaseModel):
    summary: str
    features: list[str]
    intended_users: str
    usage_summary: str
    architecture: str


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

    analysis: ProjectAnalysis | None = None