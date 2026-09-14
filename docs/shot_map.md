# Shot map (roadmap item #1)

## Goal
Plot a player's shots on a football pitch diagram so we can see **where** they shoot,
**how good** the chances were (xG), and **what happened** (outcome).

## Concept
A shot map is a scatter plot on a pitch drawing:
- each point = one shot
- `(x, y)` = shot location (StatsBomb coordinates)
- marker **size** encodes **xG** (bigger ≈ higher quality chance)
- marker **color** encodes **shot_outcome** (Goal, Saved, Off T, ...)

### StatsBomb coordinates
- Pitch is about **120 x 80**
- `x`: 0 (own goal) → 120 (opponent goal)
- `y`: 0 → 80 (touchline to touchline)
- Attacking direction in events is generally toward **x = 120**

`mplsoccer.Pitch(pitch_type="statsbomb")` draws lines in that same system so DB
coordinates land in the right place.

## What we reused vs what was new
**Reused**
- Postgres tables `shots` / `players` from ingest
- `DATABASE_URL` + SQLAlchemy connection pattern
- Columns created earlier: `x`, `y`, `xg`, `shot_outcome`

**New**
- `mplsoccer.Pitch` + `matplotlib` scatter
- Outcome → color mapping + legend
- Saving a PNG artifact (`messi_shots.png`)

## Script
`data_pipeline/plot_shot_map.py`

### Flow
1. Load env + connect to Postgres
2. SQL: join `shots` to `players`, filter by exact `player_name`
3. Build lists: `x`, `y`, `xg`, `outcomes`
4. Map outcomes to colors (`SELECT DISTINCT shot_outcome` discovered labels)
5. `Pitch(...).draw()` then `ax.scatter(...)`
6. Title with shot count + average xG
7. Legend for outcomes present in the data
8. `fig.savefig("messi_shots.png")`

### Why Messi appears
`PLAYER = "Lionel Andrés Messi Cuccittini"` is passed into SQL as `:player`.
The join uses `player_id`; the name filter selects Messi's rows only.

### Outcome labels in our DB
Blocked, Goal, Off T, Post, Saved, Saved Off Target, Saved to Post, Wayward

(Exact strings matter — e.g. `Off T` not `Off Target`.)

## Gotchas learned
- First matplotlib run builds a **font cache** (can take minutes once)
- `plt.show()` blocks the terminal until the window is closed
- Default pitch is white; `pitch_color="grass"` is optional styling
- Missing xG → use a tiny default size so scatter still works
- Open-data La Liga season is Barça-heavy, so maps are often Barça players

## How to run
```bash
# Docker DB up, venv activated, from repo root
python data_pipeline/plot_shot_map.py