#!/usr/bin/env python3
"""
NOW test the complete workflow with Oberfranken filter (cbBezirkFilter=5)
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def test_complete_oberfranken_workflow():
    """Test the complete workflow with Oberfranken filter"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    })
    
    # Set initial cookies
    initial_cookies = {
        '__cmpcc': '1',
        '__cmpconsentx47082': 'CQYqGvAQYqGvAAfQ6BENB-FgAP_AAEPAAAigJSkR5C5cDWFBeTp3QMskeYQX0cgBZgABAgaAASABCDAAcIQAkkESIAyAAAACAQAAIDSBAAAADAhAAEAAAIgBAADoAAAEgBAIIAAEABERQ0IAAAgKCIgAEAAIAAAxIkAAkAKAAILiQFAAgIAiAAABAAAAAIABAAMAAAAIAAACAAIAAAAAAAAAgAAAAAACABAIAAAAAAAAII3wPgAFgAVAAuABwADwAIAAVAAyABoADwAI4ATAAuABiADQAG8APwAhABDACaAE4AMAAYYA5wB3QD8AP0AhABFgCOAEiAJMASkAsQBigDXgG0AOIAdsA_oB_wEXgJWATEAmQBNIChwFHgKRAU2Ap8BboC5AF5gMhAZIAywBlwDTQHFgPHAhWBG8AAA.f_gACHgAAAA',
        '__cmpcccx47082': 'aCQYrQy_gAAhfRqxozGIxJkc8QzJqaGQMhoMxYliDBDUysVMF6E9WLEjE1MMkalhYyamrJDQyGWGU1GTQxYGiYMGWSMMiFoJi1JYqwjAkwAA',
        '_cc_id': 'b616c325dc88e1ae505ba80bd46882fe',
        'panoramaId_expiry': '1759991137726',
        'panoramaId': '947c1d27b3bb8d4dfc70e52580f3185ca02cacef30144e43784f041253e24e3a',
        'panoramaIdType': 'panoDevice',
        'connectId': '{"ttl":86400000,"lastUsed":1759386336895,"lastSynced":1759386336895}',
        'emqsegs': 'e0,e3m,ey,ed,e38,e3i,e3s,ec,e3o,e3b,e1,e8',
        '__gads': 'ID=2606604e4e061425:T=1759386338:RT=1759404996:S=ALNI_MboJFcXJE4aqMFvtQzMYf84WND8Jg',
        '__gpi': 'UID=0000129342773779:T=1759386338:RT=1759404996:S=ALNI_MYebYj8D0sws2npwfXIogpqvTFm6w',
        '__eoi': 'ID=cf36713925753e4a:T=1759386338:RT=1759404996:S=AA-AfjZXc8kz_f8dFx3IWngcOT9S',
        'cto_bundle': '1pWV-19jU0JWa1dYbzRqclJ1a2RiOWxPVVR4Y2RwZDBCOTFlblNScTdCdTkxbXVsQm5HN3lyY1JzSk9pZFB5a3UxanEwbVglMkZUZTdBOERXRTJhbHZFMldsUUhMWFVuQWFnSUxNaVdJOGNJeXBlM3hFJTJCOGY5eWo4M3RSSmFvQlhrcTIxTkpxaEJOYjYlMkJUZGZKN2ZsZ0klMkZkdXpwM1I1V2lvdlp0YWpkemQ0aW85R1ZRayUzRA'
    }
    
    for name, value in initial_cookies.items():
        session.cookies.set(name, value, domain='www.basketball-bund.net')
        if name in ['__cmpconsentx47082', '__cmpcccx47082', '_cc_id', 'panoramaId_expiry', 'panoramaId', 'panoramaIdType', '__gads', '__gpi', '__eoi', 'cto_bundle']:
            session.cookies.set(name, value, domain='.basketball-bund.net')
    
    try:
        # Step 1: Setup session
        print("="*60)
        print("STEP 1: Setup Bayern session state")
        print("="*60)
        
        step1_url = "https://www.basketball-bund.net/index.jsp?Action=100&Verband=2"
        step1_response = session.get(step1_url)
        print(f"Step 1 status: {step1_response.status_code}")
        
        # Step 2: Get Action=106 to setup filters
        print("\nSTEP 2: Get Action=106 page")
        step2_url = "https://www.basketball-bund.net/index.jsp?Action=106"
        step2_headers = {
            'referer': 'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2'
        }
        step2_response = session.get(step2_url, headers=step2_headers)
        print(f"Step 2 status: {step2_response.status_code}")
        
        # Step 3: POST with Oberfranken filter for season 2018
        print("\nSTEP 3: POST Action=106 with Oberfranken filter (season 2018)")
        print("="*60)
        
        post_url = "https://www.basketball-bund.net/index.jsp?Action=106"
        post_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'dnt': '1',
            'origin': 'https://www.basketball-bund.net',
            'pragma': 'no-cache',
            'referer': 'https://www.basketball-bund.net/index.jsp?Action=106',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1'
        }
        
        post_data = {
            'saison_id': '2018',
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '-3',
            'cbGeschlechtFilter': '0',
            'cbBezirkFilter': '5',  # Oberfranken - NOW THIS SHOULD WORK!
            'cbKreisFilter': '0'
        }
        
        post_response = session.post(post_url, headers=post_headers, data=post_data)
        print(f"POST status: {post_response.status_code}")
        print(f"POST response length: {len(post_response.text)}")
        
        # Save response
        filename = 'oberfranken_2018_leagues.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(post_response.text)
        print(f"Response saved to: {filename}")
        
        # Parse response
        soup = BeautifulSoup(post_response.text, 'html.parser')
        
        if "Keine Einträge gefunden" in post_response.text:
            print("❌ Still no entries found for Oberfranken 2018")
        else:
            print("✅ SUCCESS! Found Oberfranken leagues for 2018!")
            
            # Extract leagues with names and IDs
            leagues_found = []
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                if 'liga_id=' in href:
                    match = re.search(r'liga_id=(\d+)', href)
                    if match:
                        liga_id = match.group(1)
                        league_name = link.get_text(strip=True)
                        
                        # Get parent row for additional info
                        parent_row = link.find_parent('tr')
                        bezirk = "Unknown"
                        kreis = "Unknown"
                        
                        if parent_row:
                            cells = parent_row.find_all(['td', 'th'])
                            if len(cells) >= 4:
                                # Try to extract Bezirk and Kreis from cells
                                for i, cell in enumerate(cells):
                                    cell_text = cell.get_text(strip=True)
                                    if i == 1:  # Assuming Bezirk is 2nd column
                                        bezirk = cell_text
                                    elif i == 2:  # Assuming Kreis is 3rd column
                                        kreis = cell_text
                        
                        if league_name and liga_id:
                            leagues_found.append({
                                'id': liga_id,
                                'name': league_name,
                                'bezirk': bezirk,
                                'kreis': kreis,
                                'href': href
                            })
            
            # Remove duplicates
            unique_leagues = []
            seen_ids = set()
            for league in leagues_found:
                if league['id'] not in seen_ids:
                    unique_leagues.append(league)
                    seen_ids.add(league['id'])
            
            print(f"\nTotal Oberfranken leagues found: {len(unique_leagues)}")
            
            if unique_leagues:
                print("\n--- OBERFRANKEN LEAGUES 2018 ---")
                for i, league in enumerate(unique_leagues, 1):
                    print(f"{i:2d}. ID: {league['id']:>6} | NAME: {league['name']}")
                    if league['kreis'] != "Unknown":
                        print(f"     BEZIRK: {league['bezirk']} | KREIS: {league['kreis']}")
                
                # Save to JSON
                json_filename = 'oberfranken_leagues_2018_WORKING.json'
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(unique_leagues, f, indent=2, ensure_ascii=False)
                print(f"\n✅ OBERFRANKEN LEAGUES SAVED TO: {json_filename}")
                
                # Test one league with statistik.do
                if unique_leagues:
                    test_liga_id = unique_leagues[0]['id']
                    test_name = unique_leagues[0]['name']
                    
                    print(f"\n--- TESTING STATISTIK.DO WITH LIGA_ID {test_liga_id} ---")
                    print(f"League: {test_name}")
                    
                    statistik_url = f"https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id={test_liga_id}&saison_id=2018&_top=-1"
                    stat_response = session.get(statistik_url)
                    
                    print(f"Statistik status: {stat_response.status_code}")
                    print(f"Statistik response length: {len(stat_response.text)}")
                    
                    if stat_response.status_code == 200 and len(stat_response.text) > 10000:
                        print("✅ Statistik.do WORKS with this liga_id!")
                        
                        # Count tables (players)
                        stat_soup = BeautifulSoup(stat_response.text, 'html.parser')
                        tables = stat_soup.find_all('table')
                        print(f"Player tables found: {len(tables)}")
                        
                        # Save sample
                        with open(f'sample_statistik_liga_{test_liga_id}.html', 'w', encoding='utf-8') as f:
                            f.write(stat_response.text)
                        print(f"Sample saved to: sample_statistik_liga_{test_liga_id}.html")
                    else:
                        print("❌ Statistik.do not working with this liga_id")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_complete_oberfranken_workflow()
