from __future__ import annotations

from readme_gen.github.models import GitHubRepositoryMetadata
from readme_gen.models import (
    ProjectInfo,
    RepositoryMetadata,
)


def repository_metadata_from_github(
    github: GitHubRepositoryMetadata,
) -> RepositoryMetadata:
    """
    Convert GitHub-specific metadata into provider-neutral repository
    metadata used by the rest of readme-gen.
    """
    license_name: str | None = None
    license_spdx_id: str | None = None

    if github.license is not None:
        license_name = github.license.name
        license_spdx_id = github.license.spdx_id

    return RepositoryMetadata(
        owner=github.owner,
        name=github.name,
        url=github.url,
        description=github.description,
        homepage=github.homepage,
        topics=list(github.topics),
        default_branch=github.default_branch,
        primary_language=github.primary_language,
        language_bytes=dict(github.languages),
        license_name=license_name,
        license_spdx_id=license_spdx_id,
        issues_url=github.issues_url if github.has_issues else None,
        actions_url=github.actions_url,
        stars=github.stars,
        forks=github.forks,
        archived=github.archived,
    )


def apply_repository_metadata(
    project: ProjectInfo,
    metadata: RepositoryMetadata,
) -> None:
    """
    Attach repository metadata to a scanned project and fill appropriate
    project-level fields when the scanner did not already determine them.

    Scanner-derived information remains authoritative where available.
    """
    project.repository = metadata

    if not project.repository_url and metadata.url:
        project.repository_url = metadata.url

    if not project.description and metadata.description:
        project.description = metadata.description

    if not project.license:
        project.license = (
            metadata.license_spdx_id
            or metadata.license_name
        )