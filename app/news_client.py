import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv

NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"

load_dotenv()


class NewsApiConfigError(RuntimeError):
    """Raised when the News API client is not configured correctly."""


class NewsApiRequestError(RuntimeError):
    """Raised when News API returns an error or cannot be reached."""


def get_news_api_key() -> str:
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        raise NewsApiConfigError(
            "Missing NEWSAPI_KEY. Add it to your environment before using the news endpoint."
        )
    return api_key


def build_article_text(article: dict) -> str:
    parts = [
        article.get("title", "").strip(),
        article.get("description", "").strip(),
        article.get("content", "").strip(),
    ]
    return "\n\n".join(part for part in parts if part)


def fetch_articles(query: str, page_size: int = 5) -> list[dict[str, str | None]]:
    params = urlencode(
        {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
        }
    )
    request = Request(
        f"{NEWS_API_BASE_URL}?{params}",
        headers={"X-Api-Key": get_news_api_key()},
    )

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise NewsApiRequestError(f"News API request failed ({exc.code}): {detail}") from exc
    except URLError as exc:
        raise NewsApiRequestError(f"News API request failed: {exc.reason}") from exc

    if payload.get("status") != "ok":
        raise NewsApiRequestError(payload.get("message", "News API returned an error."))

    articles = []
    for article in payload.get("articles", []):
        title = article.get("title", "").strip()
        article_text = build_article_text(article)
        if not title or not article_text:
            continue

        source = article.get("source") or {}
        articles.append(
            {
                "title": title,
                "source": source.get("name", "Unknown source"),
                "description": article.get("description", "").strip(),
                "url": article.get("url", "").strip(),
                "image_url": article.get("urlToImage"),
                "published_at": article.get("publishedAt"),
                "article_text": article_text,
            }
        )

    return articles
