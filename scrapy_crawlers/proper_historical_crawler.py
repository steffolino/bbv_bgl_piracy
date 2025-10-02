#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random
import re

def crawl_historical_seasons_properly():
    """
    PROPER historical crawler:
    1. Use Action=106 POST with your EXACT parameters to get league list
    2. Extract liga_id links from the table
    3. Crawl each league with Action=107 for player data
    """
    
    print("🏀 PROPER HISTORICAL SEASONS CRAWLER")
    print("Step 1: Action=106 POST → Get league list")
    print("Step 2: Extract liga_id links from table")
    print("Step 3: Action=107 → Get player data for each league")
    
    # Target seasons (excluding 2018 which you already have)
    target_seasons = [2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023, 2024]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.basketball-bund.net',
        'Referer': 'https://www.basketball-bund.net/index.jsp?Action=106',
    })
    
    all_players = []
    season_summary = {}
    
    for season in target_seasons:
        print(f"\n📅 SEASON {season}")
        
        # STEP 1: Get league list using your EXACT POST parameters
        print(f"  🔍 Step 1: Getting league list (Action=106)")
        leagues = get_league_list(session, season)
        
        if not leagues:
            print(f"  ❌ No leagues found for season {season}")
            continue
        
        print(f"  ✅ Found {len(leagues)} leagues")
        
        # STEP 2: Crawl each league for player data
        season_players = []
        for i, league in enumerate(leagues, 1):
            print(f"  🏀 League {i}/{len(leagues)}: {league['name']} (ID: {league['liga_id']})")
            
            players = crawl_league_players(session, league, season)
            if players:
                season_players.extend(players)
                print(f"    ✅ {len(players)} players")
            else:
                print(f"    ❌ No players")
            
            # Rate limiting
            time.sleep(random.uniform(1, 3))
        
        # Save season results
        if season_players:
            all_players.extend(season_players)
            season_summary[season] = {
                'total_players': len(season_players),
                'total_leagues': len(leagues),
                'leagues': [league['name'] for league in leagues]
            }
            
            # Save individual season file
            save_season_players(season, season_players, leagues)
            
            print(f"  📊 Season {season} complete: {len(season_players)} players from {len(leagues)} leagues")
        
        print(f"  ⏱️  Waiting before next season...")
        time.sleep(random.uniform(3, 6))
    
    # Save comprehensive dataset
    if all_players:
        save_comprehensive_players(all_players, season_summary)
        update_frontend_data(all_players, list(season_summary.keys()))
    
    print(f"\n🎯 CRAWL COMPLETE!")
    print(f"📊 Total players: {len(all_players)}")
    print(f"📅 Seasons: {list(season_summary.keys())}")

def get_league_list(session, season):
    """
    Step 1: Use Action=106 POST with EXACT parameters to get league list
    """
    
    # YOUR EXACT POST DATA
    post_data = {
        'Action': '106',
        'saison_id': str(season),
        'cbSpielklasseFilter': '0',
        'cbAltersklasseFilter': '-3',
        'cbGeschlechtFilter': '0',
        'cbBezirkFilter': '5',
        'cbKreisFilter': '0'
    }
    
    try:
        response = session.post(
            'https://www.basketball-bund.net/index.jsp?Action=106',
            data=post_data,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"    ❌ HTTP {response.status_code}")
            return []
        
        print(f"    ✅ Response: {len(response.text):,} chars")
        
        # Parse HTML to extract league links
        soup = BeautifulSoup(response.text, 'html.parser')
        leagues = extract_league_links(soup, season)
        
        return leagues
        
    except Exception as e:
        print(f"    💥 Error: {str(e)[:100]}")
        return []

def extract_league_links(soup, season):
    """
    Extract liga_id links from the Action=106 response table
    """
    
    leagues = []
    
    # Look for links with liga_id parameter
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link.get('href', '')
        
        # Match liga_id links: Action=107 or Action=108 with liga_id
        if 'liga_id=' in href and ('Action=107' in href or 'Action=108' in href):
            
            # Extract liga_id
            liga_id_match = re.search(r'liga_id=(\d+)', href)
            if liga_id_match:
                liga_id = liga_id_match.group(1)
                
                # Get league name from link text or surrounding context
                league_name = link.get_text(strip=True)
                if not league_name:
                    # Try to get name from parent cell
                    parent = link.find_parent(['td', 'th'])
                    if parent:
                        league_name = parent.get_text(strip=True)
                
                if not league_name:
                    league_name = f"League {liga_id}"
                
                league = {
                    'liga_id': liga_id,
                    'name': league_name,
                    'href': href,
                    'season': season
                }
                
                leagues.append(league)
    
    # Remove duplicates by liga_id
    seen_ids = set()
    unique_leagues = []
    for league in leagues:
        if league['liga_id'] not in seen_ids:
            seen_ids.add(league['liga_id'])
            unique_leagues.append(league)
    
    print(f"    📋 Extracted {len(unique_leagues)} unique leagues from table")
    
    return unique_leagues

