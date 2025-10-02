#!/usr/bin/env python3
"""
Crawl real player data using the league IDs from basketball-bund export
Uses the working URL patterns from our existing crawler
"""
import requests
import json
import re
from datetime import datetime
import sqlite3

def crawl_league_with_real_patterns(league_id, season_year=2024):
    """Use the actual working URL patterns to crawl league data"""
    
    base_url = "https://www.basketball-bund.net"
    
    # Working URL patterns from existing crawler
    urls_to_try = [
        f"{base_url}/liga-{season_year}/{league_id}/",
        f"{base_url}/liga-{season_year}/{league_id}/tabelle/",
        f"{base_url}/liga-{season_year}/{league_id}/spielplan/", 
        f"{base_url}/liga-{season_year}/{league_id}/statistiken/",
        f"{base_url}/ajax/ligaTabelle.php?ligaID={league_id}&saisonYear={season_year}",
        f"{base_url}/ajax/ligaSpielplan.php?ligaID={league_id}&saisonYear={season_year}",
        f"{base_url}/ajax/ligaStatistiken.php?ligaID={league_id}&saisonYear={season_year}"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    results = {}
    
    for url in urls_to_try:
        try:
            print(f"🔍 Trying: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200 and len(response.text) > 100:
                print(f"✅ Success! Got {len(response.text)} chars")
                
                # Try to parse JSON first
                try:
                    data = response.json()
                    results[url] = {
                        'type': 'json',
                        'data': data,
                        'size': len(str(data))
                    }
                    print(f"   📊 JSON response with {len(str(data))} chars")
                except:
                    # HTML response - look for player data
                    html = response.text
                    results[url] = {
                        'type': 'html', 
                        'data': html,
                        'size': len(html)
                    }
                    
                    # Look for player names in HTML
                    player_patterns = [
                        r'<td[^>]*>([A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+)</td>',  # Name pattern
                        r'spieler/(\d+)/([^"]+)"',  # Player links
                        r'data-spieler="([^"]+)"',  # Player data attributes
                    ]
                    
                    found_players = set()
                    for pattern in player_patterns:
                        matches = re.findall(pattern, html)
                        for match in matches:
                            if isinstance(match, tuple):
                                found_players.add(match[-1])
                            else:
                                found_players.add(match)
                    
                    if found_players:
                        print(f"   👥 Found {len(found_players)} potential players")
                        results[url]['players'] = list(found_players)
                        
            else:
                print(f"❌ Failed: Status {response.status_code}, Size {len(response.text)}")
                
        except Exception as e:
            print(f"💥 Error: {str(e)}")
    
    return results

def extract_real_league_ids():
    """Extract league IDs from the basketball-bund export"""
    file_path = r"c:\Users\StretzS\Downloads\ligaErgExtended (1).txt"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract league IDs
    league_pattern = r'Liganr\.: (\d+)\)'
    league_ids = list(set(re.findall(league_pattern, content)))
    
    return league_ids

def save_player_data_to_db(league_data):
    """Save extracted player data to database"""
    conn = sqlite3.connect('real_player_data.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS real_leagues (
            league_id INTEGER PRIMARY KEY,
            season_year INTEGER,
            name TEXT,
            last_crawled TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS real_players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            league_id INTEGER,
            season_year INTEGER,
            data_source TEXT,
            extracted_at TIMESTAMP,
            raw_data TEXT
        )
    ''')
    
    # Insert data
    for league_id, data in league_data.items():
        cursor.execute('''
            INSERT OR REPLACE INTO real_leagues 
            (league_id, season_year, last_crawled) 
            VALUES (?, ?, ?)
        ''', (league_id, 2024, datetime.now()))
        
        for url, info in data.items():
            if 'players' in info:
                for player in info['players']:
                    cursor.execute('''
                        INSERT INTO real_players 
                        (name, league_id, season_year, data_source, extracted_at, raw_data)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (player, league_id, 2024, url, datetime.now(), str(info)))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("🏀 CRAWLING REAL PLAYER DATA FROM BASKETBALL-BUND")
    print("=" * 55)
    
    # Get real league IDs from export
    league_ids = extract_real_league_ids()
    print(f"📋 Found {len(league_ids)} real league IDs from export")
    
    # Try different seasons
    seasons = [2024, 2023, 2022]
    all_data = {}
    
    # Focus on a few key leagues first
    priority_leagues = league_ids[:3]  # First 3 leagues
    
    for league_id in priority_leagues:
        print(f"\n🎯 Crawling League ID: {league_id}")
        
        for season in seasons:
            print(f"   📅 Season {season}")
            data = crawl_league_with_real_patterns(league_id, season)
            
            if data:
                key = f"{league_id}_{season}"
                all_data[key] = data
                print(f"   ✅ Got data from {len(data)} URLs")
                
                # Show any players found
                total_players = 0
                for url, info in data.items():
                    if 'players' in info:
                        total_players += len(info['players'])
                
                if total_players > 0:
                    print(f"   👥 Total players found: {total_players}")
                    break  # Found data for this league, no need to try other seasons
            else:
                print(f"   ❌ No data for season {season}")
    
    # Save results
    if all_data:
        save_player_data_to_db(all_data)
        print(f"\n💾 SAVED REAL PLAYER DATA TO DATABASE")
        print(f"📊 Total league/season combinations: {len(all_data)}")
        
        # Show summary
        conn = sqlite3.connect('real_player_data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM real_players')
        player_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT league_id) FROM real_players')
        league_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"👥 Total real players in database: {player_count}")
        print(f"🏟️ Leagues with player data: {league_count}")
    else:
        print(f"\n❌ NO PLAYER DATA FOUND")
        print("The league IDs might be from a different season or system")
