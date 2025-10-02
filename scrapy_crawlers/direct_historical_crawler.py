#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random

def crawl_historical_direct():
    """
    Direct historical crawl using known liga_id values
    Skip Action=106 discovery - go straight to Action=107
    """
    
    print("🏀 DIRECT HISTORICAL CRAWLER")
    print("Using known liga_id values with Action=107")
    
    # Known liga_ids that should exist across multiple seasons
    # Starting with the one you provided: 1701
    known_liga_ids = [
        1701,  # Your example
        # We can add more as we discover them
    ]
    
    # Target historical seasons
    target_seasons = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023, 2024]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    })
    
    all_players = []
    season_summary = {}
    
    for season in target_seasons:
        print(f"\n📅 SEASON {season}")
        season_players = []
        
        for liga_id in known_liga_ids:
            print(f"  🏀 Liga {liga_id}")
            
            # Direct Action=107 URL
            url = f'https://www.basketball-bund.net/index.jsp?Action=107&liga_id={liga_id}&saison_id={season}'
            
            players = crawl_league_direct(session, url, liga_id, season)
            if players:
                season_players.extend(players)
                print(f"    ✅ {len(players)} players")
            else:
                print(f"    ❌ No players")
            
            # Rate limiting
            time.sleep(random.uniform(1, 3))
        
        if season_players:
            all_players.extend(season_players)
            season_summary[season] = {
                'total_players': len(season_players),
                'total_leagues': len([lid for lid in known_liga_ids if any(p['liga_id'] == str(lid) for p in season_players)]),
                'liga_ids': list(set([p['liga_id'] for p in season_players]))
            }
            
            print(f"  📊 Season {season}: {len(season_players)} players")
            
            # Save individual season
            save_season_data(season, season_players)
        else:
            print(f"  ❌ Season {season}: No data")
        
        time.sleep(random.uniform(2, 4))
    
    # Save comprehensive results
    if all_players:
        save_comprehensive_data(all_players, season_summary)
    
    print(f"\n🎯 DIRECT CRAWL COMPLETE!")
    print(f"📊 Total players: {len(all_players)}")
    print(f"📅 Successful seasons: {list(season_summary.keys())}")

def crawl_league_direct(session, url, liga_id, season):
    """
    Crawl a specific Action=107 URL directly
    """
    
    try:
        print(f"    🔍 GET {url}")
        response = session.get(url, timeout=30)
        
        if response.status_code != 200:
            print(f"      ❌ HTTP {response.status_code}")
            return []
        
        print(f"      ✅ Response: {len(response.text):,} chars")
        
        # Save raw response for debugging
        filename = f'action_107_response_{season}_{liga_id}.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"      💾 Saved: {filename}")
        
        # Parse players from response
        soup = BeautifulSoup(response.text, 'html.parser')
        players = extract_players_from_action_107(soup, liga_id, season)
        
        return players
        
    except Exception as e:
        print(f"      💥 Error: {str(e)[:50]}")
        return []

def extract_players_from_action_107(soup, liga_id, season):
    """
    Extract player data from Action=107 league statistics page
    """
    
    players = []
    
    # Look for player statistics tables
    tables = soup.find_all('table')
    
    for table_idx, table in enumerate(tables):
        rows = table.find_all('tr')
        
        # Skip tables with too few rows (likely headers/navigation)
        if len(rows) < 2:
            continue
        
        header_row = rows[0]
        header_cells = header_row.find_all(['th', 'td'])
        header_texts = [cell.get_text(strip=True).lower() for cell in header_cells]
        
        # Check if this looks like a player statistics table
        player_indicators = ['name', 'spieler', 'punkte', 'spiele', 'team', 'mannschaft']
        if not any(indicator in ' '.join(header_texts) for indicator in player_indicators):
            continue
        
        print(f"      📋 Found player table {table_idx + 1} with {len(rows)-1} data rows")
        
        # Process data rows
        for row_idx, row in enumerate(rows[1:], 1):  # Skip header
            cells = row.find_all(['td', 'th'])
            
            if len(cells) < 2:  # Need at least name and some data
                continue
            
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            # Skip empty or header-like rows
            if not cell_texts[0] or len(cell_texts[0]) < 2:
                continue
            
            if any(header_word in cell_texts[0].lower() for header_word in ['name', 'spieler', 'rang', 'pos']):
                continue
            
            # Create player record
            player = {
                'name': cell_texts[0],
                'season_id': season,
                'liga_id': str(liga_id),
                'table_index': table_idx,
                'row_index': row_idx,
                'extraction_method': 'Action=107 Direct',
                'extracted_at': datetime.now().isoformat(),
                'raw_data': cell_texts
            }
            
            # Try to extract common statistics
            if len(cell_texts) > 1:
                player['team'] = cell_texts[1] if len(cell_texts) > 1 else 'Unknown'
            
            if len(cell_texts) > 2:
                # Try to identify points/games columns
                for i, value in enumerate(cell_texts[2:], 2):
                    if value.isdigit():
                        if i == 2:
                            player['stat_1'] = int(value)
                        elif i == 3:
                            player['stat_2'] = int(value)
                        elif i == 4:
                            player['stat_3'] = int(value)
            
            # Check for Litzendorf
            full_text = ' '.join(cell_texts).lower()
            if 'litzendorf' in full_text:
                player['is_litzendorf'] = True
            
            players.append(player)
    
    return players

def save_season_data(season, players):
    """Save individual season data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'direct_season_{season}_{timestamp}.json'
    
    data = {
        'season': season,
        'method': 'Action=107 Direct',
        'timestamp': datetime.now().isoformat(),
        'total_players': len(players),
        'players': players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"    💾 Saved: {filename}")

def save_comprehensive_data(all_players, season_summary):
    """Save comprehensive multi-season dataset"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'direct_historical_comprehensive_{timestamp}.json'
    
    data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'Direct Action=107 Historical Crawl',
        'total_players': len(all_players),
        'seasons_crawled': list(season_summary.keys()),
        'season_summary': season_summary,
        'players': all_players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comprehensive file: {filename}")

if __name__ == "__main__":
    crawl_historical_direct()
