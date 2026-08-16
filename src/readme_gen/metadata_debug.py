import json

from readme_gen.ai.prompts import build_metadata_payload
from readme_gen.models import ProjectInfo


def format_metadata_debug(project: ProjectInfo) -> str:
    """Serialize analyzer output without file contents or secret values."""
    return json.dumps(
        build_metadata_payload(project),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
