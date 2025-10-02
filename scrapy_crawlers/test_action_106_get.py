#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def test_action_106_get_method():
    """
    Test Action=106 using GET method with URL parameters instead of POST
    Based on user's suggestion: Action=106 with URL parameters
    """
    
    print("🔍 TESTING ACTION=106 WITH GET METHOD")
    print("Using URL parameters instead of POST data")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    })
    
    # Test with 2010 
    season = 2010
    
    print(f"\n📅 Testing season {season}")
    
    try:
        # Build URL with GET parameters
        base_url = 'https://www.basketball-bund.net/index.jsp'
        params = {
            'Action': '106',
            'saison_id': str(season),
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '-3',
            'cbGeschlechtFilter': '0', 
            'cbBezirkFilter': '5',  # Oberfranken
            'cbKreisFilter': '0'
        }
        
        url = f"{base_url}?Action=106&saison_id={season}&cbSpielklasseFilter=0&cbAltersklasseFilter=-3&cbGeschlechtFilter=0&cbBezirkFilter=5&cbKreisFilter=0"
        
        print(f"🔗 URL: {url}")
        
        response = session.get(url, timeout=30)
        
        print(f"📥 Status: {response.status_code}")
        print(f"📏 Response size: {len(response.text):,} chars")
        
        if response.status_code == 200:
            # Save response for analysis
            filename = f'test_action106_get_{season}.html'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"💾 Saved response: {filename}")
            
            # Check for "Keine Einträge gefunden"
            if 'Keine Einträge gefunden' in response.text:
                print("❌ Server returned 'Keine Einträge gefunden'")
            else:
                print("✅ No 'Keine Einträge gefunden' message")
            
            # Parse league links
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for Action=107 links
            action_107_links = soup.find_all('a', href=re.compile(r'Action=107'))
            print(f"\n🏀 Found {len(action_107_links)} Action=107 links:")
            
            for i, link in enumerate(action_107_links[:10]):  # Show first 10
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"  {i+1}. {text}")
                print(f"     {href}")
            
            # Also look for any links with liga_id
            liga_id_links = soup.find_all('a', href=re.compile(r'liga_id='))
            print(f"\n🔗 Found {len(liga_id_links)} liga_id links:")
            
            for i, link in enumerate(liga_id_links[:10]):  # Show first 10
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Extract liga_id
                liga_id_match = re.search(r'liga_id=(\d+)', href)
                if liga_id_match:
                    liga_id = liga_id_match.group(1)
                    print(f"  {i+1}. {text} (liga_id: {liga_id})")
                    print(f"     {href}")
            
            # Look in tables specifically
            tables = soup.find_all('table')
            print(f"\n📊 Found {len(tables)} tables in response")
            
            for table_idx, table in enumerate(tables):
                table_links = table.find_all('a', href=re.compile(r'Action=107|liga_id='))
                if table_links:
                    print(f"  Table {table_idx+1}: {len(table_links)} league links")
                    for link in table_links[:3]:  # Show first 3 from each table
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        print(f"    - {text}: {href}")
                        
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")

if __name__ == "__main__":
    test_action_106_get_method()
