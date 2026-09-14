# FBref scrape + player matching (roadmap item #3)

## Goal
Pull **season-level aggregate stats** for Barcelona **2018/2019** from FBref and
**link** those rows to StatsBomb `player_id`s already in Postgres.

This season matches our ingested open data (`competitions.season_name = 2018/2019`).

## Concept
### StatsBomb vs FBref
| StatsBomb (Postgres) | FBref |
|----------------------|--------|
| Event-level shots (x, y, xG, outcome) | Season aggregates (MP, Gls, Ast, …) |
| Long official names + numeric `player_id` | Shorter display names |

### Why scraping was fragile
Live `pandas.read_html(url)` / `requests.get` returned **HTTP 403 Forbidden**.
FBref blocks many automated clients.

**Workaround:** save the page in a browser (HTML only), then parse the local file.
That is still scraping (HTML tables → DataFrame); only the download step is manual.

## Scripts
### `data_pipeline/scrape_fbref.py`
1. Resolve paths from repo root (`Path(__file__).parents[1]`) so cwd does not break paths
2. Read `data_pipeline/fbref_raw/barcelona_2018_2019.html`
3. `pd.read_html` → multiple tables on the page
4. Auto-select a player stats table (has "Player", many columns)
5. Flatten MultiIndex columns
6. Write `output/fbref/barcelona_2018_2019_standard.csv`

### `data_pipeline/match_fbref_players.py`
Join FBref `Player` names to Postgres `players`.

**Pass 1 — exact normalized match**
- Lowercase, strip accents/punctuation, collapse spaces
- `merge` on that `norm` string
- Works when both sides use the same full name (e.g. Ivan Rakitić)

**Pass 2 — token-subset match** (for leftovers)
- Split names into word sets
- Match if FBref tokens ⊆ StatsBomb tokens and **exactly one** candidate
- Example: `{lionel, messi}` ⊆ `{lionel, andres, messi, cuccittini}`

**Result (typical run)**
- Exact matches: 5
- Token-subset added: 17
- Total matched: 22
- Still unmatched: ~12 (often not in open-data `players`, nicknames, or ambiguous tokens)

Output: `output/fbref/barcelona_2018_2019_matched.csv` (includes `player_id`).

## Reused vs new
**Reused:** Postgres `players`, dotenv/SQLAlchemy, 2018/19 season focus  
**New:** HTML table scrape, 403 handling via saved HTML, name entity resolution

## Gotchas
- Run scrape/match with Docker DB up for matching
- `data_pipeline/fbref_raw/` is gitignored (large HTML); keep scripts + CSV/docs in git
- Relative paths failed when cwd was `data_pipeline/` — fixed via `__file__` root
- Exact norm match alone is not enough for Messi-style long StatsBomb names
- Rows like "Opponent Total" are not players — filter them out

## How to run
```bash
# 1) Save FBref 2018-19 Barcelona page to:
#    data_pipeline/fbref_raw/barcelona_2018_2019.html
python data_pipeline/scrape_fbref.py

# 2) Match to StatsBomb ids (DB must be running)
python data_pipeline/match_fbref_players.py