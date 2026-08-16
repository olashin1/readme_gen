from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from readme_gen.github.models import GitHubRepositoryMetadata


@dataclass(frozen=True, slots=True)
class RepositoryContext:
    """
    Resolved repository input ready for downstream analysis.

    Regardless of whether the user supplied a local path or GitHub URL,
    downstream code receives a local filesystem path that can be passed
    directly to the existing scanner.

    Attributes:
        path:
            Local filesystem path containing the repository.

        source:
            Human-readable source identifier, such as a local path or GitHub
            repository URL.

        github:
            GitHub metadata when the repository originated from GitHub.
            Local repositories currently leave this as None.
    """

    path: Path
    source: str
    github: GitHubRepositoryMetadata | None = None

    @property
    def is_github(self) -> bool:
        """
        Return True when this context originated from a GitHub repository.
        """
        return self.github is not None