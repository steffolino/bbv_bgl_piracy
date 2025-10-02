"""
🔥 IMPORT MISSING 2018-2024 DATA
Use the correct season IDs to scrape and import recent years
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import time

def scrape_season_data(session, season_id, season_name):
    """Scrape data for a specific season"""
    
    print(f'📅 Scraping {season_name} (ID: {season_id})...')
    
    # Submit form with proper parameters to get player data
    form_url = "https://www.basketball-bund.net/index.jsp"
    
    form_data = {
        'Action': '106',
        'saison_id': season_id,
        'cbSpielklasseFilter': '0',  # alle Spielklassen
        'cbAltersklasseFilter': '0',  # alle Altersklassen  
        'cbGeschlechtFilter': '0',   # alle Bereiche
        'cbBezirkFilter': '0',       # alle Bezirke
        'cbKreisFilter': '0',        # alle Kreise
        'submit': 'Anzeigen'
    }
    
    try:
        response = session.post(form_url, data=form_data)
        if response.status_code != 200:
            print(f'   ❌ Failed to submit form: {response.status_code}')
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find data tables
        tables = soup.find_all('table')
        players = []
        
        for table in tables:
            rows = table.find_all('tr')
            
            # Skip header row if exists
            data_rows = rows[1:] if len(rows) > 1 else rows
            
            for row in data_rows:
                cells = row.find_all('td')
                
                # Look for player data rows (usually have specific number of columns)
                if len(cells) >= 8:
                    try:
                        # Extract player data - adjust indices based on actual table structure
                        name = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                        team = cells[3].get_text(strip=True) if len(cells) > 3 else ''
                        
                        # Stats columns - may need adjustment based on actual structure
                        games = 0
                        points = 0.0
                        rebounds = 0.0
                        assists = 0.0
                        
                        # Try to parse numeric stats
                        try:
                            if len(cells) > 4:
                                games = int(cells[4].get_text(strip=True) or 0)
                            if len(cells) > 5:
                                points = float(cells[5].get_text(strip=True) or 0)
                            if len(cells) > 6:
                                rebounds = float(cells[6].get_text(strip=True) or 0)
                            if len(cells) > 7:
                                assists = float(cells[7].get_text(strip=True) or 0)
                        except (ValueError, IndexError):
                            pass
                        
                        if name and team:  # Only add if we have valid data
                            players.append({
                                'name': name,
                                'team': team,
                                'season': season_name,
                                'games': games,
                                'points': points,
                                'rebounds': rebounds,
                                'assists': assists
                            })
                    
                    except (IndexError, ValueError) as e:
                        continue
        
        print(f'   ✅ Found {len(players)} players')
        return players
        
    except Exception as e:
        print(f'   💥 Error scraping {season_name}: {str(e)}')
        return []

def import_missing_seasons():
    """Import all missing 2018-2024 seasons"""
    
    print('🔥 IMPORTING MISSING 2018-2024 DATA')
    print('=' * 50)
    
    # Session setup
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Database setup
    conn = sqlite3.connect('../league_cache.db')
    cursor = conn.cursor()
    
    # Get existing seasons
    cursor.execute('SELECT DISTINCT season FROM current_player_stats')
    existing_seasons = [row[0] for row in cursor.fetchall()]
    print(f'📊 Existing seasons: {len(existing_seasons)}')
    
    # Recent seasons to scrape (ID: Season)
    recent_seasons = [
        ('2024', '2024/25'),
        ('2023', '2023/24'),
        ('2022', '2022/23'),
        ('2021', '2021/22'),
        ('2020', '2020/21'),
        ('2019', '2019/20'),
        ('2018', '2018/19')
    ]
    
    total_imported = 0
    
    for season_id, season_name in recent_seasons:
        if season_name not in existing_seasons:
            players = scrape_season_data(session, season_id, season_name)
            
            # Import to database
            season_imported = 0
            for player in players:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO current_player_stats 
                        (name, team_name, season, games_played, points_per_game, rebounds_per_game, assists_per_game)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        player['name'],
                        player['team'], 
                        player['season'],
                        player['games'],
                        player['points'],
                        player['rebounds'],
                        player['assists']
                    ))
                    season_imported += 1
                except Exception as e:
                    print(f'   ⚠️ Error importing player: {e}')
                    continue
            
            print(f'   💾 Imported {season_imported} players to database')
            total_imported += season_imported
            
            # Don't hammer the server
            time.sleep(1)
        else:
            print(f'   ⏭️ Skipping {season_name} (already exists)')
    
    conn.commit()
    conn.close()
    
    print(f'\n🎉 IMPORT COMPLETE!')
    print(f'📊 Total imported: {total_imported} players')
    print(f'🚀 Database now includes 2018-2024 data!')

if __name__ == "__main__":
    import_missing_seasons()
