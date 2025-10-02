"""
🔍 TESTING 2018-2024 DATA AVAILABILITY
Check if missing years are actually available but just not scraped
"""

import requests
import json
from datetime import datetime

def test_recent_years():
    """Test if 2018-2024 data is available using same API structure"""
    
    print('🔍 TESTING 2018-2024 DATA AVAILABILITY')
    print('=' * 50)

    # Test the same endpoint structure for recent years
    base_url = 'https://www.basketball-bund.net'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Test for years 2018-2024
    test_years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]

    available_years = []
    
    for year in test_years:
        print(f'\n📅 Testing {year}/{str(year+1)[-2:]} season:')
        
        # Try the same endpoint pattern that worked for 2003-2017
        test_url = f'{base_url}/rest/wam/action/106'
        
        # Use the same payload structure from our working scrapers
        payload = {
            'vars': {
                'season': year,
                'startrow': 0,
                'region': 'oberfranken'  # Same region as our existing data
            }
        }
        
        try:
            response = requests.post(test_url, json=payload, headers=headers, timeout=10)
            print(f'   Status: {response.status_code}')
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'competitions' in data and len(data['competitions']) > 0:
                        comp_count = len(data['competitions'])
                        print(f'   ✅ Found {comp_count} competitions')
                        available_years.append(year)
                        
                        # Check if competitions have real data
                        for comp in data['competitions'][:3]:  # Check first 3
                            comp_name = comp.get('name', 'Unknown')
                            comp_id = comp.get('id', 'No ID')
                            print(f'      - {comp_name} (ID: {comp_id})')
                            
                    elif 'message' in data:
                        print(f'   ⚠️ Message: {data["message"]}')
                    else:
                        print(f'   📊 Response keys: {list(data.keys()) if data else "Empty"}')
                except Exception as e:
                    print(f'   📄 JSON parse error: {str(e)[:50]}')
            else:
                print(f'   ❌ HTTP Error: {response.status_code}')
                
        except Exception as e:
            print(f'   💥 Request failed: {str(e)[:50]}...')

    print(f'\n🎯 RESULTS SUMMARY:')
    print(f'   Available Years: {available_years}')
    print(f'   Missing Years: {[y for y in test_years if y not in available_years]}')
    
    if available_years:
        print(f'   🎉 GOOD NEWS: {len(available_years)} years have data available!')
        print('   🚀 We can scrape these missing years!')
    else:
        print('   😞 No recent years have data available')
        
    return available_years

if __name__ == "__main__":
    available = test_recent_years()
    
    if available:
        print(f'\n🔥 NEXT STEPS:')
        print('1. Run our existing scrapers for available years')
        print('2. Update season parameters in scraper configs')
        print('3. Import new data to get full 2003-2024 coverage')
        print('4. Achieve 95%+ data completion!')
