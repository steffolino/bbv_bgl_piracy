#!/usr/bin/env python3
import json
import sqlite3
from collections import defaultdict
from datetime import datetime

def extract_player_data():
    """Extract real player statistics from the historical basketball data"""
    
    print("🏀 EXTRACTING REAL PLAYER DATA")
    print("=" * 60)
    
    # Load historical production data
    with open('historical_production_data.json', 'r', encoding='utf-8') as f:
        historical_data = json.load(f)
    
    print(f"📊 Processing {len(historical_data)} league seasons...")
    
    all_players = {}
    all_matches = []
    season_stats = defaultdict(lambda: defaultdict(dict))
    
    total_matches = 0
    total_players = 0
    
    for league_season in historical_data:
        league_id = league_season.get('league_id')
        season_year = league_season.get('season_year')
        matches = league_season.get('matches', [])
        league_name = league_season.get('found_league_name', '')
        
        if not matches:
            continue
            
        print(f"🏀 League {league_id} ({season_year}): {len(matches)} matches")
        total_matches += len(matches)
        
        for match in matches:
            match_data = {
                'league_id': league_id,
                'season_year': season_year,
                'league_name': league_name,
                'match': match
            }
            all_matches.append(match_data)
            
            # Extract player stats from match
            if isinstance(match, dict):
                # Look for player data in various possible structures
                for key in ['home_players', 'guest_players', 'players', 'boxscore', 'stats']:
                    if key in match:
                        players_data = match[key]
                        if isinstance(players_data, list):
                            for player in players_data:
                                if isinstance(player, dict) and 'name' in player:
                                    player_name = player['name']
                                    player_id = f"{player_name}_{league_id}_{season_year}"
                                    
                                    if player_name not in all_players:
                                        all_players[player_name] = {
                                            'name': player_name,
                                            'seasons': [],
                                            'career_stats': {},
                                            'teams': set()
                                        }
                                    
                                    # Extract stats
                                    stats = {
                                        'points': player.get('points', player.get('pts', 0)),
                                        'games': 1,
                                        'three_pointers_made': player.get('3pm', player.get('three_made', 0)),
                                        'three_pointers_attempted': player.get('3pa', player.get('three_attempted', 0)),
                                        'free_throws_made': player.get('ftm', player.get('ft_made', 0)),
                                        'free_throws_attempted': player.get('fta', player.get('ft_attempted', 0)),
                                        'rebounds': player.get('reb', player.get('rebounds', 0)),
                                        'assists': player.get('ast', player.get('assists', 0)),
                                    }
                                    
                                    # Add to season stats
                                    season_key = f"{season_year}_{league_id}"
                                    if player_name not in season_stats[season_key]:
                                        season_stats[season_key][player_name] = {
                                            'season_year': season_year,
                                            'league_id': league_id,
                                            'league_name': league_name,
                                            'games': 0,
                                            'total_points': 0,
                                            'total_3pm': 0,
                                            'total_3pa': 0,
                                            'total_ftm': 0,
                                            'total_fta': 0,
                                            'total_rebounds': 0,
                                            'total_assists': 0
                                        }
                                    
                                    # Aggregate stats
                                    season_stats[season_key][player_name]['games'] += 1
                                    season_stats[season_key][player_name]['total_points'] += stats['points']
                                    season_stats[season_key][player_name]['total_3pm'] += stats['three_pointers_made']
                                    season_stats[season_key][player_name]['total_3pa'] += stats['three_pointers_attempted']
                                    season_stats[season_key][player_name]['total_ftm'] += stats['free_throws_made']
                                    season_stats[season_key][player_name]['total_fta'] += stats['free_throws_attempted']
                                    season_stats[season_key][player_name]['total_rebounds'] += stats['rebounds']
                                    season_stats[season_key][player_name]['total_assists'] += stats['assists']
                                    
                                    total_players += 1
    
    print(f"\n📊 EXTRACTION SUMMARY:")
    print(f"   🎯 Total matches processed: {total_matches}")
    print(f"   👥 Total players found: {len(all_players)}")
    print(f"   📈 Player-season combinations: {total_players}")
    
    # Calculate career averages
    for player_name, player_data in all_players.items():
        career_totals = {
            'games': 0,
            'points': 0,
            'three_made': 0,
            'three_attempted': 0,
            'ft_made': 0,
            'ft_attempted': 0,
            'rebounds': 0,
            'assists': 0
        }
        
        # Sum across all seasons
        for season_key, players in season_stats.items():
            if player_name in players:
                stats = players[player_name]
                career_totals['games'] += stats['games']
                career_totals['points'] += stats['total_points']
                career_totals['three_made'] += stats['total_3pm']
                career_totals['three_attempted'] += stats['total_3pa']
                career_totals['ft_made'] += stats['total_ftm']
                career_totals['ft_attempted'] += stats['total_fta']
                career_totals['rebounds'] += stats['total_rebounds']
                career_totals['assists'] += stats['total_assists']
                
                player_data['seasons'].append({
                    'season': stats['season_year'],
                    'league': stats['league_name'],
                    'games': stats['games'],
                    'ppg': stats['total_points'] / max(stats['games'], 1),
                    'three_pct': stats['total_3pm'] / max(stats['total_3pa'], 1) * 100 if stats['total_3pa'] > 0 else 0,
                    'ft_pct': stats['total_ftm'] / max(stats['total_fta'], 1) * 100 if stats['total_fta'] > 0 else 0
                })
        
        # Calculate career averages
        if career_totals['games'] > 0:
            player_data['career_stats'] = {
                'games': career_totals['games'],
                'ppg': career_totals['points'] / career_totals['games'],
                'three_pct': career_totals['three_made'] / max(career_totals['three_attempted'], 1) * 100 if career_totals['three_attempted'] > 0 else 0,
                'ft_pct': career_totals['ft_made'] / max(career_totals['ft_attempted'], 1) * 100 if career_totals['ft_attempted'] > 0 else 0,
                'rpg': career_totals['rebounds'] / career_totals['games'],
                'apg': career_totals['assists'] / career_totals['games']
            }
    
    # Save to database
    conn = sqlite3.connect('player_stats.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            career_games INTEGER,
            career_ppg REAL,
            career_three_pct REAL,
            career_ft_pct REAL,
            career_rpg REAL,
            career_apg REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_seasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            season_year INTEGER,
            league_id INTEGER,
            league_name TEXT,
            games INTEGER,
            total_points INTEGER,
            ppg REAL,
            total_3pm INTEGER,
            total_3pa INTEGER,
            three_pct REAL,
            total_ftm INTEGER,
            total_fta INTEGER,
            ft_pct REAL,
            total_rebounds INTEGER,
            rpg REAL,
            total_assists INTEGER,
            apg REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_name) REFERENCES players (name)
        )
    ''')
    
    # Insert players
    for player_name, player_data in all_players.items():
        if player_data['career_stats']:
            cursor.execute('''
                INSERT OR REPLACE INTO players 
                (name, career_games, career_ppg, career_three_pct, career_ft_pct, career_rpg, career_apg)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                player_name,
                player_data['career_stats']['games'],
                player_data['career_stats']['ppg'],
                player_data['career_stats']['three_pct'],
                player_data['career_stats']['ft_pct'],
                player_data['career_stats']['rpg'],
                player_data['career_stats']['apg']
            ))
    
    # Insert season stats
    for season_key, players in season_stats.items():
        for player_name, stats in players.items():
            cursor.execute('''
                INSERT OR REPLACE INTO player_seasons 
                (player_name, season_year, league_id, league_name, games, total_points, ppg,
                 total_3pm, total_3pa, three_pct, total_ftm, total_fta, ft_pct,
                 total_rebounds, rpg, total_assists, apg)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                player_name,
                stats['season_year'],
                stats['league_id'],
                stats['league_name'],
                stats['games'],
                stats['total_points'],
                stats['total_points'] / max(stats['games'], 1),
                stats['total_3pm'],
                stats['total_3pa'],
                stats['total_3pm'] / max(stats['total_3pa'], 1) * 100 if stats['total_3pa'] > 0 else 0,
                stats['total_ftm'],
                stats['total_fta'],
                stats['total_ftm'] / max(stats['total_fta'], 1) * 100 if stats['total_fta'] > 0 else 0,
                stats['total_rebounds'],
                stats['total_rebounds'] / max(stats['games'], 1),
                stats['total_assists'],
                stats['total_assists'] / max(stats['games'], 1)
            ))
    
    conn.commit()
    
    # Show top players
    cursor.execute('''
        SELECT name, career_games, career_ppg, career_three_pct, career_ft_pct 
        FROM players 
        WHERE career_games > 5
        ORDER BY career_ppg DESC 
        LIMIT 10
    ''')
    top_players = cursor.fetchall()
    
    print(f"\n🏆 TOP PLAYERS BY PPG (min 5 games):")
    print("=" * 60)
    print("Player                    | G   | PPG  | 3P%  | FT%")
    print("-" * 60)
    for player in top_players:
        name, games, ppg, three_pct, ft_pct = player
        print(f"{name:<25} | {games:<3} | {ppg:4.1f} | {three_pct:4.1f} | {ft_pct:4.1f}")
    
    conn.close()
    
    print(f"\n✅ Player database saved as 'player_stats.db'")
    return len(all_players), total_matches

if __name__ == "__main__":
    players, matches = extract_player_data()
