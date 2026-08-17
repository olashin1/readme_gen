from unittest.mock import Mock

import pytest
from google.genai import errors

from readme_gen.ai import analyzer
from readme_gen.models import ProjectInfo


def _project() -> ProjectInfo:
    return ProjectInfo(root=".", name="example")


def test_analyze_project_turns_quota_error_into_actionable_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = Mock()
    client.models.generate_content.side_effect = errors.ClientError(
        429,
        {"error": {"message": "Quota exceeded"}},
    )
    monkeypatch.setattr(analyzer, "get_gemini_client", lambda: client)

    with pytest.raises(RuntimeError, match="quota exceeded") as caught:
        analyzer.analyze_project(_project())

    assert "--no-ai" in str(caught.value)


def test_analyze_project_hides_api_response_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = Mock()
    client.models.generate_content.side_effect = errors.ServerError(
        503,
        {"error": {"message": "sensitive upstream detail"}},
    )
    monkeypatch.setattr(analyzer, "get_gemini_client", lambda: client)

    with pytest.raises(RuntimeError, match="HTTP 503") as caught:
        analyzer.analyze_project(_project())

    assert "sensitive upstream detail" not in str(caught.value)
    assert "--no-ai" in str(caught.value)


def test_analyze_project_removes_emojis_from_every_generated_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = Mock()
    client.models.generate_content.return_value.parsed = {
        "tagline": "🚀 Ship projects faster",
        "summary": "Analyze repositories 🔍 without guesswork.",
        "highlights": ["✅ Detects tools", "Works across stacks 🧑‍💻"],
        "usage_summary": "⚡ Run the CLI.",
        "architecture": "Scanner ➡️ analyzer ➡️ renderer",
    }
    monkeypatch.setattr(analyzer, "get_gemini_client", lambda: client)

    analysis = analyzer.analyze_project(_project())

    assert analysis.tagline == "Ship projects faster"
    assert analysis.summary == "Analyze repositories without guesswork."
    assert analysis.highlights == ["Detects tools", "Works across stacks"]
    assert analysis.usage_summary == "Run the CLI."
    assert analysis.architecture == "Scanner analyzer renderer"
