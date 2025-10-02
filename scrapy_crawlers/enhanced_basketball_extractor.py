#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def extract_comprehensive_player_data():
    """Extract players with league names and player identity preservation"""
    
    print("🎯 COMPREHENSIVE PLAYER EXTRACTION")
    print("✅ Extracting league names from page titles")
    print("✅ Preserving player identities for historical tracking")
    print("✅ Preparing data for player profiles")
    
    liga_id = 26212
    saison_id = 2018
    
    # Player statistics endpoints
    endpoints = [
        ('statBesteWerferArchiv', 'Best Shooters'),
        ('statBesteFreiWerferArchiv', 'Best Free Throw Shooters'),  
        ('statBeste3erWerferArchiv', 'Best 3-Point Shooters'),
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Referer': 'https://www.basketball-bund.net/',
    }
    
    all_players = []
    league_info = None
    
    for endpoint_code, endpoint_name in endpoints:
        print(f"\n📊 {endpoint_name} ({endpoint_code})")
        
        url = f"https://www.basketball-bund.net/statistik.do?reqCode={endpoint_code}&liga_id={liga_id}&saison_id={saison_id}&_top=-1"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Extract league info from first successful page
                if not league_info:
                    league_info = extract_league_info(response.text, liga_id, saison_id)
                    print(f"   🏀 League: {league_info.get('league_name', 'Unknown')}")
                    print(f"   📅 Season: {league_info.get('season_display', 'Unknown')}")
                
                players = parse_player_statistics_comprehensive(
                    response.text, endpoint_code, endpoint_name, url, league_info
                )
                
                print(f"   ✅ Extracted {len(players)} players")
                if players:
                    sample = players[0]
                    print(f"   📝 Sample: {sample.get('player_full_name', 'N/A')} ({sample.get('team_name', 'N/A')}) - {sample.get('total_points', 0)} pts")
                
                all_players.extend(players)
                
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Create player identity database for historical tracking
    player_identities = create_player_identity_database(all_players)
    
    # Generate comprehensive output
    final_data = create_comprehensive_output(all_players, player_identities, league_info)
    
    print(f"\n💾 FINAL RESULTS:")
    print(f"   👤 {len(all_players)} total player records")
    print(f"   🆔 {len(player_identities)} unique player identities")
    print(f"   🏀 League: {final_data.get('league_info', {}).get('league_name', 'Unknown')}")
    print(f"   📊 {len(set(p.get('statistic_category') for p in all_players))} statistic categories")
    
    return final_data

def extract_league_info(html_content, liga_id, saison_id):
    """Extract league name and season info from page title"""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for page title with league information
        title_elements = soup.find_all(['td', 'div', 'h1', 'h2'], class_=lambda x: x and 'title' in x.lower())
        
        for element in title_elements:
            text = element.get_text(strip=True)
            
            # Look for patterns like "Bezirksliga Herren (Senioren Oberfranken)"
            if 'saison' in text.lower() and any(term in text.lower() for term in ['liga', 'oberfranken', 'bezirk']):
                # Extract season
                season_match = re.search(r'(\d{4}/\d{4})', text)
                season_display = season_match.group(1) if season_match else f"{saison_id}/{saison_id+1}"
                
                # Extract league name - everything after "Saison: YYYY/YYYY) - "
                league_match = re.search(r'.*?saison:\s*\d{4}/\d{4}\)\s*-\s*(.+)', text, re.IGNORECASE)
                if league_match:
                    league_name = league_match.group(1).strip()
                else:
                    # Fallback: look for text patterns
                    if 'oberfranken' in text.lower():
                        league_name = "Bezirksliga Herren (Senioren Oberfranken)"
                    else:
                        league_name = text.split('-')[-1].strip()
                
                return {
                    'liga_id': liga_id,
                    'saison_id': saison_id,
                    'season_display': season_display,
                    'league_name': league_name,
                    'full_title': text
                }
        
        # Fallback if no title found
        return {
            'liga_id': liga_id,
            'saison_id': saison_id,
            'season_display': f"{saison_id}/{saison_id+1}",
            'league_name': f"League {liga_id}",
            'full_title': None
        }
        
    except Exception as e:
        print(f"      Warning: Could not extract league info: {e}")
        return {
            'liga_id': liga_id,
            'saison_id': saison_id,
            'season_display': f"{saison_id}/{saison_id+1}",
            'league_name': f"League {liga_id}",
            'full_title': None
        }

