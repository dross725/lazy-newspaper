# Lazy Newspaper

A simple FastAPI starter with a vanilla HTML/CSS/JS frontend and a Groq-backed article summarizer.

## Features

- FastAPI app entrypoint with a JSON summarize endpoint
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

Then set `GROQ_API_KEY` inside `.env` or export it in your shell.

## Run

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## API

`POST /api/summarize`

```json
{
  "article_text": "Paste article text here...",
  "tone": "clear and concise"
}
```
