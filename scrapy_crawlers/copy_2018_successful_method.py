#!/usr/bin/env python3
"""
Copy the EXACT successful 2018 approach for all seasons
Based on the working sample_export.csv format
"""

import requests
import json
import time
from bs4 import BeautifulSoup
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Copy2018SuccessfulMethod:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.basketball-bund.net"
        self.setup_session()
        
    def setup_session(self):
        """Setup session with proper headers and YOUR authentication cookies"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
        })
        
        # Add your working authentication cookies
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
            # Also set for .basketball-bund.net domain for some cookies
            if name in ['__cmpconsentx47082', '__cmpcccx47082', '_cc_id', 'panoramaId_expiry', 'panoramaId', 'panoramaIdType', '__gads', '__gpi', '__eoi', 'cto_bundle']:
                self.session.cookies.set(name, value, domain='.basketball-bund.net')
    
    def get_player_statistics_2018_method(self, liga_id: str, season: int) -> List[Dict]:
        """
        Use the EXACT 2018 successful method:
        statistik.do?reqCode=statBesteWerferArchiv&liga_id=26212&saison_id=2018&_top=-1
        """
        logger.info(f"Using 2018 successful method for liga_id {liga_id}, season {season}")
        
        # The three working reqCodes from 2018 success
        req_codes = [
            'statBesteWerferArchiv',      # Best scorers (points)
            'statBesteFreiWerferArchiv',  # Best free throw shooters
            'statBeste3erWerferArchiv'    # Best 3-point shooters
        ]
        
        all_players = []
        
        for req_code in req_codes:
            url = f"{self.base_url}/statistik.do?reqCode={req_code}&liga_id={liga_id}&saison_id={season}&_top=-1"
            
            try:
                logger.info(f"Requesting: {req_code} for liga {liga_id}")
                response = self.session.get(url)
                response.raise_for_status()
                
                players = self.parse_2018_style_response(response.text, liga_id, season, req_code, url)
                
                # Merge with existing players or add new ones
                for player in players:
                    existing = next((p for p in all_players if p['name'] == player['name'] and p['team'] == player['team']), None)
                    if existing:
                        # Add this stat category to existing player
                        existing[f'{req_code}_rank'] = player.get('rank')
                        existing[f'{req_code}_value'] = player.get('stat_value')
                    else:
                        # New player
                        new_player = {
                            'liga_id': liga_id,
                            'season': season,
                            'name': player['name'],
                            'team': player['team'],
                            'source_url': url,
                            'extraction_method': '2018_successful_copy'
                        }
                        new_player[f'{req_code}_rank'] = player.get('rank')
                        new_player[f'{req_code}_value'] = player.get('stat_value')
                        all_players.append(new_player)
                
                logger.info(f"Extracted {len(players)} players from {req_code}")
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error getting {req_code} for liga_id {liga_id}: {e}")
                continue
        
        logger.info(f"Total unique players for liga {liga_id}: {len(all_players)}")
        return all_players
    
    def parse_2018_style_response(self, html: str, liga_id: str, season: int, req_code: str, url: str) -> List[Dict]:
        """Parse player statistics using the successful 2018 format"""
        soup = BeautifulSoup(html, 'html.parser')
        players = []
        
        # Check for error messages first
        if "does not contain handler parameter" in html and "reqCode" in html:
            logger.warning(f"Error response detected for {req_code}")
            return players
        
        # Find the statistics table - same pattern as working 2018 data
        table = soup.find('table')
        if not table:
            logger.warning(f"No table found for {req_code}")
            return players
        
        rows = table.find_all('tr')
        logger.info(f"Found {len(rows)} rows in table for {req_code}")
        
        # Skip header row(s)
        data_rows = rows[1:] if len(rows) > 1 else []
        
        for row_idx, row in enumerate(data_rows):
            cells = row.find_all('td')
            if len(cells) >= 4:  # Need at least rank, lastname, firstname, team
                try:
                    # Parse using same structure as successful 2018 export
                    rank = cells[0].get_text(strip=True)
                    last_name = cells[1].get_text(strip=True)
                    first_name = cells[2].get_text(strip=True)
                    team = cells[3].get_text(strip=True)
                    
                    # Get statistical value (usually in 4th or 5th column)
                    stat_value = ""
                    if len(cells) > 4:
                        stat_value = cells[4].get_text(strip=True)
                    
                    # Only include if we have valid data
                    if rank and last_name and team:
                        players.append({
                            'rank': rank,
                            'name': f"{first_name} {last_name}".strip(),
                            'team': team,
                            'stat_value': stat_value,
                            'req_code': req_code,
                            'row_index': row_idx + 1  # 1-indexed like CSV
                        })
                        
                except Exception as e:
                    logger.warning(f"Error parsing row {row_idx} for {req_code}: {e}")
                    continue
        
        logger.info(f"Successfully parsed {len(players)} players from {req_code}")
        return players
    
    def crawl_known_working_leagues(self) -> Dict:
        """Crawl known working liga_ids using 2018 successful method"""
        
        # Known working liga_ids from previous successful extractions
        working_liga_ids = [
            '1701',   # BG Litzendorf league (149 players confirmed)
            '250',    # Another working league
            '3340',   # Another working league
            '26212'   # The exact 2018 successful liga_id from CSV
        ]
        
        # Seasons to crawl (2003-2024, including 2018 to verify)
        seasons = list(range(2003, 2025))
        
        all_data = {
            'leagues': [],
            'players': [],
            'metadata': {
                'extraction_method': '2018_successful_method_copy',
                'extraction_timestamp': time.time(),
                'seasons_attempted': seasons,
                'liga_ids_attempted': working_liga_ids,
                'base_url_pattern': 'statistik.do?reqCode={reqCode}&liga_id={liga_id}&saison_id={season}&_top=-1'
            }
        }
        
        successful_extractions = 0
        
        for season in seasons:
            logger.info(f"Processing season {season}")
            
            for liga_id in working_liga_ids:
                logger.info(f"Processing liga_id {liga_id} for season {season}")
                
                # Use the exact 2018 successful method
                players = self.get_player_statistics_2018_method(liga_id, season)
                
                if players:
                    all_data['players'].extend(players)
                    successful_extractions += 1
                    
                    # Log success
                    logger.info(f"✅ Season {season}, Liga {liga_id}: {len(players)} players")
                    
                    # Special logging for BG Litzendorf
                    litzendorf_players = [p for p in players if 'litzendorf' in p['team'].lower()]
                    if litzendorf_players:
                        logger.info(f"🏀 Found {len(litzendorf_players)} BG Litzendorf players")
                else:
                    logger.info(f"❌ Season {season}, Liga {liga_id}: No players")
                
                # Rate limiting between leagues
                time.sleep(2)
            
            # Rate limiting between seasons
            time.sleep(3)
        
        all_data['metadata']['successful_extractions'] = successful_extractions
        all_data['metadata']['total_players'] = len(all_data['players'])
        
        return all_data
    
    def save_results(self, data: Dict, filename: str = "copy_2018_successful_method.json"):
        """Save results using same pattern as successful 2018 extraction"""
        filepath = f"C:\\Users\\StretzS\\projects\\bbv_bgl_piracy\\scrapy_crawlers\\{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {filepath}")
        logger.info(f"Total extractions: {data['metadata']['successful_extractions']}")
        logger.info(f"Total players: {len(data['players'])}")
        
        # Also create a CSV in the same format as the successful sample_export.csv
        self.create_csv_export(data, filename.replace('.json', '.csv'))
    
    def create_csv_export(self, data: Dict, csv_filename: str):
        """Create CSV export in exact same format as successful sample_export.csv"""
        csv_filepath = f"C:\\Users\\StretzS\\projects\\bbv_bgl_piracy\\scrapy_crawlers\\{csv_filename}"
        
        with open(csv_filepath, 'w', encoding='utf-8', newline='') as f:
            # Write header (same as sample_export.csv)
            f.write("liga_id,season,req_code,url,extraction_timestamp,rank,last_name,first_name,team,stat_value,games,avg,full_name\n")
            
            for player in data['players']:
                for req_code in ['statBesteWerferArchiv', 'statBesteFreiWerferArchiv', 'statBeste3erWerferArchiv']:
                    if f'{req_code}_rank' in player:
                        # Create row in exact same format as successful CSV
                        rank = player.get(f'{req_code}_rank', '')
                        stat_value = player.get(f'{req_code}_value', '')
                        
                        # Split name back to first/last
                        name_parts = player['name'].split(' ', 1)
                        first_name = name_parts[0] if len(name_parts) > 0 else ''
                        last_name = name_parts[1] if len(name_parts) > 1 else ''
                        
                        # Build URL same as successful format
                        url = f"https://www.basketball-bund.net/statistik.do?reqCode={req_code}&liga_id={player['liga_id']}&saison_id={player['season']}&_top=-1"
                        
                        # Write CSV row
                        f.write(f"{player['liga_id']},{player['season']},{req_code},{url},{data['metadata']['extraction_timestamp']},{rank},{last_name},{first_name},{player['team']},{stat_value},,,{player['name']}\n")
        
        logger.info(f"CSV export saved: {csv_filepath}")

def main():
    """Main execution - copy the exact 2018 successful approach"""
    logger.info("Starting crawler using EXACT 2018 successful method")
    logger.info("Based on working sample_export.csv format")
    
    crawler = Copy2018SuccessfulMethod()
    
    # Run the extraction using proven 2018 method
    data = crawler.crawl_known_working_leagues()
    
    # Save results
    crawler.save_results(data)
    
    logger.info("✅ Extraction complete using 2018 successful method!")

if __name__ == "__main__":
    main()
