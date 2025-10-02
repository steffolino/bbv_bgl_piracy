#!/usr/bin/env python3

import sqlite3
import json
import os

def check_player_data():
    """Check what actual player data we have in our databases"""
    
    databases = ['basketball_analytics.db', 'player_stats.db', 'league_cache.db']
    
    for db_name in databases:
        if not os.path.exists(db_name):
            print(f"Database {db_name} not found")
            continue
            
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f'\n=== {db_name} ===')
            for table in tables:
                table_name = table[0]
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                count = cursor.fetchone()[0]
                
                if count > 0:
                    cursor.execute(f'PRAGMA table_info({table_name})')
                    columns = [col[1] for col in cursor.fetchall()]
                    print(f'{table_name}: {count} records')
                    print(f'  Columns: {columns}')
                    
                    # If it looks like player data, show sample
                    if 'player' in table_name.lower() or any('name' in col.lower() for col in columns):
                        cursor.execute(f'SELECT * FROM {table_name} LIMIT 5')
                        sample = cursor.fetchall()
                        print(f'  Sample data:')
                        for row in sample:
                            print(f'    {row}')
                    print()
            
            conn.close()
        except Exception as e:
            print(f'Error reading {db_name}: {e}')

    # Also check JSON files
    json_files = ['real_players_extracted.json', 'real_federation_data.json', 'historical_production_data.json']
    
    for json_file in json_files:
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f'\n=== {json_file} ===')
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            print(f'{key}: {len(value)} items')
                            if len(value) > 0 and 'name' in str(value[0]).lower():
                                print(f'  Sample: {value[:3]}')
                        else:
                            print(f'{key}: {type(value)}')
                elif isinstance(data, list):
                    print(f'List with {len(data)} items')
                    if len(data) > 0:
                        print(f'  Sample: {data[:3]}')
            except Exception as e:
                print(f'Error reading {json_file}: {e}')

if __name__ == "__main__":
    check_player_data()
