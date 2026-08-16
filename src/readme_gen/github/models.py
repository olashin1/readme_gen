from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class GitHubRepository:
    """
    Identifies a GitHub repository.

    Attributes:
        owner:
            GitHub user or organization that owns the repository.

        name:
            Repository name without a trailing ".git" suffix.

        ref:
            Optional Git reference such as a branch, tag, or commit SHA.
    """

    owner: str
    name: str
    ref: str | None = None

    @property
    def full_name(self) -> str:
        """
        Return the canonical owner/repository representation.
        """
        return f"{self.owner}/{self.name}"

    @property
    def url(self) -> str:
        """
        Return the canonical HTTPS repository URL.
        """
        return f"https://github.com/{self.full_name}"


@dataclass(frozen=True, slots=True)
class GitHubLicense:
    """
    Normalized GitHub license information.
    """

    key: str | None = None
    name: str | None = None
    spdx_id: str | None = None
    url: str | None = None


@dataclass(frozen=True, slots=True)
class GitHubRepositoryMetadata:
    """
    GitHub-specific repository metadata used by readme-gen.

    This model deliberately contains only information useful to README
    generation rather than exposing the entire GitHub API response.
    """

    owner: str
    name: str
    full_name: str
    url: str

    description: str | None = None
    homepage: str | None = None

    default_branch: str | None = None

    topics: tuple[str, ...] = ()
    primary_language: str | None = None
    languages: dict[str, int] = field(default_factory=dict)

    license: GitHubLicense | None = None

    stars: int = 0
    forks: int = 0
    open_issues: int = 0

    has_issues: bool = True
    archived: bool = False
    fork: bool = False

    @property
    def issues_url(self) -> str:
        """
        Return the repository's GitHub Issues URL.
        """
        return f"{self.url}/issues"

    @property
    def actions_url(self) -> str:
        """
        Return the repository's GitHub Actions URL.
        """
        return f"{self.url}/actions"