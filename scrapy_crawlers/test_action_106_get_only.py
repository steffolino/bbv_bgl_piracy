#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def test_action_106_get_only():
    """
    Test Action=106 as pure GET request, no POST data
    """
    
    print("🔍 TESTING ACTION=106 AS PURE GET REQUEST")
    print("No POST data, only GET parameters")
    
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
        # Pure GET request with Action=106 and parameters in URL
        url = f"https://www.basketball-bund.net/index.jsp?Action=106&saison_id={season}&cbSpielklasseFilter=0&cbAltersklasseFilter=-3&cbGeschlechtFilter=0&cbBezirkFilter=5&cbKreisFilter=0"
        
        print(f"🔗 URL: {url}")
        print(f"📋 Method: GET (no POST data)")
        
        # Use GET method explicitly
        response = session.get(url, timeout=30)
        
        print(f"📥 Status: {response.status_code}")
        print(f"📏 Response size: {len(response.text):,} chars")
        
        if response.status_code == 200:
            # Save response for analysis
            filename = f'action_106_get_only_{season}.html'
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
            
            # Look for any links containing Action=107
            action_107_links = soup.find_all('a', href=re.compile(r'Action=107'))
            print(f"\n🏀 Found {len(action_107_links)} Action=107 links:")
            
            if action_107_links:
                discovered_leagues = []
                
                for i, link in enumerate(action_107_links):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Extract liga_id
                    liga_id_match = re.search(r'liga_id=(\d+)', href)
                    if liga_id_match:
                        liga_id = liga_id_match.group(1)
                        
                        discovered_leagues.append({
                            'liga_id': liga_id,
                            'name': text,
                            'href': href,
                            'season': season
                        })
                        
                        print(f"  {i+1}. {text} (liga_id: {liga_id})")
                        
                        # Check for known leagues
                        if liga_id == '1701':
                            print(f"      🌟 Bezirksliga Herren - BG Litzendorf league!")
                        elif liga_id in ['250', '3340', '263', '8025', '261', '256', '248', '2659', '6964', '697']:
                            print(f"      ✅ Known league from previous tests")
                
                if discovered_leagues:
                    # Save discovered leagues
                    discovery_file = f'action_106_get_leagues_{season}.json'
                    with open(discovery_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            'season': season,
                            'method': 'Action=106 GET only',
                            'url': url,
                            'discovery_timestamp': datetime.now().isoformat(),
                            'total_leagues': len(discovered_leagues),
                            'leagues': discovered_leagues
                        }, f, indent=2, ensure_ascii=False)
                    
                    print(f"\n💾 Leagues saved: {discovery_file}")
                    print(f"✅ Successfully discovered {len(discovered_leagues)} leagues!")
                    
                    # Show summary
                    known_leagues = [l for l in discovered_leagues if l['liga_id'] in ['1701', '250', '3340', '263', '8025', '261', '256', '248', '2659', '6964', '697']]
                    new_leagues = [l for l in discovered_leagues if l['liga_id'] not in ['1701', '250', '3340', '263', '8025', '261', '256', '248', '2659', '6964', '697']]
                    
                    print(f"📊 Summary:")
                    print(f"   ✅ Known leagues: {len(known_leagues)}")
                    print(f"   🆕 New leagues: {len(new_leagues)}")
                    
                    if new_leagues:
                        print(f"   🆕 New leagues discovered:")
                        for league in new_leagues[:5]:  # Show first 5
                            print(f"      {league['name']} (ID: {league['liga_id']})")
                        if len(new_leagues) > 5:
                            print(f"      ... and {len(new_leagues)-5} more")
                            
                else:
                    print("❌ No valid leagues found in Action=107 links")
            else:
                print("❌ No Action=107 links found")
                
                # Alternative: look for any links with liga_id
                liga_id_links = soup.find_all('a', href=re.compile(r'liga_id='))
                print(f"🔍 Found {len(liga_id_links)} links with liga_id:")
                
                for i, link in enumerate(liga_id_links[:5]):  # Show first 5
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    liga_id_match = re.search(r'liga_id=(\d+)', href)
                    if liga_id_match:
                        liga_id = liga_id_match.group(1)
                        print(f"  {i+1}. {text} (liga_id: {liga_id})")
                        print(f"     {href}")
                        
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")

if __name__ == "__main__":
    test_action_106_get_only()
