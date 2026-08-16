from __future__ import annotations

import io
import json
import urllib.error
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from readme_gen.github.client import (
    GitHubAuthenticationError,
    GitHubClient,
    GitHubDownloadError,
    GitHubRateLimitError,
    GitHubRepositoryNotFoundError,
)
from readme_gen.github.models import GitHubRepository


class FakeResponse:
    """
    Minimal urllib-compatible response used by the GitHub client tests.
    """

    def __init__(self, body: bytes) -> None:
        self._body = io.BytesIO(body)

    def read(self, size: int = -1) -> bytes:
        return self._body.read(size)

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        self._body.close()


def make_http_error(
    status_code: int,
    headers: dict[str, str] | None = None,
) -> urllib.error.HTTPError:
    """
    Create an HTTPError for exercising GitHub client error handling.
    """
    return urllib.error.HTTPError(
        url="https://api.github.com/example",
        code=status_code,
        msg="Test error",
        hdrs=headers or {},
        fp=None,
    )


def make_zip_bytes() -> bytes:
    """
    Create an in-memory ZIP shaped like a GitHub repository archive.
    """
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "owner-project-abc123/README.md",
            "# Project\n",
        )

        archive.writestr(
            "owner-project-abc123/src/main.py",
            'print("hello")\n',
        )

    return buffer.getvalue()


def test_client_uses_explicit_token() -> None:
    client = GitHubClient(token="test-token")

    request = client._build_request(
        "https://api.github.com/repos/owner/project"
    )

    assert request.get_header("Authorization") == "Bearer test-token"


def test_client_uses_environment_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "GITHUB_TOKEN",
        "environment-token",
    )

    client = GitHubClient()

    request = client._build_request(
        "https://api.github.com/repos/owner/project"
    )

    assert (
        request.get_header("Authorization")
        == "Bearer environment-token"
    )


def test_client_allows_unauthenticated_requests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "GITHUB_TOKEN",
        raising=False,
    )

    client = GitHubClient()

    request = client._build_request(
        "https://api.github.com/repos/owner/project"
    )

    assert request.get_header("Authorization") is None


def test_get_repository_metadata() -> None:
    repository_payload = {
        "full_name": "owner/project",
        "html_url": "https://github.com/owner/project",
        "description": "Example project",
        "homepage": "https://example.com",
        "default_branch": "main",
        "topics": [
            "python",
            "cli",
        ],
        "language": "Python",
        "license": {
            "key": "mit",
            "name": "MIT License",
            "spdx_id": "MIT",
            "url": "https://api.github.com/licenses/mit",
        },
        "stargazers_count": 123,
        "forks_count": 12,
        "open_issues_count": 4,
        "has_issues": True,
        "archived": False,
        "fork": False,
    }

    languages_payload = {
        "Python": 8000,
        "Shell": 1000,
    }

    responses = [
        FakeResponse(
            json.dumps(repository_payload).encode("utf-8")
        ),
        FakeResponse(
            json.dumps(languages_payload).encode("utf-8")
        ),
    ]

    repository = GitHubRepository(
        owner="owner",
        name="project",
    )

    client = GitHubClient()

    with patch(
        "urllib.request.urlopen",
        side_effect=responses,
    ):
        metadata = client.get_repository_metadata(
            repository
        )

    assert metadata.owner == "owner"
    assert metadata.name == "project"
    assert metadata.full_name == "owner/project"

    assert (
        metadata.url
        == "https://github.com/owner/project"
    )

    assert metadata.description == "Example project"
    assert metadata.homepage == "https://example.com"
    assert metadata.default_branch == "main"

    assert metadata.topics == (
        "python",
        "cli",
    )

    assert metadata.primary_language == "Python"

    assert metadata.languages == {
        "Python": 8000,
        "Shell": 1000,
    }

    assert metadata.license is not None
    assert metadata.license.spdx_id == "MIT"

    assert metadata.stars == 123
    assert metadata.forks == 12
    assert metadata.open_issues == 4

    assert metadata.has_issues is True
    assert metadata.archived is False
    assert metadata.fork is False


