#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def test_litzendorf_player_stats():
    """
    Test player stats endpoints for liga_id=1701 where we know BG Litzendorf plays
    """
    
    print("🏀 TESTING LITZENDORF PLAYER STATS")
    print("Using liga_id=1701 (Bezirksliga Herren) where BG Litzendorf was found")
    
    # Test the player stats endpoints for liga_id=1701
    endpoints = [
        {
            'name': 'Best Scorers',
            'reqCode': 'statBesteWerferArchiv',
            'description': 'Top scoring players (points per game)'
        },
        {
            'name': 'Best Free Throw Shooters', 
            'reqCode': 'statBesteFreiWerferArchiv',
            'description': 'Top free throw percentage players'
        },
        {
            'name': 'Best 3-Point Shooters',
            'reqCode': 'statBeste3erWerferArchiv', 
            'description': 'Top 3-point percentage players'
        }
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    })
    
    all_player_data = []
    
    for endpoint in endpoints:
        print(f"\n📊 {endpoint['name']} - Liga 1701")
        
        # Build URL for liga_id=1701
        url = f"https://www.basketball-bund.net/statistik.do?reqCode={endpoint['reqCode']}&liga_id=1701&saison_id=2010&_top=-1"
        print(f"   🔗 {url}")
        
        try:
            response = session.get(url, timeout=30)
            print(f"   📥 Status: {response.status_code}")
            print(f"   📏 Size: {len(response.text):,} chars")
            
            if response.status_code == 200:
                if 'Keine Einträge gefunden' in response.text:
                    print("   ❌ No entries found")
                elif len(response.text) < 5000:
                    print("   ⚠️  Small response - might be empty") 
                else:
                    print("   ✅ Substantial content found")
                    
                    # Save response
                    filename = f"player_stats_{endpoint['reqCode']}_1701_2010.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"   💾 Saved: {filename}")
                    
                    # Parse players with corrected parser
                    config = {
                        'stat_type': endpoint['reqCode'],
                        'stat_name': endpoint['name']
                    }
                    players = parse_corrected_player_stats_1701(response.text, config)
                    
                    if players:
                        print(f"   🏀 Found {len(players)} players!")
                        
                        # Show first few players
                        for i, player in enumerate(players[:3]):
                            full_name = f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
                            team = player.get('team', 'Unknown')
                            primary_stat = player.get('primary_stat_value', 'N/A')
                            stat_label = player.get('primary_stat_label', 'stat')
                            print(f"      {i+1}. {full_name} ({team}) - {primary_stat} {stat_label}")
                        
                        if len(players) > 3:
                            print(f"      ... and {len(players)-3} more")
                        
                        all_player_data.extend(players)
                        
                        # Check for Litzendorf players  
                        litzendorf_players = [p for p in players if 'litzendorf' in str(p.get('team', '')).lower()]
                        if litzendorf_players:
                            print(f"   🌟 {len(litzendorf_players)} Litzendorf players found!")
                            for lp in litzendorf_players:
                                full_name = f"{lp.get('first_name', '')} {lp.get('last_name', '')}".strip()
                                stat_value = lp.get('primary_stat_value', 'N/A')
                                stat_label = lp.get('primary_stat_label', 'stat')
                                print(f"      🏆 {full_name} - {stat_value} {stat_label}")
                        else:
                            print(f"   ⚪ No Litzendorf players in this stat category")
                    else:
                        print("   ❌ No players parsed")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
        
        time.sleep(2)  # Rate limiting
    
    # Summary
    print(f"\n🎯 LITZENDORF PLAYER STATS TEST COMPLETE")
    print(f"📊 Total players found: {len(all_player_data)}")
    
    if all_player_data:
        # Save results
        save_litzendorf_player_data(all_player_data, endpoints)
        
        # Show breakdown
        for endpoint in endpoints:
            endpoint_players = [p for p in all_player_data if p.get('stat_type') == endpoint['reqCode']]
            litz_count = len([p for p in endpoint_players if 'litzendorf' in str(p.get('team', '')).lower()])
            litz_indicator = f" (🌟 {litz_count} Litzendorf)" if litz_count > 0 else ""
            print(f"  {endpoint['name']}: {len(endpoint_players)} players{litz_indicator}")
    
    return all_player_data

