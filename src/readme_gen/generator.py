from readme_gen.formatting import render_readme
from readme_gen.models import ProjectInfo


def generate_readme(
    project: ProjectInfo,
) -> str:
    """
    Generate a polished GitHub-oriented README for a scanned project.
    """
    return render_readme(project)