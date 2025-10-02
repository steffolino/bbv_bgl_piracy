#!/usr/bin/env python3
"""
🎯 FIXED OBERFRANKEN CRAWLER 🎯
- Extract FULL league names from correct column (6th column)
- Handle PAGINATION (startrow parameters)
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime

class FixedOberfrankenCrawler:
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
    
    def setup_session(self):
        """Setup Bayern session state"""
        try:
            setup_url = "https://www.basketball-bund.net/index.jsp?Action=100&Verband=2"
            response = self.session.get(setup_url)
            return response.status_code == 200
        except:
            return False
    
    def get_all_leagues_for_season(self, season):
        """Get ALL leagues for a season, handling pagination"""
        print(f"\n{'='*60}")
        print(f"🎯 DISCOVERING ALL LEAGUES FOR SEASON {season}")
        print(f"{'='*60}")
        
        all_leagues = []
        startrow = 0
        page = 1
        
        while True:
            print(f"\n📄 Page {page} (startrow={startrow})")
            
            try:
                # GET Action=106 page first
                get_url = "https://www.basketball-bund.net/index.jsp?Action=106"
                get_headers = {
                    'referer': 'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2'
                }
                self.session.get(get_url, headers=get_headers)
                
                # POST with Oberfranken filter + pagination
                post_url = "https://www.basketball-bund.net/index.jsp?Action=106"
                if startrow > 0:
                    post_url += f"&startrow={startrow}"
                
                post_headers = {
                    'content-type': 'application/x-www-form-urlencoded',
                    'referer': 'https://www.basketball-bund.net/index.jsp?Action=106'
                }
                
                post_data = {
                    'saison_id': season,
                    'cbSpielklasseFilter': '0',
                    'cbAltersklasseFilter': '0',  # ALL age classes (not just Senioren)
                    'cbGeschlechtFilter': '0',    # ALL genders
                    'cbBezirkFilter': '5',        # Oberfranken
                    'cbKreisFilter': '0'
                }
                
                if startrow > 0:
                    post_data['startrow'] = str(startrow)
                
                response = self.session.post(post_url, headers=post_headers, data=post_data)
                
                if response.status_code != 200:
                    print(f"    ❌ Failed: {response.status_code}")
                    break
                
                if "Keine Einträge gefunden" in response.text:
                    print(f"    ⚠️ No entries found")
                    break
                
                # Parse leagues from this page
                soup = BeautifulSoup(response.text, 'html.parser')
                page_leagues = self.parse_leagues_from_page(soup, season)
                
                if not page_leagues:
                    print(f"    ⚠️ No leagues parsed on this page")
                    break
                
                all_leagues.extend(page_leagues)
                print(f"    ✅ Found {len(page_leagues)} leagues on page {page}")
                
                # Check for pagination
                next_startrow = self.get_next_startrow(soup)
                if next_startrow is None or next_startrow <= startrow:
                    print(f"    📄 No more pages")
                    break
                
                startrow = next_startrow
                page += 1
                
                # Small delay between pages
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    ❌ Error on page {page}: {e}")
                break
        
        # Remove duplicates
        unique_leagues = []
        seen_ids = set()
        for league in all_leagues:
            if league['id'] not in seen_ids:
                seen_ids.add(league['id'])
                unique_leagues.append(league)
        
        print(f"\n✅ TOTAL LEAGUES FOUND: {len(unique_leagues)} (across {page} pages)")
        for i, league in enumerate(unique_leagues, 1):
            print(f"  {i:2d}. ID: {league['id']:>6} | {league['full_name']}")
            print(f"      {league['spielklasse']} | {league['altersklasse']} | {league['geschlecht']}")
        
        return unique_leagues
    
    def parse_leagues_from_page(self, soup, season):
        """Parse leagues from a single page, extracting from correct columns"""
        leagues = []
        
        # Find the main data table
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                # Look for rows with liga_id links in the actions column
                has_liga_id = False
                liga_id = None
                
                for cell in cells:
                    links = cell.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        match = re.search(r'liga_id=(\d+)', href)
                        if match:
                            liga_id = match.group(1)
                            has_liga_id = True
                            break
                    if has_liga_id:
                        break
                
                if has_liga_id and liga_id and len(cells) >= 6:
                    # Extract from correct columns
                    try:
                        spielklasse = cells[0].get_text(strip=True) if len(cells) > 0 else ""
                        altersklasse = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                        geschlecht = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                        bezirk = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                        kreis = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                        full_name = cells[5].get_text(strip=True) if len(cells) > 5 else ""  # 6th column!
                        
                        # Validate this looks like real data
                        if spielklasse and full_name and bezirk.lower() == 'oberfranken':
                            league = {
                                'id': liga_id,
                                'season': season,
                                'spielklasse': spielklasse,
                                'altersklasse': altersklasse,
                                'geschlecht': geschlecht,
                                'bezirk': bezirk,
                                'kreis': kreis,
                                'full_name': full_name,
                            }
                            leagues.append(league)
                            
                    except Exception as e:
                        continue  # Skip problematic rows
        
        return leagues
    
    def get_next_startrow(self, soup):
        """Find the next startrow value for pagination"""
        # Look for pagination links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            # Look for startrow parameter
            match = re.search(r'startrow=(\d+)', href)
            if match:
                return int(match.group(1))
        
        # Also check for "Seite X / Y" text to confirm pagination exists
        page_text = soup.get_text()
        if re.search(r'Seite \d+ / \d+', page_text):
            # If we found pagination text but no next link, we might be on last page
            return None
        
        return None
    
    def test_single_season(self, season="2018"):
        """Test the fixed crawler on a single season"""
        print(f"🧪 TESTING FIXED CRAWLER ON SEASON {season}")
        
        if not self.setup_session():
            print("❌ Session setup failed")
            return
        
        leagues = self.get_all_leagues_for_season(season)
        
        print(f"\n📊 SUMMARY:")
        print(f"Total leagues: {len(leagues)}")
        
        # Group by category
        by_spielklasse = {}
        by_altersklasse = {}
        
        for league in leagues:
            # By Spielklasse
            sk = league['spielklasse']
            if sk not in by_spielklasse:
                by_spielklasse[sk] = 0
            by_spielklasse[sk] += 1
            
            # By Altersklasse
            ak = league['altersklasse']
            if ak not in by_altersklasse:
                by_altersklasse[ak] = 0
            by_altersklasse[ak] += 1
        
        print(f"\nBy Spielklasse:")
        for sk, count in sorted(by_spielklasse.items()):
            print(f"  {sk}: {count}")
        
        print(f"\nBy Altersklasse:")
        for ak, count in sorted(by_altersklasse.items()):
            print(f"  {ak}: {count}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'oberfranken_leagues_fixed_{season}_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(leagues, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filename}")
        return leagues

def main():
    crawler = FixedOberfrankenCrawler()
    crawler.test_single_season("2018")

if __name__ == "__main__":
    main()
