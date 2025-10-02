import sqlite3
import json
import os

# Check all database files for real data
databases = ['league_cache.db', 'basketball_analytics.db', 'extended_league_cache.db', 'archive_results.db', 'crawl_logs.db', 'player_stats.db']

total_leagues = 0
total_teams = 0 
total_players = 0
total_games = 0
total_stats = 0

print('=== REAL DATA INVENTORY ===')
print()

for db_file in databases:
    if os.path.exists(db_file):
        print(f'Database: {db_file}')
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f'  {table_name}: {count} records')
                    
                    if 'league' in table_name.lower():
                        total_leagues += count
                    elif 'team' in table_name.lower():
                        total_teams += count
                    elif 'player' in table_name.lower():
                        total_players += count
                    elif 'game' in table_name.lower() or 'match' in table_name.lower():
                        total_games += count
                    elif 'stat' in table_name.lower():
                        total_stats += count
            
            conn.close()
            print()
        except Exception as e:
            print(f'  Error reading {db_file}: {e}')
            print()

# Check JSON files
json_files = ['real_federation_data.json', 'historical_production_data.json', 'extended_historical_data.json', 'real_players_extracted.json']

print('JSON Files:')
for json_file in json_files:
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    print(f'  {json_file}: {len(data)} records')
                elif isinstance(data, dict):
                    print(f'  {json_file}: {len(data)} keys')
        except Exception as e:
            print(f'  Error reading {json_file}: {e}')

print()
print('SUMMARY:')
print(f'Total Leagues: {total_leagues}')
print(f'Total Teams: {total_teams}')  
print(f'Total Players: {total_players}')
print(f'Total Games: {total_games}')
print(f'Total Stats: {total_stats}')
