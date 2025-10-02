#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import time
import random

def extract_all_oberfranken_data():
    """Extract ALL leagues from Bezirk Oberfranken for ALL seasons 2003-2024"""
    
    print("🎯 COMPLETE OBERFRANKEN BASKETBALL DATA EXTRACTION")
    print("✅ All leagues in Bezirk Oberfranken")
    print("✅ All seasons from 2003 to latest available")
    print("✅ All player statistics across all categories")
    
    # Bezirk Oberfranken filter
    bezirk_oberfranken = 5
    
    # All seasons from 2003 to latest
    seasons = list(range(2003, 2025))  # 2003 to 2024
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Referer': 'https://www.basketball-bund.net/',
    }
    
    all_data = []
    total_players = 0
    total_leagues = 0
    
    print(f"\n🗓️ PROCESSING {len(seasons)} SEASONS: {seasons[0]} to {seasons[-1]}")
    
    for season_idx, saison_id in enumerate(seasons):
        print(f"\n📅 SEASON {saison_id} ({season_idx+1}/{len(seasons)}) - {saison_id}/{saison_id+1}")
        
        # Step 1: Discover all leagues in Oberfranken for this season
        leagues = discover_oberfranken_leagues(saison_id, bezirk_oberfranken, headers)
        
        if not leagues:
            print(f"   ❌ No leagues found for season {saison_id}")
            continue
        
        print(f"   📋 Found {len(leagues)} leagues in Oberfranken")
        total_leagues += len(leagues)
        
        # Step 2: Extract data from each league
        season_data = {
            'saison_id': saison_id,
            'season_display': f"{saison_id}/{saison_id+1}",
            'bezirk': 'Oberfranken',
            'leagues': []
        }
        
        for league_idx, league in enumerate(leagues):
            liga_id = league.get('liga_id')
            league_name = league.get('league_name', f"League {liga_id}")
            
            print(f"\n   🏀 {league_idx+1}/{len(leagues)}: {league_name} (ID: {liga_id})")
            
            # Extract all player data from this league
            league_data = extract_league_complete_data(liga_id, saison_id, league_name, headers)
            
            if league_data and (league_data.get('total_players', 0) > 0):
                season_data['leagues'].append(league_data)
                players_count = league_data.get('total_players', 0)
                total_players += players_count
                print(f"      ✅ {players_count} players extracted")
            else:
                print(f"      ❌ No player data")
            
            # Rate limiting
            time.sleep(random.uniform(1, 2))
        
        if season_data['leagues']:
            all_data.append(season_data)
            season_players = sum(l.get('total_players', 0) for l in season_data['leagues'])
            print(f"   🎯 SEASON {saison_id} TOTAL: {len(season_data['leagues'])} leagues, {season_players} players")
        
        # Rate limiting between seasons
        time.sleep(random.uniform(2, 3))
    
    # Save comprehensive results
    save_comprehensive_results(all_data, total_players, total_leagues)
    
    print(f"\n🏆 COMPLETE OBERFRANKEN EXTRACTION FINISHED:")
    print(f"   📅 {len([s for s in all_data if s['leagues']])} seasons with data")
    print(f"   🏀 {total_leagues} total leagues processed")
    print(f"   👤 {total_players} total players extracted")
    
    return all_data

