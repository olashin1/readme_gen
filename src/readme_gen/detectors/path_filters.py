from pathlib import Path


TEST_DIRECTORY_NAMES = {"__tests__", "test", "tests"}


def is_test_file(root: Path, path: Path) -> bool:
    relative = path.relative_to(root)
    return (
        bool(TEST_DIRECTORY_NAMES.intersection(relative.parts[:-1]))
        or relative.name.startswith("test_")
        or relative.name.endswith((".test.js", ".test.jsx", ".test.ts", ".test.tsx"))
    )
