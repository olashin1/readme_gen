from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProjectInfo:
    name: str
    root: Path

    description: str | None = None
    repository_url: str | None = None
    license: str | None = None

    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    package_managers: list[str] = field(default_factory=list)

    dependencies: list[str] = field(default_factory=list)
    dev_dependencies: list[str] = field(default_factory=list)

    scripts: dict[str, str] = field(default_factory=dict)
    entry_points: list[str] = field(default_factory=list)

    source_dirs: list[str] = field(default_factory=list)
    test_dirs: list[str] = field(default_factory=list)
    important_files: list[str] = field(default_factory=list)
    directory_tree: list[str] = field(default_factory=list)