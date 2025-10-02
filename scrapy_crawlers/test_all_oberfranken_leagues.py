#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import time
import random

def extract_all_oberfranken_leagues_single_season():
    """Extract ALL leagues from Bezirk Oberfranken for a single season (2018) as test"""
    
    print("🎯 ALL OBERFRANKEN LEAGUES - SINGLE SEASON TEST")
    print("✅ All leagues in Bezirk Oberfranken")
    print("✅ Season 2018/2019 (known to have data)")
    print("✅ Complete player statistics")
    
    # Test with 2018 season (we know it has data)
    saison_id = 2018
    bezirk_oberfranken = 5
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Referer': 'https://www.basketball-bund.net/',
    }
    
    print(f"\n📅 PROCESSING SEASON {saison_id} ({saison_id}/{saison_id+1})")
    
    # Step 1: Discover ALL leagues in Oberfranken
    print(f"\n🔍 DISCOVERING ALL OBERFRANKEN LEAGUES...")
    leagues = discover_all_oberfranken_leagues(saison_id, bezirk_oberfranken, headers)
    
    if not leagues:
        print(f"❌ No leagues found!")
        return
    
    print(f"✅ Found {len(leagues)} leagues in Oberfranken for {saison_id}")
    
    # Show discovered leagues
    for i, league in enumerate(leagues[:10]):  # Show first 10
        print(f"   {i+1}. Liga {league['liga_id']}: {league['league_name']}")
    if len(leagues) > 10:
        print(f"   ... and {len(leagues)-10} more leagues")
    
    # Step 2: Extract data from each league
    all_players = []
    successful_leagues = 0
    
    for league_idx, league in enumerate(leagues):
        liga_id = league.get('liga_id')
        league_name = league.get('league_name', f"League {liga_id}")
        
        print(f"\n🏀 {league_idx+1}/{len(leagues)}: {league_name} (ID: {liga_id})")
        
        # Extract players from this league
        league_players = extract_league_players(liga_id, saison_id, league_name, headers)
        
        if league_players:
            all_players.extend(league_players)
            successful_leagues += 1
            print(f"   ✅ {len(league_players)} players extracted")
        else:
            print(f"   ❌ No players found")
        
        # Rate limiting
        time.sleep(random.uniform(1, 2))
    
    # Save results
    print(f"\n💾 SAVING RESULTS...")
    save_results(all_players, successful_leagues, len(leagues), saison_id)
    
    print(f"\n🏆 OBERFRANKEN EXTRACTION COMPLETE:")
    print(f"   🏀 {successful_leagues}/{len(leagues)} leagues had player data")
    print(f"   👤 {len(all_players)} total players extracted")
    print(f"   📅 Season: {saison_id}/{saison_id+1}")
    
    return all_players

def discover_all_oberfranken_leagues(saison_id, bezirk_filter, headers):
    """Use multiple methods to discover ALL leagues in Oberfranken"""
    
    print("   Method 1: Discovery page...")
    leagues_method1 = discover_via_discovery_page(saison_id, bezirk_filter, headers)
    
    print("   Method 2: Known working IDs...")
    leagues_method2 = discover_via_known_patterns(saison_id, headers)
    
    print("   Method 3: ID range scanning...")
    leagues_method3 = discover_via_id_scanning(saison_id, headers)
    
    # Combine all methods
    all_leagues = {}
    
    for league in leagues_method1 + leagues_method2 + leagues_method3:
        liga_id = league.get('liga_id')
        if liga_id and liga_id not in all_leagues:
            all_leagues[liga_id] = league
    
    result = list(all_leagues.values())
    print(f"   ✅ Total unique leagues found: {len(result)}")
    
    return result

