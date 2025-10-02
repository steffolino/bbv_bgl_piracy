#!/usr/bin/env python3
"""
Follow the EXACT workflow: Action=100&Verband=2 → click Spielbetrieb-Archiv → Action=106
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def follow_proper_workflow():
    """Follow the exact navigation workflow to get to Action=106 properly"""
    
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
    
    print("="*60)
    print("STEP 1: GET Action=100&Verband=2 (setup session state)")
    print("="*60)
    
    # Step 1: Visit Action=100&Verband=2 to set up session state
    step1_url = "https://www.basketball-bund.net/index.jsp?Action=100&Verband=2"
    step1_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1'
    }
    
    try:
        step1_response = session.get(step1_url, headers=step1_headers)
        print(f"Step 1 status: {step1_response.status_code}")
        print(f"Step 1 response length: {len(step1_response.text)}")
        
        # Check if we got a new SESSION cookie
        session_cookie = None
        for cookie in session.cookies:
            if cookie.name == 'SESSION':
                session_cookie = cookie.value
                print(f"SESSION cookie: {session_cookie}")
                break
        
        # Save step 1 response
        with open('step1_action100_verband2.html', 'w', encoding='utf-8') as f:
            f.write(step1_response.text)
        print("Step 1 response saved to: step1_action100_verband2.html")
        
        print("\n" + "="*60)
        print("STEP 2: GET Action=106 (with proper referer and session)")
        print("="*60)
        
        # Step 2: Now visit Action=106 with proper referer
        step2_url = "https://www.basketball-bund.net/index.jsp?Action=106"
        step2_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7',
            'cache-control': 'no-cache',
            'dnt': '1',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2',  # CRITICAL!
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1'
        }
        
        step2_response = session.get(step2_url, headers=step2_headers)
        print(f"Step 2 status: {step2_response.status_code}")
        print(f"Step 2 response length: {len(step2_response.text)}")
        
        # Save step 2 response
        with open('step2_action106_with_proper_referer.html', 'w', encoding='utf-8') as f:
            f.write(step2_response.text)
        print("Step 2 response saved to: step2_action106_with_proper_referer.html")
        
        # Parse step 2 response
        soup = BeautifulSoup(step2_response.text, 'html.parser')
        
        # Check for "Keine Einträge gefunden"
        if "Keine Einträge gefunden" in step2_response.text:
            print("❌ Still 'Keine Einträge gefunden' even with proper workflow")
        else:
            print("✅ Different response! No 'Keine Einträge gefunden'")
        
        # Check what bezirk options are available
        print("\n--- CHECKING BEZIRK FILTER OPTIONS ---")
        bezirk_select = soup.find('select', {'name': 'cbBezirkFilter'})
        if bezirk_select:
            options = bezirk_select.find_all('option')
            print(f"Bezirk filter options found: {len(options)}")
            for option in options:
                value = option.get('value', '')
                text = option.get_text(strip=True)
                selected = 'SELECTED' if option.get('selected') else ''
                print(f"  Option: value='{value}' text='{text}' {selected}")
        else:
            print("❌ No cbBezirkFilter select found")
        
        # Look for leagues
        print("\n--- CHECKING FOR LEAGUES ---")
        liga_links = soup.find_all('a', href=True)
        liga_count = 0
        for link in liga_links:
            href = link.get('href', '')
            if 'liga_id=' in href:
                liga_count += 1
                if liga_count <= 5:  # Show first 5
                    liga_match = re.search(r'liga_id=(\d+)', href)
                    liga_id = liga_match.group(1) if liga_match else 'unknown'
                    league_name = link.get_text(strip=True)
                    print(f"  Liga {liga_count}: ID={liga_id} NAME='{league_name}'")
        
        if liga_count > 5:
            print(f"  ... and {liga_count - 5} more leagues")
        elif liga_count == 0:
            print("❌ No liga_id links found")
        else:
            print(f"✅ Total {liga_count} leagues found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    follow_proper_workflow()
