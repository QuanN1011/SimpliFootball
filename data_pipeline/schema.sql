CREATE TABLE competitions (
    competition_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    competition_name TEXT NOT NULL,
    season_name TEXT NOT NULL,
    PRIMARY KEY (competition_id, season_id)
);

CREATE TABLE matches (
    match_id INTEGER PRIMARY KEY,
    competition_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    match_date DATE,
    home_team TEXT,
    away_team TEXT,
    FOREIGN KEY (competition_id, season_id)
        REFERENCES competitions (competition_id, season_id)
);

CREATE TABLE players (
    player_id INTEGER PRIMARY KEY,
    player_name TEXT NOT NULL
);

CREATE TABLE shots (
    shot_id TEXT PRIMARY KEY,          -- StatsBomb event id
    match_id INTEGER NOT NULL REFERENCES matches (match_id),
    player_id INTEGER REFERENCES players (player_id),
    minute INTEGER,
    second INTEGER,
    x DOUBLE PRECISION,
    y DOUBLE PRECISION,
    shot_outcome TEXT,
    xg DOUBLE PRECISION
);