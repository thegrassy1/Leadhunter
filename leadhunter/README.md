# LeadHunter

Local-first lead generation and pipeline for small-business acquisition targets in southern/central Wisconsin and northern Illinois.

## Structure

- `backend/` — FastAPI, SQLAlchemy (async SQLite), scrapers, scoring, Gmail + Anthropic integrations
- `frontend/` — React 18, Vite, Tailwind CSS v4, TanStack Query, Recharts
- `data/` — SQLite file `leadhunter.db` (created on first API start)

## Quick start (development)

**Backend** (from `leadhunter/backend`):

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

**Frontend** (from `leadhunter/frontend`):

```bash
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

## Configuration

Copy `.env.example` to `.env` in `leadhunter/` (or set env vars). For email drafting, set `ANTHROPIC_API_KEY`. For Gmail send/receive, add OAuth `credentials.json` under `backend/credentials/` (see Google Cloud Gmail API setup).

## Docker

From `leadhunter/`:

```bash
docker compose up --build
```

- API: port 8000  
- Web (nginx + static build): port 5173 — nginx proxies `/api` to the API service

## Scraping

Scrapers respect `robots.txt`, use httpx with jittered delays, and dedupe on `source_url`. Listing HTML selectors may need tuning as sites change; raw snippets are stored for debugging.

## License

Use responsibly and in compliance with each site’s terms and applicable law.
