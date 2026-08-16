from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from unittest.mock import Mock

import pytest

from readme_gen.github.models import (
    GitHubRepositoryMetadata,
)
from readme_gen.repository.resolver import (
    GitHubRepositorySource,
    LocalRepositorySource,
    RepositorySourceError,
    resolve_repository_source,
)


def test_resolver_returns_local_source_for_path() -> None:
    source = resolve_repository_source(".")

    assert isinstance(
        source,
        LocalRepositorySource,
    )


def test_resolver_returns_github_source_for_url() -> None:
    client = Mock()

    source = resolve_repository_source(
        "https://github.com/owner/project",
        github_client=client,
    )

    assert isinstance(
        source,
        GitHubRepositorySource,
    )


def test_local_repository_source_resolves_path(
    tmp_path: Path,
) -> None:
    source = LocalRepositorySource(
        tmp_path
    )

    with source.open() as repository:
        assert repository.path == tmp_path.resolve()
        assert repository.source == str(
            tmp_path.resolve()
        )
        assert repository.github is None
        assert repository.is_github is False


def test_local_repository_source_rejects_missing_path(
    tmp_path: Path,
) -> None:
    source = LocalRepositorySource(
        tmp_path / "missing"
    )

    with pytest.raises(
        RepositorySourceError
    ):
        with source.open():
            pass


def test_local_repository_source_rejects_file(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "README.md"
    file_path.write_text(
        "# Test\n",
        encoding="utf-8",
    )

    source = LocalRepositorySource(
        file_path
    )

    with pytest.raises(
        RepositorySourceError
    ):
        with source.open():
            pass


def test_resolver_rejects_empty_source() -> None:
    with pytest.raises(
        RepositorySourceError
    ):
        resolve_repository_source("   ")


def test_github_repository_source_returns_context(
    tmp_path: Path,
) -> None:
    metadata = GitHubRepositoryMetadata(
        owner="owner",
        name="project",
        full_name="owner/project",
        url="https://github.com/owner/project",
        description="Example project",
        default_branch="main",
    )

    client = Mock()

    client.get_repository_metadata.return_value = (
        metadata
    )

    @contextmanager
    def fake_download_repository(
        repository,
    ) -> Iterator[Path]:
        yield tmp_path

    client.download_repository.side_effect = (
        fake_download_repository
    )

    source = GitHubRepositorySource(
        "https://github.com/owner/project",
        client=client,
    )

    with source.open() as repository:
        assert repository.path == tmp_path

        assert (
            repository.source
            == "https://github.com/owner/project"
        )

        assert repository.github == metadata
        assert repository.is_github is True

    client.get_repository_metadata.assert_called_once()

    client.download_repository.assert_called_once()


def test_github_source_parses_repository_before_client_calls(
    tmp_path: Path,
) -> None:
    metadata = GitHubRepositoryMetadata(
        owner="owner",
        name="project",
        full_name="owner/project",
        url="https://github.com/owner/project",
    )

    client = Mock()

    client.get_repository_metadata.return_value = (
        metadata
    )

    @contextmanager
    def fake_download_repository(
        repository,
    ) -> Iterator[Path]:
        assert repository.owner == "owner"
        assert repository.name == "project"

        yield tmp_path

    client.download_repository.side_effect = (
        fake_download_repository
    )

    source = GitHubRepositorySource(
        "https://github.com/owner/project",
        client=client,
    )

    with source.open():
        pass

    repository_argument = (
        client.get_repository_metadata
        .call_args
        .args[0]
    )

    assert repository_argument.owner == "owner"
    assert repository_argument.name == "project"