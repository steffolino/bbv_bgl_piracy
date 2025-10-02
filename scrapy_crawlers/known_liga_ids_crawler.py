#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random

def crawl_known_liga_ids():
    """
    Use known liga_ids from your 2010 example and test them across seasons
    """
    
    print("🏀 KNOWN LIGA_IDS HISTORICAL CRAWLER")
    print("Using liga_ids from your 2010 Oberfranken example")
    
    # Known liga_ids from your 2010 example
    known_liga_ids = [
        {'liga_id': '3340', 'name': 'Senioren Ü45'},
        {'liga_id': '263', 'name': 'Senioren Ü40 (männlich)'},
        {'liga_id': '8025', 'name': 'Senioreninnen Ü40'},
        {'liga_id': '261', 'name': 'Senioren Ü35'},
        {'liga_id': '1701', 'name': 'Bezirksliga Herren'},
        {'liga_id': '256', 'name': 'Bezirkspokal Herren'},
        {'liga_id': '248', 'name': 'Bezirksliga Damen A'},
        {'liga_id': '2659', 'name': 'Bezirksliga Damen B'},
        {'liga_id': '6964', 'name': 'Bezirksliga Damen Meisterschaft'},
        {'liga_id': '697', 'name': 'Bezirkspokal Damen'}
    ]
    
    # Target seasons
    target_seasons = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023, 2024]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    })
    
    all_players = []
    season_summary = {}
    
    for season in target_seasons:
        print(f"\n📅 SEASON {season}")
        season_players = []
        working_leagues = []
        
        for liga_info in known_liga_ids:
            liga_id = liga_info['liga_id']
            league_name = liga_info['name']
            
            print(f"  🏀 Testing {league_name} (ID: {liga_id})")
            
            # Direct Action=107 URL
            url = f'https://www.basketball-bund.net/index.jsp?Action=107&liga_id={liga_id}&saison_id={season}'
            
            players = crawl_league_direct(session, url, liga_id, league_name, season)
            if players:
                season_players.extend(players)
                working_leagues.append(liga_info)
                print(f"    ✅ {len(players)} players")
            else:
                print(f"    ❌ No players")
            
            # Rate limiting
            time.sleep(random.uniform(1, 2))
        
        # Save season results
        if season_players:
            all_players.extend(season_players)
            season_summary[season] = {
                'total_players': len(season_players),
                'working_leagues': len(working_leagues),
                'league_names': [lg['name'] for lg in working_leagues]
            }
            
            save_season_data(season, season_players, working_leagues)
            print(f"  📊 Season {season}: {len(season_players)} players from {len(working_leagues)} leagues")
        else:
            print(f"  ❌ Season {season}: No data found")
        
        time.sleep(random.uniform(2, 4))
    
    # Save comprehensive results
    if all_players:
        save_comprehensive_data(all_players, season_summary)
        update_frontend_data(all_players, list(season_summary.keys()))
    
    print(f"\n🎯 KNOWN LIGA_IDS CRAWL COMPLETE!")
    print(f"📊 Total players: {len(all_players)}")
    print(f"📅 Successful seasons: {list(season_summary.keys())}")
    
    # Summary by season
    for season, summary in season_summary.items():
        print(f"  {season}: {summary['total_players']} players, {summary['working_leagues']} leagues")

def crawl_league_direct(session, url, liga_id, league_name, season):
    """
    Crawl a specific Action=107 URL directly
    """
    
    try:
        response = session.get(url, timeout=30)
        
        if response.status_code != 200:
            return []
        
        # Quick check for meaningful content
        if len(response.text) < 10000:  # Too small, likely error page
            return []
        
        # Save raw response for debugging
        filename = f'direct_action_107_{season}_{liga_id}.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Parse players from response
        soup = BeautifulSoup(response.text, 'html.parser')
        players = extract_players_from_action_107(soup, liga_id, league_name, season)
        
        return players
        
    except Exception as e:
        print(f"      💥 Error: {str(e)[:50]}")
        return []

