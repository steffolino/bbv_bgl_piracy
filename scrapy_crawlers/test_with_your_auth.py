#!/usr/bin/env python3
"""
Test 2018 URL with YOUR PROVIDED authentication
"""

import requests
from bs4 import BeautifulSoup

def test_with_your_authentication():
    """Test using your exact authentication cookies"""
    
    session = requests.Session()
    
    # Set User-Agent
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    })
    
    # Add your authentication cookies
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
        # Also set for .basketball-bund.net domain for some cookies
        if name in ['__cmpconsentx47082', '__cmpcccx47082', '_cc_id', 'panoramaId_expiry', 'panoramaId', 'panoramaIdType', '__gads', '__gpi', '__eoi', 'cto_bundle']:
            session.cookies.set(name, value, domain='.basketball-bund.net')

    # Test the exact 2018 working URL
    test_url = "https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id=26212&saison_id=2018&_top=-1"
    
    print(f"Testing with YOUR authentication cookies:")
    print(f"URL: {test_url}")
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7',
        'cache-control': 'no-cache',
        'dnt': '1',
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
    
    try:
        response = session.get(test_url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        
        # Check for success indicators
        if "reqCode" in response.text and "does not contain handler" in response.text:
            print("❌ Still getting reqCode parameter error")
        elif "Seite nicht gefunden" in response.text:
            print("❌ Page not found")
        elif "Alexander" in response.text and "Flügel" in response.text:
            print("✅ SUCCESS! Found player data (Alexander Flügel from CSV)")
        elif len(response.text) > 5000:
            print("✅ SUCCESS! Got substantial HTML content")
        else:
            print("⚠️  Unclear result")
            
        # Look for table content
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        print(f"Tables found: {len(tables)}")
        
        if tables:
            # Check first table for player data
            first_table = tables[0]
            rows = first_table.find_all('tr')
            print(f"Rows in first table: {len(rows)}")
            
            # Look for actual player names from our CSV
            known_players = ['Alexander', 'Flügel', 'Patrick', 'Geber', 'Schuster']
            for player in known_players:
                if player in response.text:
                    print(f"✅ Found expected player: {player}")
                    break
            else:
                print("❌ No expected players found")
        
        # Save response
        with open('test_with_your_auth_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Response saved to test_with_your_auth_response.html")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_with_your_authentication()
