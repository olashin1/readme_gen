import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. "
            "Add it to your .env file or environment variables."
        )

    return genai.Client(api_key=api_key)