#!/usr/bin/env python3
"""
Test Action=106 WITHOUT Bezirk filter to see ALL leagues
Then find which Bezirk actually contains our leagues
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def test_all_districts():
    """Test Action=106 without Bezirk filter to find ALL leagues"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    })
    
    # Your working authentication cookies
    cookies = {
        '__cmpcc': '1',
        '__cmpconsentx47082': 'CQYqGvAQYqGvAAfQ6BENB-FgAP_AAEPAAAigJSkR5C5cDWFBeTp3QMskeYQX0cgBZgABAgaAASABCDAAcIQAkkESIAyAAAACAQAAIDSBAAAADAhAAEAAAIgBAADoAAAEgBAIIAAEABERQ0IAAAgKCIgAEAAIAAAxIkAAkAKAAILiQFAAgIAiAAABAAAAAIABAAMAAAAIAAACAAIAAAAAAAAAgAAAAAACABAIAAAAAAAAII3wPgAFgAVAAuABwADwAIAAVAAyABoADwAI4ATAAuABiADQAG8APwAhABDACaAE4AMAAYYA5wB3QD8AP0AhABFgCOAEiAJMASkAsQBigDXgG0AOIAdsA_oB_wEXgJWATEAmQBNIChwFHgKRAU2Ap8BboC5AF5gMhAZIAywBlwDTQHFgPHAhWBG8AAA.f_gACHgAAAA',
        '__cmpcccx47082': 'aCQYrQy_gAAhfRqxozGIxJkc8QzJqaGQMhoMxYliDBDUysVMF6E9WLEjE1MMkalhYyamrJDQyGWGU1GTQxYGiYMGWSMMiFoJi1JYqwjAkwAA',
        '_cc_id': 'b616c325dc88e1ae505ba80bd46882fe',
        'panoramaId_expiry': '1759991137726',
        'panoramaId': '947c1d27b3bb8d4dfc70e52580f3185ca02cacef30144e43784f041253e24e3a',
        'panoramaIdType': 'panoDevice',
        'connectId': '{"ttl":86400000,"lastUsed":1759386336895,"lastSynced":1759386336895}',
        'SESSION': 'NTAwZTU4MjYtZDFjNC00NGI5LWIyMGItMWM1YmFhZjhjZjll',
        'emqsegs': 'e0,e3m,ey,ed,e38,e3g,e3q,ec,e3o,e3b,e1,e8',
        '__gads': 'ID=2606604e4e061425:T=1759386338:RT=1759401127:S=ALNI_MboJFcXJE4aqMFvtQzMYf84WND8Jg',
        '__gpi': 'UID=0000129342773779:T=1759386338:RT=1759401127:S=ALNI_MYebYj8D0sws2npwfXIogpqvTFm6w',
        '__eoi': 'ID=cf36713925753e4a:T=1759386338:RT=1759401127:S=AA-AfjZXc8kz_f8dFx3IWngcOT9S',
        'cto_bundle': 'H6fkil9jU0JWa1dYbzRqclJ1a2RiOWxPVVR4akgwUHg3QkhhOWUybmRGWU9FSzlhaXhnR2hVWVVaZm9Ha010Y0xuNUZyYkVCTjJ6aHk0ajZUekJuMnhtTU1zUDhiV3gwbVZ5YyUyQkkzN25BUWhWN2U2aVh4aktQU0VsclZCdElNYW01TnN1SDglMkJXdFhpYUxSWjNmUnl6NTcwUmpwWVoxTFBWdjFRaXNwakVWRGtIazZ3JTNE'
    }
    
    for name, value in cookies.items():
        session.cookies.set(name, value, domain='www.basketball-bund.net')
        if name in ['__cmpconsentx47082', '__cmpcccx47082', '_cc_id', 'panoramaId_expiry', 'panoramaId', 'panoramaIdType', '__gads', '__gpi', '__eoi', 'cto_bundle']:
            session.cookies.set(name, value, domain='.basketball-bund.net')
    
    print(f"{'='*60}")
    print(f"TESTING 2018 - ALL DISTRICTS (cbBezirkFilter=0)")
    print(f"{'='*60}")
    
    url = "https://www.basketball-bund.net/index.jsp?Action=106"
    headers = {
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
    
    # Use 0 for "alle Bezirke" instead of 5 for Oberfranken
    data = {
        'saison_id': '2018',
        'cbSpielklasseFilter': '0',
        'cbAltersklasseFilter': '-3',
        'cbGeschlechtFilter': '0',
        'cbBezirkFilter': '0',  # ALL DISTRICTS
        'cbKreisFilter': '0'
    }
    
    try:
        response = session.post(url, headers=headers, data=data)
        print(f"Status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        # Save the full response
        filename = f'action106_2018_ALL_districts.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Full response saved to: {filename}")
        
        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if "Keine Einträge gefunden" in response.text:
            print("❌ Still no entries found even with ALL districts!")
            return
        
        print("✅ Found entries! Extracting leagues...")
        
        # Extract ALL leagues with their names, IDs, and districts
        leagues_found = []
        
        # Look for liga_id in href attributes
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if 'liga_id=' in href:
                match = re.search(r'liga_id=(\d+)', href)
                if match:
                    liga_id = match.group(1)
                    league_name = link.get_text(strip=True)
                    if league_name and liga_id:
                        # Try to find the district/bezirk info
                        parent_row = link.find_parent('tr')
                        bezirk = "Unknown"
                        if parent_row:
                            cells = parent_row.find_all(['td', 'th'])
                            if len(cells) >= 4:  # Assuming structure: Name, Bezirk, Kreis, etc.
                                for cell in cells:
                                    cell_text = cell.get_text(strip=True)
                                    if any(word in cell_text.lower() for word in ['bayern', 'franken', 'ober', 'unter', 'mittel']):
                                        bezirk = cell_text
                                        break
                        
                        leagues_found.append({
                            'id': liga_id,
                            'name': league_name,
                            'bezirk': bezirk,
                            'href': href
                        })
        
        # Remove duplicates
        unique_leagues = []
        seen_ids = set()
        for league in leagues_found:
            if league['id'] not in seen_ids:
                unique_leagues.append(league)
                seen_ids.add(league['id'])
        
        print(f"Total unique leagues found: {len(unique_leagues)}")
        
        if unique_leagues:
            print("\n--- ALL LEAGUE NAMES, IDs, AND DISTRICTS ---")
            for i, league in enumerate(unique_leagues, 1):
                print(f"{i:3d}. ID: {league['id']:>6} | BEZIRK: {league['bezirk']:>15} | NAME: {league['name']}")
            
            # Look specifically for Oberfranken/Franken leagues
            franken_leagues = []
            for league in unique_leagues:
                if any(word in league['name'].lower() + league['bezirk'].lower() for word in 
                       ['franken', 'oberfranken', 'bamberg', 'bayreuth', 'coburg', 'hof', 'litzendorf', 'bezirk ober']):
                    franken_leagues.append(league)
            
            if franken_leagues:
                print(f"\n--- FRANKEN/OBERFRANKEN LEAGUES ({len(franken_leagues)}) ---")
                for i, league in enumerate(franken_leagues, 1):
                    print(f"{i:2d}. ID: {league['id']:>6} | BEZIRK: {league['bezirk']:>15} | NAME: {league['name']}")
            
            # Save to JSON
            json_filename = f'all_leagues_2018_districts.json'
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(unique_leagues, f, indent=2, ensure_ascii=False)
            print(f"\nAll leagues saved to: {json_filename}")
            
            if franken_leagues:
                franken_json = f'franken_leagues_2018.json'
                with open(franken_json, 'w', encoding='utf-8') as f:
                    json.dump(franken_leagues, f, indent=2, ensure_ascii=False)
                print(f"Franken leagues saved to: {franken_json}")
        else:
            print("❌ NO LEAGUES FOUND!")
                        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_all_districts()
