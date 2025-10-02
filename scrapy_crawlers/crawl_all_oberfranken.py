#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def crawl_all_oberfranken_systematic():
    """Use the USER'S EXACT URL patterns to systematically crawl all leagues and seasons"""
    
    print("🎯 SYSTEMATIC OBERFRANKEN CRAWL")
    print("Using YOUR EXACT working URL patterns:")
    print("https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id=XXXX&saison_id=YYYY&_top=-1")
    
    # Test league IDs around your known working one (26212)
    base_liga_id = 26212
    test_range = range(base_liga_id - 50, base_liga_id + 50)  # Test 100 league IDs around known working one
    
    # Test seasons from 2003 to 2024
    seasons = list(range(2003, 2025))
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Referer': 'https://www.basketball-bund.net/',
    }
    
    working_urls = []
    all_players = []
    league_database = {}
    
    # Test your known working combination first
    print(f"\n✅ TESTING KNOWN WORKING: liga_id={base_liga_id}, season=2018")
    working_leagues = test_liga_season_combination(base_liga_id, 2018, headers)
    if working_leagues:
        print(f"   ✅ Confirmed working: {len(working_leagues)} endpoints")
        working_urls.extend(working_leagues)
    
    # Now systematically test other seasons for the known working league
    print(f"\n📅 TESTING ALL SEASONS for known league {base_liga_id}")
    for season in seasons:
        if season == 2018:
            continue  # Already tested
        
        print(f"   Testing season {season}...")
        working = test_liga_season_combination(base_liga_id, season, headers)
        if working:
            print(f"      ✅ Season {season}: {len(working)} working endpoints")
            working_urls.extend(working)
        else:
            print(f"      ❌ Season {season}: No data")
        
        time.sleep(0.5)  # Rate limiting
    
    # Test other league IDs for seasons that worked
    working_seasons = list(set(url['saison_id'] for url in working_urls))
    print(f"\n🔍 TESTING OTHER LEAGUE IDs for working seasons: {working_seasons}")
    
    for liga_id in test_range:
        if liga_id == base_liga_id:
            continue  # Already tested
        
        # Test this league for seasons we know have data
        for season in working_seasons[:3]:  # Test top 3 working seasons
            working = test_liga_season_combination(liga_id, season, headers)
            if working:
                print(f"   ✅ Found new league: {liga_id} in season {season}")
                working_urls.extend(working)
            
            time.sleep(0.2)  # Rate limiting
    
    # Save working URLs database
    save_working_urls_database(working_urls)
    
    # Extract players from all working URLs
    print(f"\n📊 EXTRACTING PLAYERS from {len(working_urls)} working URLs")
    for i, url_info in enumerate(working_urls):
        print(f"   {i+1}/{len(working_urls)}: Liga {url_info['liga_id']}, Season {url_info['saison_id']}, {url_info['endpoint']}")
        
        try:
            response = requests.get(url_info['url'], headers=headers, timeout=15)
            if response.status_code == 200:
                players = extract_players_from_response(response.text, url_info)
                all_players.extend(players)
                print(f"      ✅ {len(players)} players")
            else:
                print(f"      ❌ HTTP {response.status_code}")
        except Exception as e:
            print(f"      ❌ Error: {e}")
        
        time.sleep(1)  # Rate limiting
    
    # Save final comprehensive data
    save_comprehensive_data(all_players, working_urls)
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"   📊 {len(working_urls)} working URLs found")
    print(f"   👤 {len(all_players)} total players extracted")
    print(f"   🏀 {len(set(p.get('liga_id') for p in all_players))} unique leagues")
    print(f"   📅 {len(set(p.get('season_id') for p in all_players))} seasons covered")

def test_liga_season_combination(liga_id, saison_id, headers):
    """Test if a liga_id + saison_id combination has data using your URL patterns"""
    
    # Your exact URL patterns
    test_urls = [
        f"https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id={liga_id}&saison_id={saison_id}&_top=-1",
        f"https://www.basketball-bund.net/statistik.do?reqCode=statBesteFreiWerferArchiv&liga_id={liga_id}&saison_id={saison_id}&_top=-1",
        f"https://www.basketball-bund.net/statistik.do?reqCode=statBeste3erWerferArchiv&liga_id={liga_id}&saison_id={saison_id}&_top=-1",
    ]
    
    working_urls = []
    
    for url in test_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Check if page has actual player data
                if has_player_data(response.text):
                    endpoint = url.split('reqCode=')[1].split('&')[0]
                    working_urls.append({
                        'url': url,
                        'liga_id': liga_id,
                        'saison_id': saison_id,
                        'endpoint': endpoint,
                        'tested_at': datetime.now().isoformat()
                    })
                    
        except Exception as e:
            continue
    
    return working_urls

