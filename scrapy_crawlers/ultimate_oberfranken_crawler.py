#!/usr/bin/env python3
"""
🎯 ULTIMATE OBERFRANKEN CRAWLER 🎯
Crawl ALL leagues in ALL seasons for Oberfranken (2003-2024)
Using the proper workflow we discovered!
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
import csv
from datetime import datetime

class OberfrankenCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
        })
        
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
        
        self.results = {
            'seasons_crawled': [],
            'total_leagues': 0,
            'total_players': 0,
            'errors': [],
            'crawl_start': datetime.now().isoformat()
        }
        
        # ALL SEASONS TO CRAWL
        self.seasons = [str(year) for year in range(2003, 2025)]  # 2003-2024
        
    def setup_session(self):
        """Setup Bayern session state with Action=100&Verband=2"""
        try:
            setup_url = "https://www.basketball-bund.net/index.jsp?Action=100&Verband=2"
            response = self.session.get(setup_url)
            
            if response.status_code == 200:
                print("✅ Session setup successful")
                return True
            else:
                print(f"❌ Session setup failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Session setup error: {e}")
            return False
    
    def get_leagues_for_season(self, season):
        """Get all Oberfranken leagues for a specific season"""
        print(f"\n{'='*60}")
        print(f"🎯 DISCOVERING LEAGUES FOR SEASON {season}")
        print(f"{'='*60}")
        
        try:
            # Step 1: GET Action=106 page
            get_url = "https://www.basketball-bund.net/index.jsp?Action=106"
            get_headers = {
                'referer': 'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2'
            }
            get_response = self.session.get(get_url, headers=get_headers)
            
            # Step 2: POST with Oberfranken filter
            post_url = "https://www.basketball-bund.net/index.jsp?Action=106"
            post_headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.basketball-bund.net',
                'referer': 'https://www.basketball-bund.net/index.jsp?Action=106'
            }
            
            post_data = {
                'saison_id': season,
                'cbSpielklasseFilter': '0',
                'cbAltersklasseFilter': '-3',  # Senioren
                'cbGeschlechtFilter': '0',
                'cbBezirkFilter': '5',  # Oberfranken
                'cbKreisFilter': '0'
            }
            
            post_response = self.session.post(post_url, headers=post_headers, data=post_data)
            
            if post_response.status_code != 200:
                print(f"❌ Failed to get leagues for {season}: {post_response.status_code}")
                return []
            
            print(f"Response length: {len(post_response.text)}")
            
            # Parse leagues
            soup = BeautifulSoup(post_response.text, 'html.parser')
            
            if "Keine Einträge gefunden" in post_response.text:
                print(f"⚠️ No leagues found for season {season}")
                return []
            
            # Extract liga_ids and names
            leagues = []
            seen_ids = set()
            
            # Find all links with liga_id
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                match = re.search(r'liga_id=(\d+)', href)
                if match:
                    liga_id = match.group(1)
                    if liga_id not in seen_ids:
                        seen_ids.add(liga_id)
                        
                        # Find league name from table structure
                        parent_row = link.find_parent('tr')
                        league_name = "Unknown"
                        
                        if parent_row:
                            cells = parent_row.find_all(['td', 'th'])
                            for cell in cells:
                                cell_text = cell.get_text(strip=True)
                                if cell_text and len(cell_text) > 5:  # Avoid empty cells
                                    if any(word in cell_text.lower() for word in ['liga', 'oberliga', 'bezirk', 'kreis', 'pokal', 'meisterschaft']):
                                        league_name = cell_text
                                        break
                        
                        leagues.append({
                            'id': liga_id,
                            'name': league_name,
                            'season': season
                        })
            
            print(f"✅ Found {len(leagues)} leagues for season {season}")
            for i, league in enumerate(leagues, 1):
                print(f"  {i:2d}. ID: {league['id']:>6} | {league['name']}")
            
            return leagues
            
        except Exception as e:
            error_msg = f"Error getting leagues for season {season}: {e}"
            print(f"❌ {error_msg}")
            self.results['errors'].append(error_msg)
            return []
    
    def crawl_players_for_league(self, league):
        """Crawl all players for a specific league"""
        liga_id = league['id']
        season = league['season']
        league_name = league['name']
        
        print(f"\n  🔍 Crawling players: Liga {liga_id} ({league_name}) - Season {season}")
        
        try:
            # Use statistik.do endpoint for player data
            statistik_url = f"https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id={liga_id}&saison_id={season}&_top=-1"
            
            response = self.session.get(statistik_url)
            
            if response.status_code != 200:
                print(f"    ❌ Failed to get player data: {response.status_code}")
                return []
            
            if len(response.text) < 5000:
                print(f"    ⚠️ Response too short, probably no data")
                return []
            
            # Parse player data
            soup = BeautifulSoup(response.text, 'html.parser')
            players = []
            
            # Look for player tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:  # Should have at least: Name, Vorname, Team, Points
                        
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        
                        # Skip header rows
                        if any(header in ' '.join(cell_texts).lower() for header in ['platz', 'name', 'vorname', 'mannschaft', 'punkte']):
                            continue
                        
                        # Look for rows with actual player data
                        if len(cell_texts) >= 4 and cell_texts[0] and cell_texts[1]:
                            # Try to extract player info
                            try:
                                # Common patterns: [Rank], Lastname, Firstname, Team, Points, Games, Avg
                                if cell_texts[0].isdigit():  # Has rank
                                    lastname = cell_texts[1]
                                    firstname = cell_texts[2] if len(cell_texts) > 2 else ""
                                    team = cell_texts[3] if len(cell_texts) > 3 else ""
                                    points = cell_texts[4] if len(cell_texts) > 4 else ""
                                    games = cell_texts[5] if len(cell_texts) > 5 else ""
                                else:  # No rank
                                    lastname = cell_texts[0]
                                    firstname = cell_texts[1] if len(cell_texts) > 1 else ""
                                    team = cell_texts[2] if len(cell_texts) > 2 else ""
                                    points = cell_texts[3] if len(cell_texts) > 3 else ""
                                    games = cell_texts[4] if len(cell_texts) > 4 else ""
                                
                                # Validate this looks like player data
                                if lastname and len(lastname) > 1 and not lastname.isdigit():
                                    player = {
                                        'lastname': lastname,
                                        'firstname': firstname,
                                        'team': team,
                                        'points': points,
                                        'games': games,
                                        'liga_id': liga_id,
                                        'league_name': league_name,
                                        'season': season,
                                        'bezirk': 'Oberfranken'
                                    }
                                    players.append(player)
                                    
                            except Exception as e:
                                continue  # Skip problematic rows
            
            # Remove duplicates
            unique_players = []
            seen = set()
            for player in players:
                key = f"{player['lastname']}_{player['firstname']}_{player['team']}"
                if key not in seen:
                    seen.add(key)
                    unique_players.append(player)
            
            print(f"    ✅ Found {len(unique_players)} players")
            
            # Show BG Litzendorf players if found
            litzendorf_players = [p for p in unique_players if 'litzendorf' in p['team'].lower()]
            if litzendorf_players:
                print(f"    🎯 BG LITZENDORF PLAYERS: {len(litzendorf_players)}")
                for player in litzendorf_players[:5]:  # Show first 5
                    print(f"      - {player['firstname']} {player['lastname']} ({player['points']} pts)")
            
            return unique_players
            
        except Exception as e:
            error_msg = f"Error crawling players for liga {liga_id} season {season}: {e}"
            print(f"    ❌ {error_msg}")
            self.results['errors'].append(error_msg)
            return []
    
    def save_results(self, all_players):
        """Save results to CSV and JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CSV
        csv_filename = f'oberfranken_all_players_{timestamp}.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            if all_players:
                fieldnames = all_players[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_players)
        
        # Save JSON
        json_filename = f'oberfranken_all_players_{timestamp}.json'
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(all_players, jsonfile, indent=2, ensure_ascii=False)
        
        # Save summary
        summary_filename = f'oberfranken_crawl_summary_{timestamp}.json'
        self.results['crawl_end'] = datetime.now().isoformat()
        self.results['total_players'] = len(all_players)
        
        with open(summary_filename, 'w', encoding='utf-8') as summaryfile:
            json.dump(self.results, summaryfile, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"💾 RESULTS SAVED")
        print(f"{'='*60}")
        print(f"Players CSV: {csv_filename}")
        print(f"Players JSON: {json_filename}")
        print(f"Summary: {summary_filename}")
        
        return csv_filename, json_filename, summary_filename
    
    def crawl_all_seasons(self):
        """Crawl ALL seasons for Oberfranken"""
        print(f"🚀 STARTING ULTIMATE OBERFRANKEN CRAWL")
        print(f"Seasons: {self.seasons[0]} - {self.seasons[-1]} ({len(self.seasons)} seasons)")
        print(f"Started: {self.results['crawl_start']}")
        
        # Setup session
        if not self.setup_session():
            print("❌ Failed to setup session")
            return
        
        all_players = []
        
        for season in self.seasons:
            print(f"\n🎯 SEASON {season} ({self.seasons.index(season) + 1}/{len(self.seasons)})")
            
            # Get leagues for this season
            leagues = self.get_leagues_for_season(season)
            
            if not leagues:
                print(f"⚠️ No leagues found for season {season}")
                continue
            
            self.results['seasons_crawled'].append({
                'season': season,
                'leagues_found': len(leagues),
                'leagues': [{'id': l['id'], 'name': l['name']} for l in leagues]
            })
            
            self.results['total_leagues'] += len(leagues)
            
            # Crawl players for each league
            season_players = []
            for i, league in enumerate(leagues, 1):
                print(f"\n  Liga {i}/{len(leagues)}: {league['name']} (ID: {league['id']})")
                
                players = self.crawl_players_for_league(league)
                season_players.extend(players)
                
                # Small delay to be nice to the server
                time.sleep(0.5)
            
            all_players.extend(season_players)
            print(f"\n✅ Season {season} complete: {len(season_players)} players")
            
            # Save intermediate results every few seasons
            if len(self.results['seasons_crawled']) % 5 == 0:
                print(f"\n💾 Intermediate save after {len(self.results['seasons_crawled'])} seasons...")
                self.save_results(all_players)
        
        # Final results
        print(f"\n🎉 CRAWL COMPLETE!")
        print(f"Seasons crawled: {len(self.results['seasons_crawled'])}")
        print(f"Total leagues: {self.results['total_leagues']}")
        print(f"Total players: {len(all_players)}")
        print(f"Errors: {len(self.results['errors'])}")
        
        # Count BG Litzendorf players
        litzendorf_players = [p for p in all_players if 'litzendorf' in p['team'].lower()]
        print(f"🎯 BG LITZENDORF PLAYERS FOUND: {len(litzendorf_players)}")
        
        if litzendorf_players:
            print(f"\nBG Litzendorf by season:")
            by_season = {}
            for player in litzendorf_players:
                season = player['season']
                if season not in by_season:
                    by_season[season] = []
                by_season[season].append(player)
            
            for season in sorted(by_season.keys()):
                print(f"  {season}: {len(by_season[season])} players")
        
        # Save final results
        return self.save_results(all_players)

def main():
    crawler = OberfrankenCrawler()
    try:
        csv_file, json_file, summary_file = crawler.crawl_all_seasons()
        print(f"\n🎉 SUCCESS! All files saved.")
        print(f"Check {csv_file} for the complete dataset!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Crawl interrupted by user")
        # Save partial results
        if hasattr(crawler, 'all_players'):
            crawler.save_results(getattr(crawler, 'all_players', []))
    except Exception as e:
        print(f"\n❌ Crawl failed: {e}")

if __name__ == "__main__":
    main()
