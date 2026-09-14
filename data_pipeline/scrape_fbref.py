"""
Parse FBref Barcelona 2018-19 standard stats from a saved HTML page.

FBref often returns HTTP 403 to automated requests, so:
1. Open https://fbref.com/en/squads/206d90db/2018-2019/Barcelona-Stats
2. File → Save Page As… → Web Page, HTML Only
3. Save as: data_pipeline/fbref_raw/barcelona_2018_2019.html
4. Run from anywhere: python data_pipeline/scrape_fbref.py
"""

from pathlib import Path

import pandas as pd

# Resolve from repo root (parent of data_pipeline/), not process cwd
ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "data_pipeline" / "fbref_raw" / "barcelona_2018_2019.html"
OUT_DIR = ROOT / "output" / "fbref"
OUT_DIR.mkdir(parents=True, exist_ok=True)

if not HTML_PATH.exists():
    raise FileNotFoundError(
        f"Missing {HTML_PATH}. Save the FBref 2018-19 Barcelona page there first."
    )

dfs = pd.read_html(HTML_PATH)
print(f"tables: {len(dfs)}")
for i, t in enumerate(dfs):
    print(i, t.shape, list(t.columns)[:6])

# Prefer a player table with many stat columns (standard squad stats)
table_index = 0
for i, t in enumerate(dfs):
    cols = [str(c).lower() for c in t.columns]
    flat = " ".join(cols)
    if "player" in flat and t.shape[1] >= 10:
        table_index = i
        break

df = dfs[table_index].copy()


def flatten_columns(columns):
    if not isinstance(columns, pd.MultiIndex):
        return columns
    flat = []
    for col in columns:
        parts = [str(x) for x in col if not str(x).startswith("Unnamed")]
        flat.append("_".join(parts) if parts else str(col[-1]))
    return flat


df.columns = flatten_columns(df.columns)

out_csv = OUT_DIR / "barcelona_2018_2019_standard.csv"
df.to_csv(out_csv, index=False)
print(f"Saved {out_csv} using table index {table_index} ({df.shape[0]} rows)")
