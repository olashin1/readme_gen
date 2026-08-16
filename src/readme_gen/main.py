from __future__ import annotations

from pathlib import Path

import typer

from readme_gen.ai.analyzer import analyze_project
from readme_gen.generator import generate_readme
from readme_gen.github.client import GitHubError
from readme_gen.repository import (
    RepositorySourceError,
    resolve_repository_source,
)
from readme_gen.repository.metadata import (
    apply_repository_metadata,
    repository_metadata_from_github,
)
from readme_gen.scanner import scan_project


app = typer.Typer()


@app.command()
def main(
    source: str = typer.Argument(
        ".",
        help=(
            "Local project path or GitHub repository URL "
            "to analyze."
        ),
    ),
    output: Path = typer.Option(
        Path("README.md"),
        "--output",
        "-o",
        help="Output file for the generated README.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite the output file if it already exists.",
    ),
    no_ai: bool = typer.Option(
        False,
        "--no-ai",
        help="Generate the README without Gemini analysis.",
    ),
) -> None:
    """
    Analyze a software repository and generate a polished README.
    """
    try:
        repository_source = resolve_repository_source(source)
    except RepositorySourceError as error:
        typer.echo(
            f"Invalid repository source: {error}",
            err=True,
        )
        raise typer.Exit(code=1) from error

    try:
        with repository_source.open() as repository:
            if repository.is_github:
                typer.echo(
                    f"Fetching GitHub repository: "
                    f"{repository.source}"
                )
            else:
                typer.echo(
                    f"Analyzing local repository: "
                    f"{repository.path}"
                )

            output_path = _resolve_output_path(
                output=output,
                repository_path=repository.path,
                is_github=repository.is_github,
            )

            _check_output_path(
                output_path=output_path,
                force=force,
            )

            typer.echo("Scanning project...")

            project = scan_project(
                repository.path
            )

            if repository.github is not None:
                repository_metadata = (
                    repository_metadata_from_github(
                        repository.github
                    )
                )

                apply_repository_metadata(
                    project,
                    repository_metadata,
                )

            if not no_ai:
                typer.echo(
                    "Analyzing project with Gemini..."
                )

                try:
                    project.analysis = analyze_project(
                        project
                    )
                except RuntimeError as error:
                    typer.echo(
                        f"AI analysis failed: {error}",
                        err=True,
                    )
                    raise typer.Exit(
                        code=1
                    ) from error

            typer.echo("Generating README...")

            readme = generate_readme(project)

            try:
                output_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                output_path.write_text(
                    readme,
                    encoding="utf-8",
                )

            except OSError as error:
                typer.echo(
                    f"Failed to write README: {error}",
                    err=True,
                )
                raise typer.Exit(
                    code=1
                ) from error

    except RepositorySourceError as error:
        typer.echo(
            f"Repository error: {error}",
            err=True,
        )
        raise typer.Exit(code=1) from error

    except GitHubError as error:
        typer.echo(
            f"GitHub error: {error}",
            err=True,
        )
        raise typer.Exit(code=1) from error

    typer.echo(
        f"Generated README: {output_path}"
    )


def _resolve_output_path(
    output: Path,
    repository_path: Path,
    is_github: bool,
) -> Path:
    """
    Resolve where the generated README should be written.

    Absolute output paths are always respected.

    For local repositories, relative output paths are resolved relative to
    the repository itself.

    For GitHub repositories, the scanned repository exists only inside a
    temporary directory. Relative output paths are therefore resolved
    relative to the user's current working directory so the generated README
    survives after the temporary repository is cleaned up.
    """
    if output.is_absolute():
        return output.resolve()

    if is_github:
        return (
            Path.cwd()
            / output
        ).resolve()

    return (
        repository_path
        / output
    ).resolve()


def _check_output_path(
    output_path: Path,
    force: bool,
) -> None:
    """
    Prevent accidental overwrites unless the user explicitly opts in.
    """
    if not output_path.exists():
        return

    if force:
        return

    typer.echo(
        (
            f"Output file already exists: {output_path}\n"
            "Use --force to overwrite it."
        ),
        err=True,
    )

    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()