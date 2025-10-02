#!/usr/bin/env python3

import sqlite3

def show_all_leagues():
    """Show all leagues by name from all databases"""
    
    print('=== ALL LEAGUES BY NAME ===')
    
    # Check basketball_analytics.db
    try:
        conn = sqlite3.connect('basketball_analytics.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT name FROM leagues WHERE name IS NOT NULL AND name != "" ORDER BY name')
        analytics_leagues = cursor.fetchall()
        
        print(f'\n📊 BASKETBALL_ANALYTICS.DB ({len(analytics_leagues)} leagues):')
        for i, (name,) in enumerate(analytics_leagues, 1):
            print(f'{i:3d}. {name}')
        
        conn.close()
    except Exception as e:
        print(f'Error reading basketball_analytics.db: {e}')
    
    # Check league_cache.db
    try:
        conn = sqlite3.connect('league_cache.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT league_name FROM league_cache WHERE league_name IS NOT NULL AND league_name != "" ORDER BY league_name')
        cache_leagues = cursor.fetchall()
        
        print(f'\n💾 LEAGUE_CACHE.DB ({len(cache_leagues)} leagues):')
        for i, (name,) in enumerate(cache_leagues, 1):
            print(f'{i:3d}. {name}')
        
        conn.close()
    except Exception as e:
        print(f'Error reading league_cache.db: {e}')
    
    # Also check for leagues with match data
    try:
        conn = sqlite3.connect('league_cache.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT league_name, match_count, league_id 
            FROM league_cache 
            WHERE league_name IS NOT NULL AND league_name != "" AND match_count > 0 
            ORDER BY match_count DESC
        ''')
        leagues_with_matches = cursor.fetchall()
        
        print(f'\n🏀 LEAGUES WITH MATCHES ({len(leagues_with_matches)} leagues):')
        for i, (name, match_count, league_id) in enumerate(leagues_with_matches, 1):
            print(f'{i:3d}. {name} - {match_count} matches (ID: {league_id})')
        
        conn.close()
    except Exception as e:
        print(f'Error reading league match data: {e}')

if __name__ == "__main__":
    show_all_leagues()
