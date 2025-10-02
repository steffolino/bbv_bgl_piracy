#!/usr/bin/env python3
"""
🎯 ROBUST OBERFRANKEN CRAWLER with ANOMALY DETECTION 🎯
- Complete league metadata (Spielklasse, Altersklasse, Geschlecht)
- Extensive logging and anomaly detection
- Stops on suspicious data patterns
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
import csv
from datetime import datetime
import logging

class RobustOberfrankenCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
        })
        
        # Setup logging
        self.setup_logging()
        
        # Set authentication cookies
        cookies = {
            '__cmpcc': '1',
            '__cmpconsentx47082': 'CQYqGvAQYqGvAAfQ6BENB-FgAP_AAEPAAAigJSkR5C5cDWFBeTp3QMskeYQX0cgBZgABAgaAASABCDAAcIQAkkESIAyAAAACAQAAIDSBAAAADAhAAEAAAIgBAADoAAAEgBAIIAAEABERQ0IAAAgKCIgAEAAIAAAxIkAAkAKAAILiQFAAgIAiAAABAAAAAIABAAMAAAAIAAACAAIAAAAAAAAAgAAAAAACABAIAAAAAAAAII3wPgAFgAVAAuABwADwAIAAVAAyABoADwAI4ATAAuABiADQAG8APwAhABDACaAE4AMAAYYA5wB3QD8AP0AhABFgCOAEiAJMASkAsQBigDXgG0AOIAdsA_oB_wEXgJWATEAmQBNIChwFHgKRAU2Ap8BboC5AF5gMhAZIAywBlwDTQHFgPHAhWBG8AAA.f_gACHgAAAA',
            '__cmpcccx47082': 'aCQYrQy_gAAhfRqxozGIxJkc8QzJqaGQMhoMxYliDBDUysVMF6E9WLEjE1MMkalhYyamrJDQyGWGU1GTQxYGiYMGWSMMiFoJi1JYqwjAkwAA',
            '_cc_id': 'b616c325dc88e1ae505ba80bd46882fe',
            'panoramaId_expiry': '1759991137726',
            'panoramaId': '947c1d27b3bb8d4dfc70e52580f3185ca02cacef30144e43784f041253e24e3a',
            'panoramaIdType': 'panoDevice',
            'connectId': '{"ttl":86400000,"lastUsed":1759386336895,"lastSynced":1759386336895}',
            'emqsegs': 'e0,e3m,ey,ed,e38,e3i,e3s,ec,e3o,e3b,e1,e8',
            '__gads': 'ID=2606604e4e061425:T=1759386338:RT=1759404996:S=ALNI_MboJFcXJE4aqMFvtQzMYf84WND8Jg',
            '__gpi': 'UID=0000129342773779:T=1759386338:RT=1759404996:S=ALNI_MYebYj8D0sws2npwfXIogpqvTFm6w',
            '__eoi': 'ID=cf36713925753e4a:T=1759386338:RT=1759404996:S=AA-AfjZXc8kz_f8dFx3IWngcOT9S',
            'cto_bundle': '1pWV-19jU0JWa1dYbzRqclJ1a2RiOWxPVVR4Y2RwZDBCOTFlblNScTdCdTkxbXVsQm5HN3lyY1JzSk9pZFB5a3UxanEwbVglMkZUZTdBOERXRTJhbHZFMldsUUhMWFVuQWFnSUxNaVdJOGNJeXBlM3hFJTJCOGY5eWo4M3RSSmFvQlhrcTIxTkpxaEJOYjYlMkJUZGZKN2ZsZ0klMkZkdXpwM1I1V2lvdlp0YWpkemQ0aW85R1ZRayUzRA'
        }
        
        for name, value in cookies.items():
            self.session.cookies.set(name, value, domain='www.basketball-bund.net')
            if name in ['__cmpconsentx47082', '__cmpcccx47082', '_cc_id', 'panoramaId_expiry', 'panoramaId', 'panoramaIdType', '__gads', '__gpi', '__eoi', 'cto_bundle']:
                self.session.cookies.set(name, value, domain='.basketball-bund.net')
        
        # Anomaly detection thresholds
        self.anomalies = []
        self.thresholds = {
            'min_players_per_league': 8,    # Expect at least 8 players per league
            'max_players_per_league': 200,  # More than 200 players is suspicious
            'min_leagues_per_season': 5,    # Expect at least 5 leagues per season
            'max_response_size': 500000,    # Response larger than 500KB might be wrong
            'min_response_size': 5000       # Response smaller than 5KB probably empty
        }
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f'oberfranken_crawl_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 ROBUST OBERFRANKEN CRAWLER STARTED")
        self.logger.info(f"Log file: {log_filename}")
    
    def flag_anomaly(self, level, message, data=None):
        """Flag anomalies and decide whether to continue"""
        anomaly = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'data': data
        }
        self.anomalies.append(anomaly)
        
        if level == 'CRITICAL':
            self.logger.critical(f"🚨 CRITICAL ANOMALY: {message}")
            if data:
                self.logger.critical(f"Data: {data}")
            print(f"\n{'='*70}")
            print(f"🚨 CRITICAL ANOMALY DETECTED!")
            print(f"Message: {message}")
            if data:
                print(f"Data: {data}")
            print(f"{'='*70}")
            
            response = input("Continue crawling? (y/N): ").strip().lower()
            if response != 'y':
                raise Exception(f"Crawl stopped due to critical anomaly: {message}")
        
        elif level == 'WARNING':
            self.logger.warning(f"⚠️ WARNING: {message}")
            print(f"⚠️ WARNING: {message}")
        
        elif level == 'INFO':
            self.logger.info(f"ℹ️ INFO: {message}")
    
    def setup_session(self):
        """Setup Bayern session state"""
        self.logger.info("Setting up session state...")
        try:
            setup_url = "https://www.basketball-bund.net/index.jsp?Action=100&Verband=2"
            response = self.session.get(setup_url)
            
            if response.status_code == 200:
                self.logger.info("✅ Session setup successful")
                return True
            else:
                self.flag_anomaly('CRITICAL', f"Session setup failed with status {response.status_code}")
                return False
        except Exception as e:
            self.flag_anomaly('CRITICAL', f"Session setup error: {e}")
            return False
    
    def get_all_leagues_for_season(self, season):
        """Get ALL leagues for a season with extensive logging"""
        self.logger.info(f"{'='*60}")
        self.logger.info(f"🎯 DISCOVERING LEAGUES FOR SEASON {season}")
        self.logger.info(f"{'='*60}")
        
        all_leagues = []
        startrow = 0
        page = 1
        
        while True:
            self.logger.info(f"📄 Processing page {page} (startrow={startrow})")
            
            try:
                # GET Action=106 page first
                get_url = "https://www.basketball-bund.net/index.jsp?Action=106"
                get_response = self.session.get(get_url, headers={
                    'referer': 'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2'
                })
                
                self.logger.info(f"GET request status: {get_response.status_code}")
                
                # POST with Oberfranken filter + pagination
                post_url = "https://www.basketball-bund.net/index.jsp?Action=106"
                if startrow > 0:
                    post_url += f"&startrow={startrow}"
                
                post_data = {
                    'saison_id': season,
                    'cbSpielklasseFilter': '0',
                    'cbAltersklasseFilter': '0',  # ALL age classes
                    'cbGeschlechtFilter': '0',    # ALL genders  
                    'cbBezirkFilter': '5',        # Oberfranken
                    'cbKreisFilter': '0'
                }
                
                if startrow > 0:
                    post_data['startrow'] = str(startrow)
                
                self.logger.info(f"POST data: {post_data}")
                
                response = self.session.post(post_url, data=post_data, headers={
                    'content-type': 'application/x-www-form-urlencoded',
                    'referer': 'https://www.basketball-bund.net/index.jsp?Action=106'
                })
                
                self.logger.info(f"POST response status: {response.status_code}, size: {len(response.text)}")
                
                # Check response size anomalies
                if len(response.text) > self.thresholds['max_response_size']:
                    self.flag_anomaly('WARNING', f"Response size very large: {len(response.text)} bytes on page {page}")
                elif len(response.text) < self.thresholds['min_response_size']:
                    self.flag_anomaly('WARNING', f"Response size very small: {len(response.text)} bytes on page {page}")
                
                if response.status_code != 200:
                    self.flag_anomaly('CRITICAL', f"Failed to get page {page}: HTTP {response.status_code}")
                    break
                
                if "Keine Einträge gefunden" in response.text:
                    self.logger.info("No entries found on this page")
                    break
                
                # Parse leagues from this page
                soup = BeautifulSoup(response.text, 'html.parser')
                page_leagues = self.parse_leagues_from_page(soup, season, page)
                
                if not page_leagues:
                    self.flag_anomaly('WARNING', f"No leagues parsed from page {page} despite having content")
                    break
                
                all_leagues.extend(page_leagues)
                self.logger.info(f"✅ Found {len(page_leagues)} leagues on page {page}")
                
                # Check for pagination
                next_startrow = self.get_next_startrow(soup)
                if next_startrow is None or next_startrow <= startrow:
                    self.logger.info("No more pages found")
                    break
                
                startrow = next_startrow
                page += 1
                
                # Delay between pages
                time.sleep(0.5)
                
            except Exception as e:
                self.flag_anomaly('CRITICAL', f"Error processing page {page}: {e}")
                break
        
        # Remove duplicates and validate
        unique_leagues = []
        seen_ids = set()
        for league in all_leagues:
            if league['id'] not in seen_ids:
                seen_ids.add(league['id'])
                unique_leagues.append(league)
        
        # Check league count anomalies
        total_leagues = len(unique_leagues)
        if total_leagues < self.thresholds['min_leagues_per_season']:
            self.flag_anomaly('CRITICAL', f"Very few leagues found for season {season}: {total_leagues}")
        elif total_leagues == 0:
            self.flag_anomaly('CRITICAL', f"NO leagues found for season {season}")
        
        self.logger.info(f"✅ TOTAL UNIQUE LEAGUES: {total_leagues} (across {page} pages)")
        
        # Log detailed league breakdown
        by_spielklasse = {}
        by_altersklasse = {}
        for league in unique_leagues:
            sk = league['spielklasse']
            ak = league['altersklasse']
            by_spielklasse[sk] = by_spielklasse.get(sk, 0) + 1
            by_altersklasse[ak] = by_altersklasse.get(ak, 0) + 1
        
        self.logger.info(f"Leagues by Spielklasse: {by_spielklasse}")
        self.logger.info(f"Leagues by Altersklasse: {by_altersklasse}")
        
        return unique_leagues
    
    def parse_leagues_from_page(self, soup, season, page_num):
        """Parse leagues with detailed validation"""
        leagues = []
        
        # Save page content for debugging
        debug_filename = f'debug_page_{season}_{page_num}.html'
        with open(debug_filename, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        self.logger.info(f"Debug: Page content saved to {debug_filename}")
        
        tables = soup.find_all('table')
        self.logger.info(f"Found {len(tables)} tables on page {page_num}")
        
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            self.logger.info(f"Table {table_idx}: {len(rows)} rows")
            
            for row_idx, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                
                if len(cells) < 6:
                    continue  # Need at least 6 columns
                
                # Look for liga_id in any cell
                liga_id = None
                for cell in cells:
                    links = cell.find_all('a', href=True)
                    for link in links:
                        match = re.search(r'liga_id=(\d+)', link.get('href', ''))
                        if match:
                            liga_id = match.group(1)
                            break
                    if liga_id:
                        break
                
                if liga_id and len(cells) >= 6:
                    try:
                        # Extract all columns
                        spielklasse = cells[0].get_text(strip=True)
                        altersklasse = cells[1].get_text(strip=True)
                        geschlecht = cells[2].get_text(strip=True)
                        bezirk = cells[3].get_text(strip=True)
                        kreis = cells[4].get_text(strip=True)
                        full_name = cells[5].get_text(strip=True)
                        
                        # Validate this is Oberfranken data
                        if bezirk.lower() != 'oberfranken':
                            continue
                        
                        # Validate fields are not empty
                        if not spielklasse or not full_name:
                            self.flag_anomaly('WARNING', f"Empty required fields in row {row_idx}: spielklasse='{spielklasse}', full_name='{full_name}'")
                            continue
                        
                        league = {
                            'id': liga_id,
                            'season': season,
                            'spielklasse': spielklasse,
                            'altersklasse': altersklasse, 
                            'geschlecht': geschlecht,
                            'bezirk': bezirk,
                            'kreis': kreis,
                            'full_name': full_name,
                            'parsed_from_page': page_num,
                            'parsed_from_table': table_idx,
                            'parsed_from_row': row_idx
                        }
                        
                        leagues.append(league)
                        self.logger.info(f"Parsed league: {liga_id} - {full_name}")
                        
                    except Exception as e:
                        self.flag_anomaly('WARNING', f"Error parsing row {row_idx} on page {page_num}: {e}")
                        continue
        
        self.logger.info(f"Successfully parsed {len(leagues)} leagues from page {page_num}")
        return leagues
    
    def get_next_startrow(self, soup):
        """Find next pagination startrow"""
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            match = re.search(r'startrow=(\d+)', href)
            if match:
                return int(match.group(1))
        return None
    
    def crawl_players_for_league(self, league):
        """Crawl players with anomaly detection"""
        liga_id = league['id']
        season = league['season'] 
        full_name = league['full_name']
        
        self.logger.info(f"🔍 Crawling players: Liga {liga_id} ({full_name}) - Season {season}")
        
        try:
            statistik_url = f"https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id={liga_id}&saison_id={season}&_top=-1"
            
            response = self.session.get(statistik_url)
            self.logger.info(f"Player request status: {response.status_code}, size: {len(response.text)}")
            
            if response.status_code != 200:
                self.flag_anomaly('WARNING', f"Failed to get players for liga {liga_id}: HTTP {response.status_code}")
                return []
            
            # Check response size
            if len(response.text) < self.thresholds['min_response_size']:
                self.flag_anomaly('WARNING', f"Very small player response for liga {liga_id}: {len(response.text)} bytes")
            
            # Save debug content
            debug_filename = f'debug_players_{liga_id}_{season}.html'
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Parse players
            soup = BeautifulSoup(response.text, 'html.parser')
            players = self.parse_players_from_response(soup, league)
            
            # Check player count anomalies
            player_count = len(players)
            if player_count < self.thresholds['min_players_per_league']:
                self.flag_anomaly('CRITICAL', f"Very few players in liga {liga_id} ({full_name}): {player_count} players")
            elif player_count > self.thresholds['max_players_per_league']:
                self.flag_anomaly('WARNING', f"Very many players in liga {liga_id} ({full_name}): {player_count} players")
            
            # Check for BG Litzendorf
            litzendorf_players = [p for p in players if 'litzendorf' in p['team'].lower()]
            if litzendorf_players:
                self.logger.info(f"🎯 BG LITZENDORF FOUND: {len(litzendorf_players)} players")
                for player in litzendorf_players[:3]:  # Log first 3
                    self.logger.info(f"  - {player['firstname']} {player['lastname']} ({player['points']} pts)")
            
            self.logger.info(f"✅ Found {player_count} total players")
            return players
            
        except Exception as e:
            self.flag_anomaly('CRITICAL', f"Error crawling players for liga {liga_id}: {e}")
            return []
    
    def parse_players_from_response(self, soup, league):
        """Parse players with full league metadata"""
        players = []
        
        tables = soup.find_all('table')
        self.logger.info(f"Found {len(tables)} tables in player response")
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:
                    
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    
                    # Skip header rows
                    if any(header in ' '.join(cell_texts).lower() for header in ['platz', 'name', 'vorname', 'mannschaft', 'punkte']):
                        continue
                    
                    # Parse player data
                    try:
                        if cell_texts[0] and cell_texts[1] and len(cell_texts[0]) > 1:
                            # Determine if first column is rank
                            if cell_texts[0].isdigit():
                                lastname = cell_texts[1]
                                firstname = cell_texts[2] if len(cell_texts) > 2 else ""
                                team = cell_texts[3] if len(cell_texts) > 3 else ""
                                points = cell_texts[4] if len(cell_texts) > 4 else ""
                                games = cell_texts[5] if len(cell_texts) > 5 else ""
                            else:
                                lastname = cell_texts[0]
                                firstname = cell_texts[1] if len(cell_texts) > 1 else ""
                                team = cell_texts[2] if len(cell_texts) > 2 else ""
                                points = cell_texts[3] if len(cell_texts) > 3 else ""
                                games = cell_texts[4] if len(cell_texts) > 4 else ""
                            
                            # Validate player data
                            if lastname and len(lastname) > 1 and not lastname.isdigit():
                                player = {
                                    'lastname': lastname,
                                    'firstname': firstname,
                                    'team': team,
                                    'points': points,
                                    'games': games,
                                    'liga_id': league['id'],
                                    'season': league['season'],
                                    'bezirk': league['bezirk'],
                                    'spielklasse': league['spielklasse'],     # ✅ ADDED
                                    'altersklasse': league['altersklasse'],   # ✅ ADDED
                                    'geschlecht': league['geschlecht'],       # ✅ ADDED
                                    'league_full_name': league['full_name'],  # ✅ ADDED
                                    'kreis': league['kreis']                  # ✅ ADDED
                                }
                                players.append(player)
                                
                    except Exception as e:
                        continue
        
        # Remove duplicates
        unique_players = []
        seen = set()
        for player in players:
            key = f"{player['lastname']}_{player['firstname']}_{player['team']}"
            if key not in seen:
                seen.add(key)
                unique_players.append(player)
        
        return unique_players
    
    def test_single_season_robust(self, season="2018"):
        """Test with full logging and anomaly detection"""
        self.logger.info(f"🧪 TESTING ROBUST CRAWLER ON SEASON {season}")
        
        if not self.setup_session():
            return None
        
        # Get leagues
        leagues = self.get_all_leagues_for_season(season)
        if not leagues:
            self.flag_anomaly('CRITICAL', f"No leagues found for season {season}")
            return None
        
        # Test first few leagues for players
        all_players = []
        test_leagues = leagues[:3]  # Test first 3 leagues
        
        for league in test_leagues:
            players = self.crawl_players_for_league(league)
            all_players.extend(players)
            
            # Small delay
            time.sleep(1)
        
        # Save results with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save leagues
        leagues_file = f'oberfranken_leagues_robust_{season}_{timestamp}.json'
        with open(leagues_file, 'w', encoding='utf-8') as f:
            json.dump(leagues, f, indent=2, ensure_ascii=False)
        
        # Save players CSV
        if all_players:
            players_file = f'oberfranken_players_robust_{season}_{timestamp}.csv'
            with open(players_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_players[0].keys())
                writer.writeheader()
                writer.writerows(all_players)
            
            self.logger.info(f"💾 Players saved to: {players_file}")
        
        # Save anomalies
        if self.anomalies:
            anomalies_file = f'anomalies_{season}_{timestamp}.json'
            with open(anomalies_file, 'w', encoding='utf-8') as f:
                json.dump(self.anomalies, f, indent=2, ensure_ascii=False)
            
            self.logger.warning(f"⚠️ {len(self.anomalies)} anomalies detected, saved to: {anomalies_file}")
        
        self.logger.info(f"✅ Test complete: {len(leagues)} leagues, {len(all_players)} players")
        return leagues, all_players

def main():
    crawler = RobustOberfrankenCrawler()
    try:
        result = crawler.test_single_season_robust("2018")
        if result:
            leagues, players = result
            print(f"\n🎉 SUCCESS!")
            print(f"Leagues: {len(leagues)}")
            print(f"Players: {len(players)}")
            print(f"Anomalies: {len(crawler.anomalies)}")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    main()
