import requests
import pandas as pd
import sqlalchemy as db
import os
API_KEY = os.getenv("API_KEY")
headers = { 'X-Auth-Token': API_KEY }
db_path = 'sqlite:///pl_fixtures.db'

def fetch_and_store_fixtures():

    url = 'https://api.football-data.org/v4/competitions/PL/matches?season=2024'

    # 1. Fetch the data
    resp = requests.get(url, headers=headers)

    # 2. Always check for errors
    if resp.status_code != 200:
        raise RuntimeError(f"API returned {resp.status_code}: {resp.text}")

    # 3. Load JSON
    data = resp.json()


    # 4. Pull out the list of fixtures
    matches = data.get('matches')
    if matches is None:
        raise KeyError("No 'matches' key in the response! Full payload:")
        print(json.dumps(data, indent=2))

    # 5. Convert that list of dicts into a DataFrame
    #    If you want to flatten nested fields (like score.home, score.away, homeTeam.name, etc.)
    df = pd.json_normalize(matches)


    #  Persist to SQLite
    engine = db.create_engine(db_path)
    df['referees'] = df['referees'].apply(str)
    df.to_sql('pl_matches', con=engine, if_exists='replace', index=False)

# Query to get desired team's fixtures
def get_team_fixtures(team_name):
    engine = db.create_engine(db_path)
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
                "homeTeam.name" = :team 
                OR "awayTeam.name" = :team
            ORDER BY "utcDate"
        """), {"team": team_name}).fetchall()

        # Force conversion to DataFrame, even if empty
        return pd.DataFrame(results, columns=['utcDate', 'Home', 'Away', 'Status', 'Score_H', 'Score_A'])
