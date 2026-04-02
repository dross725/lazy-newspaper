import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.groq_client import GroqConfigError, summarize_article
from app.news_client import NewsApiConfigError, NewsApiRequestError, fetch_articles


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

app = FastAPI(title="Lazy Newspaper")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class SummarizeRequest(BaseModel):
    article_text: str = Field(..., min_length=50, description="Raw article text to summarize.")
    tone: str = Field(default="clear and concise", min_length=3, max_length=80)


class SummarizeResponse(BaseModel):
    headline: str
    summary: str
    angle: str
    model: str


class NewsArticle(BaseModel):
    title: str
    source: str
    description: str
    url: str
    image_url: str | None = None
    published_at: str | None = None
    article_text: str


class NewsSearchResponse(BaseModel):
    query: str
    total_results: int
    articles: list[NewsArticle]


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"default_model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")},
    )


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/news", response_model=NewsSearchResponse)
async def get_news(
    q: str = Query(..., min_length=2, max_length=100, description="Search query for articles."),
    page_size: int = Query(5, ge=1, le=10, description="Maximum number of articles to return."),
) -> NewsSearchResponse:
    try:
        articles = fetch_articles(query=q, page_size=page_size)
    except NewsApiConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except NewsApiRequestError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return NewsSearchResponse(
        query=q,
        total_results=len(articles),
        articles=[NewsArticle.model_validate(article) for article in articles],
    )


@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize(payload: SummarizeRequest) -> SummarizeResponse:
    try:
        result = summarize_article(payload.article_text, payload.tone)
    except GroqConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Groq request failed: {exc}") from exc

    return SummarizeResponse(
        headline=result.get("headline", "").strip(),
        summary=result.get("summary", "").strip(),
        angle=result.get("angle", "").strip(),
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    )