def parse_player_statistics_comprehensive(html_content, endpoint_code, endpoint_name, source_url, league_info):
    """Parse with comprehensive player identity and league data"""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        players = []
        
        # Find all table rows containing player data
        all_rows = soup.find_all('tr')
        
        player_rows = []
        for row in all_rows:
            cells = row.find_all('td')
            
            # Look for rows with sportItem classes (player data rows)
            has_sport_item = any('sportItem' in str(cell) for cell in cells)
            
            if has_sport_item and len(cells) >= 6:
                player_rows.append(row)
        
        print(f"      Found {len(player_rows)} player data rows")
        
        # Parse each player row
        for row_idx, row in enumerate(player_rows):
            cells = row.find_all('td')
            
            try:
                # Extract cell text and clean it
                cell_texts = []
                for cell in cells:
                    text = cell.get_text()
                    text = text.replace('\u00a0', ' ')  # Replace non-breaking space
                    text = text.strip()
                    cell_texts.append(text)
                
                if len(cell_texts) >= 6:
                    # Create comprehensive player record
                    player_data = {
                        # Source information
                        'source_url': source_url,
                        'endpoint_code': endpoint_code,
                        'statistic_category': endpoint_name,
                        'extracted_at': datetime.now().isoformat(),
                        'row_index': row_idx,
                        
                        # League information (IMPORTANT!)
                        'liga_id': league_info.get('liga_id'),
                        'league_name': league_info.get('league_name'),
                        'season_id': league_info.get('saison_id'),
                        'season_display': league_info.get('season_display'),
                        
                        # Player identity (CRITICAL for profiles!)
                        'rank_in_category': None,
                        'surname': None,
                        'first_name': None,
                        'player_full_name': None,
                        'team_name': None,
                        
                        # Statistics
                        'total_points': 0,
                        'games_played': 0,
                        'points_per_game': 0.0,
                        
                        # Raw data for debugging
                        'raw_cells': cell_texts
                    }
                    
                    # Parse based on known column structure
                    # Column 0: Rank (like "1.", "2.")
                    rank_text = cell_texts[0].rstrip('.')
                    try:
                        player_data['rank_in_category'] = int(rank_text)
                    except:
                        pass
                    
                    # Column 1: Surname
                    if len(cell_texts[1]) > 0:
                        player_data['surname'] = cell_texts[1]
                    
                    # Column 2: First name  
                    if len(cell_texts[2]) > 0:
                        player_data['first_name'] = cell_texts[2]
                    
                    # Column 3: Team
                    if len(cell_texts[3]) > 0:
                        player_data['team_name'] = cell_texts[3]
                    
                    # Column 4: Points
                    try:
                        player_data['total_points'] = int(cell_texts[4])
                    except:
                        pass
                    
                    # Column 5: Games
                    try:
                        player_data['games_played'] = int(cell_texts[5])
                    except:
                        pass
                    
                    # Column 6: Average (if exists)
                    if len(cell_texts) >= 7:
                        try:
                            avg_text = cell_texts[6].replace(',', '.')
                            player_data['points_per_game'] = float(avg_text)
                        except:
                            pass
                    
                    # Create full name for player identity
                    if player_data['first_name'] and player_data['surname']:
                        player_data['player_full_name'] = f"{player_data['first_name']} {player_data['surname']}"
                    
                    # Create unique player identifier
                    if player_data['player_full_name'] and player_data['team_name']:
                        player_data['player_id'] = f"{player_data['player_full_name']}_{player_data['team_name']}".replace(' ', '_').lower()
                    
                    # Only add if we have valid player data
                    if (player_data.get('player_full_name') and 
                        player_data.get('team_name') and 
                        player_data.get('total_points', 0) > 0):
                        players.append(player_data)
                
            except Exception as e:
                # Skip problematic rows but continue
                continue
        
        return players
        
    except Exception as e:
        print(f"      Error parsing HTML: {e}")
        return []

