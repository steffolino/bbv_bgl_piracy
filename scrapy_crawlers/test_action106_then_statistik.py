#!/usr/bin/env python3
"""
Test Action=106 to get valid liga_ids, then test statistik.do with those exact liga_ids
"""

import requests
from bs4 import BeautifulSoup
import re

def test_action106_then_statistik():
    """Test the full workflow: Action=106 → get liga_id → test statistik.do"""
    
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
    
    # Step 1: Test Action=106 for season 2010
    print("=== STEP 1: Action=106 for season 2010 ===")
    
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
        'saison_id': '2010',
        'cbSpielklasseFilter': '0',
        'cbAltersklasseFilter': '-3',
        'cbGeschlechtFilter': '0',
        'cbBezirkFilter': '5',  # Oberfranken
        'cbKreisFilter': '0'
    }
    
    try:
        response = session.post(url, headers=headers, data=data)
        print(f"Action=106 status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        # Save response first to see what we get
        with open('test_action106_2010.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Action=106 response saved to test_action106_2010.html")
        
        # Check what the actual content contains
        print("\n=== CONTENT PREVIEW ===")
        print(response.text[:1000])
        print("...")
        print(response.text[-500:])
        
        if "Keine Einträge gefunden" in response.text:
            print("❌ No leagues found message detected")
            return
        
        # Parse liga_ids from response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for liga_id in links
        liga_ids = []
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            match = re.search(r'liga_id=(\d+)', href)
            if match:
                liga_id = match.group(1)
                if liga_id not in liga_ids:
                    liga_ids.append(liga_id)
        
        print(f"Found liga_ids: {liga_ids}")
        
        # Save Action=106 response
        with open('test_action106_2010.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Action=106 response saved to test_action106_2010.html")
        
        if not liga_ids:
            print("❌ No liga_ids found in Action=106 response")
            return
        
        # Step 2: Test statistik.do with first valid liga_id
        print(f"\n=== STEP 2: Test statistik.do with liga_id {liga_ids[0]} ===")
        
        test_liga_id = liga_ids[0]
        statistik_url = f"https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id={test_liga_id}&saison_id=2010&_top=-1"
        
        print(f"Testing: {statistik_url}")
        
        stat_response = session.get(statistik_url)
        print(f"Statistik status: {stat_response.status_code}")
        print(f"Statistik response length: {len(stat_response.text)}")
        
        # Check for errors
        if "does not contain handler parameter" in stat_response.text:
            print("❌ Handler parameter error")
        elif "reqCode" in stat_response.text and "Error" in stat_response.text:
            print("❌ reqCode error")
        elif "Seite nicht gefunden" in stat_response.text:
            print("❌ Page not found")
        else:
            print("✅ No obvious errors")
            
        # Look for player data
        stat_soup = BeautifulSoup(stat_response.text, 'html.parser')
        tables = stat_soup.find_all('table')
        print(f"Tables found: {len(tables)}")
        
        if tables:
            first_table = tables[0]
            rows = first_table.find_all('tr')
            print(f"Rows in first table: {len(rows)}")
            
            # Show first few rows
            for i, row in enumerate(rows[:5]):
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                print(f"Row {i}: {cell_texts}")
        
        # Save statistik response
        with open(f'test_statistik_liga_{test_liga_id}.html', 'w', encoding='utf-8') as f:
            f.write(stat_response.text)
        print(f"Statistik response saved to test_statistik_liga_{test_liga_id}.html")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_action106_then_statistik()
