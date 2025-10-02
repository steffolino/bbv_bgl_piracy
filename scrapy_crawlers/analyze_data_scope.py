#!/usr/bin/env python3

import sqlite3
import json

def analyze_available_data():
    """Analyze what data we have available for extraction"""
    
    conn = sqlite3.connect('basketball_analytics.db')
    cursor = conn.cursor()

    print('=== AVAILABLE DATA SCOPE ===')

    # Check leagues
    cursor.execute('SELECT COUNT(DISTINCT league_name) FROM leagues WHERE league_name IS NOT NULL AND league_name != ""')
    league_count = cursor.fetchone()[0]
    print(f'Leagues with names: {league_count}')

    # Check teams  
    cursor.execute('SELECT COUNT(DISTINCT team_name) FROM teams WHERE team_name IS NOT NULL AND team_name != ""')
    team_count = cursor.fetchone()[0]
    print(f'Teams with names: {team_count}')

    # Check matches with results
    cursor.execute('SELECT COUNT(*) FROM matches WHERE home_score IS NOT NULL AND guest_score IS NOT NULL')
    matches_with_results = cursor.fetchone()[0]
    print(f'Matches with results: {matches_with_results}')

    # Sample some leagues
    print('\n=== SAMPLE LEAGUES ===')
    cursor.execute('SELECT DISTINCT league_name FROM leagues WHERE league_name IS NOT NULL AND league_name != "" LIMIT 10')
    sample_leagues = cursor.fetchall()
    for league in sample_leagues:
        print(f'- {league[0]}')

    # Sample some teams with league info
    print('\n=== SAMPLE TEAMS BY LEAGUE ===')
    cursor.execute('''
        SELECT l.league_name, t.team_name 
        FROM teams t 
        JOIN leagues l ON t.league_id = l.league_id 
        WHERE l.league_name IS NOT NULL AND t.team_name IS NOT NULL 
        LIMIT 20
    ''')
    sample_teams = cursor.fetchall()
    for league, team in sample_teams:
        print(f'- {team} ({league})')

    # Check for match results by league
    print('\n=== MATCHES WITH RESULTS BY LEAGUE ===')
    cursor.execute('''
        SELECT l.league_name, COUNT(*) as match_count
        FROM matches m
        JOIN teams ht ON m.home_team_id = ht.team_id
        JOIN leagues l ON ht.league_id = l.league_id
        WHERE m.home_score IS NOT NULL AND m.guest_score IS NOT NULL
        GROUP BY l.league_name
        ORDER BY match_count DESC
        LIMIT 10
    ''')
    league_matches = cursor.fetchall()
    for league, count in league_matches:
        print(f'- {league}: {count} matches with results')

    conn.close()

    print('\n=== CRAWLING EXPANSION OPPORTUNITIES ===')
    print('1. Extract player data from more leagues beyond just "Senioren Oberfranken"')
    print('2. Process matches with results to extract player statistics')
    print('3. Crawl team rosters from basketball-bund.net team pages')
    print('4. Extract player data from historical seasons')
    print('5. Process league standings and team statistics')

if __name__ == "__main__":
    analyze_available_data()
