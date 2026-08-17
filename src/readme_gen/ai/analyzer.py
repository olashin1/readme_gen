import re

from google.genai import errors, types

from readme_gen.ai.client import get_gemini_client
from readme_gen.ai.prompts import build_project_prompt
from readme_gen.models import ProjectAnalysis, ProjectInfo


MODEL_NAME = "gemini-3-flash-preview"

_EMOJI_PATTERN = re.compile(
    "|".join(
        [
            r"[0-9#*]\ufe0f?\u20e3",
            r"[\U0001F1E6-\U0001F1FF]{2}",
            (
                r"[\u231A-\u231B\u23E9-\u23F3\u23F8-\u23FA"
                r"\u25AA-\u25AB\u25B6\u25C0\u25FB-\u25FE"
                r"\u2600-\u27BF\u2934-\u2935\u2B05-\u2B07"
                r"\u2B1B-\u2B1C\u2B50\u2B55\u3030\u303D"
                r"\u3297\u3299\U0001F000-\U0001FAFF]"
                r"[\ufe0e\ufe0f\U0001F3FB-\U0001F3FF]*"
                r"(?:\u200d[\u2600-\u27BF\U0001F000-\U0001FAFF]"
                r"[\ufe0e\ufe0f\U0001F3FB-\U0001F3FF]*)*"
                r"[\U000E0020-\U000E007E]*\U000E007F?"
            ),
        ]
    )
)


def analyze_project(
    project: ProjectInfo,
) -> ProjectAnalysis:
    """
    Analyze a scanned software project with Gemini.

    Gemini is responsible for understanding what the project does and
    producing structured landing-page content. README formatting and layout
    remain deterministic and are handled elsewhere in readme-gen.
    """
    client = get_gemini_client()

    prompt = build_project_prompt(
        project
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ProjectAnalysis,
                automatic_function_calling=(
                    types.AutomaticFunctionCallingConfig(
                        disable=True,
                    )
                ),
            ),
        )
    except errors.APIError as error:
        if error.code == 429:
            raise RuntimeError(
                "Gemini API quota exceeded. Wait for the quota to reset, "
                "check your plan and billing, or run with --no-ai."
            ) from error

        raise RuntimeError(
            f"Gemini API request failed (HTTP {error.code}). "
            "Try again later or run with --no-ai."
        ) from error

    if response.parsed is None:
        raise RuntimeError(
            "Gemini returned no structured project analysis."
        )

    try:
        analysis = ProjectAnalysis.model_validate(
            response.parsed
        )
        return _remove_emojis(analysis)
    except Exception as error:
        raise RuntimeError(
            "Gemini returned an invalid structured project analysis."
        ) from error


def _remove_emojis(analysis: ProjectAnalysis) -> ProjectAnalysis:
    return analysis.model_copy(
        update={
            "tagline": _remove_emojis_from_text(analysis.tagline),
            "summary": _remove_emojis_from_text(analysis.summary),
            "highlights": [
                _remove_emojis_from_text(highlight)
                for highlight in analysis.highlights
            ],
            "usage_summary": _remove_emojis_from_text(analysis.usage_summary),
            "architecture": _remove_emojis_from_text(analysis.architecture),
        }
    )


def _remove_emojis_from_text(value: str) -> str:
    value = _EMOJI_PATTERN.sub(" ", value)
    value = re.sub(r"[^\S\r\n]+", " ", value)
    value = re.sub(r" +([,.;:!?])", r"\1", value)
    return "\n".join(line.strip() for line in value.splitlines()).strip()
