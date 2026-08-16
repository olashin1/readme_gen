from pathlib import Path

import typer

from readme_gen.generator import generate_readme
from readme_gen.scanner import scan_project


app = typer.Typer()


@app.command()
def main(
    path: Path = typer.Argument(Path(".")),
    output: Path = typer.Option(
        Path("README.generated.md"),
        "--output",
        "-o",
        help="Output file for the generated README.",
    ),
):
    project_path = path.resolve()

    if not project_path.exists():
        typer.echo(
            f"Path does not exist: {project_path}",
            err=True,
        )
        raise typer.Exit(code=1)

    if not project_path.is_dir():
        typer.echo(
            f"Path is not a directory: {project_path}",
            err=True,
        )
        raise typer.Exit(code=1)

    project = scan_project(project_path)
    readme = generate_readme(project)

    output_path = (
        output
        if output.is_absolute()
        else project_path / output
    )

    output_path.write_text(
        readme,
        encoding="utf-8",
    )

    typer.echo(
        f"Generated README: {output_path}"
    )


if __name__ == "__main__":
    app()