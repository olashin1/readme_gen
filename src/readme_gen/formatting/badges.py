from __future__ import annotations

from readme_gen.detectors.badges import detect_badges
from readme_gen.models import BadgeInfo, ProjectInfo


def generate_badges(project: ProjectInfo) -> list[str]:
    """Render the deterministic badge selection as Markdown."""
    return [render_badge(badge) for badge in detect_badges(project)]


def render_badge(badge: BadgeInfo) -> str:
    alt_text = badge.name.replace("[", "\\[").replace("]", "\\]")
    image = f"![{alt_text}]({badge.image_url})"
    if badge.link_target:
        return f"[{image}]({badge.link_target})"
    return image
