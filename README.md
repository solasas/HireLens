# Smart Resume Screener

An AI-powered resume screening system. Upload candidate resumes (PDF) and a job
description, and it extracts structured data from both with an LLM, scores each
candidate against the job with a deterministic matching engine, generates an
explainable evaluation, and ranks candidates for the role.

## Features

- **PDF resume parsing** — text extraction with layout-aware reading order,
  detection of empty/scanned PDFs, whitespace normalization.
- **Structured extraction** — an LLM turns raw resume and job-description text
  into structured JSON (skills, experience, education, projects,
  certifications / required & preferred skills, responsibilities, domains),
  with schema validation and one automatic retry on a malformed response.
- **Deterministic matching engine** — five weighted components computed with
  plain code, not the LLM: skill match (with alias normalization — `JS` →
  `JavaScript`, `Postgres` → `PostgreSQL`, etc. — and fuzzy-typo tolerance),
  experience match, education match, semantic similarity (via embeddings),
  and project/domain relevance.
- **Explainable evaluation** — an LLM generates the qualitative narrative
  (strengths, concerns, relevant experience, a recommendation) grounded in
  the already-computed deterministic scores. The LLM never invents the
  numeric score or the fit level; those are computed, not generated.
- **Candidate ranking** — every evaluated candidate for a job, ranked by
  score with deterministic tie-breaking, paginated.
- **Dashboard** — candidate count, average score, strong-match count, recent
  evaluations, across all jobs.
- **Provider-agnostic** — LLM and embedding calls go through a small
  interface (`LLMProvider`, `EmbeddingProvider`); a concrete provider is
  swapped in via config, not hardcoded into business logic. Gemini is
  implemented; OpenAI is stubbed for a future implementation.
- **PostgreSQL persistence** — candidates, resumes, job descriptions, and
  evaluations, with Alembic migrations.
- **React frontend** — dashboard, job description management, resume
  upload with progress, evaluation results, candidate ranking, and
  candidate detail pages.

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Python, FastAPI, async SQLAlchemy 2.0, Pydantic v2 |
| Database | PostgreSQL 16, Alembic migrations |
| PDF parsing | PyMuPDF |
| LLM / embeddings | Google Gemini (`google-genai`), behind a provider interface |
| Frontend | React 18, Vite, Axios, React Router |
| Containerization | Docker, Docker Compose |
| Testing | pytest, pytest-asyncio (unit tests use fakes; DB-dependent tests run against real Postgres) |

## Project structure

```
.
├── docker-compose.yml
├── .env.example                # backend + shared config template
├── backend/
│   ├── app/
│   │   ├── api/v1/routers/     # HTTP boundary only — no business logic
│   │   ├── core/               # config, logging, exception hierarchy
│   │   ├── db/                 # SQLAlchemy engine/session, declarative base
│   │   ├── domain/scoring/     # pure, deterministic matching engine — no I/O
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── repositories/       # persistence — the only layer that queries the DB
│   │   ├── schemas/            # Pydantic request/response & extraction schemas
│   │   └── services/           # orchestration: PDF parsing, LLM/embedding
│   │       ├── llm/            #   provider abstraction + Gemini implementation
│   │       └── embeddings/     #   provider abstraction + Gemini implementation
│   ├── alembic/versions/       # migrations
│   └── tests/                  # pytest — unit tests (fakes) + DB integration tests
└── frontend/
    └── src/
        ├── api/                # axios client + per-resource request functions
        ├── components/         # reusable UI (common/, upload/, evaluation/, layout/)
        ├── hooks/               # useAsync — shared loading/error/data state
        └── pages/               # one file per route, composed from components/
```

## Quick start (Docker Compose)

