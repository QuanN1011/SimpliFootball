import os

from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import create_engine, text

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="SimpliFootball API")
engine = create_engine(os.environ["DATABASE_URL"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/shots/summary")
def shots_summary():
    with engine.connect() as conn:
        total_shots = conn.execute(text("SELECT COUNT(*) FROM shots")).scalar()
        players = conn.execute(text("SELECT COUNT(*) FROM players")).scalar()
        matches = conn.execute(
            text("SELECT COUNT(DISTINCT match_id) FROM shots")
        ).scalar()
    return {
        "total_shots": total_shots,
        "players": players,
        "matches_with_shots": matches,
    }
@app.get("/shots/top-players")
def top_players(limit: int = 10):
    sql = text(
        """
        SELECT p.player_name, COUNT(*) AS shots, ROUND(SUM(s.xg)::numeric, 3) AS total_xg
        FROM shots s
        JOIN players p ON p.player_id = s.player_id
        GROUP BY p.player_name
        ORDER BY shots DESC
        LIMIT :limit
        """
    )
    with engine.connect() as conn:
        rows = conn.execute(sql, {"limit": limit}).mappings().all()
    return [dict(r) for r in rows]
