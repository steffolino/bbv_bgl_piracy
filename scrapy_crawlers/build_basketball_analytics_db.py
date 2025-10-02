#!/usr/bin/env python3
import json
import sqlite3
from collections import defaultdict
from datetime import datetime
import re

def build_basketball_analytics_db():
    """Build comprehensive basketball analytics database from real match data"""
    
    print("🏀 BUILDING BASKETBALL ANALYTICS DATABASE")
    print("=" * 60)
    
    # Load historical production data
    with open('historical_production_data.json', 'r', encoding='utf-8') as f:
        historical_data = json.load(f)
    
    # Create database
    conn = sqlite3.connect('basketball_analytics.db')
    cursor = conn.cursor()
    
    # Create comprehensive schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leagues (
            id INTEGER PRIMARY KEY,
            league_id INTEGER UNIQUE,
            name TEXT,
            district_name TEXT,
            level INTEGER,
            region TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seasons (
            id INTEGER PRIMARY KEY,
            season_year INTEGER,
            league_id INTEGER,
            total_matches INTEGER,
            completed_matches INTEGER,
            teams_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (league_id) REFERENCES leagues (league_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY,
            team_permanent_id INTEGER UNIQUE,
            team_name TEXT,
            team_name_small TEXT,
            club_id INTEGER,
            first_seen_season INTEGER,
            last_seen_season INTEGER,
            total_seasons INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            match_id INTEGER UNIQUE,
            league_id INTEGER,
            season_year INTEGER,
            match_day INTEGER,
            match_no INTEGER,
            kickoff_date TEXT,
            kickoff_time TEXT,
            home_team_id INTEGER,
            guest_team_id INTEGER,
            home_team_name TEXT,
            guest_team_name TEXT,
            result TEXT,
            home_score INTEGER,
            guest_score INTEGER,
            confirmed BOOLEAN,
            cancelled BOOLEAN,
            forfeit BOOLEAN,
            has_boxscore BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (league_id) REFERENCES leagues (league_id),
            FOREIGN KEY (home_team_id) REFERENCES teams (team_permanent_id),
            FOREIGN KEY (guest_team_id) REFERENCES teams (team_permanent_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_season_stats (
            id INTEGER PRIMARY KEY,
            team_permanent_id INTEGER,
            season_year INTEGER,
            league_id INTEGER,
            games_played INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            points_for INTEGER DEFAULT 0,
            points_against INTEGER DEFAULT 0,
            point_differential INTEGER DEFAULT 0,
            avg_points_for REAL DEFAULT 0,
            avg_points_against REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_permanent_id) REFERENCES teams (team_permanent_id),
            FOREIGN KEY (league_id) REFERENCES leagues (league_id)
        )
    ''')
    
    print(f"📊 Processing {len(historical_data)} league seasons...")
    
    leagues_added = 0
    seasons_added = 0
    teams_added = 0
    matches_added = 0
    
    all_teams = {}
    team_stats = defaultdict(lambda: defaultdict(dict))
    
    for league_season in historical_data:
        league_id = league_season.get('league_id')
        season_year = league_season.get('season_year')
        matches = league_season.get('matches', [])
        league_name = league_season.get('found_league_name', '')
        district_name = league_season.get('found_district_name', '')
        
        if not matches or not league_id:
            continue
        
        # Insert league
        cursor.execute('''
            INSERT OR IGNORE INTO leagues (league_id, name, district_name)
            VALUES (?, ?, ?)
        ''', (league_id, league_name, district_name))
        leagues_added += 1
        
        # Process matches and extract teams
        completed_matches = 0
        teams_in_season = set()
        
        for match in matches:
            if not isinstance(match, dict):
                continue
                
            match_id = match.get('matchId')
            if not match_id:
                continue
            
            home_team = match.get('homeTeam', {}) or {}
            guest_team = match.get('guestTeam', {}) or {}
            result = match.get('result', '')
            
            # Extract team data
            home_team_id = home_team.get('teamPermanentId')
            guest_team_id = guest_team.get('teamPermanentId')
            home_team_name = home_team.get('teamname', '')
            guest_team_name = guest_team.get('teamname', '')
            
            if home_team_id:
                teams_in_season.add(home_team_id)
                if home_team_id not in all_teams:
                    all_teams[home_team_id] = {
                        'name': home_team_name,
                        'name_small': home_team.get('teamnameSmall', ''),
                        'club_id': home_team.get('clubId'),
                        'first_season': season_year,
                        'last_season': season_year,
                        'seasons': set([season_year])
                    }
                else:
                    all_teams[home_team_id]['seasons'].add(season_year)
                    all_teams[home_team_id]['last_season'] = max(all_teams[home_team_id]['last_season'], season_year)
            
            if guest_team_id:
                teams_in_season.add(guest_team_id)
                if guest_team_id not in all_teams:
                    all_teams[guest_team_id] = {
                        'name': guest_team_name,
                        'name_small': guest_team.get('teamnameSmall', ''),
                        'club_id': guest_team.get('clubId'),
                        'first_season': season_year,
                        'last_season': season_year,
                        'seasons': set([season_year])
                    }
                else:
                    all_teams[guest_team_id]['seasons'].add(season_year)
                    all_teams[guest_team_id]['last_season'] = max(all_teams[guest_team_id]['last_season'], season_year)
            
            # Parse scores
            home_score = 0
            guest_score = 0
            if result and ':' in result:
                try:
                    scores = result.split(':')
                    home_score = int(scores[0].strip())
                    guest_score = int(scores[1].strip())
                    completed_matches += 1
                except ValueError:
                    pass
            
            # Insert match
            cursor.execute('''
                INSERT OR IGNORE INTO matches 
                (match_id, league_id, season_year, match_day, match_no, kickoff_date, kickoff_time,
                 home_team_id, guest_team_id, home_team_name, guest_team_name, result, 
                 home_score, guest_score, confirmed, cancelled, forfeit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match_id, league_id, season_year, 
                match.get('matchDay'), match.get('matchNo'),
                match.get('kickoffDate'), match.get('kickoffTime'),
                home_team_id, guest_team_id, home_team_name, guest_team_name,
                result, home_score, guest_score,
                match.get('ergebnisbestaetigt', False),
                match.get('abgesagt', False),
                match.get('verzicht', False)
            ))
            matches_added += 1
            
            # Update team stats
            if home_team_id and guest_team_id and result and ':' in result:
                season_key = f"{season_year}_{league_id}"
                
                # Initialize team stats
                for team_id in [home_team_id, guest_team_id]:
                    if team_id not in team_stats[season_key]:
                        team_stats[season_key][team_id] = {
                            'games': 0, 'wins': 0, 'losses': 0,
                            'points_for': 0, 'points_against': 0
                        }
                
                # Update home team stats
                team_stats[season_key][home_team_id]['games'] += 1
                team_stats[season_key][home_team_id]['points_for'] += home_score
                team_stats[season_key][home_team_id]['points_against'] += guest_score
                if home_score > guest_score:
                    team_stats[season_key][home_team_id]['wins'] += 1
                else:
                    team_stats[season_key][home_team_id]['losses'] += 1
                
                # Update guest team stats  
                team_stats[season_key][guest_team_id]['games'] += 1
                team_stats[season_key][guest_team_id]['points_for'] += guest_score
                team_stats[season_key][guest_team_id]['points_against'] += home_score
                if guest_score > home_score:
                    team_stats[season_key][guest_team_id]['wins'] += 1
                else:
                    team_stats[season_key][guest_team_id]['losses'] += 1
        
        # Insert season
        cursor.execute('''
            INSERT OR IGNORE INTO seasons 
            (season_year, league_id, total_matches, completed_matches, teams_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (season_year, league_id, len(matches), completed_matches, len(teams_in_season)))
        seasons_added += 1
    
    # Insert teams
    for team_id, team_data in all_teams.items():
        cursor.execute('''
            INSERT OR REPLACE INTO teams 
            (team_permanent_id, team_name, team_name_small, club_id, 
             first_seen_season, last_seen_season, total_seasons)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            team_id, team_data['name'], team_data['name_small'], team_data['club_id'],
            team_data['first_season'], team_data['last_season'], len(team_data['seasons'])
        ))
        teams_added += 1
    
    # Insert team season stats
    for season_key, teams in team_stats.items():
        season_year, league_id = map(int, season_key.split('_'))
        for team_id, stats in teams.items():
            cursor.execute('''
                INSERT OR REPLACE INTO team_season_stats 
                (team_permanent_id, season_year, league_id, games_played, wins, losses,
                 points_for, points_against, point_differential, avg_points_for, avg_points_against)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                team_id, season_year, league_id,
                stats['games'], stats['wins'], stats['losses'],
                stats['points_for'], stats['points_against'],
                stats['points_for'] - stats['points_against'],
                stats['points_for'] / max(stats['games'], 1),
                stats['points_against'] / max(stats['games'], 1)
            ))
    
    conn.commit()
    
    print(f"\n📊 DATABASE SUMMARY:")
    print(f"   🏆 Leagues: {leagues_added}")
    print(f"   📅 Seasons: {seasons_added}")  
    print(f"   🏀 Teams: {teams_added}")
    print(f"   🎯 Matches: {matches_added}")
    
    # Show top teams by performance
    cursor.execute('''
        SELECT t.team_name, ts.season_year, ts.games_played, ts.wins, ts.losses,
               ROUND(ts.avg_points_for, 1) as ppg, ROUND(ts.point_differential, 1) as diff
        FROM team_season_stats ts
        JOIN teams t ON ts.team_permanent_id = t.team_permanent_id
        WHERE ts.games_played >= 10
        ORDER BY ts.point_differential DESC
        LIMIT 15
    ''')
    top_teams = cursor.fetchall()
    
    print(f"\n🏆 TOP TEAMS BY POINT DIFFERENTIAL (min 10 games):")
    print("=" * 80)
    print("Team                          | Season | G  | W  | L  | PPG  | +/-")
    print("-" * 80)
    for team in top_teams:
        name, season, games, wins, losses, ppg, diff = team
        print(f"{name:<30} | {season}  | {games:<2} | {wins:<2} | {losses:<2} | {ppg:<4} | {diff:+5.1f}")
    
    # Historical coverage
    cursor.execute('SELECT MIN(season_year), MAX(season_year), COUNT(DISTINCT season_year) FROM seasons')
    min_year, max_year, total_years = cursor.fetchone()
    
    cursor.execute('SELECT COUNT(*) FROM matches WHERE home_score > 0 OR guest_score > 0')
    completed_matches = cursor.fetchone()[0]
    
    print(f"\n📊 HISTORICAL COVERAGE:")
    print("=" * 60)
    print(f"📅 Years: {min_year} - {max_year} ({total_years} seasons)")
    print(f"🎯 Completed matches: {completed_matches}")
    print(f"🏀 Total teams tracked: {len(all_teams)}")
    
    conn.close()
    
    print(f"\n✅ Basketball analytics database saved as 'basketball_analytics.db'")
    return leagues_added, teams_added, matches_added

if __name__ == "__main__":
    leagues, teams, matches = build_basketball_analytics_db()