def parse_corrected_player_stats_1701(html_content, config):
    """
    Parse player statistics with corrected column mapping for liga_id=1701
    """
    
    players = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for tables with player data
    tables = soup.find_all('table')
    
    for table_idx, table in enumerate(tables):
        # Look for sportItem cells
        sport_item_cells = table.find_all('td', class_=lambda x: x and 'sportItem' in x)
        
        if not sport_item_cells:
            continue
        
        # Process rows
        rows = table.find_all('tr')
        for row_idx, row in enumerate(rows):
            row_cells = row.find_all('td', class_=lambda x: x and 'sportItem' in x)
            
            if len(row_cells) < 7:  # Need all 7 columns
                continue
            
            cell_texts = [cell.get_text(strip=True) for cell in row_cells]
            
            # Parse with correct column mapping
            if len(cell_texts) >= 7:
                player = {
                    'rank': cell_texts[0],
                    'last_name': cell_texts[1], 
                    'first_name': cell_texts[2],
                    'team': cell_texts[3],
                    'stat_value_1': cell_texts[4],
                    'stat_value_2': cell_texts[5], 
                    'stat_value_3': cell_texts[6],
                    'season_id': 2010,
                    'liga_id': '1701',
                    'league_name': 'Bezirksliga Herren',
                    'stat_type': config['stat_type'],
                    'stat_category': config['stat_name'],
                    'table_index': table_idx,
                    'row_index': row_idx,
                    'extraction_method': 'corrected statistik.do parser liga 1701',
                    'extracted_at': datetime.now().isoformat(),
                    'raw_data': cell_texts
                }
                
                # Add stat-specific labels and primary stat
                if config['stat_type'] == 'statBesteWerferArchiv':
                    # Best Scorers: Total Points, Games, PPG
                    player['total_points'] = cell_texts[4]
                    player['games_played'] = cell_texts[5]
                    player['points_per_game'] = cell_texts[6]
                    player['primary_stat_value'] = cell_texts[6]
                    player['primary_stat_label'] = 'PPG'
                    
                elif config['stat_type'] == 'statBesteFreiWerferArchiv':
                    # Best FT Shooters: FT Made, FT Attempted, FT%
                    player['ft_made'] = cell_texts[4] 
                    player['ft_attempted'] = cell_texts[5]
                    player['ft_percentage'] = cell_texts[6]
                    player['primary_stat_value'] = cell_texts[6]
                    player['primary_stat_label'] = 'FT%'
                    
                elif config['stat_type'] == 'statBeste3erWerferArchiv':
                    # Best 3P Shooters: 3P Made, 3P Attempted, 3P%
                    player['three_point_made'] = cell_texts[4]
                    player['three_point_attempted'] = cell_texts[5] 
                    player['three_point_percentage'] = cell_texts[6]
                    player['primary_stat_value'] = cell_texts[6]
                    player['primary_stat_label'] = '3P%'
                
                # Full name
                player['full_name'] = f"{player['first_name']} {player['last_name']}".strip()
                
                # Check for Litzendorf (case insensitive)
                team_lower = player['team'].lower()
                if 'litzendorf' in team_lower or 'bg litzendorf' in team_lower:
                    player['is_litzendorf'] = True
                    player['team_type'] = 'BG Litzendorf'
                
                # Skip empty names or invalid data
                if (player['last_name'] and 
                    len(player['last_name']) > 1 and 
                    not player['last_name'].isdigit() and
                    player['team'] and
                    len(player['team']) > 1):
                    
                    players.append(player)
    
    return players

def save_litzendorf_player_data(players, endpoints):
    """Save Litzendorf player data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'litzendorf_player_stats_liga1701_2010_{timestamp}.json'
    
    litzendorf_players = [p for p in players if p.get('is_litzendorf')]
    
    data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'corrected statistik.do parser liga 1701',
        'liga_id': '1701',
        'league_name': 'Bezirksliga Herren',
        'season_id': 2010,
        'endpoints_tested': endpoints,
        'total_players': len(players),
        'litzendorf_players_count': len(litzendorf_players),
        'litzendorf_players': litzendorf_players,
        'all_players': players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Litzendorf data saved: {filename}")
    if litzendorf_players:
        print(f"🌟 Litzendorf players found: {len(litzendorf_players)}")
        for lp in litzendorf_players:
            full_name = f"{lp.get('first_name', '')} {lp.get('last_name', '')}".strip()
            stat_value = lp.get('primary_stat_value', 'N/A')
            stat_label = lp.get('primary_stat_label', 'stat')
            print(f"   🏆 {full_name} - {stat_value} {stat_label} ({lp.get('stat_category')})")
    else:
        print("🌟 No Litzendorf players found in this league")

if __name__ == "__main__":
    test_litzendorf_player_stats()
