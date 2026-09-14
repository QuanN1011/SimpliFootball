# SimpliFootball — progress so far

## Goal
Full-stack soccer analytics app (FastAPI + PostgreSQL + React) using real match/event data.

## What we've done

### 1. Data exploration (`data_pipeline/explore_statsbomb.py`)
Used **statsbombpy** to learn StatsBomb open data:

- `sb.competitions()` → leagues/seasons
- `sb.matches(competition_id, season_id)` → games
- `sb.events(match_id)` → on-ball actions

**Season we picked:** La Liga `competition_id=11`, `season_id=4`  
**Example match:** `16196`  
**Player example:** Lionel Andrés Messi Cuccittini (exact StatsBomb name)

**Things we learned:**
- `NoAuthWarning` is normal for open data
- Event type column is `type` (e.g. `"Shot"`), not `type_name`
- Shot result is `shot_outcome`, not `shot_outcome_name`
- Position is `location` as `[x, y]`, not separate x/y columns
- Many columns are sparse (shot fields only filled on shot events)

Notes also live in `docs/data-sources.md`.

### 2. Feature branch
Left `main` for real feature work:

- Branch: `feature/statsbomb-ingest`
- Why: keep exploration on main; build pipeline without blocking main

### 3. Database schema (`data_pipeline/schema.sql`)
Designed minimal tables for v1 (shots-focused):

| Table | Purpose |
|-------|---------|
| `competitions` | league + season |
| `matches` | games in that season |
| `players` | player id + name |
| `shots` | shot events with x, y, outcome, xG |

### 4. Docker Postgres
Used **Docker Compose** instead of installing Postgres on macOS:

- `docker-compose.yml` defines a `postgres:16` service
- Container name: `simplifootball-db`
- DB/user/password: `simplifootball` / `postgres` / `postgres`
- Port: `5432` on localhost
- Volume keeps data after stop/restart

**Useful commands:**
- `docker compose up -d` — start DB
- `docker compose stop` — stop container
- `docker exec -i simplifootball-db psql ... < schema.sql` — apply schema
- `\dt` — list tables

### 5. Python ↔ Postgres wiring
- `.env` holds `DATABASE_URL` (gitignored)
- `requirements.txt`: statsbombpy, pandas, sqlalchemy, psycopg, python-dotenv
- `test_db.py`: smoke test (`SELECT 1`)

URL shape comes from Compose credentials + SQLAlchemy docs:
`postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME`

### 6. Ingest (`data_pipeline/ingest_shots.py`)
**Ingest** = fetch external data → clean/shape → insert into our DB.

Script flow:
1. Upsert competition row
2. Upsert all matches for the season
3. For each match: fetch events → keep shots → upsert players + shots
4. Split `location` → `x`, `y`
5. `ON CONFLICT DO NOTHING` so re-runs are safe

Casts (`int`, `float`, `str`) make pandas values match SQL column types; missing/NaN → `NULL`.

## Tooling notes
- VS Code/Cursor **Jupyter kernel** was slow/unreliable → prefer terminal: `.venv/bin/python ...`
- `source .venv/bin/activate` only affects the terminal, not the Jupyter kernel
- Bare `python` may not exist on Mac until venv is activated

## Git status (conceptually)
- Exploration committed on `main`
- Ingest work committed on `feature/statsbomb-ingest` (push when ready)
- Commit = local snapshot; push = upload to GitHub

## What's next
1. Verify season ingest counts in Postgres
2. Push feature branch / open PR into `main` when ready
3. FastAPI: read from Postgres (e.g. shots by player)
4. React UI later