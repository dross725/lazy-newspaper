import json
import os

from dotenv import load_dotenv
from groq import Groq

DEFAULT_MODEL = "llama-3.1-8b-instant"


load_dotenv()


class GroqConfigError(RuntimeError):
    """Raised when the Groq client is not configured correctly."""


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise GroqConfigError(
            "Missing GROQ_API_KEY. Add it to your environment before using the summarize endpoint."
        )
    return Groq(api_key=api_key)


def summarize_article(article_text: str, tone: str = "clear and concise") -> dict[str, str]:
    client = get_groq_client()
    model = os.getenv("GROQ_MODEL", DEFAULT_MODEL)

    system_prompt = (
        "You are a newsroom assistant. Return a compact JSON object with keys "
        '"headline", "summary", and "angle". '
        "The headline should be catchy but factual. The summary should be 2-4 sentences. "
        "The angle should be a short note about the most interesting framing for the story."
    )

    user_prompt = (
        f"Tone: {tone}\n"
        "Summarize the following article text.\n"
        "Return JSON only with the required keys.\n\n"
        f"{article_text}"
    )

    completion = client.chat.completions.create(
        model=model,
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    payload = completion.choices[0].message.content or "{}"
    return json.loads(payload)
