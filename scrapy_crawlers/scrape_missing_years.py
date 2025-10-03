#!/usr/bin/env python3
"""
🚀 SCRAPE MISSING YEARS 2018-2024
Get the fucking missing basketball data that should have been there all along
"""

import requests
import sqlite3
import time
import json
from bs4 import BeautifulSoup

def scrape_missing_years():
    print('🚀 SCRAPING MISSING YEARS 2018-2024')
    print('=' * 50)

    # Session with proper cookies (from working current_season_scraper.py)
    cookies = {
        '__cmpcc': '1',
        '__cmpconsentx47082': 'CQYqGvAQYqGvAAfQ6BENB-FgAP_AAEPAAAigJSkR5C5cDWFBeTp3QMskeYQX0cgBZgABAgaAASABCDAAcIQAkkESIAyAAAACAQAAIDSBAAAADAhAAEAAAIgBAADoAAAEgBAIIAAEABERQ0IAAAgKCIgAEAAIAAAxIkAAkAKAAILiQFAAgIAiAAABAAAAAIABAAMAAAAIAAACAAIAAAAAAAAAgAAAAAACABAIAAAAAAAAII3wPgAFgAVAAuABwADwAIAAVAAyABoADwAI4ATAAuABiADQAG8APwAhABDACaAE4AMAAYYA5wB3QD8AP0AhABFgCOAEiAJMASkAsQBigDXgG0AOIAdsA_oB_wEXgJWATEAmQBNIChwFHgKRAU2Ap8BboC5AF5gMhAZIAywBlwDTQHFgPHAhWBG8AAA.f_gACHgAAAA',
        'SESSION': 'NDkzOWM2ZDktMzYyOS00MjlhLTk1OTEtNzFlYmNjZTZmNWNh',
        '_cc_id': 'b616c325dc88e1ae505ba80bd46882fe'
    }

    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://www.basketball-bund.net/'
    })

    base_url = 'https://www.basketball-bund.net'
    
    # Connect to database
    # Use project root path for DB, matching main workflow
    conn = sqlite3.connect('league_cache.db')
    cursor = conn.cursor()

    print('📊 Current database status:')
    cursor.execute('SELECT season, COUNT(*) FROM current_player_stats GROUP BY season ORDER BY season')
    for season, count in cursor.fetchall():
        print(f'   {season}: {count:,} players')

    total_new_players = 0

    # Target the missing years systematically
    for year in range(2018, 2025):
        season_name = f'{year}/{str(year+1)[2:]}'  # e.g., 2018/19
        print(f'\n🎯 SCRAPING SEASON {season_name}')
        print('-' * 30)

        # Check if we already have sufficient data for this season
        cursor.execute('SELECT COUNT(*) FROM current_player_stats WHERE season = ?', (season_name,))
        existing_count = cursor.fetchone()[0]
        
        # Only skip if we have a reasonable amount of data (>500 players)
        if existing_count > 500:
            print(f'   ✅ Already have {existing_count} players for {season_name}, skipping')
            continue
        elif existing_count > 0:
            print(f'   🔄 Only {existing_count} players for {season_name}, re-scraping for complete data')
            # Delete incomplete data to re-scrape properly
            cursor.execute('DELETE FROM current_player_stats WHERE season = ?', (season_name,))
            conn.commit()

        # Use the REST API approach that we know works
        try:
            print(f'   🔍 Scanning for leagues in season {season_name}...')
            
            # Try different league ID ranges for this year
            # Current leagues are 47950+, historical should be lower
            base_id = 47950 - (2025 - year) * 100  # Rough estimate going backwards
            
            found_leagues = []
            
            # Scan around the estimated range
            for league_id in range(base_id - 50, base_id + 50):
                try:
                    api_url = f'{base_url}/rest/competition/actual/id/{league_id}'
                    response = session.get(api_url, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        api_season = data.get('season', {}).get('name', '')
                        
                        # Check if this is our target season
                        if season_name in api_season or str(year) in api_season:
                            found_leagues.append(league_id)
                            league_name = data.get('name', 'Unknown')
                            print(f'   ✅ Found league {league_id}: {league_name} ({api_season})')
                            
                            if len(found_leagues) >= 10:  # Limit to avoid too many leagues
                                break
                    
                    time.sleep(0.1)  # Be polite
                    
                except:
                    continue
            
            if not found_leagues:
                print(f'   ❌ No leagues found for {season_name}')
                continue
            
            print(f'   🏀 Processing {len(found_leagues)} leagues for {season_name}...')
            season_players = 0
            
            # Process each league
            for league_id in found_leagues:
                try:
                    api_url = f'{base_url}/rest/competition/actual/id/{league_id}'
                    response = session.get(api_url, timeout=10)
                    
                    if response.status_code != 200:
                        continue
                    
                    data = response.json()
                    teams = data.get('teams', [])
                    
                    for team in teams:
                        team_name = team.get('name', 'Unknown')
                        players = team.get('players', [])
                        
                        for player in players:
                            try:
                                player_name = f"{player.get('firstName', '')} {player.get('lastName', '')}".strip()
                                
                                if not player_name:
                                    continue
                                
                                # Get stats
                                stats = player.get('statistics', {})
                                games = stats.get('games', 0)
                                minutes = stats.get('minutes', 0)
                                points = stats.get('points', 0)
                                rebounds = stats.get('rebounds', 0)
                                assists = stats.get('assists', 0)
                                
                                # Build unique ID (player+team+season)
                                import hashlib
                                raw_id = f"{player_name}|{team_name}|{season_name}"
                                id_hash = hashlib.md5(raw_id.encode('utf-8')).hexdigest()

                                # Use only columns that exist and are relevant
                                cursor.execute('''
                                    INSERT OR REPLACE INTO current_player_stats 
                                    (id, player_name, team_name, games_played, points_total, points_avg, season)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    id_hash,
                                    player_name,
                                    team_name,
                                    games,
                                    points,
                                    float(points) / games if games else 0.0,
                                    season_name
                                ))
                                season_players += 1
                            except Exception as e:
                                continue
                    
                    time.sleep(0.5)  # Be polite between leagues
                    
                except Exception as e:
                    continue
            
            conn.commit()
            total_new_players += season_players
            print(f'   ✅ Added {season_players:,} players for {season_name}')
            
            time.sleep(1)

        except Exception as e:
            print(f'   ❌ Error scraping {season_name}: {e}')
            continue

    print(f'\n🏆 SCRAPING COMPLETE!')
    print(f'   Total new players added: {total_new_players:,}')
    
    # Show final database status
    print(f'\n📊 FINAL DATABASE STATUS:')
    cursor.execute('SELECT season, COUNT(*) FROM current_player_stats GROUP BY season ORDER BY season')
    all_seasons = cursor.fetchall()
    
    for season, count in all_seasons:
        print(f'   {season}: {count:,} players')
    
    total_players = sum(count for _, count in all_seasons)
    print(f'\n   🎯 TOTAL: {total_players:,} players across {len(all_seasons)} seasons')
    
    # Check coverage
    expected_years = list(range(2003, 2025))  # 22 years
    covered_years = [int(season.split('/')[0]) for season, _ in all_seasons]
    missing_years = [year for year in expected_years if year not in covered_years]
    
    coverage_pct = (len(covered_years) / len(expected_years)) * 100
    print(f'   📈 Coverage: {len(covered_years)}/{len(expected_years)} years ({coverage_pct:.1f}%)')
    
    if missing_years:
        print(f'   ❌ Still missing: {missing_years}')
    else:
        print(f'   ✅ COMPLETE COVERAGE! All years from 2003-2024!')

    conn.close()

if __name__ == "__main__":
    scrape_missing_years()
