from __future__ import annotations

import re
from urllib.parse import urlparse

from readme_gen.github.models import GitHubRepository


_GITHUB_HOSTS = {"github.com", "www.github.com"}

_REPOSITORY_COMPONENT_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


class InvalidGitHubURL(ValueError):
    """
    Raised when a value cannot be interpreted as a supported GitHub repository URL.
    """


def is_github_url(value: str) -> bool:
    """
    Return True if the value appears to be a supported GitHub repository URL.

    This function is intended for input routing. It does not raise an exception
    for malformed input.

    Examples:
        https://github.com/openai/openai-python
        https://github.com/openai/openai-python.git
    """
    try:
        parse_github_url(value)
    except InvalidGitHubURL:
        return False

    return True


def parse_github_url(value: str) -> GitHubRepository:
    """
    Parse a GitHub repository URL into a GitHubRepository.

    Supported forms:

        https://github.com/owner/repository
        https://github.com/owner/repository/
        https://github.com/owner/repository.git

    Query strings and fragments are ignored.

    Args:
        value: GitHub repository URL.

    Returns:
        A parsed GitHubRepository.

    Raises:
        InvalidGitHubURL: If the input is not a supported GitHub repository URL.
    """
    raw_value = value.strip()

    if not raw_value:
        raise InvalidGitHubURL("GitHub URL cannot be empty.")

    parsed = urlparse(raw_value)

    if parsed.scheme not in {"http", "https"}:
        raise InvalidGitHubURL(
            "GitHub repository URL must use http:// or https://."
        )

    hostname = parsed.hostname.lower() if parsed.hostname else ""

    if hostname not in _GITHUB_HOSTS:
        raise InvalidGitHubURL(
            f"Expected a github.com URL, received host "
            f"{hostname or '<missing>'!r}."
        )

    path_parts = [part for part in parsed.path.split("/") if part]

    if len(path_parts) != 2:
        raise InvalidGitHubURL(
            "GitHub repository URL must have the form "
            "'https://github.com/owner/repository'."
        )

    owner, repository_name = path_parts

    if repository_name.endswith(".git"):
        repository_name = repository_name[:-4]

    if not owner:
        raise InvalidGitHubURL("GitHub repository owner cannot be empty.")

    if not repository_name:
        raise InvalidGitHubURL("GitHub repository name cannot be empty.")

    if not _REPOSITORY_COMPONENT_PATTERN.fullmatch(owner):
        raise InvalidGitHubURL(
            f"Invalid GitHub repository owner: {owner!r}."
        )

    if not _REPOSITORY_COMPONENT_PATTERN.fullmatch(repository_name):
        raise InvalidGitHubURL(
            f"Invalid GitHub repository name: {repository_name!r}."
        )

    return GitHubRepository(
        owner=owner,
        name=repository_name,
    )