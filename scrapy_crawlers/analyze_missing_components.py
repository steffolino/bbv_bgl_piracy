#!/usr/bin/env python3

import sqlite3
import json
import os

def analyze_missing_components():
    """Analyze what components are missing from our basketball analytics platform"""
    
    print('=== BASKETBALL ANALYTICS PLATFORM STATUS ===')

    # Check databases
    databases = ['basketball_analytics.db', 'player_stats.db', 'league_cache.db']
    
    for db_name in databases:
        if os.path.exists(db_name):
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
            tables = cursor.fetchall()
            
            print(f'\n{db_name}:')
            for table in tables:
                table_name = table[0]
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                count = cursor.fetchone()[0]
                print(f'  {table_name}: {count} records')
                
                # Check if matches have boxscore data
                if 'match' in table_name.lower():
                    try:
                        cursor.execute(f'SELECT COUNT(*) FROM {table_name} WHERE matchBoxscore IS NOT NULL AND matchBoxscore != "None"')
                        boxscore_count = cursor.fetchone()[0]
                        print(f'    -> {boxscore_count} matches with boxscore data')
                    except:
                        pass
            
            conn.close()

    # Check player data
    if os.path.exists('real_players_extracted.json'):
        with open('real_players_extracted.json', 'r') as f:
            player_data = json.load(f)
            
        print(f'\nPlayer Data: {len(player_data["players"])} players')
        print(f'Teams represented: {len(set(p["team"] for p in player_data["players"]))} teams')
        print(f'Leagues: {len(set(p["league"] for p in player_data["players"]))} leagues')

    print('\n=== MISSING COMPONENTS ANALYSIS ===')
    
    missing_components = []
    
    # Frontend components
    frontend_public = '../apps/frontend-public'
    if not os.path.exists(f'{frontend_public}/pages/teams.vue'):
        missing_components.append('Teams page with team statistics')
    if not os.path.exists(f'{frontend_public}/pages/leagues.vue'):
        missing_components.append('Leagues page with standings/tables')
    if not os.path.exists(f'{frontend_public}/pages/matches.vue'):
        missing_components.append('Matches page with live scores')
    
    # API endpoints
    api_worker = '../apps/api-worker'
    if not os.path.exists(f'{api_worker}/src/index.ts'):
        missing_components.append('API backend infrastructure')
    
    # Data completeness
    if len(player_data['players']) < 100:
        missing_components.append(f'More player data (currently only {len(player_data["players"])} players)')
    
    # Advanced features
    missing_components.extend([
        'Player comparison functionality',
        'Advanced analytics (PER, efficiency ratings)',
        'Historical season data comparison',
        'Live match updates',
        'Team roster management',
        'League standings calculation',
        'Player photos/avatars',
        'Mobile responsive design optimization',
        'Export functionality (PDF reports, etc.)',
        'Search and filter persistence',
        'User favorites/bookmarks'
    ])
    
    print('\nMISSING COMPONENTS:')
    for i, component in enumerate(missing_components, 1):
        print(f'{i:2d}. {component}')
    
    print(f'\nTotal missing components: {len(missing_components)}')
    
    print('\n=== PRIORITY RECOMMENDATIONS ===')
    priority_items = [
        'API backend endpoints for data serving',
        'Teams page with comprehensive team statistics',
        'Leagues page with standings and tables',
        'Matches page with scores and schedules',
        'Player comparison tools',
        'More comprehensive player data extraction'
    ]
    
    print('\nHIGH PRIORITY:')
    for i, item in enumerate(priority_items, 1):
        print(f'{i}. {item}')

if __name__ == "__main__":
    analyze_missing_components()
