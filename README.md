# Lazy Newspaper

A simple FastAPI starter with a vanilla HTML/CSS/JS frontend, `newsapi.org` article search, and a Groq-backed summarizer.

## Features

- FastAPI app entrypoint with a JSON summarize endpoint
- News search endpoint backed by `newsapi.org`
- Server-rendered landing page with plain HTML
- Static CSS and JavaScript frontend
- Groq client helper for article summarization

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then set `NEWSAPI_KEY` and `GROQ_API_KEY` inside `.env` or export them in your shell.

## Run

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## API

`GET /api/news?q=technology&page_size=5`

Returns recent matching articles from `newsapi.org`, including a prebuilt `article_text` field that can be sent to the summarizer.

`POST /api/summarize`

```json
{
  "article_text": "Paste article text here...",
  "tone": "clear and concise"
}
```
