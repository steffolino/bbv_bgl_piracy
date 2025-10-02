#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def extract_players_fixed():
    """Extract players with corrected CSS class detection"""
    
    print("🎯 EXTRACTING PLAYERS WITH FIXED CSS DETECTION")
    
    # Use the saved HTML file to test locally first
    html_files = [
        ('player_stats_statBesteWerferArchiv_2018.html', 'statBesteWerferArchiv', 'Best Shooters'),
        ('player_stats_statBesteFreiWerferArchiv_2018.html', 'statBesteFreiWerferArchiv', 'Best Free Throw Shooters'),
        ('player_stats_statBeste3erWerferArchiv_2018.html', 'statBeste3erWerferArchiv', 'Best 3-Point Shooters')
    ]
    
    all_players = []
    
    for filename, endpoint_code, endpoint_name in html_files:
        print(f"\n📊 {endpoint_name} ({filename})")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            players = parse_player_table_fixed(html_content, endpoint_code, endpoint_name)
            
            print(f"   ✅ Extracted {len(players)} players")
            if players:
                print(f"   📝 Sample: {players[0].get('full_name', 'N/A')} ({players[0].get('team', 'N/A')}) - {players[0].get('points', 0)} pts")
                print(f"   📝 Last: {players[-1].get('full_name', 'N/A')} ({players[-1].get('team', 'N/A')}) - {players[-1].get('points', 0)} pts")
            
            all_players.extend(players)
            
        except Exception as e:
            print(f"   ❌ Error reading {filename}: {e}")
    
    # Save results
    print(f"\n💾 TOTAL EXTRACTED: {len(all_players)} players")
    
    if all_players:
        # Save detailed results
        output = {
            'source': 'basketball-bund.net player statistics',
            'extraction_method': 'Fixed CSS class detection',
            'extracted_at': datetime.now().isoformat(),
            'total_players': len(all_players),
            'players': all_players
        }
        
        with open('players_extracted_fixed.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        # Create frontend-compatible format
        frontend_players = []
        for player in all_players:
            frontend_player = {
                'name': player.get('full_name', ''),
                'team': player.get('team', ''),
                'league': 'Bezirksliga Herren Oberfranken',
                'season': '2018/2019',
                'games': player.get('games', 0),
                'points': player.get('points', 0),
                'points_per_game': player.get('average', 0.0),
                'statistic_type': player.get('statistic_type', ''),
                'rank': player.get('rank', 0)
            }
            frontend_players.append(frontend_player)
        
        with open('real_players_extracted_final.json', 'w', encoding='utf-8') as f:
            json.dump(frontend_players, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Saved detailed data to players_extracted_fixed.json")
        print(f"   📱 Saved frontend data to real_players_extracted_final.json")
        
        # Show summary
        teams = set(p.get('team', '') for p in all_players)
        print(f"   🏀 {len(teams)} different teams")
        print(f"   📊 Statistics types: {set(p.get('statistic_type', '') for p in all_players)}")
    
    return all_players

def parse_player_table_fixed(html_content, endpoint_code, endpoint_name):
    """Parse with better logic for finding player data rows"""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        players = []
        
        # Find all table rows
        all_rows = soup.find_all('tr')
        
        # Look for rows containing 'sportItem' in any cell's class attribute
        player_rows = []
        for row in all_rows:
            cells = row.find_all('td')
            
            # Check if any cell has sportItem class (in any format)
            has_sport_item = False
            for cell in cells:
                class_attr = cell.get('class', [])
                class_str = str(class_attr) + ' ' + cell.get('class', '')
                
                # Check for sportItem in class string (handles both list and string formats)
                if 'sportItem' in str(cell):
                    has_sport_item = True
                    break
            
            if has_sport_item and len(cells) >= 6:
                player_rows.append(row)
        
        print(f"      Found {len(player_rows)} rows with sportItem classes")
        
        # Parse each player row
        for row_idx, row in enumerate(player_rows):
            cells = row.find_all('td')
            
            try:
                player_data = {
                    'endpoint': endpoint_code,
                    'statistic_type': endpoint_name,
                    'extracted_at': datetime.now().isoformat(),
                    'row_index': row_idx
                }
                
                # Extract cell text
                cell_texts = []
                for cell in cells:
                    # Clean up the cell text (remove &nbsp; and extra whitespace)
                    text = cell.get_text()
                    text = text.replace('\u00a0', ' ')  # Replace non-breaking space
                    text = text.strip()
                    cell_texts.append(text)
                
                if len(cell_texts) >= 6:
                    # Parse based on known column structure
                    # Column 0: Rank (like "1.", "2.")
                    rank_text = cell_texts[0].rstrip('.')
                    try:
                        player_data['rank'] = int(rank_text)
                    except:
                        pass
                    
                    # Column 1: Surname
                    player_data['surname'] = cell_texts[1]
                    
                    # Column 2: First name  
                    player_data['first_name'] = cell_texts[2]
                    
                    # Column 3: Team
                    player_data['team'] = cell_texts[3]
                    
                    # Column 4: Points
                    try:
                        player_data['points'] = int(cell_texts[4])
                    except:
                        player_data['points'] = 0
                    
                    # Column 5: Games
                    try:
                        player_data['games'] = int(cell_texts[5])
                    except:
                        player_data['games'] = 0
                    
                    # Column 6: Average (if exists)
                    if len(cell_texts) >= 7:
                        try:
                            avg_text = cell_texts[6].replace(',', '.')
                            player_data['average'] = float(avg_text)
                        except:
                            player_data['average'] = 0.0
                    
                    # Create full name
                    if player_data['first_name'] and player_data['surname']:
                        player_data['full_name'] = f"{player_data['first_name']} {player_data['surname']}"
                    
                    # Only add if we have valid player data
                    if (player_data.get('full_name') and 
                        player_data.get('team') and 
                        player_data.get('points', 0) > 0):
                        players.append(player_data)
                
            except Exception as e:
                # Skip problematic rows
                continue
        
        return players
        
    except Exception as e:
        print(f"      Error parsing HTML: {e}")
        return []

if __name__ == "__main__":
    extract_players_fixed()
