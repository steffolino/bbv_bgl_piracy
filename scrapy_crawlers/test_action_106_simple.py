#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def test_action_106_simple():
    """
    Test simple Action=106 GET request with URL parameters
    """
    
    print("🔍 TESTING SIMPLE ACTION=106")
    print("Using GET request with URL parameters")
    
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
        # Simple Action=106 URL - exactly as user suggested
        url = f"https://www.basketball-bund.net/index.jsp?Action=106&saison_id={season}&cbSpielklasseFilter=0&cbAltersklasseFilter=-3&cbGeschlechtFilter=0&cbBezirkFilter=5&cbKreisFilter=0"
        
        print(f"🔗 URL: {url}")
        
        response = session.get(url, timeout=30)
        
        print(f"📥 Status: {response.status_code}")
        print(f"📏 Response size: {len(response.text):,} chars")
        
        if response.status_code == 200:
            # Save response for analysis
            filename = f'action_106_simple_{season}.html'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"💾 Saved response: {filename}")
            
            # Check for "Keine Einträge gefunden"
            if 'Keine Einträge gefunden' in response.text:
                print("❌ Response contains 'Keine Einträge gefunden'")
            else:
                print("✅ No 'Keine Einträge gefunden' message found")
            
            # Parse for league links
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for any links with Action=107
            action_107_links = soup.find_all('a', href=re.compile(r'Action=107'))
            print(f"\n🏀 Found {len(action_107_links)} Action=107 links:")
            
            if action_107_links:
                for i, link in enumerate(action_107_links[:10]):  # Show first 10
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Extract liga_id
                    liga_id_match = re.search(r'liga_id=(\d+)', href)
                    liga_id = liga_id_match.group(1) if liga_id_match else 'Unknown'
                    
                    print(f"  {i+1}. {text} (liga_id: {liga_id})")
                    print(f"     {href}")
                    
                    # Check for Litzendorf league
                    if liga_id == '1701':
                        print(f"      🌟 This is the Bezirksliga Herren where BG Litzendorf plays!")
                        
                # Save discovered leagues
                leagues = []
                for link in action_107_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    liga_id_match = re.search(r'liga_id=(\d+)', href)
                    if liga_id_match:
                        liga_id = liga_id_match.group(1)
                        leagues.append({
                            'liga_id': liga_id,
                            'name': text,
                            'href': href,
                            'season': season
                        })
                
                if leagues:
                    discovery_file = f'action_106_leagues_{season}.json'
                    with open(discovery_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            'season': season,
                            'method': 'Action=106 GET',
                            'url': url,
                            'discovery_timestamp': datetime.now().isoformat(),
                            'total_leagues': len(leagues),
                            'leagues': leagues
                        }, f, indent=2, ensure_ascii=False)
                    
                    print(f"\n💾 Leagues saved: {discovery_file}")
                    print(f"✅ Successfully discovered {len(leagues)} leagues!")
            else:
                print("❌ No Action=107 links found")
                
                # Look for any links at all
                all_links = soup.find_all('a', href=True)
                print(f"📝 Total links in response: {len(all_links)}")
                
                # Check first few links
                for i, link in enumerate(all_links[:5]):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    print(f"  {i+1}. {text[:50]}: {href[:100]}")
                        
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")

if __name__ == "__main__":
    test_action_106_simple()
