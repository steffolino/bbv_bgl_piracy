# Oberfranken Extended Stats & Badges Ingestion Script
# This script computes extended stats and badges from the raw player data and stores them in separate tables.
# Assumes the raw data is already ingested in oberfranken_ingest.db.

import sqlite3
import json

DB_PATH = 'oberfranken_ingest.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create extended tables
c.execute('''CREATE TABLE IF NOT EXISTS player_extended_stats (
    player_name TEXT,
    season TEXT,
    liga_id TEXT,
    stat_type TEXT,
    value REAL
)''')
c.execute('''CREATE TABLE IF NOT EXISTS player_badges (
    player_name TEXT,
    badge_type TEXT,
    season TEXT,
    description TEXT
)''')
conn.commit()

# Example: Compute top 10 FT% for each season and all-time
# (Assumes FT% is available in stats_json as 'ft_percent' or similar)
def compute_top_10_ft():
    # Per season
    seasons = [row[0] for row in c.execute('SELECT DISTINCT season FROM players')]
    for season in seasons:
        ft_stats = []
        for row in c.execute('SELECT player_name, stats_json FROM players WHERE season=?', (season,)):
            player_name, stats_json = row
            try:
                stats = json.loads(stats_json)
                ft_percent = float(stats.get('ft_percent', 0))
                ft_stats.append((player_name, ft_percent))
            except Exception:
                continue
        ft_stats.sort(key=lambda x: x[1], reverse=True)
        for rank, (player_name, ft_percent) in enumerate(ft_stats[:10]):
            c.execute('''INSERT INTO player_badges (player_name, badge_type, season, description) VALUES (?, ?, ?, ?)''',
                      (player_name, 'Top 10 FT%', season, f'Rank {rank+1} FT%: {ft_percent}'))
    conn.commit()

# Example: Compute all-time highs (points)
def compute_all_time_highs():
    points_stats = []
    for row in c.execute('SELECT player_name, stats_json FROM players'):
        player_name, stats_json = row
        try:
            stats = json.loads(stats_json)
            points = float(stats.get('points', 0))
            points_stats.append((player_name, points))
        except Exception:
            continue
    points_stats.sort(key=lambda x: x[1], reverse=True)
    for rank, (player_name, points) in enumerate(points_stats[:10]):
        c.execute('''INSERT INTO player_badges (player_name, badge_type, season, description) VALUES (?, ?, ?, ?)''',
                  (player_name, 'All-Time High Points', 'all', f'Rank {rank+1} Points: {points}'))
    conn.commit()

# Example: Compute career averages
def compute_career_averages():
    player_points = {}
    player_games = {}
    for row in c.execute('SELECT player_name, stats_json FROM players'):
        player_name, stats_json = row
        try:
            stats = json.loads(stats_json)
            points = float(stats.get('points', 0))
            games = float(stats.get('games', 1))
            player_points[player_name] = player_points.get(player_name, 0) + points
            player_games[player_name] = player_games.get(player_name, 0) + games
        except Exception:
            continue
    for player_name in player_points:
        avg = player_points[player_name] / max(player_games[player_name], 1)
        c.execute('''INSERT INTO player_extended_stats (player_name, season, liga_id, stat_type, value) VALUES (?, ?, ?, ?, ?)''',
                  (player_name, 'career', '', 'points_avg', avg))
    conn.commit()

if __name__ == '__main__':
    compute_top_10_ft()
    compute_all_time_highs()
    compute_career_averages()
    print('Extended stats and badges computed and stored separately.')