def test_metadata_generates_repository_links() -> None:
    repository_payload = {
        "full_name": "owner/project",
        "html_url": "https://github.com/owner/project",
    }

    responses = [
        FakeResponse(
            json.dumps(repository_payload).encode("utf-8")
        ),
        FakeResponse(b"{}"),
    ]

    client = GitHubClient()

    repository = GitHubRepository(
        owner="owner",
        name="project",
    )

    with patch(
        "urllib.request.urlopen",
        side_effect=responses,
    ):
        metadata = client.get_repository_metadata(
            repository
        )

    assert (
        metadata.issues_url
        == "https://github.com/owner/project/issues"
    )

    assert (
        metadata.actions_url
        == "https://github.com/owner/project/actions"
    )


def test_download_repository_archive(
    tmp_path: Path,
) -> None:
    client = GitHubClient()

    repository = GitHubRepository(
        owner="owner",
        name="project",
    )

    destination = tmp_path / "repository.zip"

    archive_bytes = make_zip_bytes()

    with patch(
        "urllib.request.urlopen",
        return_value=FakeResponse(
            archive_bytes
        ),
    ):
        result = client.download_repository_archive(
            repository,
            destination,
        )

    assert result == destination.resolve()
    assert destination.exists()

    assert destination.read_bytes() == archive_bytes


def test_extract_repository_archive(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "repository.zip"

    archive_path.write_bytes(
        make_zip_bytes()
    )

    extraction_path = tmp_path / "extracted"

    client = GitHubClient()

    project_path = (
        client.extract_repository_archive(
            archive_path,
            extraction_path,
        )
    )

    assert (
        project_path.name
        == "owner-project-abc123"
    )

    assert (
        project_path / "README.md"
    ).exists()

    assert (
        project_path / "src" / "main.py"
    ).exists()


def test_download_repository_context_manager() -> None:
    repository = GitHubRepository(
        owner="owner",
        name="project",
    )

    client = GitHubClient()

    archive_bytes = make_zip_bytes()

    with patch(
        "urllib.request.urlopen",
        return_value=FakeResponse(
            archive_bytes
        ),
    ):
        with client.download_repository(
            repository
        ) as project_path:
            temporary_path = project_path

            assert project_path.exists()

            assert (
                project_path / "README.md"
            ).exists()

    assert not temporary_path.exists()


def test_401_raises_authentication_error() -> None:
    client = GitHubClient()

    with patch(
        "urllib.request.urlopen",
        side_effect=make_http_error(401),
    ):
        with pytest.raises(
            GitHubAuthenticationError
        ):
            client._get_json(
                "/repos/owner/project"
            )


def test_403_rate_limit_raises_rate_limit_error() -> None:
    client = GitHubClient()

    error = make_http_error(
        403,
        {
            "X-RateLimit-Remaining": "0",
        },
    )

    with patch(
        "urllib.request.urlopen",
        side_effect=error,
    ):
        with pytest.raises(
            GitHubRateLimitError
        ):
            client._get_json(
                "/repos/owner/project"
            )


def test_404_raises_repository_not_found() -> None:
    client = GitHubClient()

    with patch(
        "urllib.request.urlopen",
        side_effect=make_http_error(404),
    ):
        with pytest.raises(
            GitHubRepositoryNotFoundError
        ):
            client._get_json(
                "/repos/owner/project"
            )


def test_429_raises_rate_limit_error() -> None:
    client = GitHubClient()

    with patch(
        "urllib.request.urlopen",
        side_effect=make_http_error(429),
    ):
        with pytest.raises(
            GitHubRateLimitError
        ):
            client._get_json(
                "/repos/owner/project"
            )


def test_extract_rejects_bad_zip(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "repository.zip"

    archive_path.write_bytes(
        b"not a zip archive"
    )

    client = GitHubClient()

    with pytest.raises(
        GitHubDownloadError
    ):
        client.extract_repository_archive(
            archive_path,
            tmp_path / "extracted",
        )


def test_extract_rejects_unsafe_paths(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "repository.zip"

    with zipfile.ZipFile(
        archive_path,
        "w",
    ) as archive:
        archive.writestr(
            "../dangerous.txt",
            "unsafe",
        )

    client = GitHubClient()

    with pytest.raises(
        GitHubDownloadError
    ):
        client.extract_repository_archive(
            archive_path,
            tmp_path / "extracted",
        )