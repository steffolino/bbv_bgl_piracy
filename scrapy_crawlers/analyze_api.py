#!/usr/bin/env python3
"""
🔍 DETAILED LEAGUE API ANALYSIS
Check what the actual API responses look like
"""

import requests
import json
import time

def analyze_league_api():
    print('🔍 DETAILED LEAGUE API ANALYSIS')
    print('=' * 40)

    base_url = 'https://www.basketball-bund.net'
    
    # Authentication cookies from current_season_scraper.py
    cookies = {
        '__cmpcc': '1',
        '__cmpconsentx47082': 'CQYqGvAQYqGvAAfQ6BENB-FgAP_AAEPAAAigJSkR5C5cDWFBeTp3QMskeYQX0cgBZgABAgaAASABCDAAcIQAkkESIAyAAAACAQAAIDSBAAAADAhAAEAAAIgBAADoAAAEgBAIIAAEABERQ0IAAAgKCIgAEAAIAAAxIkAAkAKAAILiQFAAgIAiAAABAAAAAIABAAMAAAAIAAACAAIAAAAAAAAAgAAAAAACABAIAAAAAAAAII3wPgAFgAVAAuABwADwAIAAVAAyABoADwAI4ATAAuABiADQAG8APwAhABDACaAE4AMAAYYA5wB3QD8AP0AhABFgCOAEiAJMASkAsQBigDXgG0AOIAdsA_oB_wEXgJWATEAmQBNIChwFHgKRAU2Ap8BboC5AF5gMhAZIAywBlwDTQHFgPHAhWBG8AAA.f_gACHgAAAA',
        'SESSION': 'NDkzOWM2ZDktMzYyOS00MjlhLTk1OTEtNzFlYmNjZTZmNWNh',
        '_cc_id': 'b616c325dc88e1ae505ba80bd46882fe'
    }

    session = requests.Session()
    session.cookies.update(cookies)

    # Test a few different league IDs and examine the full response
    test_ids = [47900, 47000, 46000, 45000]
    
    print('📋 RAW API RESPONSES:')
    
    for league_id in test_ids:
        print(f'\n🎯 League ID {league_id}:')
        print('-' * 30)
        
        try:
            url = f'{base_url}/rest/competition/actual/id/{league_id}'
            response = session.get(url, timeout=10)
            
            print(f'Status Code: {response.status_code}')
            print(f'URL: {url}')
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f'JSON Response Keys: {list(data.keys())}')
                    
                    # Print first few lines of actual response
                    response_text = json.dumps(data, indent=2)[:500]
                    print(f'Response Preview:\n{response_text}...')
                    
                    # Look for season info specifically
                    if 'season' in data:
                        print(f'Season Data: {data["season"]}')
                    
                    if 'name' in data:
                        print(f'League Name: {data["name"]}')
                        
                    if 'teams' in data:
                        print(f'Teams Count: {len(data["teams"])}')
                        
                    if 'matches' in data:
                        print(f'Matches Count: {len(data["matches"])}')
                    
                except json.JSONDecodeError:
                    print(f'Response is not JSON. Content length: {len(response.text)}')
                    print(f'First 200 chars: {response.text[:200]}')
            else:
                print(f'Error response: {response.text[:200]}')
                
        except Exception as e:
            print(f'Request failed: {e}')
            
        time.sleep(0.5)  # Be polite
    
    print('\n🔬 ALTERNATIVE API ENDPOINTS TO TEST:')
    
    # Try different API patterns that might work for historical data
    alternative_patterns = [
        f'{base_url}/rest/competition/season/2023/id/47000',
        f'{base_url}/rest/competition/archive/id/47000',
        f'{base_url}/rest/competition/history/47000',
        f'{base_url}/api/league/47000/2023',
        f'{base_url}/rest/wam/data'  # The payload-based endpoint
    ]
    
    for pattern in alternative_patterns:
        print(f'\n🧪 Testing: {pattern}')
        try:
            response = session.get(pattern, timeout=5)
            print(f'   Status: {response.status_code}')
            if response.status_code == 200:
                print(f'   ✅ SUCCESS! Content length: {len(response.text)}')
            elif response.status_code == 404:
                print(f'   ❌ Not found')
            else:
                print(f'   ⚠️ Other status: {response.text[:100]}')
        except Exception as e:
            print(f'   ❌ Error: {e}')

if __name__ == "__main__":
    analyze_league_api()
