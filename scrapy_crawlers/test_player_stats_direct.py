#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def test_player_statistics_directly():
    """Test player statistics URLs directly for season 2018 where we know data exists"""
    
    print("🎯 TESTING PLAYER STATISTICS FOR 2018 SEASON")
    print("Using known working liga_id=26212, saison_id=2018")
    
    liga_id = 26212
    saison_id = 2018
    
    # Player statistics endpoints from user's examples
    player_endpoints = [
        'statBesteWerferArchiv',         # Best shooters
        'statBesteFreiWerferArchiv',     # Best free throw shooters  
        'statBeste3erWerferArchiv',      # Best 3-point shooters
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Referer': 'https://www.basketball-bund.net/',
    }
    
    results = []
    
    for endpoint in player_endpoints:
        print(f"\n📊 TESTING: {endpoint}")
        
        url = f"https://www.basketball-bund.net/statistik.do?reqCode={endpoint}&liga_id={liga_id}&saison_id={saison_id}&_top=-1"
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"   Status: {response.status_code}")
            print(f"   Content Length: {len(response.text)}")
            
            if response.status_code == 200:
                # Save full HTML for inspection
                filename = f'player_stats_{endpoint}_{saison_id}.html'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"   💾 Saved HTML: {filename}")
                
                # Parse and look for player data
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for any tables
                tables = soup.find_all('table')
                print(f"   📊 Found {len(tables)} tables")
                
                # Check content for player indicators
                page_text = soup.get_text().lower()
                player_indicators = ['spieler', 'name', 'punkte', 'werfer', 'treffer']
                found_indicators = [indicator for indicator in player_indicators if indicator in page_text]
                print(f"   🔍 Player indicators found: {found_indicators}")
                
                # Look for data tables specifically
                data_tables = []
                for i, table in enumerate(tables):
                    table_text = table.get_text().lower()
                    rows = table.find_all('tr')
                    
                    # Check if this table has player-like data
                    has_player_terms = any(term in table_text for term in ['spieler', 'name', 'punkte'])
                    has_multiple_rows = len(rows) > 1
                    
                    if has_player_terms and has_multiple_rows:
                        data_tables.append((i, table, len(rows)))
                        print(f"   📋 Data table {i}: {len(rows)} rows, contains player terms")
                        
                        # Show first few rows of promising tables
                        if len(rows) > 1:
                            header_row = rows[0]
                            header_text = header_row.get_text(strip=True)
                            print(f"      Header: {header_text}")
                            
                            if len(rows) > 1:
                                first_data_row = rows[1]
                                first_data_text = first_data_row.get_text(strip=True)
                                print(f"      First row: {first_data_text}")
                
                # Try to extract actual player data
                if data_tables:
                    best_table = max(data_tables, key=lambda x: x[2])  # Table with most rows
                    extracted_players = extract_players_from_table(best_table[1], url)
                    print(f"   ✅ Extracted {len(extracted_players)} players")
                    
                    if extracted_players:
                        print(f"   📝 Sample player: {extracted_players[0]}")
                else:
                    extracted_players = []
                    print(f"   ❌ No player data tables found")
                
                results.append({
                    'endpoint': endpoint,
                    'url': url,
                    'status': 'success',
                    'tables_found': len(tables),
                    'data_tables': len(data_tables),
                    'players_extracted': len(extracted_players),
                    'players': extracted_players[:5],  # First 5 players
                    'indicators_found': found_indicators,
                    'html_file': filename
                })
                
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                results.append({
                    'endpoint': endpoint,
                    'url': url,
                    'status': 'failed',
                    'http_status': response.status_code
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'endpoint': endpoint,
                'url': url,
                'status': 'error',
                'error': str(e)
            })
    
    # Save results
    output = {
        'test_timestamp': datetime.now().isoformat(),
        'liga_id': liga_id,
        'saison_id': saison_id,
        'endpoints_tested': player_endpoints,
        'results': results,
        'summary': {
            'total_endpoints': len(player_endpoints),
            'successful_endpoints': len([r for r in results if r.get('status') == 'success']),
            'total_players_found': sum(r.get('players_extracted', 0) for r in results)
        }
    }
    
    with open('player_stats_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 SUMMARY:")
    print(f"   ✅ {output['summary']['successful_endpoints']}/{len(player_endpoints)} endpoints successful")
    print(f"   👤 {output['summary']['total_players_found']} total players found")
    print(f"   📄 Results saved to player_stats_test_results.json")

def extract_players_from_table(table, source_url):
    """Extract player data from table with improved logic"""
    
    try:
        players = []
        rows = table.find_all('tr')
        
        if len(rows) < 2:
            return []
        
        # Try to identify header row and data rows
        header_row = rows[0]
        header_cells = header_row.find_all(['th', 'td'])
        headers = [cell.get_text(strip=True).lower() for cell in header_cells]
        
        # Process each data row
        for row_idx, row in enumerate(rows[1:]):
            cells = row.find_all(['td', 'th'])
            
            if len(cells) >= 2:
                player_data = {
                    'source_url': source_url,
                    'row_index': row_idx,
                    'extracted_at': datetime.now().isoformat()
                }
                
                # Map cells to data
                for cell_idx, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True)
                    
                    if cell_text:  # Only process non-empty cells
                        # Store raw data
                        if cell_idx < len(headers):
                            header = headers[cell_idx]
                            player_data[f'col_{cell_idx}_{header}'] = cell_text
                        else:
                            player_data[f'col_{cell_idx}'] = cell_text
                        
                        # Try to identify specific fields
                        if cell_idx < len(headers):
                            header = headers[cell_idx]
                            
                            # Player name detection
                            if any(term in header for term in ['name', 'spieler']) and not cell_text.isdigit():
                                if len(cell_text) > 2:
                                    player_data['player_name'] = cell_text
                            
                            # Points detection
                            elif any(term in header for term in ['punkte', 'points']):
                                try:
                                    points_val = float(cell_text.replace(',', '.'))
                                    player_data['points'] = points_val
                                except:
                                    pass
                            
                            # Games detection
                            elif any(term in header for term in ['spiele', 'games']):
                                try:
                                    player_data['games'] = int(cell_text)
                                except:
                                    pass
                        
                        # Fallback: if first non-numeric cell, likely name
                        elif cell_idx == 0 and not cell_text.isdigit() and len(cell_text) > 2:
                            player_data['player_name'] = cell_text
                
                # Only add if we have meaningful data
                if len([k for k in player_data.keys() if not k.startswith('col_')]) > 3:
                    players.append(player_data)
        
        return players
        
    except Exception as e:
        print(f"      Error extracting players: {e}")
        return []

if __name__ == "__main__":
    test_player_statistics_directly()
