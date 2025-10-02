#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def test_known_league_across_seasons():
    """Test the known liga_id=26212 (Oberfranken) across multiple seasons"""
    
    print("🎯 TESTING KNOWN LEAGUE ACROSS SEASONS")
    print("Using liga_id=26212 from your working URLs")
    print("Testing different saison_id values to find all available seasons")
    
    # Your known working liga_id
    known_liga_id = 26212
    
    # Test multiple seasons (basketball seasons run like 2018 = 2018/2019 season)
    test_seasons = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    
    # Statistics endpoints from your examples
    stat_endpoints = [
        'statTeamArchiv',                # Team statistics
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
    
    all_results = []
    
    for saison_id in test_seasons:
        print(f"\n📅 TESTING SEASON {saison_id} (= {saison_id}/{saison_id+1})")
        
        season_data = {
            'liga_id': known_liga_id,
            'saison_id': saison_id,
            'season_display': f"{saison_id}/{saison_id+1}",
            'endpoints': {},
            'total_players': 0,
            'total_teams': 0
        }
        
        for endpoint in stat_endpoints:
            print(f"   📊 {endpoint}...")
            
            # Build URL based on your examples
            if endpoint == 'statTeamArchiv':
                url = f"https://www.basketball-bund.net/statistik.do?reqCode={endpoint}&liga_id={known_liga_id}&saison_id={saison_id}"
            else:
                url = f"https://www.basketball-bund.net/statistik.do?reqCode={endpoint}&liga_id={known_liga_id}&saison_id={saison_id}&_top=-1"
            
            try:
                response = requests.get(url, headers=headers, timeout=15)
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 200:
                    # Parse the response
                    data = parse_statistics_page(response.text, endpoint, url)
                    
                    endpoint_result = {
                        'url': url,
                        'status': 'success',
                        'data_count': len(data),
                        'data': data[:3] if data else []  # First 3 rows as sample
                    }
                    
                    if endpoint == 'statTeamArchiv':
                        season_data['total_teams'] += len(data)
                        print(f"      ✅ {len(data)} teams")
                    else:
                        season_data['total_players'] += len(data)
                        print(f"      ✅ {len(data)} players")
                    
                    # Save first successful response HTML for inspection
                    if len(data) > 0 and 'sample_html_saved' not in season_data:
                        filename = f'sample_success_{saison_id}_{endpoint}.html'
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"      💾 Saved sample HTML: {filename}")
                        season_data['sample_html_saved'] = filename
                    
                else:
                    endpoint_result = {
                        'url': url,
                        'status': 'failed',
                        'http_status': response.status_code
                    }
                    print(f"      ❌ HTTP {response.status_code}")
                
                season_data['endpoints'][endpoint] = endpoint_result
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
                season_data['endpoints'][endpoint] = {
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                }
            
            time.sleep(1)  # Rate limiting
        
        # Test game results too
        print(f"   🏀 Game results...")
        try:
            games_url = f"https://www.basketball-bund.net/index.jsp?Action=108&liga_id={known_liga_id}&saison_id={saison_id}"
            response = requests.get(games_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                games_data = parse_game_results(response.text, games_url)
                season_data['endpoints']['game_results'] = {
                    'url': games_url,
                    'status': 'success',
                    'data_count': len(games_data),
                    'data': games_data[:3] if games_data else []
                }
                print(f"      ✅ {len(games_data)} games")
            else:
                print(f"      ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
        
        # Summary for this season
        total_data = season_data['total_players'] + season_data['total_teams']
        if total_data > 0:
            print(f"   🎯 SEASON {saison_id} TOTAL: {season_data['total_players']} players, {season_data['total_teams']} teams")
            season_data['has_data'] = True
        else:
            print(f"   ❌ SEASON {saison_id}: No data found")
            season_data['has_data'] = False
        
        all_results.append(season_data)
        time.sleep(2)  # Rate limiting between seasons
    
    # Save results
    output = {
        'test_timestamp': datetime.now().isoformat(),
        'strategy': 'Test known liga_id across multiple seasons',
        'known_liga_id': known_liga_id,
        'bezirk': 'Oberfranken',
        'seasons_tested': test_seasons,
        'summary': {
            'total_seasons_tested': len(test_seasons),
            'seasons_with_data': len([s for s in all_results if s.get('has_data', False)]),
            'total_players_found': sum(s['total_players'] for s in all_results),
            'total_teams_found': sum(s['total_teams'] for s in all_results)
        },
        'detailed_results': all_results
    }
    
    with open('known_league_season_test.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 FINAL RESULTS:")
    print(f"   📊 {output['summary']['seasons_with_data']}/{len(test_seasons)} seasons have data")
    print(f"   👤 {output['summary']['total_players_found']} total players found")
    print(f"   🏀 {output['summary']['total_teams_found']} total teams found")
    print(f"   ✅ Saved to known_league_season_test.json")
    
    return all_results

def parse_statistics_page(html_content, endpoint, source_url):
    """Parse statistics page and extract data from tables"""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for data tables
        tables = soup.find_all('table')
        
        for table in tables:
            if is_data_table(table, endpoint):
                return extract_table_data(table, source_url)
        
        return []
        
    except Exception as e:
        return []

def is_data_table(table, endpoint):
    """Check if table contains the statistics data we want"""
    
    table_text = table.get_text().lower()
    
    if endpoint == 'statTeamArchiv':
        # Team statistics table
        indicators = ['team', 'mannschaft', 'spiele', 'punkte', 'siege']
    else:
        # Player statistics table  
        indicators = ['spieler', 'name', 'punkte', 'spiele', 'minuten']
    
    # Table must have multiple rows and contain relevant terms
    rows = table.find_all('tr')
    if len(rows) < 2:
        return False
    
    found_indicators = sum(1 for indicator in indicators if indicator in table_text)
    return found_indicators >= 2

def extract_table_data(table, source_url):
    """Extract data from HTML table"""
    
    try:
        data = []
        rows = table.find_all('tr')
        
        if len(rows) < 2:
            return []
        
        # Get headers
        header_row = rows[0]
        headers = []
        for th in header_row.find_all(['th', 'td']):
            header_text = th.get_text(strip=True).lower()
            headers.append(header_text)
        
        # Process data rows
        for row_idx, row in enumerate(rows[1:]):
            cells = row.find_all(['td', 'th'])
            
            if len(cells) >= 2:
                row_data = {
                    'source_url': source_url,
                    'row_index': row_idx,
                    'extracted_at': datetime.now().isoformat()
                }
                
                # Map cell data to headers
                for cell_idx, cell in enumerate(cells):
                    if cell_idx < len(headers):
                        header = headers[cell_idx]
                        cell_text = cell.get_text(strip=True)
                        
                        # Store raw data
                        row_data[f'col_{cell_idx}_{header}'] = cell_text
                        
                        # Try to identify and clean common fields
                        if any(term in header for term in ['name', 'spieler']) and cell_text:
                            if len(cell_text) > 1 and not cell_text.isdigit():
                                row_data['name'] = cell_text
                        
                        elif any(term in header for term in ['team', 'mannschaft']) and cell_text:
                            if len(cell_text) > 1:
                                row_data['team'] = cell_text
                        
                        elif any(term in header for term in ['punkte', 'points']) and cell_text:
                            try:
                                # Handle German decimal format
                                points_str = cell_text.replace(',', '.')
                                row_data['points'] = float(points_str)
                            except:
                                pass
                        
                        elif any(term in header for term in ['spiele', 'games']) and cell_text:
                            try:
                                row_data['games'] = int(cell_text)
                            except:
                                pass
                
                # Only add rows with meaningful data
                meaningful_fields = [k for k in row_data.keys() if not k.startswith('col_') and k not in ['source_url', 'row_index', 'extracted_at']]
                if len(meaningful_fields) > 0:
                    data.append(row_data)
        
        return data
        
    except Exception as e:
        return []

def parse_game_results(html_content, source_url):
    """Parse game results from HTML"""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        games = []
        
        # Look for game result tables
        tables = soup.find_all('table')
        
        for table in tables:
            table_text = table.get_text().lower()
            
            # Check if this looks like a games table
            if any(term in table_text for term in ['spiel', 'ergebnis', 'heimmannschaft', 'heim', 'gast']):
                rows = table.find_all('tr')
                
                for row_idx, row in enumerate(rows[1:]):  # Skip header
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:
                        game_data = {
                            'source_url': source_url,
                            'game_index': row_idx,
                            'extracted_at': datetime.now().isoformat()
                        }
                        
                        # Store all cell data
                        for cell_idx, cell in enumerate(cells):
                            cell_text = cell.get_text(strip=True)
                            game_data[f'col_{cell_idx}'] = cell_text
                        
                        games.append(game_data)
        
        return games
        
    except Exception as e:
        return []

if __name__ == "__main__":
    test_known_league_across_seasons()
