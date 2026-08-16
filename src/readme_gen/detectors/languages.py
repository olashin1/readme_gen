from pathlib import Path
from collections import Counter


EXTENSION_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".c": "C",
    ".h": "C/C++",
    ".hpp": "C++",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin",
}


def detect_languages(files: list[Path]) -> list[str]:
    languages = Counter()

    for file in files:
        language = EXTENSION_MAP.get(file.suffix.lower())

        if language:
            languages[language] += 1

    return [
        language
        for language, _ in languages.most_common()
    ]