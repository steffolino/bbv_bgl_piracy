#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

def test_bezirk_availability():
    """
    Test what Bezirk options are available for historical seasons
    """
    
    print("🔍 TESTING BEZIRK AVAILABILITY FOR HISTORICAL SEASONS")
    
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
    
    # Test seasons: 2013, 2018, 2024
    test_seasons = [2013, 2018, 2024]
    
    for season in test_seasons:
        print(f"\n📅 TESTING SEASON {season}")
        
        # Test with cbBezirkFilter=0 (all districts) first
        post_data = {
            'Action': '106',
            'saison_id': str(season),
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '-3',  # Senioren
            'cbGeschlechtFilter': '0',
            'cbBezirkFilter': '0',  # All Bezirke
            'cbKreisFilter': '0'
        }
        
        response = session.post(
            'https://www.basketball-bund.net/index.jsp?Action=106',
            data=post_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"  ✅ Response received: {len(response.text):,} chars")
            
            # Parse response to find available Bezirk options
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find cbBezirkFilter select element
            bezirk_select = soup.find('select', {'name': 'cbBezirkFilter'})
            if bezirk_select:
                options = bezirk_select.find_all('option')
                print(f"  📍 Available Bezirk options ({len(options)}):")
                for option in options:
                    value = option.get('value', 'N/A')
                    text = option.get_text(strip=True)
                    selected = 'SELECTED' if 'SELECTED' in str(option) else ''
                    print(f"    - Value: {value} | Text: {text} {selected}")
            else:
                print(f"  ❌ No cbBezirkFilter select found")
            
            # Check for actual league data in the response
            league_content = check_league_content(soup, season)
            if league_content:
                print(f"  📊 Found {len(league_content)} league entries")
                for i, league in enumerate(league_content[:3]):  # Show first 3
                    print(f"    {i+1}. {league}")
            else:
                print(f"  ❌ No league entries found in data table")
            
            # Save response for analysis
            filename = f"bezirk_test_{season}_cbBezirkFilter_0.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"  💾 Saved: {filename}")
        
        else:
            print(f"  ❌ HTTP {response.status_code}")

def check_league_content(soup, season):
    """
    Check for actual league content in the data table
    """
    league_entries = []
    
    # Look for table rows that might contain league data
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                # Filter out header/empty rows
                if (cell_texts[0] and 
                    'Liga' not in cell_texts[0] and 
                    'Name' not in cell_texts[0] and
                    'Kreis' not in cell_texts[0] and
                    len(cell_texts[0]) > 3):
                    league_entries.append(' | '.join(cell_texts[:3]))
    
    return league_entries

if __name__ == "__main__":
    test_bezirk_availability()
