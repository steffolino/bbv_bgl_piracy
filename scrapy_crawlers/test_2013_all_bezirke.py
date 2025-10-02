#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

def test_2013_all_bezirke():
    """
    Test 2013 with cbBezirkFilter=0 (all districts) to see what's available
    """
    
    print("🔍 TESTING 2013 WITH ALL BEZIRKE (cbBezirkFilter=0)")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.basketball-bund.net',
        'Referer': 'https://www.basketball-bund.net/index.jsp?Action=106',
    })
    
    # Try with cbBezirkFilter=0 (all districts)
    post_data = {
        'Action': '106',
        'saison_id': '2013',
        'cbSpielklasseFilter': '0',
        'cbAltersklasseFilter': '-3',
        'cbGeschlechtFilter': '0',
        'cbBezirkFilter': '0',  # ALL BEZIRKE
        'cbKreisFilter': '0'
    }
    
    response = session.post(
        'https://www.basketball-bund.net/index.jsp?Action=106',
        data=post_data,
        timeout=30
    )
    
    if response.status_code == 200:
        print(f"✅ Response: {len(response.text):,} chars")
        
        # Save response
        with open('action_106_response_2013_all_bezirke.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Parse and look for league links
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Search for liga_id links
        links = soup.find_all('a', href=True)
        liga_links = []
        
        for link in links:
            href = link.get('href', '')
            if 'liga_id=' in href:
                liga_links.append({
                    'href': href,
                    'text': link.get_text(strip=True)
                })
        
        print(f"🔗 Found {len(liga_links)} liga_id links:")
        for i, link in enumerate(liga_links[:10], 1):  # Show first 10
            print(f"  {i}. {link['text']} -> {link['href']}")
        
        if len(liga_links) > 10:
            print(f"  ... and {len(liga_links) - 10} more")
        
        # Also check Bezirk dropdown options
        bezirk_select = soup.find('select', {'name': 'cbBezirkFilter'})
        if bezirk_select:
            options = bezirk_select.find_all('option')
            print(f"\n📍 Available Bezirk options:")
            for option in options:
                value = option.get('value', 'N/A')
                text = option.get_text(strip=True)
                selected = 'SELECTED' if 'SELECTED' in str(option) else ''
                print(f"  - Value: {value} | Text: {text} {selected}")
        
        return len(liga_links) > 0
    
    else:
        print(f"❌ HTTP {response.status_code}")
        return False

if __name__ == "__main__":
    success = test_2013_all_bezirke()
    if success:
        print("\n✅ Found leagues for 2013! We can crawl historical data.")
    else:
        print("\n❌ No leagues found for 2013.")