def discover_via_discovery_page(saison_id, bezirk_filter, headers):
    """Method 1: Use the official discovery page"""
    
    url = "https://www.basketball-bund.net/index.jsp"
    params = {
        'Action': '106',
        'viewid': '',
        'saison_id': saison_id,
        'cbSpielklasseFilter': '0',      # All classes
        'cbAltersklasseFilter': '-3',    # All age groups
        'cbGeschlechtFilter': '0',       # All genders
        'cbBezirkFilter': bezirk_filter, # Oberfranken = 5
        'cbKreisFilter': '0'             # All districts
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Save discovery page for analysis
            with open(f'discovery_oberfranken_{saison_id}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            leagues = parse_discovery_page(response.text, saison_id)
            print(f"      Discovery page: {len(leagues)} leagues")
            return leagues
        else:
            print(f"      Discovery page failed: HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print(f"      Discovery page error: {e}")
        return []

def discover_via_known_patterns(saison_id, headers):
    """Method 2: Test known working liga_id patterns"""
    
    # We know 26212 works, so test similar IDs
    base_id = 26212
    test_range = 100  # Test ±100 around known working ID
    
    leagues = []
    
    for offset in range(-test_range, test_range + 1):
        liga_id = base_id + offset
        
        if test_liga_id_exists(liga_id, saison_id, headers):
            leagues.append({
                'liga_id': liga_id,
                'league_name': f"League {liga_id}",
                'saison_id': saison_id,
                'discovery_method': 'pattern_scan'
            })
        
        # Rate limiting
        if offset % 10 == 0:
            time.sleep(0.5)
    
    print(f"      Pattern scanning: {len(leagues)} leagues")
    return leagues

def discover_via_id_scanning(saison_id, headers):
    """Method 3: Scan common liga_id ranges"""
    
    # Common ranges based on basketball-bund.net structure
    ranges_to_test = [
        (26000, 26300),  # Around our known working ID
        (25000, 25300),  # Nearby range
        (27000, 27300),  # Nearby range
    ]
    
    leagues = []
    
    for start, end in ranges_to_test:
        print(f"      Scanning range {start}-{end}...")
        
        for liga_id in range(start, end + 1):
            if test_liga_id_exists(liga_id, saison_id, headers):
                leagues.append({
                    'liga_id': liga_id,
                    'league_name': f"League {liga_id}",
                    'saison_id': saison_id,
                    'discovery_method': 'id_scan'
                })
            
            # Rate limiting
            if liga_id % 20 == 0:
                time.sleep(0.2)
    
    print(f"      ID scanning: {len(leagues)} leagues")
    return leagues

def test_liga_id_exists(liga_id, saison_id, headers):
    """Test if a liga_id has any data for the given season"""
    
    test_url = f"https://www.basketball-bund.net/statistik.do?reqCode=statTeamArchiv&liga_id={liga_id}&saison_id={saison_id}"
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Check if page contains actual data (not just empty structure)
            content = response.text.lower()
            
            # Look for indicators of actual data
            data_indicators = ['oberfranken', 'bezirk', 'liga', 'team', 'mannschaft']
            has_data = any(indicator in content for indicator in data_indicators)
            
            # Also check for table rows indicating teams/data
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')
            has_data_tables = any(len(table.find_all('tr')) > 3 for table in tables)
            
            return has_data or has_data_tables
        
        return False
        
    except Exception:
        return False

def parse_discovery_page(html_content, saison_id):
    """Parse the discovery page to extract league information"""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        leagues = []
        
        # Look for all links with liga_id
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            liga_id_match = re.search(r'liga_id=(\d+)', href)
            
            if liga_id_match:
                liga_id = int(liga_id_match.group(1))
                league_name = link.get_text(strip=True)
                
                # If link text is empty, get context from parent
                if not league_name or len(league_name) < 3:
                    parent = link.parent
                    if parent:
                        league_name = parent.get_text(strip=True)
                
                if league_name and len(league_name) > 3:
                    leagues.append({
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'saison_id': saison_id,
                        'discovery_method': 'discovery_page'
                    })
        
        # Remove duplicates
        unique_leagues = {}
        for league in leagues:
            liga_id = league['liga_id']
            if liga_id not in unique_leagues:
                unique_leagues[liga_id] = league
        
        return list(unique_leagues.values())
        
    except Exception as e:
        print(f"      Parse error: {e}")
        return []

def extract_league_players(liga_id, saison_id, league_name, headers):
    """Extract all players from a specific league"""
    
    endpoints = [
        ('statBesteWerferArchiv', 'Best Shooters'),
        ('statBesteFreiWerferArchiv', 'Best Free Throw Shooters'),  
        ('statBeste3erWerferArchiv', 'Best 3-Point Shooters'),
    ]
    
    all_players = []
    
    for endpoint_code, endpoint_name in endpoints:
        url = f"https://www.basketball-bund.net/statistik.do?reqCode={endpoint_code}&liga_id={liga_id}&saison_id={saison_id}&_top=-1"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                players = parse_players_from_statistics(response.text, liga_id, league_name, saison_id, endpoint_name)
                all_players.extend(players)
                
                if players:
                    print(f"      {endpoint_name}: {len(players)} players")
                
        except Exception as e:
            print(f"      {endpoint_name} error: {e}")
        
        time.sleep(0.3)
    
    return all_players

def parse_players_from_statistics(html_content, liga_id, league_name, saison_id, category):
    """Parse player data from statistics page"""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract actual league name from page title
        actual_league_name = extract_actual_league_name(soup, league_name)
        
        players = []
        
        # Find player data rows
        all_rows = soup.find_all('tr')
        
        for row in all_rows:
            cells = row.find_all('td')
            has_sport_item = any('sportItem' in str(cell) for cell in cells)
            
            if has_sport_item and len(cells) >= 6:
                try:
                    cell_texts = [cell.get_text().replace('\u00a0', ' ').strip() for cell in cells]
                    
                    if len(cell_texts) >= 6:
                        player = {
                            # Identity
                            'first_name': cell_texts[2] if len(cell_texts[2]) > 0 else None,
                            'surname': cell_texts[1] if len(cell_texts[1]) > 0 else None,
                            'name': f"{cell_texts[2]} {cell_texts[1]}" if cell_texts[1] and cell_texts[2] else None,
                            
                            # Location
                            'team': cell_texts[3] if len(cell_texts[3]) > 0 else None,
                            'league': actual_league_name,
                            'league_id': liga_id,
                            'season': f"{saison_id}/{saison_id+1}",
                            'season_id': saison_id,
                            
                            # Statistics
                            'points': int(cell_texts[4]) if cell_texts[4].isdigit() else 0,
                            'games': int(cell_texts[5]) if cell_texts[5].isdigit() else 0,
                            'points_per_game': float(cell_texts[6].replace(',', '.')) if len(cell_texts) >= 7 and cell_texts[6].replace(',', '.').replace('.', '').isdigit() else 0.0,
                            
                            # Category
                            'statistic_category': category,
                            'rank_in_category': int(cell_texts[0].rstrip('.')) if cell_texts[0].rstrip('.').isdigit() else 0,
                            
                            # Metadata
                            'extracted_at': datetime.now().isoformat()
                        }
                        
                        # Create player ID
                        if player['name'] and player['team']:
                            player['player_id'] = f"{player['name']}_{player['team']}".replace(' ', '_').lower()
                        
                        # Only add valid players
                        if player.get('name') and player.get('team') and player.get('points', 0) > 0:
                            players.append(player)
                            
                except Exception:
                    continue
        
        return players
        
    except Exception:
        return []

def extract_actual_league_name(soup, fallback_name):
    """Extract actual league name from page title"""
    
    try:
        title_elements = soup.find_all(['td'], class_=lambda x: x and 'title' in x.lower())
        
        for element in title_elements:
            text = element.get_text(strip=True)
            
            if 'saison' in text.lower() and 'oberfranken' in text.lower():
                # Extract league name after "Saison: YYYY/YYYY) - "
                match = re.search(r'.*?saison:\s*\d{4}/\d{4}\)\s*-\s*(.+)', text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        return fallback_name
        
    except Exception:
        return fallback_name

def save_results(all_players, successful_leagues, total_leagues, saison_id):
    """Save extraction results"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create player identities
    player_identities = {}
    for player in all_players:
        player_id = player.get('player_id')
        if player_id:
            if player_id not in player_identities:
                player_identities[player_id] = {
                    'player_id': player_id,
                    'full_name': player.get('name'),
                    'teams': [player.get('team')],
                    'leagues': [player.get('league')],
                    'seasons': [player.get('season')],
                    'career_records': [player]
                }
            else:
                identity = player_identities[player_id]
                if player.get('team') not in identity['teams']:
                    identity['teams'].append(player.get('team'))
                if player.get('league') not in identity['leagues']:
                    identity['leagues'].append(player.get('league'))
                identity['career_records'].append(player)
    
    # Complete data
    complete_data = {
        'extraction_info': {
            'extracted_at': datetime.now().isoformat(),
            'source': 'All Oberfranken Leagues - Single Season Test',
            'season': f"{saison_id}/{saison_id+1}",
            'successful_leagues': successful_leagues,
            'total_leagues_found': total_leagues,
            'total_players': len(all_players),
            'unique_players': len(player_identities)
        },
        'players': all_players,
        'player_identities': list(player_identities.values())
    }
    
    # Save files
    with open(f'oberfranken_all_leagues_{saison_id}_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(complete_data, f, indent=2, ensure_ascii=False)
    
    with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
        json.dump({'players': all_players}, f, indent=2, ensure_ascii=False)
    
    with open('player_identities.json', 'w', encoding='utf-8') as f:
        json.dump(list(player_identities.values()), f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Saved oberfranken_all_leagues_{saison_id}_{timestamp}.json")
    print(f"   📱 Updated real_players_extracted.json")
    print(f"   🆔 Updated player_identities.json")

if __name__ == "__main__":
    extract_all_oberfranken_leagues_single_season()
