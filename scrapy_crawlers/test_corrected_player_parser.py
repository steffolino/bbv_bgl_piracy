#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def test_corrected_player_parser():
    """
    Test corrected player parser based on the data structure we discovered:
    1. Rank, 2. Last Name, 3. First Name, 4. Team, 5. Total Points, 6. Games, 7. PPG
    """
    
    print("🏀 TESTING CORRECTED PLAYER PARSER")
    print("Using saved HTML files to test parser corrections")
    
    # Test files we saved earlier
    test_files = [
        {
            'filename': 'player_stats_statBesteWerferArchiv_250_2010.html',
            'stat_type': 'statBesteWerferArchiv',
            'stat_name': 'Best Scorers',
            'columns': ['rank', 'last_name', 'first_name', 'team', 'total_points', 'games', 'ppg']
        },
        {
            'filename': 'player_stats_statBesteFreiWerferArchiv_250_2010.html',
            'stat_type': 'statBesteFreiWerferArchiv', 
            'stat_name': 'Best Free Throw Shooters',
            'columns': ['rank', 'last_name', 'first_name', 'team', 'ft_made', 'ft_attempted', 'ft_percentage']
        },
        {
            'filename': 'player_stats_statBeste3erWerferArchiv_250_2010.html',
            'stat_type': 'statBeste3erWerferArchiv',
            'stat_name': 'Best 3-Point Shooters', 
            'columns': ['rank', 'last_name', 'first_name', 'team', 'three_made', 'three_attempted', 'three_percentage']
        }
    ]
    
    all_corrected_players = []
    
    for test_file in test_files:
        print(f"\n📊 {test_file['stat_name']}")
        
        try:
            with open(test_file['filename'], 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            players = parse_corrected_player_stats(html_content, test_file)
            
            if players:
                print(f"   ✅ {len(players)} players parsed correctly")
                
                # Show first few players with corrected structure
                for i, player in enumerate(players[:3]):
                    full_name = f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
                    team = player.get('team', 'Unknown')
                    primary_stat = player.get('primary_stat_value', 'N/A')
                    stat_label = player.get('primary_stat_label', 'stat')
                    print(f"      {i+1}. {full_name} ({team}) - {primary_stat} {stat_label}")
                
                if len(players) > 3:
                    print(f"      ... and {len(players)-3} more")
                
                all_corrected_players.extend(players)
                
                # Check for Litzendorf players
                litzendorf_players = [p for p in players if 'litzendorf' in str(p.get('team', '')).lower()]
                if litzendorf_players:
                    print(f"   🌟 {len(litzendorf_players)} Litzendorf players found!")
                    for lp in litzendorf_players:
                        full_name = f"{lp.get('first_name', '')} {lp.get('last_name', '')}".strip()
                        stat_value = lp.get('primary_stat_value', 'N/A')
                        print(f"      🏆 {full_name} - {stat_value}")
            else:
                print(f"   ❌ No players parsed")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
    
    # Save corrected results
    if all_corrected_players:
        save_corrected_player_data(all_corrected_players)
    
    print(f"\n🎯 CORRECTED PARSER TEST COMPLETE")
    print(f"📊 Total corrected players: {len(all_corrected_players)}")
    
    # Breakdown by stat type
    for test_file in test_files:
        stat_players = [p for p in all_corrected_players if p.get('stat_type') == test_file['stat_type']]
        litz_count = len([p for p in stat_players if 'litzendorf' in str(p.get('team', '')).lower()])
        litz_indicator = f" (🌟 {litz_count} Litzendorf)" if litz_count > 0 else ""
        print(f"  {test_file['stat_name']}: {len(stat_players)} players{litz_indicator}")

def parse_corrected_player_stats(html_content, config):
    """
    Parse player statistics with corrected column mapping:
    1=Rank, 2=LastName, 3=FirstName, 4=Team, 5=Stat1, 6=Stat2, 7=Stat3
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
                    'liga_id': '250',
                    'stat_type': config['stat_type'],
                    'stat_category': config['stat_name'],
                    'table_index': table_idx,
                    'row_index': row_idx,
                    'extraction_method': 'corrected statistik.do parser',
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
                
                # Check for Litzendorf
                if 'litzendorf' in player['team'].lower():
                    player['is_litzendorf'] = True
                
                # Skip empty names or invalid data
                if (player['last_name'] and 
                    len(player['last_name']) > 1 and 
                    not player['last_name'].isdigit() and
                    player['team'] and
                    len(player['team']) > 1):
                    
                    players.append(player)
    
    return players

def save_corrected_player_data(players):
    """Save corrected player data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'corrected_player_stats_liga250_2010_{timestamp}.json'
    
    data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'corrected statistik.do player parser',
        'liga_id': '250',
        'season_id': 2010,
        'total_players': len(players),
        'litzendorf_players': [p for p in players if p.get('is_litzendorf')],
        'stat_breakdown': {},
        'players': players
    }
    
    # Stat breakdown
    for stat_type in ['statBesteWerferArchiv', 'statBesteFreiWerferArchiv', 'statBeste3erWerferArchiv']:
        stat_players = [p for p in players if p.get('stat_type') == stat_type]
        data['stat_breakdown'][stat_type] = len(stat_players)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Corrected data saved: {filename}")
    print(f"🌟 Litzendorf players: {len(data['litzendorf_players'])}")

if __name__ == "__main__":
    test_corrected_player_parser()
