#!/usr/bin/env python3
"""
🕵️ HISTORICAL LEAGUE DISCOVERY TEST
Test if we can find basketball leagues from 2018-2024
"""

import requests
import time
import json

def test_historical_leagues():
    print('🕵️ TESTING HISTORICAL LEAGUE DISCOVERY')
    print('=' * 50)

    # Test if we can find historical leagues by scanning ID ranges
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

    # Test different league ID ranges to find historical leagues
    print('🔍 Scanning for leagues around known current IDs...')

    # Current leagues start around 47950+, let's check backwards
    test_ranges = [
        (47900, 47950),  # Just before current
        (47000, 47100),  # ~1000 back
        (46000, 46100),  # ~2000 back  
        (45000, 45100),  # ~3000 back
        (40000, 40100),  # Way back
    ]

    found_leagues = []

    for start, end in test_ranges:
        print(f'\n🎯 Testing range {start}-{end}...')
        
        # Sample 10 IDs from this range
        for league_id in range(start, min(start + 10, end)):
            try:
                url = f'{base_url}/rest/competition/actual/id/{league_id}'
                response = session.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    season = data.get('season', {}).get('name', 'Unknown')
                    name = data.get('name', 'Unknown')
                    
                    print(f'   ✅ League {league_id}: {name} ({season})')
                    found_leagues.append({
                        'id': league_id,
                        'name': name,
                        'season': season
                    })
                
                time.sleep(0.1)  # Be polite
                
            except Exception as e:
                continue

    print(f'\n🏆 FOUND {len(found_leagues)} HISTORICAL LEAGUES!')
    for league in found_leagues:
        print(f'   ID {league["id"]}: {league["season"]} - {league["name"]}')

    if found_leagues:
        print(f'\n🎯 BREAKTHROUGH! We can access historical leagues!')
        min_id = min(l["id"] for l in found_leagues)
        max_id = max(l["id"] for l in found_leagues)
        print(f'   Range to scan more thoroughly: {min_id} to {max_id}')
        
        # Test if we can get player data from these leagues
        print(f'\n🏀 Testing player data extraction from historical leagues...')
        test_league = found_leagues[0]
        
        try:
            # Try to get team and player data
            url = f'{base_url}/rest/competition/actual/id/{test_league["id"]}'
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                teams = data.get('teams', [])
                matches = data.get('matches', [])
                
                print(f'   ✅ League {test_league["id"]} has {len(teams)} teams, {len(matches)} matches')
                
                if teams:
                    print(f'   🏀 Sample teams: {[team.get("name", "Unknown") for team in teams[:3]]}')
                
                return True
                
        except Exception as e:
            print(f'   ❌ Error getting player data: {e}')
            
    else:
        print(f'\n❌ No historical leagues found in tested ranges')
        print(f'   Try different authentication or API endpoints')
        
    return False

if __name__ == "__main__":
    test_historical_leagues()
