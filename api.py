import requests
import pandas as pd
import sqlalchemy as db

API_KEY = 'de4d265554f54a1eae00108032004800'
headers = { 'X-Auth-Token': API_KEY }

url = 'https://api.football-data.org/v4/competitions/PL/matches?season=2024'

# 1. Fetch the data
resp = requests.get(url, headers=headers)

# 2. Always check for errors
if resp.status_code != 200:
    raise RuntimeError(f"API returned {resp.status_code}: {resp.text}")

# 3. Load JSON
data = resp.json()

# 4. Inspect the top‐level keys so you know where “matches” lives

# 5. Pull out the list of fixtures
matches = data.get('matches')
if matches is None:
    raise KeyError("No 'matches' key in the response! Full payload:")
    print(json.dumps(data, indent=2))

# 6. Convert that list of dicts into a DataFrame
#    If you want to flatten nested fields (like score.home, score.away, homeTeam.name, etc.)
df = pd.json_normalize(matches)


#  Persist to SQLite
engine = db.create_engine('sqlite:///pl_matches.db')
df['referees'] = df['referees'].apply(str)
df.to_sql('pl_matches', con=engine, if_exists='replace', index=False)

# Query to only get Manchester United fixtures
with engine.connect() as conn:
    results = conn.execute(db.text("""
        SELECT 
            "utcDate",
            "homeTeam.name" AS home,
            "awayTeam.name" AS away,
            "status",
            "score.fullTime.home" AS score_h,
            "score.fullTime.away" AS score_a
        FROM pl_matches
        WHERE 
            "homeTeam.name" = 'Manchester United FC' 
            OR "awayTeam.name" = 'Manchester United FC'
        ORDER BY "utcDate"
    """)).fetchall()

    manu_fixtures = pd.DataFrame(results, columns=['utcDate', 'Home', 'Away', 'Status', 'Score_H', 'Score_A'])
    print(manu_fixtures)