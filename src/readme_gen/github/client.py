from __future__ import annotations

import json
import os
import shutil
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from readme_gen.github.models import (
    GitHubLicense,
    GitHubRepository,
    GitHubRepositoryMetadata,
)


GITHUB_API_BASE_URL = "https://api.github.com"

# GitHub's REST API is versioned. Keeping the version explicit makes our
# integration deterministic rather than silently changing with API behavior.
GITHUB_API_VERSION = "2022-11-28"

DEFAULT_TIMEOUT_SECONDS = 30


class GitHubError(RuntimeError):
    """
    Base exception for GitHub-related failures.
    """


class GitHubRepositoryNotFoundError(GitHubError):
    """
    Raised when a GitHub repository cannot be found or accessed.
    """


class GitHubAuthenticationError(GitHubError):
    """
    Raised when GitHub rejects authentication credentials.
    """


class GitHubRateLimitError(GitHubError):
    """
    Raised when GitHub API rate limits prevent a request.
    """


class GitHubDownloadError(GitHubError):
    """
    Raised when a repository archive cannot be downloaded or extracted.
    """


class GitHubResponseError(GitHubError):
    """
    Raised when GitHub returns an unexpected response.
    """


class GitHubClient:
    """
    Small GitHub REST API client used by readme-gen.

    Authentication is optional for public repositories.

    When no token is supplied directly, the client looks for the
    GITHUB_TOKEN environment variable.
    """

    def __init__(
        self,
        token: str | None = None,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout

    def get_repository_metadata(
        self,
        repository: GitHubRepository,
    ) -> GitHubRepositoryMetadata:
        """
        Retrieve normalized metadata for a GitHub repository.

        This combines:

        - the main repository endpoint
        - the repository languages endpoint

        into a single GitHubRepositoryMetadata instance.
        """
        repository_data = self._get_json(
            f"/repos/{self._encode(repository.owner)}/"
            f"{self._encode(repository.name)}"
        )

        languages_data = self._get_json(
            f"/repos/{self._encode(repository.owner)}/"
            f"{self._encode(repository.name)}/languages"
        )

        if not isinstance(repository_data, dict):
            raise GitHubResponseError(
                "GitHub returned invalid repository metadata."
            )

        if not isinstance(languages_data, dict):
            raise GitHubResponseError(
                "GitHub returned invalid repository language data."
            )

        license_data = self._parse_license(
            repository_data.get("license")
        )

        topics = repository_data.get("topics", [])

        if not isinstance(topics, list):
            topics = []

        normalized_topics = tuple(
            topic
            for topic in topics
            if isinstance(topic, str)
        )

        languages: dict[str, int] = {}

        for language, byte_count in languages_data.items():
            if (
                isinstance(language, str)
                and isinstance(byte_count, int)
            ):
                languages[language] = byte_count

        repository_url = repository_data.get("html_url")

        if not isinstance(repository_url, str):
            repository_url = repository.url

        full_name = repository_data.get("full_name")

        if not isinstance(full_name, str):
            full_name = repository.full_name

        return GitHubRepositoryMetadata(
            owner=repository.owner,
            name=repository.name,
            full_name=full_name,
            url=repository_url,
            description=self._optional_string(
                repository_data.get("description")
            ),
            homepage=self._optional_string(
                repository_data.get("homepage")
            ),
            default_branch=self._optional_string(
                repository_data.get("default_branch")
            ),
            topics=normalized_topics,
            primary_language=self._optional_string(
                repository_data.get("language")
            ),
            languages=languages,
            license=license_data,
            stars=self._integer(
                repository_data.get("stargazers_count")
            ),
            forks=self._integer(
                repository_data.get("forks_count")
            ),
            open_issues=self._integer(
                repository_data.get("open_issues_count")
            ),
            has_issues=self._boolean(
                repository_data.get("has_issues"),
                default=True,
            ),
            archived=self._boolean(
                repository_data.get("archived")
            ),
            fork=self._boolean(
                repository_data.get("fork")
            ),
        )

    def download_repository_archive(
        self,
        repository: GitHubRepository,
        destination: Path,
    ) -> Path:
        """
        Download a GitHub repository as a ZIP archive.

        When repository.ref is None, GitHub uses the repository's default
        branch.
        """
        destination = destination.resolve()
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        owner = self._encode(repository.owner)
        name = self._encode(repository.name)

        url = (
            f"{GITHUB_API_BASE_URL}/repos/"
            f"{owner}/{name}/zipball"
        )

        if repository.ref:
            ref = urllib.parse.quote(
                repository.ref,
                safe="",
            )
            url = f"{url}/{ref}"

        request = self._build_request(url)

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                with destination.open("wb") as output_file:
                    shutil.copyfileobj(
                        response,
                        output_file,
                    )

        except urllib.error.HTTPError as exc:
            self._raise_for_http_error(exc)

        except urllib.error.URLError as exc:
            raise GitHubDownloadError(
                f"Unable to download "
                f"{repository.full_name}: {exc.reason}"
            ) from exc

        except OSError as exc:
            raise GitHubDownloadError(
                f"Unable to write repository archive "
                f"to {destination}: {exc}"
            ) from exc

        if (
            not destination.exists()
            or destination.stat().st_size == 0
        ):
            raise GitHubDownloadError(
                "GitHub returned an empty repository archive."
            )

        return destination

    def extract_repository_archive(
        self,
        archive_path: Path,
        destination: Path,
    ) -> Path:
        """
        Extract a downloaded GitHub ZIP archive.

        GitHub archives contain a generated top-level directory, for example:

            owner-repository-ab12cd3/

        The returned Path points directly to that project directory.
        """
        archive_path = archive_path.resolve()
        destination = destination.resolve()

        destination.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            with zipfile.ZipFile(
                archive_path,
                "r",
            ) as archive:
                self._validate_archive(archive)
                archive.extractall(destination)

        except zipfile.BadZipFile as exc:
            raise GitHubDownloadError(
                "GitHub returned an invalid ZIP archive."
            ) from exc

        except OSError as exc:
            raise GitHubDownloadError(
                f"Unable to extract repository archive: {exc}"
            ) from exc

        directories = [
            path
            for path in destination.iterdir()
            if path.is_dir()
        ]

        if len(directories) != 1:
            raise GitHubDownloadError(
                "Expected the GitHub archive to contain exactly "
                "one top-level repository directory."
            )

        return directories[0]

    @contextmanager
    def download_repository(
        self,
        repository: GitHubRepository,
    ) -> Iterator[Path]:
        """
        Download a repository into a temporary local directory.

        The directory exists only for the duration of the context manager.

        Example:

            client = GitHubClient()

            with client.download_repository(repo) as project_path:
                project = scan_project(project_path)
        """
        with tempfile.TemporaryDirectory(
            prefix="readme-gen-"
        ) as temporary_directory:
            temp_root = Path(temporary_directory)

            archive_path = (
                temp_root / "repository.zip"
            )

            extraction_path = (
                temp_root / "repository"
            )

            self.download_repository_archive(
                repository=repository,
                destination=archive_path,
            )

            project_path = self.extract_repository_archive(
                archive_path=archive_path,
                destination=extraction_path,
            )

            yield project_path

    def _get_json(
        self,
        endpoint: str,
    ) -> Any:
        """
        Perform a GET request against a GitHub REST API endpoint and decode
        its JSON response.
        """
        url = f"{GITHUB_API_BASE_URL}{endpoint}"

        request = self._build_request(url)

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                body = response.read()

        except urllib.error.HTTPError as exc:
            self._raise_for_http_error(exc)

        except urllib.error.URLError as exc:
            raise GitHubError(
                f"Unable to connect to GitHub: {exc.reason}"
            ) from exc

        try:
            return json.loads(
                body.decode("utf-8") # type: ignore
            )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            raise GitHubResponseError(
                "GitHub returned an invalid JSON response."
            ) from exc

    def _build_request(
        self,
        url: str,
    ) -> urllib.request.Request:
        """
        Construct a GitHub API request with standard headers.
        """
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
            "User-Agent": "readme-gen",
        }

        if self.token:
            headers["Authorization"] = (
                f"Bearer {self.token}"
            )

        return urllib.request.Request(
            url=url,
            headers=headers,
            method="GET",
        )

    def _raise_for_http_error(
        self,
        error: urllib.error.HTTPError,
    ) -> None:
        """
        Translate HTTP errors into readme-gen GitHub exceptions.
        """
        status_code = error.code

        if status_code == 401:
            raise GitHubAuthenticationError(
                "GitHub authentication failed. "
                "Check your GITHUB_TOKEN."
            ) from error

        if status_code == 403:
            remaining = error.headers.get(
                "X-RateLimit-Remaining"
            )

            if remaining == "0":
                raise GitHubRateLimitError(
                    "GitHub API rate limit exceeded. "
                    "Set GITHUB_TOKEN to authenticate requests "
                    "or try again later."
                ) from error

            raise GitHubAuthenticationError(
                "GitHub denied access to this repository. "
                "If the repository is private, ensure "
                "GITHUB_TOKEN has permission to read it."
            ) from error

        if status_code == 404:
            raise GitHubRepositoryNotFoundError(
                "GitHub repository was not found or is not "
                "accessible with the current credentials."
            ) from error

        if status_code == 429:
            raise GitHubRateLimitError(
                "GitHub API rate limit exceeded. "
                "Try again later."
            ) from error

        raise GitHubError(
            f"GitHub API request failed with HTTP "
            f"status {status_code}."
        ) from error

    @staticmethod
    def _parse_license(
        value: object,
    ) -> GitHubLicense | None:
        """
        Convert GitHub's license object into our normalized model.
        """
        if not isinstance(value, dict):
            return None

        return GitHubLicense(
            key=GitHubClient._optional_string(
                value.get("key")
            ),
            name=GitHubClient._optional_string(
                value.get("name")
            ),
            spdx_id=GitHubClient._optional_string(
                value.get("spdx_id")
            ),
            url=GitHubClient._optional_string(
                value.get("url")
            ),
        )

    @staticmethod
    def _validate_archive(
        archive: zipfile.ZipFile,
    ) -> None:
        """
        Validate ZIP member paths before extraction.

        This prevents archive entries from escaping the extraction
        directory through paths such as:

            ../../file
        """
        for member in archive.infolist():
            path = Path(member.filename)

            if path.is_absolute():
                raise GitHubDownloadError(
                    "GitHub archive contains an "
                    "invalid absolute path."
                )

            if ".." in path.parts:
                raise GitHubDownloadError(
                    "GitHub archive contains an unsafe path."
                )

    @staticmethod
    def _optional_string(
        value: object,
    ) -> str | None:
        """
        Return a non-empty string or None.
        """
        if not isinstance(value, str):
            return None

        value = value.strip()

        return value or None

    @staticmethod
    def _integer(
        value: object,
        default: int = 0,
    ) -> int:
        """
        Safely normalize an integer API field.
        """
        if isinstance(value, bool):
            return default

        if isinstance(value, int):
            return value

        return default

    @staticmethod
    def _boolean(
        value: object,
        default: bool = False,
    ) -> bool:
        """
        Safely normalize a boolean API field.
        """
        if isinstance(value, bool):
            return value

        return default

    @staticmethod
    def _encode(
        value: str,
    ) -> str:
        """
        URL-encode a GitHub owner or repository name.
        """
        return urllib.parse.quote(
            value,
            safe="",
        )