from pathlib import Path

from readme_gen.detectors.path_filters import is_test_file
from readme_gen.models import ProjectAsset


IMAGE_SUFFIXES = {".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
ASSET_DIRECTORIES = {".github", "assets", "docs", "public", "screenshots"}
MAX_ASSETS = 12


def detect_assets(
    root: Path,
    files: list[Path],
) -> list[ProjectAsset]:
    assets: list[ProjectAsset] = []

    for path in files:
        if is_test_file(root, path):
            continue
        if path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        relative = path.relative_to(root)
        if not set(relative.parts[:-1]).intersection(ASSET_DIRECTORIES):
            continue

        lowered = relative.as_posix().lower()
        kind = "screenshot" if any(
            word in lowered
            for word in ("demo", "preview", "screen", "showcase")
        ) else "image"
        assets.append(
            ProjectAsset(
                path=relative.as_posix(),
                kind=kind,
            )
        )

    return sorted(assets, key=lambda asset: asset.path)[:MAX_ASSETS]
