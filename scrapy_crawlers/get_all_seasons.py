"""
🔍 GET COMPLETE SEASON LIST
Show ALL available seasons on basketball-bund.net
"""

import requests
from bs4 import BeautifulSoup

def get_all_seasons():
    """Get complete list of all available seasons"""
    
    print('🔍 GETTING COMPLETE SEASON LIST')
    print('=' * 50)

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    try:
        main_url = "https://www.basketball-bund.net/index.jsp?Action=106"
        response = session.get(main_url)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for season dropdown
            season_selects = soup.find_all('select')
            for select in season_selects:
                if 'saison' in str(select).lower():
                    print(f'🎯 Found season selector!')
                    options = select.find_all('option')
                    
                    seasons = []
                    for option in options:
                        if option.get('value') and option.get('value') != '0':
                            season_text = option.text.strip()
                            season_value = option.get('value')
                            seasons.append((season_value, season_text))
                    
                    print(f'📅 ALL AVAILABLE SEASONS ({len(seasons)}):')
                    print('   ID  | Season')
                    print('   ----|------------')
                    
                    for value, text in seasons:
                        print(f'   {value:<3} | {text}')
                    
                    # Analyze for recent years
                    recent_seasons = []
                    for value, text in seasons:
                        for year in ['2018', '2019', '2020', '2021', '2022', '2023', '2024']:
                            if year in text:
                                recent_seasons.append((value, text))
                                break
                    
                    print(f'\n🎯 RECENT SEASONS (2018-2024): {len(recent_seasons)}')
                    for value, text in recent_seasons:
                        print(f'   ✅ {value}: {text}')
                    
                    if not recent_seasons:
                        print('   😞 No 2018-2024 seasons found')
                        latest = seasons[-1] if seasons else None
                        if latest:
                            print(f'   📊 Latest available: {latest[1]} (ID: {latest[0]})')
                    
                    return seasons, recent_seasons
    
    except Exception as e:
        print(f'💥 Error: {str(e)}')
        return [], []

if __name__ == "__main__":
    all_seasons, recent = get_all_seasons()
    
    if recent:
        print(f'\n🎉 GOOD NEWS: Found {len(recent)} recent seasons!')
        print('🚀 Our scrapers can target these season IDs!')
    else:
        print('\n😞 MYSTERY SOLVED: No 2018-2024 seasons in database')
        print('💡 This explains the 2017 data gap!')
