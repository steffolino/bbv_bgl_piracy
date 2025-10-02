#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random
import re

def crawl_historical_paginated():
    """
    Historical crawler with proper pagination handling
    1. Action=106 POST → Get league list (handle pagination)
    2. Extract all liga_id values from all pages
    3. Action=107 → Crawl each league for player data
    """
    
    print("🏀 HISTORICAL CRAWLER WITH PAGINATION")
    print("Step 1: Action=106 POST + pagination → Get ALL league lists")
    print("Step 2: Extract liga_id links from all pages")
    print("Step 3: Action=107 → Get player data for each league")
    
    # Target historical seasons
    target_seasons = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021, 2022, 2023, 2024]
    
    session = create_session_with_cookies()
    
    all_players = []
    season_summary = {}
    
    for season in target_seasons:
        print(f"\n📅 SEASON {season}")
        
        # Step 1: Get ALL liga_ids from all pages
        liga_ids = get_all_liga_ids_paginated(session, season)
        
        if not liga_ids:
            print(f"  ❌ No leagues found for season {season}")
            continue
        
        print(f"  ✅ Found {len(liga_ids)} leagues across all pages")
        
        # Step 2: Crawl each league for player data
        season_players = []
        for i, liga_info in enumerate(liga_ids, 1):
            liga_id = liga_info['liga_id']
            league_name = liga_info['name']
            
            print(f"  🏀 League {i}/{len(liga_ids)}: {league_name} (ID: {liga_id})")
            
            players = crawl_league_players(session, liga_id, league_name, season)
            if players:
                season_players.extend(players)
                print(f"    ✅ {len(players)} players")
            else:
                print(f"    ❌ No players")
            
            # Rate limiting
            time.sleep(random.uniform(1, 3))
        
        # Save season results
        if season_players:
            all_players.extend(season_players)
            season_summary[season] = {
                'total_players': len(season_players),
                'total_leagues': len(liga_ids),
                'leagues': [liga['name'] for liga in liga_ids]
            }
            
            save_season_players(season, season_players, liga_ids)
            print(f"  📊 Season {season} complete: {len(season_players)} players from {len(liga_ids)} leagues")
        
        print(f"  ⏱️  Waiting before next season...")
        time.sleep(random.uniform(3, 6))
    
    # Save comprehensive dataset
    if all_players:
        save_comprehensive_players(all_players, season_summary)
        update_frontend_data(all_players, list(season_summary.keys()))
    
    print(f"\n🎯 PAGINATED CRAWL COMPLETE!")
    print(f"📊 Total players: {len(all_players)}")
    print(f"📅 Seasons: {list(season_summary.keys())}")

def create_session_with_cookies():
    """Create session with proper cookies for authentication"""
    session = requests.Session()
    
    # Set headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Cache-Control': 'no-cache',
        'DNT': '1',
        'Origin': 'https://www.basketball-bund.net',
        'Pragma': 'no-cache',
        'Referer': 'https://www.basketball-bund.net/index.jsp?Action=106',
        'Sec-CH-UA': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    })
    
    # Set cookies (using your working values)
    cookies = {
        '__cmpcc': '1',
        'SESSION': 'ODA4Mzk0NTYtOThlMi00YzE0LTg4MmUtOGNiMWU2MTk3Y2M4',
        '__cmpconsentx47082': 'CQYqGvAQYqGvAAfQ6BENB-FgAP_AAEPAAAigJSkR5C5cDWFBeTp3QMskeYQX0cgBZgABAgaAASABCDAAcIQAkkESIAyAAAACAQAAIDSBAAAADAhAAEAAAIgBAADoAAAEgBAIIAAEABERQ0IAAAgKCIgAEAAIAAAxIkAAkAKAAILiQFAAgIAiAAABAAAAAIABAAMAAAAIAAACAAIAAAAAAAAAgAAAAAACABAIAAAAAAAAII3wPgAFgAVAAuABwADwAIAAVAAyABoADwAI4ATAAuABiADQAG8APwAhABDACaAE4AMAAYYA5wB3QD8AP0AhABFgCOAEiAJMASkAsQBigDXgG0AOIAdsA_oB_wEXgJWATEAmQBNIChwFHgKRAU2Ap8BboC5AF5gMhAZIAywBlwDTQHFgPHAhWBG8AAA.f_gACHgAAAA',
        '__cmpcccx47082': 'aCQYrQy_gAAhfRqxozGIxJkc8QzJqaGQMhoMxYliDBDUysVMF6E9WLEjE1MMkalhYyamrJDQyGWGU1GTQxYGiYMGWSMMiFoJi1JYqwjAkwAA',
        '_cc_id': 'b616c325dc88e1ae505ba80bd46882fe',
        'panoramaId_expiry': '1759991137726',
        'panoramaId': '947c1d27b3bb8d4dfc70e52580f3185ca02cacef30144e43784f041253e24e3a',
        'panoramaIdType': 'panoDevice',
        'connectId': '{"ttl":86400000,"lastUsed":1759386336895,"lastSynced":1759386336895}',
        '__gads': 'ID=2606604e4e061425:T=1759386338:RT=1759388948:S=ALNI_MboJFcXJE4aqMFvtQzMYf84WND8Jg',
        '__gpi': 'UID=0000129342773779:T=1759386338:RT=1759388948:S=ALNI_MYebYj8D0sws2npwfXIogpqvTFm6w',
        '__eoi': 'ID=cf36713925753e4a:T=1759386338:RT=1759388948:S=AA-AfjZXc8kz_f8dFx3IWngcOT9S',
        'emqsegs': 'e0,e3m,e38,ey,ed,e3i,e3s,ec,e3o,e3b,e1,e8',
        'cto_bundle': 'rdiVgl9jU0JWa1dYbzRqclJ1a2RiOWxPVVQ2dWJDY1paVzFadHc4JTJCcUwlMkJVMFdHa3dCM0I1RDklMkZYMTglMkJrYTdMOVRkZHdzZElleW5jdTd4VHRnWWNMSE5ScGRTc2xzUzliRHpGc1o0SFBLUmczRmp5N09WNDNzNW95RWpEM0p2S3F2b1hMd0U1QldkcndjemFtdnJIOUNxbmRzMVUlMkZmVUd2OHppWmZLTUkxY0ZwZHJzJTNE'
    }
    
    session.cookies.update(cookies)
    
    return session

