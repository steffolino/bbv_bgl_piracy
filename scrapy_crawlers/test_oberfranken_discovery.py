#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def test_oberfranken_discovery():
    """
    Test Oberfranken league discovery with exact POST parameters
    """
    
    print("🔍 TESTING OBERFRANKEN LEAGUE DISCOVERY")
    print("Using exact POST parameters from user's working request")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    })
    
    # Test with 2010 (we know this has data)
    season = 2010
    
    print(f"\n📅 Testing season {season}")
    
    try:
        # Action=106 URL
        url = 'https://www.basketball-bund.net/index.jsp'
        
        # POST data with EXACT parameters
        post_data = {
            'Action': '106',
            'saison_id': str(season),
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '-3',
            'cbGeschlechtFilter': '0', 
            'cbBezirkFilter': '5',  # Oberfranken
            'cbKreisFilter': '0'
        }
        
        print(f"🔗 URL: {url}")
        print(f"📋 POST data: {post_data}")
        
        response = session.post(url, data=post_data, timeout=30)
        
        print(f"📥 Status: {response.status_code}")
        print(f"📏 Response size: {len(response.text):,} chars")
        
        if response.status_code == 200:
            # Save response for analysis
            filename = f'test_discovery_oberfranken_{season}.html'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"💾 Saved response: {filename}")
            
            # Parse league links
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for links with Action=107 and liga_id
            links = soup.find_all('a', href=re.compile(r'Action=107.*liga_id='))
            
            print(f"\n🏀 Found {len(links)} league links:")
            
            discovered_leagues = []
            for i, link in enumerate(links):
                href = link.get('href', '')
                
                # Extract liga_id from href
                liga_id_match = re.search(r'liga_id=(\d+)', href)
                if liga_id_match:
                    liga_id = liga_id_match.group(1)
                    league_name = link.get_text(strip=True)
                    
                    if liga_id and league_name:
                        discovered_leagues.append({
                            'liga_id': liga_id,
                            'name': league_name,
                            'href': href
                        })
                        
                        print(f"  {i+1}. {league_name} (ID: {liga_id})")
                        
                        # Check if this is a Litzendorf league
                        if '1701' in liga_id:
                            print(f"      🌟 This is the Bezirksliga Herren where BG Litzendorf plays!")
            
            # Save discovered leagues
            if discovered_leagues:
                discovery_file = f'discovered_oberfranken_leagues_{season}.json'
                with open(discovery_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'season': season,
                        'discovery_timestamp': datetime.now().isoformat(),
                        'total_leagues': len(discovered_leagues),
                        'leagues': discovered_leagues
                    }, f, indent=2, ensure_ascii=False)
                
                print(f"\n💾 Discovery results saved: {discovery_file}")
                print(f"✅ Successfully discovered {len(discovered_leagues)} leagues for {season}!")
            else:
                print(f"\n❌ No leagues discovered for {season}")
                
                # Check for error messages
                if 'Keine Einträge gefunden' in response.text:
                    print("   📝 Server returned 'Keine Einträge gefunden' (No entries found)")
                elif len(response.text) < 10000:
                    print("   📝 Response too small - might be an error page")
                else:
                    print("   📝 Response looks substantial but no Action=107 links found")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")

if __name__ == "__main__":
    test_oberfranken_discovery()
