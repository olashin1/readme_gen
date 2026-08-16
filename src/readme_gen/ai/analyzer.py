from google.genai import types

from readme_gen.ai.client import get_gemini_client
from readme_gen.ai.prompts import build_project_prompt
from readme_gen.models import ProjectAnalysis, ProjectInfo


MODEL_NAME = "gemini-3-flash-preview"


def analyze_project(project: ProjectInfo) -> ProjectAnalysis:
    client = get_gemini_client()

    prompt = build_project_prompt(project)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ProjectAnalysis,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True,
            ),
        ),
    )

    if response.parsed is None:
        raise RuntimeError(
            "Gemini returned no structured project analysis."
        )

    return response.parsed # type: ignore