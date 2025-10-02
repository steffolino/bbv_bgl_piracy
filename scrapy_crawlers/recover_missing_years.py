"""
🔥 BEAST CRAWLER: MISSING YEARS RECOVERY
Scrape the 7 missing seasons (2018-2024) that exist but weren't collected
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
import csv
from datetime import datetime

class MissingYearsRecovery:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # The seasons we need to recover
        self.missing_seasons = [
            (2024, '2024/2025'),
            (2023, '2023/2024'), 
            (2022, '2022/2023'),
            (2021, '2021/2022'),
            (2020, '2020/2021'),
            (2019, '2019/2020'),
            (2018, '2018/2019')
        ]
        
        self.stats = {
            'seasons_processed': 0,
            'leagues_found': 0,
            'teams_found': 0,
            'players_found': 0
        }
        
        self.all_players = []

    def setup_session(self):
        """Setup session"""
        try:
            setup_url = "https://www.basketball-bund.net/index.jsp?Action=100&Verband=2"
            response = self.session.get(setup_url)
            return response.status_code == 200
        except:
            return False

    def get_leagues_for_season(self, season_id, season_name):
        """Get all leagues for a specific season"""
        print(f'\n🎯 RECOVERING SEASON {season_name} (ID: {season_id})')
        
        leagues = []
        startrow = 0
        
        while True:
            try:
                # GET then POST pattern (same as working scrapers)
                get_url = "https://www.basketball-bund.net/index.jsp?Action=106"
                self.session.get(get_url)
                
                post_url = "https://www.basketball-bund.net/index.jsp?Action=106"
                if startrow > 0:
                    post_url += f"&startrow={startrow}"
                
                post_data = {
                    'saison_id': str(season_id),
                    'cbSpielklasseFilter': '0',
                    'cbAltersklasseFilter': '0',
                    'cbGeschlechtFilter': '0',
                    'cbBezirkFilter': '5',  # Oberfranken
                    'cbKreisFilter': '0'
                }
                
                if startrow > 0:
                    post_data['startrow'] = str(startrow)
                
                response = self.session.post(post_url, data=post_data, headers={
                    'content-type': 'application/x-www-form-urlencoded',
                    'referer': get_url
                })
                
                if response.status_code != 200:
                    print(f'   ❌ HTTP {response.status_code}')
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for league tables
                tables = soup.find_all('table')
                leagues_found_this_page = 0
                
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            # Check if this looks like a league row
                            league_link = row.find('a', href=re.compile(r'Action=100'))
                            if league_link:
                                league_text = league_link.get_text(strip=True)
                                href = league_link.get('href', '')
                                
                                # Extract league ID
                                league_id_match = re.search(r'Liga=(\d+)', href)
                                if league_id_match:
                                    league_id = league_id_match.group(1)
                                    leagues.append({
                                        'id': league_id,
                                        'name': league_text,
                                        'season_id': season_id,
                                        'season_name': season_name
                                    })
                                    leagues_found_this_page += 1
                
                print(f'   📄 Page {startrow//20 + 1}: Found {leagues_found_this_page} leagues')
                
                if leagues_found_this_page == 0:
                    break
                
                # Check for next page
                if 'weiter' not in response.text.lower() and 'next' not in response.text.lower():
                    break
                    
                startrow += 20
                time.sleep(0.5)  # Be nice to the server
                
            except Exception as e:
                print(f'   💥 Error on page {startrow//20 + 1}: {str(e)[:100]}...')
                break
        
        print(f'   ✅ Total leagues found: {len(leagues)}')
        self.stats['leagues_found'] += len(leagues)
        return leagues

    def get_teams_and_players(self, league):
        """Get teams and players for a league"""
        try:
            # Get league page
            league_url = f"https://www.basketball-bund.net/index.jsp?Action=100&Liga={league['id']}"
            response = self.session.get(league_url)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            teams = []
            
            # Look for team links
            team_links = soup.find_all('a', href=re.compile(r'Action=101.*Team=\d+'))
            for link in team_links:
                team_name = link.get_text(strip=True)
                href = link.get('href', '')
                
                team_id_match = re.search(r'Team=(\d+)', href)
                if team_id_match:
                    team_id = team_id_match.group(1)
                    teams.append({
                        'id': team_id,
                        'name': team_name,
                        'league': league
                    })
            
            print(f'     🏀 {league["name"]}: {len(teams)} teams')
            self.stats['teams_found'] += len(teams)
            
            # Get players for each team
            all_players = []
            for team in teams:
                players = self.get_players_for_team(team)
                all_players.extend(players)
                time.sleep(0.2)  # Rate limiting
            
            return all_players
            
        except Exception as e:
            print(f'     💥 League error: {str(e)[:50]}...')
            return []

    def get_players_for_team(self, team):
        """Get players for a specific team"""
        try:
            team_url = f"https://www.basketball-bund.net/index.jsp?Action=101&Liga={team['league']['id']}&Team={team['id']}"
            response = self.session.get(team_url)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            players = []
            
            # Look for player links
            player_links = soup.find_all('a', href=re.compile(r'Action=102.*Person=\d+'))
            for link in player_links:
                player_name = link.get_text(strip=True)
                href = link.get('href', '')
                
                person_id_match = re.search(r'Person=(\d+)', href)
                if person_id_match:
                    person_id = person_id_match.group(1)
                    players.append({
                        'id': person_id,
                        'name': player_name,
                        'team': team['name'],
                        'league': team['league']['name'],
                        'season': team['league']['season_name'],
                        'season_id': team['league']['season_id']
                    })
            
            return players
            
        except Exception as e:
            return []

    def recover_missing_years(self):
        """Recover all missing years"""
        print('🔥 STARTING MISSING YEARS RECOVERY')
        print('=' * 60)
        
        if not self.setup_session():
            print('❌ Session setup failed')
            return
        
        for season_id, season_name in self.missing_seasons:
            leagues = self.get_leagues_for_season(season_id, season_name)
            
            for league in leagues:
                players = self.get_teams_and_players(league)
                self.all_players.extend(players)
            
            self.stats['seasons_processed'] += 1
            time.sleep(1)  # Rest between seasons
        
        self.stats['players_found'] = len(self.all_players)
        
        # Save results
        self.save_results()
        self.print_summary()

    def save_results(self):
        """Save recovered players to CSV"""
        if not self.all_players:
            return
        
        filename = f'recovered_players_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'team', 'league', 'season', 'season_id'])
            writer.writeheader()
            writer.writerows(self.all_players)
        
        print(f'\n💾 Saved to: {filename}')

    def print_summary(self):
        """Print recovery summary"""
        print('\n🎯 RECOVERY SUMMARY')
        print('=' * 40)
        print(f'✅ Seasons processed: {self.stats["seasons_processed"]}')
        print(f'🏆 Leagues found: {self.stats["leagues_found"]}')
        print(f'🏀 Teams found: {self.stats["teams_found"]}')
        print(f'🏃 Players recovered: {self.stats["players_found"]}')
        
        if self.stats['players_found'] > 0:
            print(f'\n🔥 SUCCESS! Recovered {self.stats["players_found"]} missing players!')
            print('🚀 This will close the 2018-2024 data gap!')
        else:
            print('\n😞 No players recovered')

if __name__ == "__main__":
    recovery = MissingYearsRecovery()
    recovery.recover_missing_years()
