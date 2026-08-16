from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from readme_gen.github.client import GitHubClient
from readme_gen.github.parser import (
    is_github_url,
    parse_github_url,
)
from readme_gen.repository.models import RepositoryContext
from readme_gen.repository.source import RepositorySource


class RepositorySourceError(ValueError):
    """
    Raised when repository input cannot be resolved.
    """


class LocalRepositorySource(RepositorySource):
    """
    Repository source backed by an existing local directory.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    @contextmanager
    def open(self) -> Iterator[RepositoryContext]:
        """
        Resolve and expose the local repository directory.
        """
        resolved_path = self.path.expanduser().resolve()

        if not resolved_path.exists():
            raise RepositorySourceError(
                f"Repository path does not exist: {resolved_path}"
            )

        if not resolved_path.is_dir():
            raise RepositorySourceError(
                f"Repository path is not a directory: {resolved_path}"
            )

        yield RepositoryContext(
            path=resolved_path,
            source=str(resolved_path),
        )


class GitHubRepositorySource(RepositorySource):
    """
    Repository source backed by a GitHub repository URL.
    """

    def __init__(
        self,
        url: str,
        client: GitHubClient | None = None,
    ) -> None:
        self.url = url
        self.client = client or GitHubClient()

    @contextmanager
    def open(self) -> Iterator[RepositoryContext]:
        """
        Retrieve GitHub metadata and expose the downloaded repository through
        a temporary local directory.
        """
        repository = parse_github_url(self.url)

        metadata = self.client.get_repository_metadata(
            repository
        )

        with self.client.download_repository(
            repository
        ) as project_path:
            yield RepositoryContext(
                path=project_path,
                source=repository.url,
                github=metadata,
            )


def resolve_repository_source(
    value: str | Path,
    *,
    github_client: GitHubClient | None = None,
) -> RepositorySource:
    """
    Resolve user input into the appropriate repository source implementation.

    GitHub URLs are routed to GitHubRepositorySource. All other values are
    treated as filesystem paths.

    Args:
        value:
            Repository input supplied by the user.

        github_client:
            Optional GitHub client dependency, primarily useful for tests.

    Returns:
        RepositorySource suitable for use as a context manager.

    Examples:
        source = resolve_repository_source(".")

        with source.open() as repository:
            project = scan_project(repository.path)

    """
    raw_value = str(value).strip()

    if not raw_value:
        raise RepositorySourceError(
            "Repository source cannot be empty."
        )

    if is_github_url(raw_value):
        return GitHubRepositorySource(
            raw_value,
            client=github_client,
        )

    return LocalRepositorySource(
        Path(raw_value)
    )