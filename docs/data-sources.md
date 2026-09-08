# Data sources

## StatsBomb open data (via statsbombpy)

We use [statsbombpy](https://github.com/statsbomb/statsbombpy) to explore StatsBomb open data. No API credentials are required; `NoAuthWarning` is expected for open-data access.

### Hierarchy

1. `sb.competitions()` — leagues/seasons (`competition_id`, `season_id`)
2. `sb.matches(competition_id=..., season_id=...)` — games (`match_id`)
3. `sb.events(match_id=...)` — on-ball events for one match

### Confusing bits from exploration

- **Column names:** event type is `type` (value `"Shot"`), not `type_name`. Shot result is `shot_outcome`, not `shot_outcome_name`.
- **Locations:** there are no separate `x` / `y` columns by default. `location` (and often `shot_end_location`) is a list like `[x, y]`. Split with `.str[0]` / `.str[1]` if needed.
- **Player names:** use the exact StatsBomb string (e.g. `Lionel Andrés Messi Cuccittini`), not a shortened display name.
- **Sparse columns:** many event columns are NaN except for that event type (e.g. `shot_*` only populated on shots).
- **Season picked in exploration:** La Liga `competition_id=11`, `season_id=4`; sample match `16196`.

### Exploration script

See `data_pipeline/explore_statsbomb.py`.