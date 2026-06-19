import os
from typing import Dict
from urllib.parse import urlparse

from google import genai
from google.genai import types


PROMPT_STYLES: Dict[str, Dict[str, str]] = {
    "question_answering": {
        "short_answer": "Short Answer Mode",
        "teacher_explanation": "Teacher Explanation Mode",
        "detailed_expert": "Detailed Expert Mode",
    },
    "summarization": {
        "short_summary": "Short Summary Mode",
        "bullet_point_summary": "Bullet Point Summary Mode",
        "executive_summary": "Executive Summary Mode",
    },
    "creative_writing": {
        "story": "Story Mode",
        "poem": "Poem Mode",
        "creative_idea": "Creative Idea Mode",
    },
}


PROMPT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "question_answering": {
        "short_answer": (
            "Answer the factual question in 2-4 clear sentences. "
            "Use simple language and avoid unnecessary detail.\n\nQuestion:\n{user_input}"
        ),
        "teacher_explanation": (
            "Act as a patient teacher. Explain the answer step by step with one helpful example. "
            "Keep the tone friendly and easy to understand.\n\nQuestion:\n{user_input}"
        ),
        "detailed_expert": (
            "Act as a subject-matter expert. Provide a detailed, accurate answer with context, "
            "key points, and any important limitations or caveats.\n\nQuestion:\n{user_input}"
        ),
    },
    "summarization": {
        "short_summary": (
            "Summarize the following text in one concise paragraph. Keep only the most important ideas.\n\n"
            "Text:\n{user_input}"
        ),
        "bullet_point_summary": (
            "Summarize the following text as 5-7 clear bullet points. Preserve the main ideas and outcomes.\n\n"
            "Text:\n{user_input}"
        ),
        "executive_summary": (
            "Create an executive summary of the following text for a busy decision-maker. Include the purpose, "
            "major insights, risks, and recommended next steps when applicable.\n\nText:\n{user_input}"
        ),
    },
    "creative_writing": {
        "story": (
            "Write an original short story based on the user's prompt. Include a clear setting, engaging conflict, "
            "and satisfying ending.\n\nPrompt:\n{user_input}"
        ),
        "poem": (
            "Write an original poem based on the user's prompt. Use vivid imagery, rhythm, and emotional impact.\n\n"
            "Prompt:\n{user_input}"
        ),
        "creative_idea": (
            "Generate creative ideas based on the user's prompt. Provide 6 distinct ideas with short explanations "
            "and make them practical enough to develop further.\n\nPrompt:\n{user_input}"
        ),
    },
}


class GeminiServiceError(Exception):
    """Raised when Gemini cannot generate a usable response."""


def remove_broken_local_proxy() -> None:
    proxy_keys = (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    )

    for key in proxy_keys:
        proxy_url = os.getenv(key)
        if not proxy_url:
            continue

        parsed_url = urlparse(proxy_url)
        if parsed_url.hostname in {"127.0.0.1", "localhost"} and parsed_url.port == 9:
            os.environ.pop(key, None)


class GeminiService:
    def __init__(self, api_key: str | None, model_name: str | None = None) -> None:
        remove_broken_local_proxy()
        self.api_key = api_key
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = genai.Client(api_key=api_key) if api_key else None

    def generate_response(self, assistant_function: str, prompt_style: str, user_input: str) -> str:
        if not self.client:
            raise GeminiServiceError("GEMINI_API_KEY is missing. Add it to .env or geminiapi.env.")

        try:
            template = PROMPT_TEMPLATES[assistant_function][prompt_style]
        except KeyError as error:
            raise GeminiServiceError("Unsupported function or prompt style.") from error

        prompt = template.format(user_input=user_input)

        try:
            remove_broken_local_proxy()
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self._temperature_for(assistant_function),
                    max_output_tokens=1200,
                ),
            )
        except Exception as error:
            raise GeminiServiceError(f"Gemini API request failed: {error}") from error

        text = (response.text or "").strip()
        if not text:
            raise GeminiServiceError("Gemini returned an empty response. Please try again.")

        return text

    @staticmethod
    def _temperature_for(assistant_function: str) -> float:
        if assistant_function == "creative_writing":
            return 0.9
        if assistant_function == "summarization":
            return 0.3
        return 0.2