def discover_oberfranken_leagues(saison_id, bezirk_filter, headers):
    """Discover ALL leagues in Bezirk Oberfranken for a specific season"""
    
    print(f"      🔍 Discovering leagues...")
    
    # Discovery URL with Oberfranken filter
    url = "https://www.basketball-bund.net/index.jsp"
    params = {
        'Action': '106',
        'viewid': '',
        'saison_id': saison_id,
        'cbSpielklasseFilter': '0',      # All classes
        'cbAltersklasseFilter': '-3',    # All age groups 
        'cbGeschlechtFilter': '0',       # All genders
        'cbBezirkFilter': bezirk_filter, # Bezirk Oberfranken = 5
        'cbKreisFilter': '0'             # All districts
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return parse_league_discovery_advanced(response.text, saison_id)
        else:
            print(f"         ❌ Discovery failed: HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print(f"         ❌ Discovery error: {e}")
        return []

def parse_league_discovery_advanced(html_content, saison_id):
    """Parse league discovery page to extract all liga_ids and names"""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        leagues = []
        
        # Method 1: Look for links with liga_id parameters
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            
            # Extract liga_id from various link patterns
            liga_id_match = re.search(r'liga_id=(\d+)', href)
            if liga_id_match:
                liga_id = int(liga_id_match.group(1))
                
                # Get league name from link text or parent elements
                league_name = link.get_text(strip=True)
                
                # If link text is empty, look in parent elements
                if not league_name or len(league_name) < 3:
                    parent = link.parent
                    if parent:
                        parent_text = parent.get_text(strip=True)
                        # Extract meaningful text
                        if len(parent_text) > len(league_name):
                            league_name = parent_text
                
                # Only add if we have a meaningful name
                if league_name and len(league_name) > 3 and not league_name.isdigit():
                    leagues.append({
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'saison_id': saison_id,
                        'source_link': href
                    })
        
        # Method 2: Look for table rows with league data
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                # Look for cells that might contain liga_id links
                for cell in cells:
                    cell_links = cell.find_all('a', href=True)
                    for cell_link in cell_links:
                        href = cell_link['href']
                        liga_id_match = re.search(r'liga_id=(\d+)', href)
                        
                        if liga_id_match:
                            liga_id = int(liga_id_match.group(1))
                            
                            # Get league name from the row context
                            row_text = row.get_text(strip=True)
                            # Extract the first meaningful text part
                            text_parts = [part.strip() for part in row_text.split() if part.strip()]
                            league_name = ' '.join(text_parts[:5])  # Take first 5 words
                            
                            if league_name and len(league_name) > 3:
                                leagues.append({
                                    'liga_id': liga_id,
                                    'league_name': league_name,
                                    'saison_id': saison_id,
                                    'source_link': href
                                })
        
        # Remove duplicates based on liga_id
        unique_leagues = {}
        for league in leagues:
            liga_id = league['liga_id']
            if liga_id not in unique_leagues:
                unique_leagues[liga_id] = league
            else:
                # Keep the one with the better name
                if len(league['league_name']) > len(unique_leagues[liga_id]['league_name']):
                    unique_leagues[liga_id] = league
        
        result_leagues = list(unique_leagues.values())
        
        # If no leagues found via links, try alternative method
        if not result_leagues:
            # Look for any numbers that could be liga_ids in the page
            page_text = soup.get_text()
            potential_ids = re.findall(r'\b(\d{5,6})\b', page_text)  # 5-6 digit numbers
            
            for potential_id in set(potential_ids):
                try:
                    liga_id = int(potential_id)
                    # Test if this is a valid liga_id by trying to access it
                    test_url = f"https://www.basketball-bund.net/statistik.do?reqCode=statTeamArchiv&liga_id={liga_id}&saison_id={saison_id}"
                    
                    result_leagues.append({
                        'liga_id': liga_id,
                        'league_name': f"League {liga_id}",
                        'saison_id': saison_id,
                        'source_link': test_url
                    })
                except:
                    continue
        
        print(f"         ✅ {len(result_leagues)} leagues discovered")
        return result_leagues
        
    except Exception as e:
        print(f"         ❌ Parse error: {e}")
        return []

def extract_league_complete_data(liga_id, saison_id, league_name, headers):
    """Extract complete player data from a specific league"""
    
    endpoints = [
        ('statBesteWerferArchiv', 'Best Shooters'),
        ('statBesteFreiWerferArchiv', 'Best Free Throw Shooters'),  
        ('statBeste3erWerferArchiv', 'Best 3-Point Shooters'),
    ]
    
    league_data = {
        'liga_id': liga_id,
        'league_name': league_name,
        'saison_id': saison_id,
        'season_display': f"{saison_id}/{saison_id+1}",
        'players': [],
        'total_players': 0
    }
    
    for endpoint_code, endpoint_name in endpoints:
        url = f"https://www.basketball-bund.net/statistik.do?reqCode={endpoint_code}&liga_id={liga_id}&saison_id={saison_id}&_top=-1"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                players = parse_player_statistics_with_league_info(
                    response.text, endpoint_code, endpoint_name, url, league_data
                )
                
                league_data['players'].extend(players)
                print(f"         {endpoint_name}: {len(players)} players")
                
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"         ❌ {endpoint_name} error: {e}")
    
    league_data['total_players'] = len(league_data['players'])
    return league_data

def parse_player_statistics_with_league_info(html_content, endpoint_code, endpoint_name, source_url, league_info):
    """Parse player statistics with complete league context"""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract actual league name from page title if available
        actual_league_name = extract_league_name_from_title(soup, league_info.get('league_name'))
        
        players = []
        
        # Find player data rows
        all_rows = soup.find_all('tr')
        player_rows = []
        
        for row in all_rows:
            cells = row.find_all('td')
            has_sport_item = any('sportItem' in str(cell) for cell in cells)
            
            if has_sport_item and len(cells) >= 6:
                player_rows.append(row)
        
        # Parse each player
        for row_idx, row in enumerate(player_rows):
            cells = row.find_all('td')
            
            try:
                cell_texts = []
                for cell in cells:
                    text = cell.get_text().replace('\u00a0', ' ').strip()
                    cell_texts.append(text)
                
                if len(cell_texts) >= 6:
                    player_data = {
                        # Identity
                        'player_full_name': f"{cell_texts[2]} {cell_texts[1]}" if len(cell_texts[1]) > 0 and len(cell_texts[2]) > 0 else None,
                        'first_name': cell_texts[2] if len(cell_texts[2]) > 0 else None,
                        'surname': cell_texts[1] if len(cell_texts[1]) > 0 else None,
                        
                        # League & Team (CRITICAL!)
                        'team_name': cell_texts[3] if len(cell_texts[3]) > 0 else None,
                        'league_name': actual_league_name,
                        'league_id': league_info.get('liga_id'),
                        'season': league_info.get('season_display'),
                        'season_id': league_info.get('saison_id'),
                        
                        # Statistics
                        'total_points': int(cell_texts[4]) if cell_texts[4].isdigit() else 0,
                        'games_played': int(cell_texts[5]) if cell_texts[5].isdigit() else 0,
                        'points_per_game': float(cell_texts[6].replace(',', '.')) if len(cell_texts) >= 7 and cell_texts[6].replace(',', '.').replace('.', '').isdigit() else 0.0,
                        
                        # Category & Rank
                        'statistic_category': endpoint_name,
                        'rank_in_category': int(cell_texts[0].rstrip('.')) if cell_texts[0].rstrip('.').isdigit() else 0,
                        
                        # Metadata
                        'source_url': source_url,
                        'extracted_at': datetime.now().isoformat()
                    }
                    
                    # Create player ID
                    if player_data['player_full_name'] and player_data['team_name']:
                        player_data['player_id'] = f"{player_data['player_full_name']}_{player_data['team_name']}".replace(' ', '_').lower()
                    
                    # Only add valid players
                    if (player_data.get('player_full_name') and 
                        player_data.get('team_name') and 
                        player_data.get('total_points', 0) > 0):
                        players.append(player_data)
                        
            except Exception as e:
                continue
        
        return players
        
    except Exception as e:
        return []

def extract_league_name_from_title(soup, fallback_name):
    """Extract actual league name from page title"""
    
    try:
        # Look for title elements
        title_elements = soup.find_all(['td'], class_=lambda x: x and 'title' in x.lower())
        
        for element in title_elements:
            text = element.get_text(strip=True)
            
            if 'saison' in text.lower() and any(term in text.lower() for term in ['liga', 'oberfranken', 'bezirk']):
                # Extract league name after "Saison: YYYY/YYYY) - "
                league_match = re.search(r'.*?saison:\s*\d{4}/\d{4}\)\s*-\s*(.+)', text, re.IGNORECASE)
                if league_match:
                    return league_match.group(1).strip()
                
                # Fallback: take everything after the last hyphen
                if ' - ' in text:
                    return text.split(' - ')[-1].strip()
        
        return fallback_name
        
    except Exception:
        return fallback_name

def save_comprehensive_results(all_data, total_players, total_leagues):
    """Save all results with proper organization"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Flatten all players for frontend
    all_players = []
    all_player_identities = {}
    
    for season_data in all_data:
        for league_data in season_data.get('leagues', []):
            for player in league_data.get('players', []):
                all_players.append(player)
                
                # Build player identity database
                player_id = player.get('player_id')
                if player_id:
                    if player_id not in all_player_identities:
                        all_player_identities[player_id] = {
                            'player_id': player_id,
                            'full_name': player.get('player_full_name'),
                            'teams': [player.get('team_name')],
                            'leagues': [player.get('league_name')],
                            'seasons': [player.get('season')],
                            'career_records': [player]
                        }
                    else:
                        identity = all_player_identities[player_id]
                        if player.get('team_name') not in identity['teams']:
                            identity['teams'].append(player.get('team_name'))
                        if player.get('league_name') not in identity['leagues']:
                            identity['leagues'].append(player.get('league_name'))
                        if player.get('season') not in identity['seasons']:
                            identity['seasons'].append(player.get('season'))
                        identity['career_records'].append(player)
    
    # Complete data file
    complete_data = {
        'extraction_info': {
            'extracted_at': datetime.now().isoformat(),
            'source': 'Complete Bezirk Oberfranken Basketball Data',
            'seasons_covered': f"2003-2024",
            'total_seasons_with_data': len(all_data),
            'total_leagues': total_leagues,
            'total_players': total_players,
            'unique_players': len(all_player_identities)
        },
        'seasons': all_data,
        'all_players': all_players,
        'player_identities': list(all_player_identities.values())
    }
    
    # Save files
    with open(f'oberfranken_complete_data_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(complete_data, f, indent=2, ensure_ascii=False)
    
    with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
        json.dump({'players': all_players}, f, indent=2, ensure_ascii=False)
    
    with open('player_identities.json', 'w', encoding='utf-8') as f:
        json.dump(list(all_player_identities.values()), f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 SAVED COMPLETE OBERFRANKEN DATA:")
    print(f"   📄 oberfranken_complete_data_{timestamp}.json")
    print(f"   📱 real_players_extracted.json ({len(all_players)} players)")
    print(f"   🆔 player_identities.json ({len(all_player_identities)} identities)")

if __name__ == "__main__":
    extract_all_oberfranken_data()
