"""
🔍 TESTING CURRENT WEBSITE STRUCTURE FOR 2018-2024
Check if the basketball-bund.net website has changed structure
"""

import requests
from bs4 import BeautifulSoup
import re
import time

def test_current_website():
    """Test current website structure and available seasons"""
    
    print('🔍 TESTING CURRENT WEBSITE STRUCTURE')
    print('=' * 60)

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    # Step 1: Check main page and season selection
    print('\n📖 Step 1: Checking main league page...')
    try:
        main_url = "https://www.basketball-bund.net/index.jsp?Action=106"
        response = session.get(main_url)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for season dropdown
            season_selects = soup.find_all('select')
            for select in season_selects:
                if 'saison' in str(select).lower():
                    print(f'   🎯 Found season selector!')
                    options = select.find_all('option')
                    
                    seasons = []
                    for option in options:
                        if option.get('value') and option.get('value') != '0':
                            season_text = option.text.strip()
                            season_value = option.get('value')
                            seasons.append((season_value, season_text))
                    
                    print(f'   📅 Available seasons ({len(seasons)}):')
                    for value, text in seasons[-10:]:  # Show last 10
                        print(f'      {value}: {text}')
                    
                    # Check if recent years are available
                    recent_seasons = [s for s in seasons if any(year in s[1] for year in ['2018', '2019', '2020', '2021', '2022', '2023', '2024'])]
                    if recent_seasons:
                        print(f'   🎉 Found {len(recent_seasons)} recent seasons!')
                        return recent_seasons
                    else:
                        print('   😞 No recent seasons found in dropdown')
                        
                        # Show latest available
                        if seasons:
                            latest = seasons[-1]
                            print(f'   📊 Latest available: {latest[1]} (ID: {latest[0]})')
        
    except Exception as e:
        print(f'   💥 Error: {str(e)[:100]}...')

    # Step 2: Test form submission for latest available season
    print('\n🧪 Step 2: Testing form submission...')
    try:
        # Try to get the form and submit it
        post_data = {
            'saison_id': '31',  # Try a recent season ID
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '0', 
            'cbGeschlechtFilter': '0',
            'cbBezirkFilter': '5',  # Oberfranken
            'cbKreisFilter': '0'
        }
        
        response = session.post(main_url, data=post_data, headers={
            'content-type': 'application/x-www-form-urlencoded',
            'referer': main_url
        })
        
        print(f'   Form submission status: {response.status_code}')
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for league tables or results
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) > 5:  # Has substantial data
                    print(f'   📊 Found data table with {len(rows)} rows')
                    
                    # Check for league names in first few rows
                    for i, row in enumerate(rows[:5]):
                        cells = row.find_all(['td', 'th'])
                        if cells:
                            row_text = ' '.join(cell.get_text(strip=True) for cell in cells)
                            if any(keyword in row_text.lower() for keyword in ['liga', 'bezirk', 'kreis']):
                                print(f'      Row {i}: {row_text[:80]}...')
                    break
        
    except Exception as e:
        print(f'   💥 Form test error: {str(e)[:100]}...')

    # Step 3: Check if website structure changed
    print('\n🔍 Step 3: Analyzing website changes...')
    try:
        # Check for any error messages or redirects
        if 'error' in response.text.lower() or 'nicht gefunden' in response.text.lower():
            print('   ⚠️ Found error messages in response')
        
        # Check for JavaScript-heavy pages
        if 'javascript' in response.text.lower() and response.text.count('script') > 10:
            print('   🌐 Website appears to be JavaScript-heavy now')
        
        # Look for new API endpoints
        api_patterns = [
            r'/api/',
            r'/rest/',
            r'\.json',
            r'ajax',
            r'endpoint'
        ]
        
        for pattern in api_patterns:
            if re.search(pattern, response.text, re.IGNORECASE):
                print(f'   🔗 Found potential API pattern: {pattern}')
        
    except Exception as e:
        print(f'   💥 Analysis error: {str(e)[:100]}...')

    return None

if __name__ == "__main__":
    recent_seasons = test_current_website()
    
    if recent_seasons:
        print(f'\n🎉 SUCCESS: Found {len(recent_seasons)} recent seasons!')
        print('🚀 The data exists - we just need to update our scrapers!')
    else:
        print('\n😞 CONCLUSION: Recent seasons not found')
        print('💡 Possible reasons:')
        print('   1. Website structure changed')
        print('   2. Seasons not yet added to system')
        print('   3. Different authentication required')
        print('   4. Data moved to different section')
