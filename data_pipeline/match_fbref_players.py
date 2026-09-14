import os
import re
import unicodedata
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "output" / "fbref" / "barcelona_2018_2019_standard.csv"

load_dotenv(ROOT / ".env")
engine = create_engine(os.environ["DATABASE_URL"])


def normalize(name: str) -> str:
    if not isinstance(name, str):
        return ""
    # strip accents
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.lower().strip()
    name = re.sub(r"[^a-z\s]", " ", name)
    name = re.sub(r"\s+", " ", name)
    return name


fbref = pd.read_csv(CSV_PATH)
# drop non-player footer rows if any
fbref = fbref[~fbref["Player"].astype(str).str.contains("Squad", case=False, na=False)]

with engine.connect() as conn:
    sb = pd.DataFrame(
        conn.execute(text("SELECT player_id, player_name FROM players")).mappings().all()
    )

fbref["norm"] = fbref["Player"].map(normalize)
sb["norm"] = sb["player_name"].map(normalize)

# 1) exact normalized match
fbref["norm"] = fbref["Player"].map(normalize)
sb["norm"] = sb["player_name"].map(normalize)

# drop obvious non-players
fbref = fbref[~fbref["Player"].astype(str).str.contains("Total", case=False, na=False)]

# 1) exact normalized match
exact = fbref.merge(sb, on="norm", how="left", suffixes=("_fbref", "_sb"))
matched = exact[exact["player_id"].notna()].copy()
unmatched = exact[exact["player_id"].isna()][["Player", "norm"]].copy()

print(f"FBref players: {len(fbref)}")
print(f"Exact norm matches: {len(matched)}")


def tokens(s: str) -> set[str]:
    return set(normalize(s).split())


# 2) token-subset match for leftovers
sb_rows = sb.to_dict("records")
extra_matches = []
still_unmatched = []

for _, row in unmatched.iterrows():
    fb_toks = tokens(row["Player"])
    if not fb_toks:
        still_unmatched.append(row["Player"])
        continue

    candidates = []
    for p in sb_rows:
        sb_toks = tokens(p["player_name"])
        if fb_toks.issubset(sb_toks):
            candidates.append(p)

    if len(candidates) == 1:
        p = candidates[0]
        extra_matches.append(
            {
                "Player": row["Player"],
                "player_name": p["player_name"],
                "player_id": p["player_id"],
                "norm": row["norm"],
            }
        )
    else:
        still_unmatched.append(row["Player"])

extra_df = pd.DataFrame(extra_matches)
if len(extra_df):
    # align columns for concat
    for col in matched.columns:
        if col not in extra_df.columns:
            extra_df[col] = pd.NA
    matched = pd.concat([matched, extra_df[matched.columns]], ignore_index=True)

print(f"Token-subset matches added: {len(extra_df)}")
print(f"Still unmatched: {len(still_unmatched)}")
print("\nSample matches:")
print(matched[["Player", "player_name", "player_id"]].head(15).to_string(index=False))
print("\nStill unmatched FBref names:")
for name in still_unmatched:
    print(name)

out = ROOT / "output" / "fbref" / "barcelona_2018_2019_matched.csv"
matched.to_csv(out, index=False)
print("\nSaved", out)