def extract_players_from_action_107(soup, liga_id, league_name, season):
    """
    Extract player data from Action=107 league statistics page
    """
    
    players = []
    
    # Look for player statistics tables
    tables = soup.find_all('table')
    
    for table_idx, table in enumerate(tables):
        rows = table.find_all('tr')
        
        if len(rows) < 2:
            continue
        
        # Check if this looks like a player statistics table
        header_found = False
        header_row = None
        
        for row in rows[:3]:  # Check first few rows for headers
            cells = row.find_all(['th', 'td'])
            cell_texts = [cell.get_text(strip=True).lower() for cell in cells]
            
            if any(indicator in ' '.join(cell_texts) for indicator in ['spieler', 'name', 'punkte', 'spiele']):
                header_found = True
                header_row = row
                break
        
        if not header_found:
            continue
        
        # Find the index where data rows start
        data_start_idx = rows.index(header_row) + 1
        
        for row_idx, row in enumerate(rows[data_start_idx:], 1):
            cells = row.find_all(['td', 'th'])
            
            if len(cells) < 2:
                continue
            
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            # Skip empty rows
            if not cell_texts[0] or len(cell_texts[0]) < 2:
                continue
            
            # Skip header-like rows that might appear in data
            if any(header_word in cell_texts[0].lower() for header_word in ['name', 'spieler', 'rang', 'pos', 'platz']):
                continue
            
            # Skip numeric-only first cells (rankings)
            if cell_texts[0].isdigit():
                continue
            
            # Create player record
            player = {
                'name': cell_texts[0],
                'season_id': season,
                'liga_id': str(liga_id),
                'league_name': league_name,
                'table_index': table_idx,
                'row_index': row_idx,
                'extraction_method': 'Direct Action=107 (Known IDs)',
                'extracted_at': datetime.now().isoformat(),
                'raw_data': cell_texts
            }
            
            # Extract team and statistics
            if len(cell_texts) > 1:
                player['team'] = cell_texts[1]
            
            # Extract numeric values
            stats = {}
            for i, value in enumerate(cell_texts[2:], 2):
                clean_value = value.replace(',', '.').strip()
                if clean_value.replace('.', '').isdigit():
                    stats[f'stat_{i-1}'] = clean_value
            
            if stats:
                player['statistics'] = stats
            
            # Check for Litzendorf
            full_text = ' '.join(cell_texts).lower()
            if 'litzendorf' in full_text:
                player['is_litzendorf'] = True
                player['team_type'] = 'BG Litzendorf'
            
            players.append(player)
    
    return players

def save_season_data(season, players, working_leagues):
    """Save individual season data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'known_ids_season_{season}_{timestamp}.json'
    
    data = {
        'season': season,
        'method': 'Direct Action=107 with Known Liga IDs',
        'timestamp': datetime.now().isoformat(),
        'total_players': len(players),
        'working_leagues': working_leagues,
        'players': players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"    💾 Saved: {filename}")

def save_comprehensive_data(all_players, season_summary):
    """Save comprehensive multi-season dataset"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'known_ids_comprehensive_{timestamp}.json'
    
    data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'Direct Action=107 with Known Liga IDs',
        'total_players': len(all_players),
        'seasons_crawled': list(season_summary.keys()),
        'season_summary': season_summary,
        'players': all_players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comprehensive file: {filename}")

def update_frontend_data(historical_players, historical_seasons):
    """Update frontend data with historical players"""
    try:
        # Load existing 2018 data
        with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        existing_players = existing_data.get('players', [])
        
        # Convert historical players to frontend format
        frontend_players = []
        for player in historical_players:
            frontend_player = {
                'name': player['name'],
                'team': player.get('team', 'Unknown'),
                'season_id': player['season_id'],
                'league': player['league_name'],
                'liga_id': player['liga_id'],
                'endpoint': 'Action=107',
                'source': 'historical_crawl',
                'extracted_at': player['extracted_at']
            }
            
            # Add Litzendorf flag
            if player.get('is_litzendorf'):
                frontend_player['is_litzendorf'] = True
            
            frontend_players.append(frontend_player)
        
        # Combine datasets
        all_players = existing_players + frontend_players
        all_seasons = sorted(list(set([2018] + historical_seasons)))
        
        # Update frontend file
        updated_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'source': 'Combined 2018 + Known Liga IDs Historical',
            'total_players': len(all_players),
            'seasons_available': all_seasons,
            'total_seasons': len(all_seasons),
            'coverage_span': f"{min(all_seasons)}-{max(all_seasons)}",
            'players': all_players
        }
        
        with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated frontend data: {len(all_players):,} total players")
        print(f"📅 Coverage: {min(all_seasons)}-{max(all_seasons)} ({len(all_seasons)} seasons)")
        
    except Exception as e:
        print(f"⚠️  Frontend update failed: {e}")

if __name__ == "__main__":
    crawl_known_liga_ids()