def get_all_liga_ids_paginated(session, season):
    """
    Get ALL liga_ids by following pagination
    """
    
    all_liga_ids = []
    startrow = 0
    page = 1
    
    while True:
        print(f"    📄 Fetching page {page} (startrow={startrow})")
        
        # Build URL with pagination
        if startrow == 0:
            url = 'https://www.basketball-bund.net/index.jsp?Action=106'
        else:
            url = f'https://www.basketball-bund.net/index.jsp?Action=106&startrow={startrow}&viewid='
        
        # POST data for season/filters
        post_data = {
            'saison_id': str(season),
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '-3',
            'cbGeschlechtFilter': '0',
            'cbBezirkFilter': '5',  # Oberfranken
            'cbKreisFilter': '0'
        }
        
        try:
            response = session.post(url, data=post_data, timeout=30)
            
            if response.status_code != 200:
                print(f"      ❌ HTTP {response.status_code}")
                break
            
            print(f"      ✅ Response: {len(response.text):,} chars")
            
            # Save page for debugging
            page_filename = f'action_106_page_{page}_{season}_startrow_{startrow}.html'
            with open(page_filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Parse liga_ids from this page
            soup = BeautifulSoup(response.text, 'html.parser')
            page_liga_ids = extract_liga_ids_from_page(soup)
            
            if not page_liga_ids:
                print(f"      ❌ No liga_ids found on page {page}")
                break
            
            print(f"      📋 Found {len(page_liga_ids)} liga_ids on page {page}")
            all_liga_ids.extend(page_liga_ids)
            
            # Check for next page
            has_next = check_has_next_page(soup, page)
            if not has_next:
                print(f"      ✅ Last page reached")
                break
            
            # Move to next page
            startrow += 10  # Assuming 10 items per page
            page += 1
            
            # Rate limiting between pages
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"      💥 Error on page {page}: {str(e)[:50]}")
            break
    
    print(f"    📊 Total liga_ids found: {len(all_liga_ids)} across {page} pages")
    return all_liga_ids

def extract_liga_ids_from_page(soup):
    """
    Extract liga_id links from a single page
    """
    
    liga_ids = []
    
    # Look for Action=107 links with liga_id parameter
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link.get('href', '')
        
        # Match: index.jsp?Action=107&liga_id=XXXX&saison_id=YYYY
        if 'Action=107' in href and 'liga_id=' in href:
            
            # Extract liga_id
            liga_id_match = re.search(r'liga_id=(\d+)', href)
            if liga_id_match:
                liga_id = liga_id_match.group(1)
                
                # Get league name from surrounding context
                league_name = get_league_name_from_link_context(link)
                
                liga_info = {
                    'liga_id': liga_id,
                    'name': league_name,
                    'href': href
                }
                
                liga_ids.append(liga_info)
    
    # Remove duplicates by liga_id
    seen_ids = set()
    unique_liga_ids = []
    for liga in liga_ids:
        if liga['liga_id'] not in seen_ids:
            seen_ids.add(liga['liga_id'])
            unique_liga_ids.append(liga)
    
    return unique_liga_ids

def get_league_name_from_link_context(link):
    """
    Extract league name from the table row context
    """
    
    # Navigate up to find the table row
    row = link.find_parent('tr')
    if row:
        cells = row.find_all('td')
        if len(cells) >= 6:  # Based on your table structure
            # League name is typically in the 6th column (index 5)
            league_name = cells[5].get_text(strip=True)
            if league_name:
                return league_name
    
    # Fallback to link context
    parent = link.find_parent(['td', 'div'])
    if parent:
        text = parent.get_text(strip=True)
        if text:
            return text
    
    return 'Unknown League'

