#!/usr/bin/env python3
"""
🔥🔥🔥 THE BEAST IS UNLEASHED! 🔥🔥🔥
CRAWLING ALL OBERFRANKEN LEAGUES FOR ALL SEASONS (2003-2024)
EXPECT THOUSANDS OF PLAYERS!
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
import csv
from datetime import datetime
import logging

class BeastOberfrankenCrawler:
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
        
        # Stats tracking
        self.stats = {
            'seasons_processed': 0,
            'total_leagues': 0,
            'total_players': 0,
            'litzendorf_players': 0,
            'anomalies': 0,
            'start_time': datetime.now(),
            'seasons_data': {}
        }
        
        # ALL SEASONS TO UNLEASH ON
        self.seasons = [str(year) for year in range(2003, 2025)]  # 22 SEASONS!
        
        print("🔥" * 70)
        print("🚀 THE BEAST IS AWAKENING! 🚀")
        print(f"TARGET: {len(self.seasons)} seasons ({self.seasons[0]}-{self.seasons[-1]})")
        print("EXPECTED: 6000+ players across all leagues!")
        print("🔥" * 70)
    
    def setup_logging(self):
        """Setup beast-level logging"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f'BEAST_UNLEASHED_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔥🔥🔥 THE BEAST IS UNLEASHED! 🔥🔥🔥")
        self.logger.info(f"Beast log: {log_filename}")
    
    def setup_session(self):
        """Setup session for beast mode"""
        try:
            setup_url = "https://www.basketball-bund.net/index.jsp?Action=100&Verband=2"
            response = self.session.get(setup_url)
            return response.status_code == 200
        except:
            return False
    
    def get_all_leagues_for_season(self, season):
        """Beast mode league discovery"""
        self.logger.info(f"🎯 BEAST DISCOVERING SEASON {season}")
        
        all_leagues = []
        startrow = 0
        page = 1
        
        while True:
            try:
                # GET then POST pattern
                get_url = "https://www.basketball-bund.net/index.jsp?Action=106"
                self.session.get(get_url, headers={
                    'referer': 'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2'
                })
                
                post_url = "https://www.basketball-bund.net/index.jsp?Action=106"
                if startrow > 0:
                    post_url += f"&startrow={startrow}"
                
                post_data = {
                    'saison_id': season,
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
                    'referer': 'https://www.basketball-bund.net/index.jsp?Action=106'
                })
                
                if response.status_code != 200 or "Keine Einträge gefunden" in response.text:
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                page_leagues = self.parse_leagues_from_page(soup, season)
                
                if not page_leagues:
                    break
                
                all_leagues.extend(page_leagues)
                self.logger.info(f"  Page {page}: {len(page_leagues)} leagues")
                
                # Check pagination
                next_startrow = self.get_next_startrow(soup)
                if next_startrow is None or next_startrow <= startrow:
                    break
                
                startrow = next_startrow
                page += 1
                time.sleep(0.3)  # Be nice to server
                
            except Exception as e:
                self.logger.error(f"Error on season {season} page {page}: {e}")
                break
        
        # Remove duplicates
        unique_leagues = []
        seen_ids = set()
        for league in all_leagues:
            if league['id'] not in seen_ids:
                seen_ids.add(league['id'])
                unique_leagues.append(league)
        
        self.logger.info(f"✅ Season {season}: {len(unique_leagues)} leagues")
        return unique_leagues
    
    def parse_leagues_from_page(self, soup, season):
        """Beast parsing"""
        leagues = []
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 6:
                    continue
                
                # Find liga_id
                liga_id = None
                for cell in cells:
                    for link in cell.find_all('a', href=True):
                        match = re.search(r'liga_id=(\d+)', link.get('href', ''))
                        if match:
                            liga_id = match.group(1)
                            break
                    if liga_id:
                        break
                
                if liga_id:
                    try:
                        spielklasse = cells[0].get_text(strip=True)
                        altersklasse = cells[1].get_text(strip=True)
                        geschlecht = cells[2].get_text(strip=True)
                        bezirk = cells[3].get_text(strip=True)
                        kreis = cells[4].get_text(strip=True)
                        full_name = cells[5].get_text(strip=True)
                        
                        if bezirk.lower() == 'oberfranken' and spielklasse and full_name:
                            leagues.append({
                                'id': liga_id,
                                'season': season,
                                'spielklasse': spielklasse,
                                'altersklasse': altersklasse,
                                'geschlecht': geschlecht,
                                'bezirk': bezirk,
                                'kreis': kreis,
                                'full_name': full_name
                            })
                    except:
                        continue
        
        return leagues
    
    def get_next_startrow(self, soup):
        """Find next page"""
        for link in soup.find_all('a', href=True):
            match = re.search(r'startrow=(\d+)', link.get('href', ''))
            if match:
                return int(match.group(1))
        return None
    
    def crawl_players_for_league(self, league):
        """Beast player crawling"""
        liga_id = league['id']
        season = league['season']
        
        try:
            statistik_url = f"https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id={liga_id}&saison_id={season}&_top=-1"
            response = self.session.get(statistik_url)
            
            if response.status_code != 200 or len(response.text) < 5000:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            players = []
            
            for table in soup.find_all('table'):
                for row in table.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        
                        # Skip headers
                        if any(h in ' '.join(cell_texts).lower() for h in ['platz', 'name', 'vorname']):
                            continue
                        
                        try:
                            if cell_texts[0] and cell_texts[1]:
                                # Parse player data
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
                                
                                if lastname and len(lastname) > 1 and not lastname.isdigit():
                                    player = {
                                        'lastname': lastname,
                                        'firstname': firstname,
                                        'team': team,
                                        'points': points,
                                        'games': games,
                                        'liga_id': liga_id,
                                        'season': season,
                                        'bezirk': league['bezirk'],
                                        'spielklasse': league['spielklasse'],
                                        'altersklasse': league['altersklasse'],
                                        'geschlecht': league['geschlecht'],
                                        'league_full_name': league['full_name'],
                                        'kreis': league['kreis']
                                    }
                                    players.append(player)
                        except:
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
            
        except Exception as e:
            self.logger.error(f"Error crawling liga {liga_id}: {e}")
            return []
    
    def save_progress(self, all_players, suffix="PROGRESS"):
        """Save progress during beast run"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CSV
        csv_file = f'BEAST_OBERFRANKEN_{suffix}_{timestamp}.csv'
        if all_players:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_players[0].keys())
                writer.writeheader()
                writer.writerows(all_players)
        
        # Save stats
        stats_file = f'BEAST_STATS_{suffix}_{timestamp}.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            current_stats = self.stats.copy()
            current_stats['total_players'] = len(all_players)
            current_stats['current_time'] = datetime.now().isoformat()
            json.dump(current_stats, f, indent=2, ensure_ascii=False, default=str)
        
        return csv_file, stats_file
    
    def unleash_the_beast(self):
        """🔥 UNLEASH THE FULL BEAST! 🔥"""
        self.logger.info(f"🔥🔥🔥 BEAST MODE ACTIVATED! TARGETING {len(self.seasons)} SEASONS! 🔥🔥🔥")
        
        if not self.setup_session():
            self.logger.critical("❌ Beast cannot setup session!")
            return
        
        all_players = []
        start_time = datetime.now()
        
        for season_idx, season in enumerate(self.seasons, 1):
            season_start = datetime.now()
            
            print(f"\n{'🔥' * 60}")
            print(f"🎯 BEAST ATTACKING SEASON {season} ({season_idx}/{len(self.seasons)})")
            print(f"{'🔥' * 60}")
            
            # Get leagues for this season
            leagues = self.get_all_leagues_for_season(season)
            
            if not leagues:
                self.logger.warning(f"⚠️ No leagues for season {season}")
                continue
            
            self.stats['seasons_data'][season] = {
                'leagues_found': len(leagues),
                'players_found': 0,
                'litzendorf_found': 0
            }
            
            # Crawl all leagues in this season
            season_players = []
            for league_idx, league in enumerate(leagues, 1):
                print(f"  🔍 Liga {league_idx}/{len(leagues)}: {league['full_name']} (ID: {league['id']})")
                
                players = self.crawl_players_for_league(league)
                season_players.extend(players)
                
                # Count BG Litzendorf
                litzendorf_count = len([p for p in players if 'litzendorf' in p['team'].lower()])
                if litzendorf_count > 0:
                    print(f"    🎯 BG LITZENDORF: {litzendorf_count} players!")
                    self.stats['litzendorf_players'] += litzendorf_count
                
                print(f"    ✅ {len(players)} players")
                
                # Small delay
                time.sleep(0.2)
            
            all_players.extend(season_players)
            self.stats['seasons_processed'] += 1
            self.stats['total_leagues'] += len(leagues)
            self.stats['seasons_data'][season]['players_found'] = len(season_players)
            
            season_time = datetime.now() - season_start
            print(f"\n✅ Season {season} complete!")
            print(f"   Leagues: {len(leagues)}")
            print(f"   Players: {len(season_players)}")
            print(f"   Time: {season_time.total_seconds():.1f}s")
            print(f"   TOTAL SO FAR: {len(all_players)} players")
            
            # Save progress every 3 seasons
            if season_idx % 3 == 0:
                csv_file, stats_file = self.save_progress(all_players, f"SEASON_{season}")
                print(f"   💾 Progress saved: {csv_file}")
            
            # Show estimated completion
            elapsed = datetime.now() - start_time
            avg_time_per_season = elapsed.total_seconds() / season_idx
            remaining_seasons = len(self.seasons) - season_idx
            estimated_remaining = remaining_seasons * avg_time_per_season
            
            print(f"   ⏱️ ETA: {estimated_remaining/60:.1f} minutes remaining")
        
        # FINAL RESULTS
        total_time = datetime.now() - start_time
        self.stats['total_players'] = len(all_players)
        
        print(f"\n{'🎉' * 70}")
        print(f"🔥🔥🔥 THE BEAST HAS COMPLETED ITS RAMPAGE! 🔥🔥🔥")
        print(f"{'🎉' * 70}")
        print(f"✅ Seasons processed: {self.stats['seasons_processed']}")
        print(f"✅ Total leagues: {self.stats['total_leagues']}")
        print(f"✅ TOTAL PLAYERS: {len(all_players)}")
        print(f"🎯 BG LITZENDORF PLAYERS: {self.stats['litzendorf_players']}")
        print(f"⏱️ Total time: {total_time.total_seconds()/60:.1f} minutes")
        print(f"{'🎉' * 70}")
        
        # Save final results
        final_csv, final_stats = self.save_progress(all_players, "FINAL")
        
        print(f"\n💾 FINAL BEAST RESULTS:")
        print(f"📊 Players CSV: {final_csv}")
        print(f"📈 Stats JSON: {final_stats}")
        
        # Show BG Litzendorf breakdown by season
        litzendorf_by_season = {}
        for player in all_players:
            if 'litzendorf' in player['team'].lower():
                season = player['season']
                if season not in litzendorf_by_season:
                    litzendorf_by_season[season] = []
                litzendorf_by_season[season].append(player)
        
        if litzendorf_by_season:
            print(f"\n🎯 BG LITZENDORF BY SEASON:")
            for season in sorted(litzendorf_by_season.keys()):
                players = litzendorf_by_season[season]
                print(f"   {season}: {len(players)} players")
        
        return all_players

def main():
    print("🔥🔥🔥 PREPARING TO UNLEASH THE BEAST! 🔥🔥🔥")
    print("This will crawl ALL Oberfranken seasons from 2003-2024!")
    print("Expected runtime: 20-30 minutes")
    print("Expected result: 6000+ players")
    
    confirm = input("\nAre you ready to UNLEASH THE BEAST? (type 'UNLEASH' to confirm): ")
    
    if confirm.strip().upper() == 'UNLEASH':
        beast = BeastOberfrankenCrawler()
        try:
            all_players = beast.unleash_the_beast()
            print(f"\n🎉 BEAST RAMPAGE COMPLETE! {len(all_players)} players conquered!")
        except KeyboardInterrupt:
            print(f"\n⚠️ Beast interrupted by user!")
            beast.save_progress(getattr(beast, 'all_players', []), "INTERRUPTED")
        except Exception as e:
            print(f"\n❌ Beast encountered error: {e}")
    else:
        print("🐕 Beast remains caged...")

if __name__ == "__main__":
    main()
