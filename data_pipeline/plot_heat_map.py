import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mplsoccer import Pitch

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])

PLAYER = "Lionel Andrés Messi Cuccittini"  # exact DB name

sql = text(
    """
    SELECT s.x, s.y, s.xg, s.shot_outcome
    FROM shots s
    JOIN players p ON p.player_id = s.player_id
    WHERE p.player_name = :player
      AND s.x IS NOT NULL AND s.y IS NOT NULL
    """
)

with engine.connect() as conn:
    rows = conn.execute(sql, {"player": PLAYER}).mappings().all()

x = [r["x"] for r in rows]
y = [r["y"] for r in rows]
xg = [r["xg"] if r["xg"] is not None else 0.01 for r in rows]
outcomes = [r["shot_outcome"] for r in rows]

colors = {
    "Goal": "green",
    "Saved": "blue",
    "Off T": "red",
    "Wayward": "gray",
    "Blocked": "orange",
    "Post": "purple",
    "Saved Off Target": "cyan",
    "Saved to Post": "magenta",
}
c = [colors.get(o, "black") for o in outcomes]

avg_xg = sum(xg) / len(xg) if xg else 0.0

pitch = Pitch(
    pitch_type="statsbomb",
    pitch_color="grass",
    line_color="white",
    line_zorder=2,
)
fig, ax = pitch.draw(figsize=(10, 7))

# density of shot locations (x, y lists from SQL — same as #1)
pitch.kdeplot(
    x,
    y,
    ax=ax,
    fill=True,
    levels=100,
    thresh=0.1,
    cut=4,
    cmap="hot",
    zorder=1,       # under pitch lines if line_zorder is higher
)

ax.set_title(f"Shot heat map: {PLAYER} ({len(rows)} shots)")
fig.savefig("output/shot_maps/messi_heat.png", dpi=150, bbox_inches="tight")
print("Saved output/shot_maps/messi_heat.png")