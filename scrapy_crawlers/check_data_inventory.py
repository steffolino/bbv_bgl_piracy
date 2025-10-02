#!/usr/bin/env python3

import sqlite3
import json

def check_current_data():
    """Check what data we currently have available"""
    
    conn = sqlite3.connect('basketball_analytics.db')
    cursor = conn.cursor()

    print('=== CURRENT DATA INVENTORY ===')

    # Check leagues
    cursor.execute("SELECT COUNT(DISTINCT name) FROM leagues WHERE name IS NOT NULL AND name != ''")
    league_count = cursor.fetchone()[0]
    print(f'Leagues with names: {league_count}')

    # Check teams  
    cursor.execute("SELECT COUNT(DISTINCT team_name) FROM teams WHERE team_name IS NOT NULL AND team_name != ''")
    team_count = cursor.fetchone()[0]
    print(f'Teams with names: {team_count}')

    # Check matches with results
    cursor.execute('SELECT COUNT(*) FROM matches WHERE home_score IS NOT NULL AND guest_score IS NOT NULL')
    matches_with_results = cursor.fetchone()[0]
    print(f'Matches with results: {matches_with_results}')

    # Total records
    cursor.execute('SELECT COUNT(*) FROM leagues')
    total_leagues = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM teams')
    total_teams = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM matches')
    total_matches = cursor.fetchone()[0]

    print(f'\nTotal records: {total_leagues} leagues, {total_teams} teams, {total_matches} matches')

    # Sample leagues with most teams
    print('\n=== TOP LEAGUES BY TEAM COUNT ===')
    cursor.execute('''
        SELECT l.name, COUNT(DISTINCT t.team_name) as team_count
        FROM leagues l
        JOIN matches m ON l.league_id = m.league_id
        JOIN teams t ON (m.home_team_id = t.team_permanent_id OR m.guest_team_id = t.team_permanent_id)
        WHERE l.name IS NOT NULL AND l.name != ''
        GROUP BY l.name
        ORDER BY team_count DESC
        LIMIT 10
    ''')
    top_leagues = cursor.fetchall()
    for league, count in top_leagues:
        print(f'- {league}: {count} teams')

    # Leagues with most matches that have results
    print('\n=== LEAGUES WITH MOST COMPLETED MATCHES ===')
    cursor.execute('''
        SELECT l.name, COUNT(*) as completed_matches
        FROM leagues l
        JOIN matches m ON l.league_id = m.league_id
        WHERE m.home_score IS NOT NULL AND m.guest_score IS NOT NULL
        AND l.name IS NOT NULL AND l.name != ''
        GROUP BY l.name
        ORDER BY completed_matches DESC
        LIMIT 10
    ''')
    completed_matches = cursor.fetchall()
    for league, count in completed_matches:
        print(f'- {league}: {count} completed matches')

    # Sample teams from different leagues
    print('\n=== SAMPLE TEAMS BY LEAGUE ===')
    cursor.execute('''
        SELECT DISTINCT l.name, t.team_name
        FROM leagues l
        JOIN matches m ON l.league_id = m.league_id
        JOIN teams t ON (m.home_team_id = t.team_permanent_id OR m.guest_team_id = t.team_permanent_id)
        WHERE l.name IS NOT NULL AND t.team_name IS NOT NULL
        ORDER BY l.name, t.team_name
        LIMIT 20
    ''')
    team_samples = cursor.fetchall()
    current_league = None
    for league, team in team_samples:
        if league != current_league:
            print(f'\n{league}:')
            current_league = league
        print(f'  - {team}')

    conn.close()

    print('\n=== PLAYER DATA EXTRACTION OPPORTUNITIES ===')
    print('Current: Only 27 players from Senioren Oberfranken league')
    print('\nPotential expansions:')
    print('1. Extract from all leagues with completed matches')
    print('2. Process team rosters from basketball-bund.net')
    print('3. Extract player stats from match results')
    print('4. Crawl historical player data from previous seasons')
    print('5. Get player profiles from team pages')

if __name__ == "__main__":
    check_current_data()
