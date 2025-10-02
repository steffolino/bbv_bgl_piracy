#!/usr/bin/env python3
"""
Debug Action=106 for specific league and year problems
SAVE LEAGUE NAMES AND IDs!
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def debug_league_extraction():
    """Debug exactly what leagues we get and save names + IDs"""
    
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
    
    # Test multiple seasons to see pattern
    seasons_to_test = ['2010', '2018', '2024']
    
    for season in seasons_to_test:
        print(f"\n{'='*60}")
        print(f"TESTING SEASON {season} - OBERFRANKEN LEAGUES")
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
        
        data = {
            'saison_id': season,
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '-3',
            'cbGeschlechtFilter': '0',
            'cbBezirkFilter': '5',  # Oberfranken
            'cbKreisFilter': '0'
        }
        
        try:
            response = session.post(url, headers=headers, data=data)
            print(f"Status: {response.status_code}")
            print(f"Response length: {len(response.text)}")
            
            # Save the full response
            filename = f'action106_season_{season}_oberfranken.html'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"Full response saved to: {filename}")
            
            # Parse the response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for different indicators
            checks = [
                "Keine Einträge gefunden",
                "No entries found", 
                "Liga",
                "liga_id=",
                "Tabelle",
                "table",
                "Oberliga",
                "Regionalliga",
                "Landesliga"
            ]
            
            print("\n--- CONTENT CHECKS ---")
            for check in checks:
                count = response.text.count(check)
                if count > 0:
                    print(f"✅ '{check}': {count} occurrences")
                else:
                    print(f"❌ '{check}': not found")
            
            # Extract ALL links with liga_id
            print("\n--- LEAGUE EXTRACTION ---")
            leagues_found = []
            
            # Method 1: Look in href attributes
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if 'liga_id=' in href:
                    match = re.search(r'liga_id=(\d+)', href)
                    if match:
                        liga_id = match.group(1)
                        league_name = link.get_text(strip=True)
                        if league_name and liga_id:
                            leagues_found.append({
                                'id': liga_id,
                                'name': league_name,
                                'href': href
                            })
            
            # Method 2: Look in onclick events
            onclick_elements = soup.find_all(attrs={"onclick": True})
            for element in onclick_elements:
                onclick = element.get('onclick', '')
                if 'liga_id' in onclick:
                    match = re.search(r'liga_id[=:]\s*["\']?(\d+)', onclick)
                    if match:
                        liga_id = match.group(1)
                        league_name = element.get_text(strip=True)
                        if league_name and liga_id:
                            leagues_found.append({
                                'id': liga_id,
                                'name': league_name,
                                'onclick': onclick
                            })
            
            # Method 3: Look in form inputs or hidden fields
            inputs = soup.find_all('input', attrs={'name': re.compile(r'liga_id', re.I)})
            for inp in inputs:
                liga_id = inp.get('value', '')
                if liga_id:
                    # Find associated label or nearby text
                    parent = inp.find_parent()
                    if parent:
                        league_name = parent.get_text(strip=True)
                        leagues_found.append({
                            'id': liga_id,
                            'name': league_name,
                            'input_type': inp.get('type', 'unknown')
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
                print("\n--- LEAGUE NAMES AND IDs ---")
                for i, league in enumerate(unique_leagues, 1):
                    print(f"{i:2d}. ID: {league['id']:>6} | NAME: {league['name']}")
                
                # Save to JSON
                json_filename = f'leagues_season_{season}_oberfranken.json'
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(unique_leagues, f, indent=2, ensure_ascii=False)
                print(f"\nLeagues saved to: {json_filename}")
            else:
                print("❌ NO LEAGUES FOUND!")
                print("\n--- CHECKING FOR ERROR MESSAGES ---")
                
                # Look for common German error messages
                error_patterns = [
                    r"Keine.*gefunden",
                    r"Nicht.*verfügbar", 
                    r"Error",
                    r"Fehler",
                    r"Session.*expired",
                    r"Anmeldung.*erforderlich"
                ]
                
                for pattern in error_patterns:
                    matches = re.findall(pattern, response.text, re.IGNORECASE)
                    if matches:
                        print(f"⚠️ Found error pattern '{pattern}': {matches}")
                
                # Show some sample content around potential issues
                print("\n--- SAMPLE CONTENT ---")
                lines = response.text.split('\n')
                for i, line in enumerate(lines):
                    if any(word in line.lower() for word in ['keine', 'error', 'fehler', 'liga', 'tabelle']):
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        print(f"Lines {start}-{end}:")
                        for j in range(start, end):
                            marker = ">>> " if j == i else "    "
                            print(f"{marker}{lines[j].strip()}")
                        print()
                        
        except Exception as e:
            print(f"❌ ERROR for season {season}: {e}")

if __name__ == "__main__":
    debug_league_extraction()