def check_has_next_page(soup, current_page):
    """
    Check if there's a next page available
    """
    
    # Look for pagination indicators
    page_text = soup.get_text()
    
    # Look for "Seite X / Y" pattern
    page_match = re.search(r'Seite\s+(\d+)\s*/\s*(\d+)', page_text)
    if page_match:
        current = int(page_match.group(1))
        total = int(page_match.group(2))
        return current < total
    
    # Look for "next page" links
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href', '')
        if 'startrow=' in href and int(re.search(r'startrow=(\d+)', href).group(1)) > current_page * 10:
            return True
    
    return False

def crawl_league_players(session, liga_id, league_name, season):
    """
    Crawl individual league for player data using Action=107
    """
    
    url = f'https://www.basketball-bund.net/index.jsp?Action=107&liga_id={liga_id}&saison_id={season}'
    
    try:
        response = session.get(url, timeout=30)
        
        if response.status_code != 200:
            return []
        
        # Parse players from Action=107 response
        soup = BeautifulSoup(response.text, 'html.parser')
        players = extract_players_from_action_107(soup, liga_id, league_name, season)
        
        return players
        
    except Exception as e:
        print(f"      💥 Error crawling league {liga_id}: {str(e)[:50]}")
        return []

def extract_players_from_action_107(soup, liga_id, league_name, season):
    """
    Extract player data from Action=107 league statistics page
    """
    
    players = []
    
    # Look for player statistics tables
    tables = soup.find_all('table')
    
    for table_idx, table in enumerate(tables):
        rows = table.find_all('tr')
        
        if len(rows) < 2:
            continue
        
        # Check if this looks like a player statistics table
        header_row = rows[0]
        header_cells = header_row.find_all(['th', 'td'])
        header_texts = [cell.get_text(strip=True).lower() for cell in header_cells]
        
        player_indicators = ['name', 'spieler', 'punkte', 'spiele', 'team', 'mannschaft']
        if not any(indicator in ' '.join(header_texts) for indicator in player_indicators):
            continue
        
        # Process data rows
        for row_idx, row in enumerate(rows[1:], 1):
            cells = row.find_all(['td', 'th'])
            
            if len(cells) < 2:
                continue
            
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            # Skip empty or header-like rows
            if not cell_texts[0] or len(cell_texts[0]) < 2:
                continue
            
            if any(header_word in cell_texts[0].lower() for header_word in ['name', 'spieler', 'rang', 'pos']):
                continue
            
            # Create player record
            player = {
                'name': cell_texts[0],
                'season_id': season,
                'liga_id': str(liga_id),
                'league_name': league_name,
                'table_index': table_idx,
                'row_index': row_idx,
                'extraction_method': 'Action=106→107 Paginated',
                'extracted_at': datetime.now().isoformat(),
                'raw_data': cell_texts
            }
            
            # Add team and stats if available
            if len(cell_texts) > 1:
                player['team'] = cell_texts[1]
            
            # Extract numeric statistics
            for i, value in enumerate(cell_texts[2:], 2):
                if value.replace('.', '').replace(',', '').isdigit():
                    player[f'stat_{i-1}'] = value
            
            # Check for Litzendorf
            full_text = ' '.join(cell_texts).lower()
            if 'litzendorf' in full_text:
                player['is_litzendorf'] = True
            
            players.append(player)
    
    return players

def save_season_players(season, players, liga_ids):
    """Save individual season data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'paginated_season_{season}_{timestamp}.json'
    
    data = {
        'season': season,
        'method': 'Action=106→107 Paginated Crawl',
        'timestamp': datetime.now().isoformat(),
        'total_players': len(players),
        'total_leagues': len(liga_ids),
        'liga_ids': liga_ids,
        'players': players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"    💾 Saved: {filename}")

def save_comprehensive_players(all_players, season_summary):
    """Save comprehensive multi-season dataset"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'paginated_historical_comprehensive_{timestamp}.json'
    
    data = {
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_method': 'Paginated Action=106→107 Historical Crawl',
        'total_players': len(all_players),
        'seasons_crawled': list(season_summary.keys()),
        'season_summary': season_summary,
        'players': all_players
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comprehensive file: {filename}")

def update_frontend_data(historical_players, historical_seasons):
    """Update frontend data with historical players"""
    try:
        # Load existing 2018 data
        with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        existing_players = existing_data.get('players', [])
        
        # Combine datasets
        all_players = existing_players + historical_players
        all_seasons = sorted(list(set([2018] + historical_seasons)))
        
        # Update frontend file
        updated_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'source': 'Combined 2018 + Paginated Historical Action=106→107 data',
            'total_players': len(all_players),
            'seasons_available': all_seasons,
            'total_seasons': len(all_seasons),
            'coverage_span': f"{min(all_seasons)}-{max(all_seasons)}",
            'players': all_players
        }
        
        with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated frontend data: {len(all_players):,} total players")
        print(f"📅 Seasons: {min(all_seasons)}-{max(all_seasons)}")
        
    except Exception as e:
        print(f"⚠️  Frontend update failed: {e}")

if __name__ == "__main__":
    crawl_historical_paginated()
