#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def extract_all_players_properly():
    """Extract players using the correct HTML structure understanding"""
    
    print("🎯 EXTRACTING ALL PLAYERS WITH PROPER PARSING")
    print("Using correct understanding of basketball-bund.net HTML structure")
    
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
    results_summary = []
    
    for endpoint_code, endpoint_name in endpoints:
        print(f"\n📊 {endpoint_name} ({endpoint_code})")
        
        url = f"https://www.basketball-bund.net/statistik.do?reqCode={endpoint_code}&liga_id={liga_id}&saison_id={saison_id}&_top=-1"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                players = parse_player_statistics_page(response.text, endpoint_code, endpoint_name, url)
                
                print(f"   ✅ Extracted {len(players)} players")
                if players:
                    print(f"   📝 Sample: {players[0].get('full_name', 'N/A')} ({players[0].get('team', 'N/A')}) - {players[0].get('points', 0)} pts")
                
                all_players.extend(players)
                results_summary.append({
                    'endpoint': endpoint_code,
                    'name': endpoint_name,
                    'url': url,
                    'players_found': len(players)
                })
                
            else:
                print(f"   ❌ HTTP {response.status_code}")
                results_summary.append({
                    'endpoint': endpoint_code,
                    'name': endpoint_name,
                    'url': url,
                    'error': f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results_summary.append({
                'endpoint': endpoint_code,
                'name': endpoint_name,
                'url': url,
                'error': str(e)
            })
    
    # Remove duplicates and create final dataset
    unique_players = remove_duplicate_players(all_players)
    
    print(f"\n💾 FINAL RESULTS:")
    print(f"   👤 {len(all_players)} total player records")
    print(f"   🔄 {len(unique_players)} unique players")
    print(f"   📊 {len([r for r in results_summary if 'players_found' in r])} successful endpoints")
    
    # Save comprehensive results
    output = {
        'source': 'basketball-bund.net player statistics',
        'extraction_method': 'Proper HTML table parsing with CSS class detection',
        'extracted_at': datetime.now().isoformat(),
        'liga_id': liga_id,
        'saison_id': saison_id,
        'season_display': f"{saison_id}/{saison_id+1}",
        'league_name': 'Bezirksliga Herren (Senioren Oberfranken)',
        'summary': {
            'total_records': len(all_players),
            'unique_players': len(unique_players),
            'endpoints_successful': len([r for r in results_summary if 'players_found' in r])
        },
        'endpoints': results_summary,
        'all_player_records': all_players,
        'unique_players': unique_players
    }
    
    filename = f'extracted_players_proper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Saved to {filename}")
    
    # Also create simplified version for frontend
    frontend_players = []
    for player in unique_players:
        frontend_player = {
            'name': player.get('full_name', ''),
            'team': player.get('team', ''),
            'league': 'Bezirksliga Herren Oberfranken',
            'season': f"{saison_id}/{saison_id+1}",
            'games': player.get('games', 0),
            'points': player.get('points', 0),
            'points_per_game': player.get('average', 0.0),
            'statistics_type': player.get('statistic_type', ''),
            'rank': player.get('rank', 0)
        }
        frontend_players.append(frontend_player)
    
    with open('frontend_players_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(frontend_players, f, indent=2, ensure_ascii=False)
    
    print(f"   📱 Frontend data saved to frontend_players_extracted.json")
    
    return unique_players

def parse_player_statistics_page(html_content, endpoint_code, endpoint_name, source_url):
    """Parse player statistics page with proper understanding of HTML structure"""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        players = []
        
        # Find the main data table by looking for rows with 'sportItem' CSS classes
        rows_with_data = soup.find_all('tr')
        
        player_rows = []
        for row in rows_with_data:
            cells = row.find_all('td')
            
            # Look for rows that contain player data (have sportItemOdd/Even classes)
            if cells and any('sportItem' in cell.get('class', []) for cell in cells):
                player_rows.append(row)
        
        print(f"      Found {len(player_rows)} player data rows")
        
        # Parse each player row
        for row_idx, row in enumerate(player_rows):
            cells = row.find_all('td')
            
            if len(cells) >= 6:  # Minimum expected columns
                try:
                    player_data = {
                        'source_url': source_url,
                        'endpoint': endpoint_code,
                        'statistic_type': endpoint_name,
                        'extracted_at': datetime.now().isoformat(),
                        'row_index': row_idx
                    }
                    
                    # Parse cells based on known structure
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    
                    # Column mapping based on the HTML structure we observed
                    if len(cell_texts) >= 6:
                        # Remove ranking indicators like "18." to get just the number
                        rank_text = cell_texts[0].replace('&nbsp;', '').strip().rstrip('.')
                        try:
                            player_data['rank'] = int(rank_text)
                        except:
                            pass
                        
                        # Names and team
                        player_data['surname'] = cell_texts[1].replace('&nbsp;', '').strip()
                        player_data['first_name'] = cell_texts[2].replace('&nbsp;', '').strip()
                        player_data['team'] = cell_texts[3].replace('&nbsp;', '').strip()
                        
                        # Create full name
                        if player_data['first_name'] and player_data['surname']:
                            player_data['full_name'] = f"{player_data['first_name']} {player_data['surname']}"
                        
                        # Statistics
                        try:
                            player_data['points'] = int(cell_texts[4].replace('&nbsp;', '').strip())
                        except:
                            pass
                        
                        try:
                            player_data['games'] = int(cell_texts[5].replace('&nbsp;', '').strip())
                        except:
                            pass
                        
                        # Average (if available)
                        if len(cell_texts) >= 7:
                            try:
                                avg_text = cell_texts[6].replace('&nbsp;', '').strip().replace(',', '.')
                                player_data['average'] = float(avg_text)
                            except:
                                pass
                    
                    # Only add if we have meaningful data
                    if player_data.get('full_name') and player_data.get('team'):
                        players.append(player_data)
                        
                except Exception as e:
                    # Skip problematic rows but continue processing
                    continue
        
        return players
        
    except Exception as e:
        print(f"      Error parsing page: {e}")
        return []

def remove_duplicate_players(all_players):
    """Remove duplicate players and combine statistics"""
    
    unique_players = {}
    
    for player in all_players:
        full_name = player.get('full_name', '')
        team = player.get('team', '')
        
        # Create unique key
        key = f"{full_name}_{team}".lower()
        
        if key not in unique_players:
            unique_players[key] = player.copy()
            unique_players[key]['statistics'] = [player.get('statistic_type', '')]
        else:
            # Merge statistics
            existing = unique_players[key]
            existing['statistics'].append(player.get('statistic_type', ''))
            
            # Keep the best ranking or highest points
            if player.get('points', 0) > existing.get('points', 0):
                existing.update(player)
                existing['statistics'] = list(set(existing['statistics']))
    
    return list(unique_players.values())

if __name__ == "__main__":
    extract_all_players_properly()
