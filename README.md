# Agent Atlas

A full-stack discovery tool for open-source AI agent projects. React + TypeScript frontend, FastAPI API, SQLAlchemy persistence. SQLite by default; PostgreSQL via `DATABASE_URL`.

## Run locally

Python 3.12+ and Node.js 22+ are recommended. Run these commands from this directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

In another terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open http://localhost:5173. API documentation: http://127.0.0.1:8000/docs.

The API creates its schema and imports the bundled README snapshot at startup. Repeated imports update records identified by their source URL without duplicating them. Removed upstream records are retained; synchronization does not delete them. To refresh the catalog, replace `data/upstream-README.md` with a reviewed upstream snapshot and restart the API.

## PostgreSQL (optional)

```sh
docker compose up -d
export DATABASE_URL='postgresql+psycopg://atlas:atlas@localhost:5432/atlas'
python -m uvicorn backend.main:app --reload
```

Compose credentials are for local development. The application does not automatically read `.env`; export the variable in your shell.

## Validate

```sh
python -m pytest -q
cd frontend
npm ci
npm run build
```

CI runs backend tests and the frontend production build. Tests cover duplicate imports, combined filters, literal wildcard handling, page validation and non-overlapping pagination. Frontend loading, empty, and connection-error states are implemented; browser verification is recorded separately in `VALIDATION.md`.

## Architecture

Browser → Vite dev proxy `/api` → FastAPI → SQLAlchemy → SQLite/PostgreSQL.

`GET /api/projects` accepts `q`, `industry`, `framework`, `page`, `page_size`, `sort` (`name` or `newest`, meaning reverse insertion order). Filtering and pagination happen in the database. Text search is a portable case-insensitive substring query, not a full-text search engine. `GET /api/facets` supplies available filters.

## Current scope

Implemented: catalog import, search, filters, sorting, pagination, responsive UI, API validation and CI configuration.

Planned: authenticated accounts, per-user bookmarks, database migrations, deployment and performance benchmarks. This version has no login, AI recommendation, or production hosting. Do not describe planned features as completed on a resume.

## Attribution

Catalog data: [ashishpatel26/500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects). The bundled source snapshot is retained for reproducibility, along with its MIT license in `data/UPSTREAM-LICENSE`. Linked projects retain their own licenses. Agent Atlas application code is a separate implementation; the catalog and linked agents are not original work by its developer.

## Publish to your GitHub

Create an empty repository called `agent-atlas` in your account, then from this directory:

```sh
git init -b main
git add .
git commit -m "Build Agent Atlas search application"
git remote add origin https://github.com/YOUR_USERNAME/agent-atlas.git
git push -u origin main
```

Never commit `.env`, database files, or API keys. `.gitignore` excludes local state. No GitHub remote has been configured by this scaffold.
