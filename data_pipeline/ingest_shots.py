# data_pipeline/ingest_shots.py
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from statsbombpy import sb

load_dotenv()

COMPETITION_ID = 11
SEASON_ID = 4

engine = create_engine(os.environ["DATABASE_URL"])


def upsert_competition(conn):
    # Pull name info from StatsBomb competitions table
    comps = sb.competitions()
    row = comps[
        (comps["competition_id"] == COMPETITION_ID)
        & (comps["season_id"] == SEASON_ID)
    ].iloc[0]

    conn.execute(
        text(
            """
            INSERT INTO competitions (competition_id, season_id, competition_name, season_name)
            VALUES (:competition_id, :season_id, :competition_name, :season_name)
            ON CONFLICT (competition_id, season_id) DO NOTHING
            """
        ),
        {
            "competition_id": int(row["competition_id"]),
            "season_id": int(row["season_id"]),
            "competition_name": row["competition_name"],
            "season_name": row["season_name"],
        },
    )


def upsert_matches(conn):
    matches = sb.matches(competition_id=COMPETITION_ID, season_id=SEASON_ID)

    for _, m in matches.iterrows():
        conn.execute(
            text(
                """
                INSERT INTO matches (
                    match_id, competition_id, season_id,
                    match_date, home_team, away_team
                )
                VALUES (
                    :match_id, :competition_id, :season_id,
                    :match_date, :home_team, :away_team
                )
                ON CONFLICT (match_id) DO NOTHING
                """
            ),
            {
                "match_id": int(m["match_id"]),
                "competition_id": COMPETITION_ID,
                "season_id": SEASON_ID,
                "match_date": m["match_date"],
                "home_team": m["home_team"],
                "away_team": m["away_team"],
            },
        )

def upsert_shots_for_match(conn, match_id: int):
    events = sb.events(match_id=match_id)
    shots = events[events["type"] == "Shot"].copy()

    for _, s in shots.iterrows():
        player_id = s.get("player_id")
        player_name = s.get("player")
        if player_id is not None and player_name is not None:
            conn.execute(
                text(
                    """
                    INSERT INTO players (player_id, player_name)
                    VALUES (:player_id, :player_name)
                    ON CONFLICT (player_id) DO NOTHING
                    """
                ),
                {"player_id": int(player_id), "player_name": player_name},
            )

        loc = s.get("location")
        x = loc[0] if isinstance(loc, (list, tuple)) and len(loc) >= 2 else None
        y = loc[1] if isinstance(loc, (list, tuple)) and len(loc) >= 2 else None

        conn.execute(
            text(
                """
                INSERT INTO shots (
                    shot_id, match_id, player_id, minute, second,
                    x, y, shot_outcome, xg
                )
                VALUES (
                    :shot_id, :match_id, :player_id, :minute, :second,
                    :x, :y, :shot_outcome, :xg
                )
                ON CONFLICT (shot_id) DO NOTHING
                """
            ),
            {
                "shot_id": str(s["id"]),
                "match_id": match_id,
                "player_id": int(player_id) if player_id is not None else None,
                "minute": int(s["minute"]) if s.get("minute") is not None else None,
                "second": int(s["second"]) if s.get("second") is not None else None,
                "x": x,
                "y": y,
                "shot_outcome": s.get("shot_outcome"),
                "xg": float(s["shot_statsbomb_xg"])
                if s.get("shot_statsbomb_xg") == s.get("shot_statsbomb_xg")
                and s.get("shot_statsbomb_xg") is not None
                else None,
            },
        )


if __name__ == "__main__":
    with engine.begin() as conn:
        upsert_competition(conn)
        upsert_matches(conn)

        matches = sb.matches(competition_id=COMPETITION_ID, season_id=SEASON_ID)
        for match_id in matches["match_id"].tolist():
            print(f"Ingesting shots for match {match_id}...")
            upsert_shots_for_match(conn, match_id=int(match_id))

    print("Loaded competition + matches + all shots for the season")