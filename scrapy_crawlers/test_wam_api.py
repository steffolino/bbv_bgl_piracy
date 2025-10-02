#!/usr/bin/env python3
"""
🔥 REAL HISTORICAL DATA DISCOVERY
Use the correct WAM API endpoint to find historical leagues
"""

import requests
import json
import time

def discover_historical_wam_data():
    print('🔥 TESTING REAL WAM API FOR HISTORICAL DATA')
    print('=' * 50)

    base_url = 'https://www.basketball-bund.net'
    wam_url = f'{base_url}/rest/wam/data'
    
    # Authentication cookies from current_season_scraper.py
    cookies = {
        '__cmpcc': '1',
        '__cmpconsentx47082': 'CQYqGvAQYqGvAAfQ6BENB-FgAP_AAEPAAAigJSkR5C5cDWFBeTp3QMskeYQX0cgBZgABAgaAASABCDAAcIQAkkESIAyAAAACAQAAIDSBAAAADAhAAEAAAIgBAADoAAAEgBAIIAAEABERQ0IAAAgKCIgAEAAIAAAxIkAAkAKAAILiQFAAgIAiAAABAAAAAIABAAMAAAAIAAACAAIAAAAAAAAAgAAAAAACABAIAAAAAAAAII3wPgAFgAVAAuABwADwAIAAVAAyABoADwAI4ATAAuABiADQAG8APwAhABDACaAE4AMAAYYA5wB3QD8AP0AhABFgCOAEiAJMASkAsQBigDXgG0AOIAdsA_oB_wEXgJWATEAmQBNIChwFHgKRAU2Ap8BboC5AF5gMhAZIAywBlwDTQHFgPHAhWBG8AAA.f_gACHgAAAA',
        'SESSION': 'NDkzOWM2ZDktMzYyOS00MjlhLTk1OTEtNzFlYmNjZTZmNWNh',
        '_cc_id': 'b616c325dc88e1ae505ba80bd46882fe'
    }

    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    print('🎯 Testing WAM API with different payloads...')
    
    # Test different payloads to discover available data
    test_payloads = [
        # Current season payload from scraper
        {
            "token": 0,
            "verbandIds": [2],  # Basketball federation
            "gebietIds": ["5_"]  # Gebiet 5 (Oberfranken region)
        },
        
        # Try without gebiet filter
        {
            "token": 0,
            "verbandIds": [2],
        },
        
        # Try different verbandIds (maybe different regions)
        {
            "token": 0,
            "verbandIds": [1, 2, 3, 4, 5],
        },
        
        # Try adding season filters
        {
            "token": 0,
            "verbandIds": [2],
            "gebietIds": ["5_"],
            "seasonIds": ["2023", "2022", "2021", "2020", "2019"]
        }
    ]
    
    for i, payload in enumerate(test_payloads):
        print(f'\n🧪 Test {i+1}: {payload}')
        print('-' * 40)
        
        try:
            response = session.post(wam_url, json=payload, timeout=15)
            
            print(f'Status Code: {response.status_code}')
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    print(f'Response Keys: {list(data.keys())}')
                    
                    # Look for league/competition data
                    if 'data' in data and data['data']:
                        competitions = data['data']
                        print(f'✅ Found {len(competitions)} competitions!')
                        
                        # Analyze first few competitions
                        for j, comp in enumerate(competitions[:3]):
                            print(f'   Competition {j+1}:')
                            print(f'     ID: {comp.get("id", "Unknown")}')
                            print(f'     Name: {comp.get("name", "Unknown")}')
                            print(f'     Season: {comp.get("season", {}).get("name", "Unknown")}')
                            print(f'     Status: {comp.get("status", "Unknown")}')
                            
                        # Look for older seasons
                        seasons_found = set()
                        for comp in competitions:
                            season_name = comp.get('season', {}).get('name', '')
                            if season_name:
                                seasons_found.add(season_name)
                        
                        print(f'   🗓️  Seasons found: {sorted(seasons_found)}')
                        
                        # Check if any competitions have historical data
                        historical_competitions = []
                        for comp in competitions:
                            season_name = comp.get('season', {}).get('name', '')
                            if any(year in season_name for year in ['2019', '2020', '2021', '2022', '2023']):
                                historical_competitions.append(comp)
                        
                        if historical_competitions:
                            print(f'   🎯 HISTORICAL LEAGUES FOUND: {len(historical_competitions)}')
                            for comp in historical_competitions:
                                print(f'     - {comp.get("id")}: {comp.get("season", {}).get("name")} - {comp.get("name")}')
                        
                        return competitions  # Return data for further analysis
                        
                    else:
                        print('❌ No competition data found')
                        print(f'Full response: {json.dumps(data, indent=2)[:500]}...')
                
                except json.JSONDecodeError:
                    print(f'Response is not JSON. Content: {response.text[:200]}')
            else:
                print(f'Error: {response.text[:200]}')
                
        except Exception as e:
            print(f'Request failed: {e}')
            
        time.sleep(1)  # Be polite between requests
    
    print('\n❌ No historical data discovered through WAM API')
    return None

if __name__ == "__main__":
    result = discover_historical_wam_data()
    if result:
        print(f'\n🏆 SUCCESS! Found {len(result)} competitions total')
    else:
        print('\n💡 Need to try different approach for historical data')
