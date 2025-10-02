#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json

def debug_known_working_league():
    """Debug why our known working league isn't being detected"""
    
    print("🐛 DEBUGGING KNOWN WORKING LEAGUE")
    print("Testing liga_id=26212 which we know has player data")
    
    liga_id = 26212
    saison_id = 2018
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Referer': 'https://www.basketball-bund.net/',
    }
    
    # Test the known working URL
    test_url = f"https://www.basketball-bund.net/statistik.do?reqCode=statTeamArchiv&liga_id={liga_id}&saison_id={saison_id}"
    
    print(f"🔗 Testing URL: {test_url}")
    
    try:
        response = requests.get(test_url, headers=headers, timeout=15)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📏 Content Length: {len(response.text)}")
        
        if response.status_code == 200:
            # Check for Oberfranken indicators
            text = response.text.lower()
            oberfranken_indicators = [
                'oberfranken',
                'coburg',
                'bamberg', 
                'bayreuth',
                'kronach',
                'lichtenfels',
                'forchheim',
                'kulmbach'
            ]
            
            print(f"\n🔍 OBERFRANKEN DETECTION:")
            found_indicators = []
            for indicator in oberfranken_indicators:
                if indicator in text:
                    found_indicators.append(indicator)
                    print(f"   ✅ Found: {indicator}")
            
            if not found_indicators:
                print(f"   ❌ No Oberfranken indicators found")
                
                # Look for any location names
                print(f"\n🗺️  SEARCHING FOR LOCATION CLUES:")
                location_words = []
                words = text.split()
                for word in words:
                    if len(word) > 4 and any(char.isupper() for char in word):
                        if any(geo in word.lower() for geo in ['stadt', 'dorf', 'berg', 'heim']):
                            location_words.append(word)
                
                for location in location_words[:10]:  # Show first 10
                    print(f"   📍 Location: {location}")
            
            # Look for league title
            soup = BeautifulSoup(response.text, 'html.parser')
            title_elements = soup.find_all(['td', 'div'], class_=lambda x: x and 'title' in str(x).lower())
            
            print(f"\n📋 TITLE ELEMENTS:")
            for i, element in enumerate(title_elements[:5]):  # Show first 5
                title_text = element.get_text(strip=True)
                if title_text:
                    print(f"   {i+1}: {title_text}")
            
            # Look for team names to understand the league
            print(f"\n🏀 LOOKING FOR TEAM DATA:")
            
            # Find tables with team-like data
            tables = soup.find_all('table')
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                if len(rows) > 5:  # Tables with substantial data
                    print(f"   Table {i+1}: {len(rows)} rows")
                    
                    # Look for team names in first few rows
                    for row_idx, row in enumerate(rows[:3]):
                        cells = row.find_all(['td', 'th'])
                        for cell in cells:
                            cell_text = cell.get_text(strip=True)
                            if cell_text and len(cell_text) > 3:
                                print(f"     Row {row_idx+1}: {cell_text}")
                        if row_idx >= 2:  # Only show first 3 rows per table
                            break
                    break  # Only analyze first substantial table
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_range_around_known_id():
    """Test range around our known working ID to find similar leagues"""
    
    print(f"\n🎯 TESTING RANGE AROUND KNOWN ID (26212)")
    
    base_id = 26212
    test_range = range(base_id - 10, base_id + 11)  # Test ±10 around known ID
    saison_id = 2018
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    working_leagues = []
    
    for liga_id in test_range:
        test_url = f"https://www.basketball-bund.net/statistik.do?reqCode=statTeamArchiv&liga_id={liga_id}&saison_id={saison_id}"
        
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200 and len(response.text) > 10000:  # Substantial content
                # Quick check for basketball content
                text = response.text.lower()
                if any(term in text for term in ['team', 'punkte', 'spiele', 'liga']):
                    
                    # Extract league name from title
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title_elements = soup.find_all(['td', 'div'], class_=lambda x: x and 'title' in str(x).lower())
                    
                    league_name = "Unknown League"
                    for element in title_elements:
                        title_text = element.get_text(strip=True)
                        if 'saison' in title_text.lower():
                            league_name = title_text
                            break
                    
                    working_leagues.append({
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'url': test_url,
                        'content_length': len(response.text)
                    })
                    
                    print(f"   ✅ {liga_id}: {league_name[:50]}...")
            
        except Exception as e:
            continue
    
    print(f"\n📊 RESULTS:")
    print(f"   ✅ Found {len(working_leagues)} working leagues")
    
    # Save results
    if working_leagues:
        with open('discovered_working_leagues.json', 'w', encoding='utf-8') as f:
            json.dump(working_leagues, f, indent=2, ensure_ascii=False)
        print(f"   💾 Saved to discovered_working_leagues.json")
        
        return working_leagues
    
    return []

if __name__ == "__main__":
    debug_known_working_league()
    test_range_around_known_id()
