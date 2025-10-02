#!/usr/bin/env python3
"""
CORRECT APPROACH: Discover liga_ids per season with Action=106, then extract with statistik.do
You're absolutely right - liga_ids change every season!
"""

import requests
import json
import time
from bs4 import BeautifulSoup
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProperSeasonCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.basketball-bund.net"
        self.setup_authenticated_session()
        
    def setup_authenticated_session(self):
        """Setup session with your working authentication"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
        })
        
        # Your working authentication cookies
        cookies = {
            '__cmpcc': '1',
            '__cmpconsentx47082': 'CQYqGvAQYqGvAAfQ6BENB-FgAP_AAEPAAAigJSkR5C5cDWFBeTp3QMskeYQX0cgBZgABAgaAASABCDAAcIQAkkESIAyAAAACAQAAIDSBAAAADAhAAEAAAIgBAADoAAAEgBAIIAAEABERQ0IAAAgKCIgAEAAIAAAxIkAAkAKAAILiQFAAgIAiAAABAAAAAIABAAMAAAAIAAACAAIAAAAAAAAAgAAAAAACABAIAAAAAAAAII3wPgAFgAVAAuABwADwAIAAVAAyABoADwAI4ATAAuABiADQAG8APwAhABDACaAE4AMAAYYA5wB3QD8AP0AhABFgCOAEiAJMASkAsQBigDXgG0AOIAdsA_oB_wEXgJWATEAmQBNIChwFHgKRAU2Ap8BboC5AF5gMhAZIAywBlwDTQHFgPHAhWBG8AAA.f_gACHgAAAA',
            '__cmpcccx47082': 'aCQYrQy_gAAhfRqxozGIxJkc8QzJqaGQMhoMxYliDBDUysVMF6E9WLEjE1MMkalhYyamrJDQyGWGU1GTQxYGiYMGWSMMiFoJi1JYqwjAkwAA',
            '_cc_id': 'b616c325dc88e1ae505ba80bd46882fe',
            'panoramaId_expiry': '1759991137726',
            'panoramaId': '947c1d27b3bb8d4dfc70e52580f3185ca02cacef30144e43784f041253e24e3a',
            'panoramaIdType': 'panoDevice',
            'connectId': '{"ttl":86400000,"lastUsed":1759386336895,"lastSynced":1759386336895}',
            'SESSION': 'NTAwZTU4MjYtZDFjNC00NGI5LWIyMGItMWM1YmFhZjhjZjll',
            'emqsegs': 'e0,e3m,ey,ed,e38,e3g,e3q,ec,e3o,e3b,e1,e8',
            '__gads': 'ID=2606604e4e061425:T=1759386338:RT=1759401127:S=ALNI_MboJFcXJE4aqMFvtQzMYf84WND8Jg',
            '__gpi': 'UID=0000129342773779:T=1759386338:RT=1759401127:S=ALNI_MYebYj8D0sws2npwfXIogpqvTFm6w',
            '__eoi': 'ID=cf36713925753e4a:T=1759386338:RT=1759401127:S=AA-AfjZXc8kz_f8dFx3IWngcOT9S',
            'cto_bundle': 'H6fkil9jU0JWa1dYbzRqclJ1a2RiOWxPVVR4akgwUHg3QkhhOWUybmRGWU9FSzlhaXhnR2hVWVVaZm9Ha010Y0xuNUZyYkVCTjJ6aHk0ajZUekJuMnhtTU1zUDhiV3gwbVZ5YyUyQkkzN25BUWhWN2U2aVh4aktQU0VsclZCdElNYW01TnN1SDglMkJXdFhpYUxSWjNmUnl6NTcwUmpwWVoxTFBWdjFRaXNwakVWRGtIazZ3JTNE'
        }
        
        for name, value in cookies.items():
            self.session.cookies.set(name, value, domain='www.basketball-bund.net')
            if name in ['__cmpconsentx47082', '__cmpcccx47082', '_cc_id', 'panoramaId_expiry', 'panoramaId', 'panoramaIdType', '__gads', '__gpi', '__eoi', 'cto_bundle']:
                self.session.cookies.set(name, value, domain='.basketball-bund.net')
    
    def discover_oberfranken_liga_ids(self, season: int) -> List[str]:
        """
        Step 1: Use Action=106 with authentication to discover liga_ids for specific season
        This is what you were trying to tell me - liga_ids change per season!
        """
        logger.info(f"Discovering liga_ids for Oberfranken season {season}")
        
        url = f"{self.base_url}/index.jsp?Action=106"
        
        headers = {
            'authority': 'www.basketball-bund.net',
            'method': 'POST',
            'path': '/index.jsp?Action=106',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7',
            'cache-control': 'no-cache',
            'dnt': '1',
            'origin': 'https://www.basketball-bund.net',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://www.basketball-bund.net/index.jsp?Action=106',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Your exact working POST data for Oberfranken
        data = {
            'saison_id': str(season),
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '-3',
            'cbGeschlechtFilter': '0',
            'cbBezirkFilter': '5',  # Oberfranken
            'cbKreisFilter': '0'
        }
        
        try:
            response = self.session.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            if "Keine Einträge gefunden" in response.text:
                logger.warning(f"No leagues found for season {season}")
                return []
            
            # Extract liga_ids from the response
            liga_ids = self.parse_liga_ids_from_action106(response.text, season)
            logger.info(f"Found {len(liga_ids)} liga_ids for season {season}: {liga_ids}")
            return liga_ids
            
        except Exception as e:
            logger.error(f"Error discovering liga_ids for season {season}: {e}")
            return []
    
    def parse_liga_ids_from_action106(self, html: str, season: int) -> List[str]:
        """Parse liga_ids from Action=106 response"""
        soup = BeautifulSoup(html, 'html.parser')
        liga_ids = []
        
        # Look for links with liga_id parameters
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if 'liga_id=' in href:
                # Extract liga_id from URL
                import re
                match = re.search(r'liga_id=(\d+)', href)
                if match:
                    liga_id = match.group(1)
                    if liga_id not in liga_ids:
                        liga_ids.append(liga_id)
        
        # Also look for form inputs or other patterns
        inputs = soup.find_all('input', {'name': 'liga_id'})
        for inp in inputs:
            value = inp.get('value', '')
            if value and value.isdigit() and value not in liga_ids:
                liga_ids.append(value)
        
        # Save response for debugging
        with open(f'action106_season_{season}_response.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        return liga_ids
    
    def extract_players_from_liga(self, liga_id: str, season: int) -> List[Dict]:
        """
        Step 2: Use discovered liga_id with working statistik.do pattern
        """
        logger.info(f"Extracting players from liga_id {liga_id}, season {season}")
        
        req_codes = [
            'statBesteWerferArchiv',      # Best scorers
            'statBesteFreiWerferArchiv',  # Best free throw shooters  
            'statBeste3erWerferArchiv'    # Best 3-point shooters
        ]
        
        all_players = []
        
        for req_code in req_codes:
            url = f"{self.base_url}/statistik.do?reqCode={req_code}&liga_id={liga_id}&saison_id={season}&_top=-1"
            
            try:
                response = self.session.get(url)
                response.raise_for_status()
                
                if "does not contain handler parameter" in response.text and "reqCode" in response.text:
                    logger.warning(f"Auth error for {req_code} liga {liga_id}")
                    continue
                
                players = self.parse_player_statistics(response.text, liga_id, season, req_code)
                
                # Merge players
                for player in players:
                    existing = next((p for p in all_players if p['name'] == player['name'] and p['team'] == player['team']), None)
                    if existing:
                        existing[f'{req_code}_rank'] = player.get('rank')
                        existing[f'{req_code}_value'] = player.get('stat_value')
                    else:
                        new_player = {
                            'liga_id': liga_id,
                            'season': season,
                            'name': player['name'],
                            'team': player['team']
                        }
                        new_player[f'{req_code}_rank'] = player.get('rank')
                        new_player[f'{req_code}_value'] = player.get('stat_value')
                        all_players.append(new_player)
                
                logger.info(f"Extracted {len(players)} players from {req_code}")
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error extracting {req_code} for liga {liga_id}: {e}")
                continue
        
        return all_players
    
    def parse_player_statistics(self, html: str, liga_id: str, season: int, req_code: str) -> List[Dict]:
        """Parse player statistics from statistik.do response"""
        soup = BeautifulSoup(html, 'html.parser')
        players = []
        
        table = soup.find('table')
        if not table:
            return players
        
        rows = table.find_all('tr')
        data_rows = rows[1:] if len(rows) > 1 else []
        
        for row in data_rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                try:
                    rank = cells[0].get_text(strip=True)
                    last_name = cells[1].get_text(strip=True)
                    first_name = cells[2].get_text(strip=True)
                    team = cells[3].get_text(strip=True)
                    stat_value = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                    
                    if rank and last_name and team:
                        players.append({
                            'rank': rank,
                            'name': f"{first_name} {last_name}".strip(),
                            'team': team,
                            'stat_value': stat_value
                        })
                        
                except Exception as e:
                    continue
        
        return players
    
    def crawl_season_properly(self, season: int) -> List[Dict]:
        """
        PROPER season crawling:
        1. Discover liga_ids for this season
        2. Extract players from each discovered liga_id
        """
        logger.info(f"=== PROPER SEASON CRAWL: {season} ===")
        
        # Step 1: Discover liga_ids for this specific season
        liga_ids = self.discover_oberfranken_liga_ids(season)
        
        if not liga_ids:
            logger.warning(f"No liga_ids found for season {season}")
            return []
        
        # Step 2: Extract players from each discovered liga_id
        all_season_players = []
        
        for liga_id in liga_ids:
            players = self.extract_players_from_liga(liga_id, season)
            all_season_players.extend(players)
            
            logger.info(f"Liga {liga_id}: {len(players)} players")
            
            # Check for BG Litzendorf
            litzendorf_players = [p for p in players if 'litzendorf' in p['team'].lower()]
            if litzendorf_players:
                logger.info(f"🏀 Found {len(litzendorf_players)} BG Litzendorf players in liga {liga_id}")
            
            time.sleep(2)  # Rate limiting
        
        logger.info(f"Season {season} total: {len(all_season_players)} players from {len(liga_ids)} leagues")
        return all_season_players
    
    def test_single_season(self, season: int = 2010):
        """Test the proper approach on a single season"""
        logger.info(f"Testing proper approach on season {season}")
        
        players = self.crawl_season_properly(season)
        
        if players:
            logger.info(f"✅ SUCCESS! Found {len(players)} players for season {season}")
            
            # Save results
            filename = f"proper_season_{season}_results.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'season': season,
                    'extraction_method': 'proper_liga_id_discovery',
                    'total_players': len(players),
                    'players': players
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to {filename}")
            
            # Show sample
            for i, player in enumerate(players[:5]):
                logger.info(f"Sample player {i+1}: {player['name']} ({player['team']}) - Liga {player['liga_id']}")
                
        else:
            logger.error(f"❌ No players found for season {season}")

def main():
    """Test the proper approach"""
    crawler = ProperSeasonCrawler()
    
    # Test with season 2010 first
    crawler.test_single_season(2010)

if __name__ == "__main__":
    main()