def crawl_league_players(session, league, season):
    """
    Step 2: Crawl individual league for player data using Action=107
    """
    
    liga_id = league['liga_id']
    
    # Use Action=107 to get player statistics
    url = f'https://www.basketball-bund.net/index.jsp?Action=107&liga_id={liga_id}&saison_id={season}'
    
    try:
        response = session.get(url, timeout=30)
        
        if response.status_code != 200:
            return []
        
        # Parse players from Action=107 response
        soup = BeautifulSoup(response.text, 'html.parser')
        players = extract_players_from_league(soup, league, season)
        
        return players
        
    except Exception as e:
        print(f"      💥 Error crawling league {liga_id}: {str(e)[:50]}")
        return []

def extract_players_from_league(soup, league, season):
    """
    Extract player data from Action=107 league page
    """
    
    players = []
    
    # Look for player data in tables
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            
            if len(cells) >= 3:  # Minimum columns for player data
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # Skip header rows
                if any(header in cell_texts[0].lower() for header in ['name', 'spieler', 'rang']):
                    continue
                
                # Check if this looks like player data
                if (cell_texts[0] and 
                    len(cell_texts[0]) > 2 and 
                    not cell_texts[0].isdigit() and
                    cell_texts[0] != ''):
                    
                    player = {
                        'name': cell_texts[0],
                        'season_id': season,
                        'league_name': league['name'],
                        'liga_id': league['liga_id'],
                        'extraction_method': 'Action=107',
                        'extracted_at': datetime.now().isoformat()
                    }
                    
                    # Add additional data if available
                    if len(cell_texts) > 1:
                        player['team'] = cell_texts[1]
                    if len(cell_texts) > 2:
                        player['additional_data'] = cell_texts[2:]
                    
                    # Check for Litzendorf
                    full_text = ' '.join(cell_texts).lower()
                    if 'litzendorf' in full_text:
                        player['is_litzendorf'] = True
                    
                    players.append(player)
    
    return players

def save_season_players(season, players, leagues):
    """
    Save individual season data
    """
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'season_{season}_players_{timestamp}.json'
    
    season_data = {
        'season': season,
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'Action=106 → Action=107',
        'total_players': len(players),
        'total_leagues': len(leagues),
        'leagues': leagues,
        'players': players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(season_data, f, indent=2, ensure_ascii=False)
    
    print(f"    💾 Saved: {filename}")

def save_comprehensive_players(all_players, season_summary):
    """
    Save comprehensive multi-season player dataset
    """
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'comprehensive_historical_players_{timestamp}.json'
    
    comprehensive_data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'Historical Action=106 → Action=107 crawl',
        'total_players': len(all_players),
        'seasons_crawled': list(season_summary.keys()),
        'season_summary': season_summary,
        'players': all_players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comprehensive dataset: {filename}")
    print(f"📊 {len(all_players):,} players across {len(season_summary)} seasons")

def update_frontend_data(historical_players, historical_seasons):
    """
    Update frontend data with historical players
    """
    
    try:
        # Load existing 2018 data
        with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        existing_players = existing_data.get('players', [])
        
        # Combine datasets
        all_players = existing_players + historical_players
        all_seasons = sorted(list(set([2018] + historical_seasons)))
        
        # Update frontend file
        updated_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'source': 'Combined 2018 + Historical Action=106→107 data',
            'total_players': len(all_players),
            'seasons_available': all_seasons,
            'total_seasons': len(all_seasons),
            'coverage_span': f"{min(all_seasons)}-{max(all_seasons)}",
            'players': all_players
        }
        
        with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated frontend data:")
        print(f"   📊 {len(all_players):,} total players")
        print(f"   📅 {len(all_seasons)} seasons: {min(all_seasons)}-{max(all_seasons)}")
        print(f"   🏀 Basketball Reference frontend ready!")
        
    except Exception as e:
        print(f"⚠️  Frontend update failed: {e}")

if __name__ == "__main__":
    crawl_historical_seasons_properly()
