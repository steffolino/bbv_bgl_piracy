#!/usr/bin/env python3
"""
Authenticated Oberfranken Basketball Crawler
Uses proper session authentication to discover leagues via Action=106
then extracts comprehensive data for all seasons 2003-2024
"""

import requests
import json
import time
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AuthenticatedOberfrankenCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.basketball-bund.net"
        self.setup_authenticated_session()
        
    def setup_authenticated_session(self):
        """Setup session with complete authentication cookies and headers"""
        # Set User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
        })
        
        # Add all authentication cookies
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
    
    def discover_oberfranken_leagues(self, season: int) -> List[Dict]:
        """
        Discover all leagues in Oberfranken for a given season using authenticated Action=106
        """
        logger.info(f"Discovering Oberfranken leagues for season {season}")
        
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
        
        # Form data for Oberfranken (cbBezirkFilter=5)
        data = {
            'saison_id': str(season),
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '-3',  # All age classes
            'cbGeschlechtFilter': '0',     # All genders
            'cbBezirkFilter': '5',         # Oberfranken
            'cbKreisFilter': '0'           # All districts
        }
        
        try:
            response = self.session.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            if "Keine Einträge gefunden" in response.text:
                logger.warning(f"No entries found for season {season}")
                return []
            
            # Parse the response to extract league information
            leagues = self.parse_league_discovery_response(response.text, season)
            logger.info(f"Found {len(leagues)} leagues for season {season}")
            return leagues
            
        except Exception as e:
            logger.error(f"Error discovering leagues for season {season}: {e}")
            return []
    
    def parse_league_discovery_response(self, html: str, season: int) -> List[Dict]:
        """Parse the Action=106 response to extract league information"""
        soup = BeautifulSoup(html, 'html.parser')
        leagues = []
        
        # Look for league tables or links
        # The exact parsing depends on the HTML structure returned
        # This is a template - we'll need to inspect the actual response
        
        # Look for links with liga_id parameters
        liga_links = soup.find_all('a', href=re.compile(r'liga_id=\d+'))
        
        for link in liga_links:
            href = link.get('href', '')
            liga_id_match = re.search(r'liga_id=(\d+)', href)
            
            if liga_id_match:
                liga_id = liga_id_match.group(1)
                league_name = link.get_text(strip=True)
                
                leagues.append({
                    'liga_id': liga_id,
                    'name': league_name,
                    'season': season,
                    'href': href
                })
        
        return leagues
    
    def get_league_standings(self, liga_id: str, season: int) -> List[Dict]:
        """Get team standings for a league using Action=107"""
        url = f"{self.base_url}/index.jsp?Action=107&liga_id={liga_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            return self.parse_standings(response.text, liga_id, season)
            
        except Exception as e:
            logger.error(f"Error getting standings for liga_id {liga_id}: {e}")
            return []
    
    def parse_standings(self, html: str, liga_id: str, season: int) -> List[Dict]:
        """Parse standings table from Action=107 response"""
        soup = BeautifulSoup(html, 'html.parser')
        standings = []
        
        # Look for standings table
        table = soup.find('table')
        if not table:
            return standings
        
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) >= 8:  # Typical standings table has rank, team, games, wins, losses, etc.
                try:
                    standings.append({
                        'liga_id': liga_id,
                        'season': season,
                        'rank': cells[0].get_text(strip=True),
                        'team': cells[1].get_text(strip=True),
                        'games': cells[2].get_text(strip=True),
                        'wins': cells[3].get_text(strip=True),
                        'losses': cells[4].get_text(strip=True),
                        'points_for': cells[5].get_text(strip=True),
                        'points_against': cells[6].get_text(strip=True),
                        'points': cells[7].get_text(strip=True)
                    })
                except Exception as e:
                    logger.warning(f"Error parsing standings row: {e}")
                    continue
        
        return standings
    
    def get_player_statistics(self, liga_id: str, season: int) -> List[Dict]:
        """Get player statistics using the working statistik.do endpoint"""
        base_url = "https://www.basketball-bund.net/statistik.do"
        stats_categories = ['SPG', 'TPG', 'APG']  # Points, Rebounds, Assists
        all_players = []
        
        for category in stats_categories:
            url = f"{base_url}?spielzeit={season}&liga_id={liga_id}&modus={category}"
            
            try:
                response = self.session.get(url)
                response.raise_for_status()
                
                players = self.parse_player_statistics(response.text, liga_id, season, category)
                
                # Merge with existing players or add new ones
                for player in players:
                    existing = next((p for p in all_players if p['name'] == player['name'] and p['team'] == player['team']), None)
                    if existing:
                        existing[f'{category.lower()}_stat'] = player['stat_value']
                    else:
                        all_players.append({
                            'liga_id': liga_id,
                            'season': season,
                            'name': player['name'],
                            'team': player['team'],
                            f'{category.lower()}_stat': player['stat_value']
                        })
                
                logger.info(f"Extracted {len(players)} players for {category} in liga_id {liga_id}")
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error getting {category} statistics for liga_id {liga_id}: {e}")
                continue
        
        return all_players
    
    def parse_player_statistics(self, html: str, liga_id: str, season: int, category: str) -> List[Dict]:
        """Parse player statistics from statistik.do response"""
        soup = BeautifulSoup(html, 'html.parser')
        players = []
        
        # Find the statistics table
        table = soup.find('table')
        if not table:
            return players
        
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) >= 4:
                try:
                    # Extract player info
                    rank = cells[0].get_text(strip=True)
                    last_name = cells[1].get_text(strip=True)
                    first_name = cells[2].get_text(strip=True)
                    team = cells[3].get_text(strip=True)
                    
                    # Statistics are in remaining columns
                    stat_value = cells[4].get_text(strip=True) if len(cells) > 4 else "0"
                    
                    players.append({
                        'rank': rank,
                        'name': f"{first_name} {last_name}".strip(),
                        'team': team,
                        'stat_value': stat_value,
                        'category': category
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing player row: {e}")
                    continue
        
        return players
    
    def crawl_comprehensive_data(self) -> Dict:
        """Crawl comprehensive data for all Oberfranken seasons"""
        logger.info("Starting comprehensive Oberfranken crawl with authentication")
        
        # Seasons to crawl (2003-2017, 2019-2024, skip 2018 as we have data)
        seasons = list(range(2003, 2018)) + list(range(2019, 2025))
        
        all_data = {
            'leagues': [],
            'standings': [],
            'players': [],
            'metadata': {
                'crawl_timestamp': time.time(),
                'seasons_crawled': seasons,
                'region': 'Oberfranken',
                'authentication': 'enabled'
            }
        }
        
        for season in seasons:
            logger.info(f"Processing season {season}")
            
            # Discover leagues for this season
            leagues = self.discover_oberfranken_leagues(season)
            all_data['leagues'].extend(leagues)
            
            # For each league, get standings and player stats
            for league in leagues:
                liga_id = league['liga_id']
                
                # Get standings
                standings = self.get_league_standings(liga_id, season)
                all_data['standings'].extend(standings)
                
                # Get player statistics
                players = self.get_player_statistics(liga_id, season)
                all_data['players'].extend(players)
                
                time.sleep(2)  # Rate limiting between leagues
            
            time.sleep(3)  # Rate limiting between seasons
        
        return all_data
    
    def save_results(self, data: Dict, filename: str = "authenticated_oberfranken_complete.json"):
        """Save crawled data to JSON file"""
        filepath = f"C:\\Users\\StretzS\\projects\\bbv_bgl_piracy\\scrapy_crawlers\\{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {filepath}")
        logger.info(f"Total leagues: {len(data['leagues'])}")
        logger.info(f"Total standings entries: {len(data['standings'])}")
        logger.info(f"Total players: {len(data['players'])}")

def main():
    """Main execution function"""
    crawler = AuthenticatedOberfrankenCrawler()
    
    # Test authentication with a single season first
    logger.info("Testing authentication with season 2010...")
    test_leagues = crawler.discover_oberfranken_leagues(2010)
    
    if test_leagues:
        logger.info(f"Authentication successful! Found {len(test_leagues)} leagues for 2010")
        logger.info("Sample leagues:", test_leagues[:3])
        
        # Proceed with full crawl
        data = crawler.crawl_comprehensive_data()
        crawler.save_results(data)
        
    else:
        logger.error("Authentication failed - no leagues discovered for test season 2010")
        logger.info("Please check session cookies and try again")

if __name__ == "__main__":
    main()