def has_player_data(html_content):
    """Check if the page actually contains player data"""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for sportItem classes (your player data rows)
        sportitem_rows = soup.find_all(['td', 'tr'], class_=lambda x: x and 'sportitem' in str(x).lower())
        
        # Also check for common player indicators
        text = html_content.lower()
        player_indicators = ['spieler', 'punkte', 'werfer']
        has_indicators = any(indicator in text for indicator in player_indicators)
        
        # Check for actual data (not just headers)
        return len(sportitem_rows) > 5 or (has_indicators and 'oberfranken' in text)
        
    except:
        return False

def extract_players_from_response(html_content, url_info):
    """Extract players using the working parser logic"""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        players = []
        
        # Find rows with sportItem classes
        all_rows = soup.find_all('tr')
        player_rows = []
        
        for row in all_rows:
            cells = row.find_all('td')
            has_sport_item = any('sportItem' in str(cell) for cell in cells)
            
            if has_sport_item and len(cells) >= 6:
                player_rows.append(row)
        
        # Parse each player row
        for row_idx, row in enumerate(player_rows):
            cells = row.find_all('td')
            
            try:
                # Extract cell text
                cell_texts = []
                for cell in cells:
                    text = cell.get_text().replace('\u00a0', ' ').strip()
                    cell_texts.append(text)
                
                if len(cell_texts) >= 6:
                    player_data = {
                        'liga_id': url_info['liga_id'],
                        'season_id': url_info['saison_id'],
                        'endpoint': url_info['endpoint'],
                        'source_url': url_info['url'],
                        'extracted_at': datetime.now().isoformat(),
                    }
                    
                    # Parse columns
                    try:
                        player_data['rank'] = int(cell_texts[0].rstrip('.'))
                    except:
                        pass
                    
                    player_data['surname'] = cell_texts[1]
                    player_data['first_name'] = cell_texts[2]
                    player_data['team'] = cell_texts[3]
                    
                    try:
                        player_data['points'] = int(cell_texts[4])
                    except:
                        player_data['points'] = 0
                    
                    try:
                        player_data['games'] = int(cell_texts[5])
                    except:
                        player_data['games'] = 0
                    
                    if len(cell_texts) >= 7:
                        try:
                            player_data['average'] = float(cell_texts[6].replace(',', '.'))
                        except:
                            pass
                    
                    # Create full name
                    if player_data['first_name'] and player_data['surname']:
                        player_data['name'] = f"{player_data['first_name']} {player_data['surname']}"
                    
                    # Only add valid players
                    if player_data.get('name') and player_data.get('team') and player_data.get('points', 0) > 0:
                        players.append(player_data)
                        
            except:
                continue
        
        return players
        
    except Exception as e:
        return []

def save_working_urls_database(working_urls):
    """Save database of working URLs to avoid re-testing"""
    
    database = {
        'created_at': datetime.now().isoformat(),
        'total_working_urls': len(working_urls),
        'unique_leagues': len(set(url['liga_id'] for url in working_urls)),
        'seasons_covered': sorted(list(set(url['saison_id'] for url in working_urls))),
        'working_urls': working_urls
    }
    
    with open('oberfranken_working_urls.json', 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"   💾 Saved {len(working_urls)} working URLs to oberfranken_working_urls.json")

def save_comprehensive_data(all_players, working_urls):
    """Save comprehensive player data"""
    
    # Create summary
    summary = {
        'extraction_timestamp': datetime.now().isoformat(),
        'source': 'Systematic Oberfranken crawl using user URL patterns',
        'total_players': len(all_players),
        'unique_leagues': len(set(p.get('liga_id') for p in all_players)),
        'seasons_covered': sorted(list(set(p.get('season_id') for p in all_players))),
        'endpoints_used': list(set(p.get('endpoint') for p in all_players)),
        'teams': sorted(list(set(p.get('team') for p in all_players if p.get('team')))),
    }
    
    # Frontend data
    frontend_data = {
        'players': all_players,
        'summary': summary
    }
    
    # Save files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with open(f'oberfranken_complete_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(frontend_data, f, indent=2, ensure_ascii=False)
    
    with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(frontend_data, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Saved complete data to oberfranken_complete_{timestamp}.json")
    print(f"   📱 Updated frontend data: real_players_extracted.json")

if __name__ == "__main__":
    crawl_all_oberfranken_systematic()
