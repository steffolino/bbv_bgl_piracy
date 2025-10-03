# Oberfranken League & Player Ingestion Script
# This script ingests all league and player data from the JSON crawl output into a database or API.
# Assumes a SQLite database for demonstration, but can be adapted for other backends.

import json
import sqlite3

# Paths to JSON files
LEAGUES_JSON = 'oberfranken_leagues_2003_2024.json'
COMPREHENSIVE_JSON = 'paginated_historical_comprehensive_20251003_092544.json'
DB_PATH = 'oberfranken_ingest.db'

# Connect to SQLite (or adapt for your backend)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS leagues (
    liga_id TEXT,
    season TEXT,
    name TEXT,
    bezirk TEXT,
    PRIMARY KEY (liga_id, season)
)''')
c.execute('''CREATE TABLE IF NOT EXISTS players (
    season TEXT,
    liga_id TEXT,
    league_name TEXT,
    player_name TEXT,
    stats_json TEXT
)''')
conn.commit()

# Ingest leagues
def ingest_leagues():
    with open(LEAGUES_JSON, 'r', encoding='utf-8') as f:
        leagues = json.load(f)
    for league in leagues:
        c.execute('''INSERT OR REPLACE INTO leagues (liga_id, season, name, bezirk) VALUES (?, ?, ?, ?)''',
                  (league['liga_id'], league['season'], league['name'], league['bezirk']))
    conn.commit()

# Ingest players
def ingest_players():
    with open(COMPREHENSIVE_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for player in data.get('players', []):
        season = player.get('season')
        liga_id = player.get('liga_id')
        league_name = player.get('league_name')
        for stat in player.get('statBesteWerferArchiv', []):
            player_name = stat.get('name')
            stats_json = json.dumps(stat)
            c.execute('''INSERT INTO players (season, liga_id, league_name, player_name, stats_json) VALUES (?, ?, ?, ?, ?)''',
                      (season, liga_id, league_name, player_name, stats_json))
    conn.commit()

if __name__ == '__main__':
    ingest_leagues()
    ingest_players()
    print('Oberfranken league and player data ingested successfully.')
