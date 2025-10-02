#!/usr/bin/env python3
"""
Test the Oberfranken Bezirksoberliga Herren liga_id=26211 to see if we find BG Litzendorf
"""

import requests
from bs4 import BeautifulSoup
import re

def test_oberfranken_bezirksoberliga():
    """Test liga_id=26211 (Bezirksoberliga Herren) to find BG Litzendorf"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    })
    
    # Set cookies
    cookies = {
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
    
    for name, value in cookies.items():
        session.cookies.set(name, value, domain='www.basketball-bund.net')
        if name in ['__cmpconsentx47082', '__cmpcccx47082', '_cc_id', 'panoramaId_expiry', 'panoramaId', 'panoramaIdType', '__gads', '__gpi', '__eoi', 'cto_bundle']:
            session.cookies.set(name, value, domain='.basketball-bund.net')
    
    print("="*70)
    print("TESTING OBERFRANKEN BEZIRKSOBERLIGA HERREN (liga_id=26211)")
    print("="*70)
    
    # Test the statistik.do URL
    liga_id = "26211"
    statistik_url = f"https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id={liga_id}&saison_id=2018&_top=-1"
    
    print(f"Testing URL: {statistik_url}")
    
    try:
        response = session.get(statistik_url)
        print(f"Status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        if response.status_code == 200 and len(response.text) > 5000:
            print("✅ SUCCESS! Got substantial response")
            
            # Look for BG Litzendorf or Litzendorf
            litzendorf_count = response.text.count('Litzendorf')
            bg_count = response.text.count('BG')
            
            print(f"'Litzendorf' mentions: {litzendorf_count}")
            print(f"'BG' mentions: {bg_count}")
            
            if litzendorf_count > 0:
                print("🎉 FOUND LITZENDORF!")
                
                # Extract context around Litzendorf mentions
                lines = response.text.split('\n')
                for i, line in enumerate(lines):
                    if 'Litzendorf' in line:
                        print(f"\nLitzendorf context (line {i}):")
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        for j in range(start, end):
                            marker = ">>> " if j == i else "    "
                            print(f"{marker}{lines[j].strip()}")
            
            # Parse for players
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')
            print(f"\nTables found: {len(tables)}")
            
            # Look for player data in tables
            player_count = 0
            litzendorf_players = []
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_text = ' '.join([cell.get_text(strip=True) for cell in cells])
                    
                    if 'Litzendorf' in row_text:
                        litzendorf_players.append(row_text)
                    
                    # Count potential player rows (rows with name-like patterns)
                    if len(cells) >= 3 and any(cell.get_text(strip=True) for cell in cells):
                        player_count += 1
            
            print(f"Potential player rows: {player_count}")
            
            if litzendorf_players:
                print(f"\n🎯 LITZENDORF PLAYERS FOUND ({len(litzendorf_players)}):")
                for i, player in enumerate(litzendorf_players, 1):
                    print(f"{i:2d}. {player}")
            
            # Save response for analysis
            filename = f'oberfranken_bezirksoberliga_herren_2018.html'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"\nResponse saved to: {filename}")
            
        else:
            print("❌ Failed or empty response")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_oberfranken_bezirksoberliga()