Requires Docker and a Gemini API key ([aistudio.google.com](https://aistudio.google.com/apikey) — free tier available).

```bash
cp .env.example .env
```

Edit `.env`:
- Set `GEMINI_API_KEY` to your key.
- Set `LLM_PROVIDER=gemini` and `EMBEDDING_PROVIDER=gemini` (both default to
  `openai` in the template, which isn't implemented yet — see Limitations).
- Change `POSTGRES_PASSWORD` from the placeholder if you like.

```bash
docker compose up -d db
docker compose run --rm backend alembic upgrade head
docker compose up -d backend frontend
```

- Frontend: <http://localhost:5173>
- Backend API: <http://localhost:8000/api/v1> (health check at `/health`)
- Postgres is published on host port **5433**, not 5432, to avoid colliding
  with a Postgres already running on your machine. The backend always talks
  to `db:5432` internally regardless of this.

## Running without Docker

Backend (requires Python 3.11+; the async SQLAlchemy models use `X | None`
syntax that needs it):

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend (requires Node 18+):

```bash
cd frontend
cp .env.example .env   # points at http://localhost:8000/api/v1 by default
npm install
npm run dev
```

## Environment variables

All backend configuration is read from environment variables (`app/core/config.py`) —
see `.env.example` for the full list with defaults. Key ones:

| Variable | Purpose |
|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Database credentials |
| `LLM_PROVIDER`, `GEMINI_API_KEY`, `GEMINI_MODEL` | LLM provider selection and config |
| `EMBEDDING_PROVIDER`, `GEMINI_EMBEDDING_MODEL` | Embedding provider selection and config |
| `CORS_ORIGINS` | Comma-separated origins allowed to call the API (the frontend's dev URL) |

The frontend reads `VITE_API_BASE_URL` from its own `.env` (see `frontend/.env.example`).

No secrets are hardcoded anywhere in the codebase; `.env` is gitignored.

## API overview

All routes are under `/api/v1`. Full interactive docs (Swagger UI) are served
by FastAPI at `/docs` when the backend is running.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/resumes/parse` | Parse a resume PDF, return extracted text (no persistence) |
| `POST` | `/resumes/extract` | Parse + LLM-extract a resume (no persistence) |
| `POST` | `/jobs/extract` | LLM-extract a job description (no persistence) |
| `POST` | `/jobs` | Extract and persist a job description |
| `GET` | `/jobs` | List jobs with candidate counts |
| `GET` | `/jobs/{job_id}` | Job detail, including structured extraction |
| `POST` | `/jobs/{job_id}/candidates` | Evaluate uploaded resumes against a job, persist results |
| `GET` | `/jobs/{job_id}/candidates` | Ranked, paginated candidate list for a job |
| `GET` | `/evaluations/{evaluation_id}` | Full evaluation detail (scores, skills, narrative) |
| `GET` | `/dashboard` | Aggregate stats across all jobs |
| `GET` | `/health` | Liveness/readiness, including DB connectivity |

## Database schema

Four entities: `candidates` (1–N `resumes`, 1–N `evaluations`), `job_descriptions`
(1–N `evaluations`). Raw text and its structured LLM extraction are stored
together per row as JSONB, rather than split into separate tables — nothing
in this app queries a single field out of an extraction, it's always read
back whole. The five match sub-scores and the final score on `evaluations`
are individual typed columns (not JSONB), because the ranking endpoint sorts
on them directly. See migrations in `backend/alembic/versions/` for the
exact history and reasoning behind each schema change.

## Testing

```bash
cd backend
docker compose up -d db          # tests that need Postgres require it running
pip install -r requirements-dev.txt
pytest -v
```

Most tests are pure unit tests using fakes for the LLM/embedding providers
(no network calls, no API cost). A smaller set are integration tests against
a real Postgres database (ranking order, tie-breaking, JSONB behavior) — these
require `db` to be running and will fail with a connection error otherwise.

## Known limitations

- **Only Gemini is implemented** for both LLM and embeddings; selecting
  `openai` in config fails at first request, not at startup.
- **Batch resume evaluation isn't resilient to transient provider errors** —
  a single failed candidate (rate limit, network blip) fails the whole
  batch, and nothing is persisted until the end, so already-made LLM/
  embedding calls for that batch are wasted on retry.
- **No authentication** on any endpoint.
- **No durable file storage** for uploaded PDFs — only the extracted text
  and structured data are kept; the original file isn't stored.
- **`Evaluation` links to `Candidate`, not a specific `Resume`** — if a
  candidate has multiple resumes on file, there's no record of which one
  produced a given evaluation.
- **No embedding caching** — a candidate's embedding is recomputed on every
  evaluation, even against a job they were already scored against before.
- **Gemini's free tier is rate-limited** (20 requests/day at the time of
  writing) — expect `429`/quota errors under heavy local testing.