def create_player_identity_database(all_players):
    """Create database of unique player identities for historical tracking"""
    
    player_identities = {}
    
    for player in all_players:
        player_id = player.get('player_id')
        if not player_id:
            continue
        
        if player_id not in player_identities:
            # Create new player identity
            player_identities[player_id] = {
                'player_id': player_id,
                'full_name': player.get('player_full_name'),
                'first_name': player.get('first_name'),
                'surname': player.get('surname'),
                'current_team': player.get('team_name'),
                'teams_played_for': [player.get('team_name')],
                'leagues_played_in': [player.get('league_name')],
                'seasons_active': [player.get('season_display')],
                'statistics_categories': [player.get('statistic_category')],
                'total_career_points': player.get('total_points', 0),
                'total_career_games': player.get('games_played', 0),
                'best_season_ppg': player.get('points_per_game', 0.0),
                'career_records': [player]
            }
        else:
            # Update existing player identity
            identity = player_identities[player_id]
            
            # Add new team if different
            if player.get('team_name') not in identity['teams_played_for']:
                identity['teams_played_for'].append(player.get('team_name'))
            
            # Add new league if different  
            if player.get('league_name') not in identity['leagues_played_in']:
                identity['leagues_played_in'].append(player.get('league_name'))
            
            # Add new season if different
            if player.get('season_display') not in identity['seasons_active']:
                identity['seasons_active'].append(player.get('season_display'))
            
            # Add new statistic category
            if player.get('statistic_category') not in identity['statistics_categories']:
                identity['statistics_categories'].append(player.get('statistic_category'))
            
            # Update career totals (for multiple categories in same season)
            if player.get('total_points', 0) > identity['total_career_points']:
                identity['total_career_points'] = player.get('total_points', 0)
            
            if player.get('games_played', 0) > identity['total_career_games']:
                identity['total_career_games'] = player.get('games_played', 0)
            
            if player.get('points_per_game', 0.0) > identity['best_season_ppg']:
                identity['best_season_ppg'] = player.get('points_per_game', 0.0)
            
            # Add this record to career history
            identity['career_records'].append(player)
    
    return player_identities

def create_comprehensive_output(all_players, player_identities, league_info):
    """Create comprehensive output with league names and player identities"""
    
    # Frontend-compatible player list
    frontend_players = []
    for player in all_players:
        frontend_player = {
            # Player identity (CRITICAL)
            'player_id': player.get('player_id'),
            'name': player.get('player_full_name'),
            'first_name': player.get('first_name'),
            'surname': player.get('surname'),
            
            # Team & League (WITH NAMES!)
            'team': player.get('team_name'),
            'league': player.get('league_name'),
            'league_id': player.get('liga_id'),
            'season': player.get('season_display'),
            'season_id': player.get('season_id'),
            
            # Statistics
            'games': player.get('games_played', 0),
            'points': player.get('total_points', 0),
            'points_per_game': player.get('points_per_game', 0.0),
            'statistic_category': player.get('statistic_category'),
            'rank_in_category': player.get('rank_in_category', 0),
            
            # Metadata
            'extracted_at': player.get('extracted_at'),
            'source_url': player.get('source_url')
        }
        frontend_players.append(frontend_player)
    
    # Comprehensive output
    output = {
        'extraction_info': {
            'extracted_at': datetime.now().isoformat(),
            'source': 'basketball-bund.net comprehensive extraction',
            'method': 'League name extraction + Player identity preservation',
            'total_records': len(all_players),
            'unique_players': len(player_identities)
        },
        
        # League information (IMPORTANT!)
        'league_info': league_info,
        
        # Player data for frontend
        'players': frontend_players,
        
        # Player identity database for profiles/history
        'player_identities': list(player_identities.values()),
        
        # Summary statistics
        'summary': {
            'total_player_records': len(all_players),
            'unique_players': len(player_identities),
            'teams': list(set(p.get('team_name') for p in all_players if p.get('team_name'))),
            'statistic_categories': list(set(p.get('statistic_category') for p in all_players)),
            'season': league_info.get('season_display') if league_info else None,
            'league': league_info.get('league_name') if league_info else None
        }
    }
    
    # Save comprehensive data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Main comprehensive file
    filename = f'comprehensive_player_data_{timestamp}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"   ✅ Saved comprehensive data to {filename}")
    
    # Frontend data file (for the Vue.js app)
    with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
        json.dump({'players': frontend_players}, f, indent=2, ensure_ascii=False)
    print(f"   📱 Updated frontend data: real_players_extracted.json")
    
    # Player identities file (for player profiles)
    with open('player_identities.json', 'w', encoding='utf-8') as f:
        json.dump(list(player_identities.values()), f, indent=2, ensure_ascii=False)
    print(f"   🆔 Saved player identities: player_identities.json")
    
    return output

if __name__ == "__main__":
    result = extract_comprehensive_player_data()
