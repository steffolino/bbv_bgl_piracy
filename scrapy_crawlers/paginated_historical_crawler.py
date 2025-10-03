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
    target_seasons = list(range(2003, 2025))
    
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
        
        # Step 2: Crawl each league for all endpoints
        season_results = []
        for i, liga_info in enumerate(liga_ids, 1):
            liga_id = liga_info['liga_id']
            league_name = liga_info['name']
            print(f"  🏀 League {i}/{len(liga_ids)}: {league_name} (ID: {liga_id})")

            league_result = {
                'season': season,
                'liga_id': liga_id,
                'league_name': league_name,
                'statBesteWerferArchiv': None,
                'statBesteFreiWerferArchiv': None,
                'statBeste3erWerferArchiv': None,
                'standings': None,
                'results': None
            }

            # Crawl statBesteWerferArchiv
            league_result['statBesteWerferArchiv'] = crawl_statistik_endpoint(session, liga_id, season, 'statBesteWerferArchiv')
            # Crawl statBesteFreiWerferArchiv
            league_result['statBesteFreiWerferArchiv'] = crawl_statistik_endpoint(session, liga_id, season, 'statBesteFreiWerferArchiv')
            # Crawl statBeste3erWerferArchiv
            league_result['statBeste3erWerferArchiv'] = crawl_statistik_endpoint(session, liga_id, season, 'statBeste3erWerferArchiv')
            # Crawl Action=107 (standings)
            league_result['standings'] = crawl_league_players(session, liga_id, league_name, season)
            # Crawl Action=108 (results)
            league_result['results'] = crawl_league_results(session, liga_id, league_name, season)

            season_results.append(league_result)
            print(f"    ✅ Endpoints crawled for league {liga_id}")
            time.sleep(random.uniform(1, 2))

        # Save season results
        if season_results:
            all_players.extend(season_results)
            season_summary[season] = {
                'total_leagues': len(liga_ids),
                'leagues': [liga['name'] for liga in liga_ids]
            }
            save_season_players(season, season_results, liga_ids)
            print(f"  📊 Season {season} complete: {len(season_results)} leagues crawled")

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
    # Set headers from working curl
    session.headers.update({
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'dnt': '1',
        'origin': 'https://www.basketball-bund.net',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://www.basketball-bund.net/index.jsp?Action=106',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    })

    # Set cookies from working curl
    cookies = {
        'SESSION': 'YjE0NGNiOWQtZDYwYi00NDVjLWEwOWYtYWY5YmY1OWQ2ZmIw',
        '__cmpcc': '1',
        '__cmpconsentx47082': 'CQYtZrAQYtZrAAfQ6BENB_FgAP_AAEPAAAigJSkR5C5cDWFBeTJ3QMskeYQX0cgBZgABAgaAASABCDAAcIQAkkESIAyAAAACAQAAIDSBAAAADAhAAEAAAIgBAADoAAAEgBAIIAAEABERQ0IAAAgKCIgAEAAIAAAxIkAAkAKAAILiQFAAgIAiAAABAAAAAIABAAMAAAAIAAACAAIAAAAAAAAAgAAAAAACABAIAAAAAAAAII3wPQAFgAVAAuABwADwAIAAVAAyABoADwAJgAXAAxABoADeAH4AQgAhgBNACcAGAAMMAc4A7oB-AH6AQgAiwBHACRAEmAJSAWIAxQBrwDaAHEAO2Af0A_4CLwErAJiATIAmkBQ4CjwFIgKbAU-At0BcgC8wGQgMkAZYAy4BpoDiwHjgQrAjeAAA.f_gACHgAAAA',
        '__cmpcccx47082': 'aCQYui6hgAAh_RqxozGI0rCyOeIZk1NDIGQ0GYsSxBghqZWKmC9CerFiRiamGSNSwsZNTVkhoZDLDKajJoYsDRMGDLJGGRC0ExaksVYRgSYAAA',
        '_cc_id': '870093237fb05496cfd48ed954561d73',
        'panoramaId_expiry': '1760077199952',
        'panoramaId': '962a795531b7c466f3736667a8c3185ca02c3382d7333b1eca5acb185015aa03',
        'panoramaIdType': 'panoDevice',
        'connectId': '{"ttl":86400000,"lastUsed":1759472400813,"lastSynced":1759472400813}',
        'emqsegs': 'e0,e3m,ey,ed,e38,e3i,e3s,ec,e3o,e3b,e1,e8',
        '__gads': 'ID=37a4d38a6355e67a:T=1759472400:RT=1759474482:S=ALNI_Ma8PYixZyZDnk9LiDRfo8ZKp1bEbA',
        '__gpi': 'UID=0000129399e70ef0:T=1759472400:RT=1759474482:S=ALNI_MbmfZvq29zMNdz2yfqjWDK2jGQJWw',
        '__eoi': 'ID=d2a31613eb138f89:T=1759472400:RT=1759474482:S=AA-AfjZtB12hn8hOxQQNPte-4bkZ',
        'cto_bundle': 'qIDl2181Y09pNmhWRFlhVWtRUXVqQ1Z5WXY2b0olMkIxUGpzaFNuanlXcGFqUUYzZVFtaWdtM0l5bDdSdWRQcW1IbFZCQ3A2SU0lMkY4bkJDSFdmSnY2MHlsRmtQejVnWnpTVHpVM2x3bEVFYW84QVB0RjBCaWo1QnB2QWdFV29WMHlaRVp5cE5yZ0h1c1dOY3ZHdnFOaUdFYTFkaG9SdDhZYzYlMkZQT2owZzYwSFdxUURuRzAlM0Q'
    }
    session.cookies.update(cookies)
    return session

def get_all_liga_ids_paginated(session, season):
    """
    Get ALL liga_ids by following pagination
    """
    
    all_liga_ids = []
    visited_startrows = set()
    startrow = 0
    page = 1
    while True:
        print(f"    📄 Fetching page {page} (startrow={startrow})")
        if startrow == 0:
            url = 'https://www.basketball-bund.net/index.jsp?Action=106'
        else:
            url = f'https://www.basketball-bund.net/index.jsp?Action=106&startrow={startrow}&viewid='
        post_data = {
            'saison_id': str(season),
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '-3',
            'cbGeschlechtFilter': '0',
            'cbBezirkFilter': '5',
            'cbKreisFilter': '0'
        }
        try:
            response = session.post(url, data=post_data, timeout=30)
            if response.status_code != 200:
                print(f"      ❌ HTTP {response.status_code}")
                break
            print(f"      ✅ Response: {len(response.text):,} chars")
            page_filename = f'action_106_page_{page}_{season}_startrow_{startrow}.html'
            with open(page_filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_liga_ids = extract_liga_ids_from_page(soup)
            if not page_liga_ids:
                print(f"      ❌ No liga_ids found on page {page}")
                break
            print(f"      📋 Found {len(page_liga_ids)} liga_ids on page {page}")
            all_liga_ids.extend(page_liga_ids)
            visited_startrows.add(startrow)
            # Find all possible startrow links on the page
            next_startrows = set()
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                match = re.search(r'startrow=(\d+)', href)
                if match:
                    sr = int(match.group(1))
                    if sr not in visited_startrows:
                        next_startrows.add(sr)
            if next_startrows:
                startrow = min(next_startrows)
                page += 1
                time.sleep(random.uniform(1, 2))
                continue
            print(f"      ✅ Last page reached")
            break
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
        
        if response.status_code != 200 or not response.text:
            print(f"      💥 Error crawling league {liga_id}: HTTP {response.status_code}")
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        players = extract_players_from_statistik(soup, liga_id, league_name, season, 'Action=107')
        
        return players
        
    except Exception as e:
        print(f"      💥 Error crawling league {liga_id}: {str(e)[:50]}")
        return []

def extract_players_from_statistik(soup, liga_id, league_name, season, endpoint):
    """
    Extract player data from statistik.do endpoints
    """
    players = []
    tables = soup.find_all('table')
    for table_idx, table in enumerate(tables):
        rows = table.find_all('tr')
        if len(rows) < 2:
            continue
        header_row = rows[0]
        header_cells = header_row.find_all(['th', 'td'])
        header_texts = [cell.get_text(strip=True).lower() for cell in header_cells]
        player_indicators = ['name', 'spieler', 'punkte', 'spiele', 'team', 'mannschaft', 'quote', '3er']
        if not any(indicator in ' '.join(header_texts) for indicator in player_indicators):
            continue
        for row_idx, row in enumerate(rows[1:], 1):
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            if not cell_texts[0] or len(cell_texts[0]) < 2:
                continue
            if any(header_word in cell_texts[0].lower() for header_word in ['name', 'spieler', 'rang', 'pos']):
                continue
            player = {
                'name': cell_texts[0],
                'season_id': season,
                'liga_id': str(liga_id),
                'league_name': league_name,
                'endpoint': endpoint,
                'table_index': table_idx,
                'row_index': row_idx,
                'extracted_at': datetime.now().isoformat(),
                'raw_data': cell_texts
            }
            for i, value in enumerate(cell_texts[1:], 1):
                player[f'col_{i}'] = value
            players.append(player)
    return players

def crawl_statistik_endpoint(session, liga_id, season, endpoint):
    url = f'https://www.basketball-bund.net/statistik.do?reqCode={endpoint}&liga_id={liga_id}&saison_id={season}&_top=-1'
    try:
        response = session.get(url, timeout=30)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        return extract_players_from_statistik(soup, liga_id, '', season, endpoint)
    except Exception as e:
        print(f"      💥 Error crawling {endpoint} for liga {liga_id}: {str(e)[:50]}")
        return []

def crawl_league_results(session, liga_id, league_name, season):
    url = f'https://www.basketball-bund.net/index.jsp?Action=108&liga_id={liga_id}&saison_id={season}&defaultview=1'
    try:
        response = session.get(url, timeout=30)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract results table rows
        tables = soup.find_all('table')
        results = []
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                if cell_texts:
                    results.append(cell_texts)
        return results
    except Exception as e:
        print(f"      💥 Error crawling results for liga {liga_id}: {str(e)[:50]}")
        return []

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
