# Shot heat map (roadmap item #2)

## Goal
Show where a player's shots **concentrate** on the pitch using a smooth density
surface, not one marker per shot.

## Concept
### Shot map (#1) vs heat map (#2)
| Shot map | Heat map |
|----------|----------|
| One point per shot | Continuous density |
| Exact locations + xG/outcome encodings | "Where shots pile up" |
| `scatter` | KDE (`kdeplot`) |

### What a KDE is
A **kernel density estimate** places a smooth bump on each shot location and adds
them up. Regions with many nearby shots become "hotter." This estimates a spatial
density over `(x, y)` — it is **not** the same as high xG.

Interview line: "The heatmap smooths individual events into a density field so
concentration is easier to see than overlapping scatter points."

## Reused vs new
**Reused from #1**
- Postgres query for one player's `x`, `y`
- StatsBomb coordinates + `Pitch(pitch_type="statsbomb")`
- Saving under `output/shot_maps/`

**New**
- `pitch.kdeplot(...)`
- Colormap / thresh / levels (smoothing appearance)

## Script
`data_pipeline/plot_heat_map.py`

### Flow
1. Connect to Postgres (same as shot map)
2. Load player's shot coordinates
3. Draw StatsBomb pitch
4. Overlay KDE fill with a colormap
5. Save PNG (e.g. `output/shot_maps/messi_heat.png`)

## Gotchas
- Blob in the attacking third for Messi is **expected**, not a bug
- `cmap="hot"` on green grass looks harsh — softer maps like `YlOrRd` read better
- `thresh` / `levels` change how hard-edged the blob looks
- Hot ≠ high quality chance; density ≠ xG
- Too few shots → blotchy or over-smoothed KDE

## How to run
```bash
# Docker DB up, venv on, repo root
python data_pipeline/plot_heat_map.py