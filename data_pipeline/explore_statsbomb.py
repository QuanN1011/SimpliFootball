# %%
import pandas as pd
from statsbombpy import sb

# %%
# set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# %%
# Get competitions and display the first 20 rows and shape of the dataframe
competitions = sb.competitions()
print(competitions.head(20))
print(competitions.shape)

# %%
# Filter to find a specific competition you recognize
messi_barca = competitions[competitions['competition_name'].str.contains('La Liga', case=False, na=False)]
messi_barca

# %%
# Filter to find a specific season you recognize
competition_id = 11
season_id = 4

matches = sb.matches(competition_id=competition_id, season_id=season_id)
print(matches.shape)
matches

# %%
# Pick a match_id from the matches dataframe to explore events
match_id = 16196  # replace with the real match_id you picked

events = sb.events(match_id=match_id)
print(events.shape)
print(events.columns.tolist())

# %%
print(events['player'].dropna().unique()[:30])  # Display the first 30 unique player names

# %%
player_name = 'Lionel Andrés Messi Cuccittini'  # replace with the real player name you picked
shots = events[(events['type'] == 'Shot') & (events['player'] == player_name)]

print(shots.shape)
print(shots[['player', 'location', 'shot_end_location', 'shot_outcome', 'minute', 'second', 'shot_statsbomb_xg']].head())

# %%
print(shots['location'].head()) # usually [x,y] not separate columns, so we need to split them into two columns

shots = shots.copy()  # Create a copy of the shots dataframe to avoid SettingWithCopyWarning
shots['x'] = shots['location'].str[0]
shots['y'] = shots['location'].str[1]
print(shots[['player', 'x', 'y', 'shot_outcome']].head())
# %%
