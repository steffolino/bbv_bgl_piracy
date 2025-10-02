#!/usr/bin/env python3

import requests
import json
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
import re

class SystematicBasketballCrawler:
    """Systematic crawler following the exact strategy provided by user"""
    
    def __init__(self):
        self.base_url = "https://www.basketball-bund.net"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Referer': 'https://www.basketball-bund.net/',
        })
        
        # Statistics endpoints to crawl for each league
        self.stat_endpoints = [
            'statTeamArchiv',                # Team statistics
            'statBesteWerferArchiv',         # Best shooters
            'statBesteFreiWerferArchiv',     # Best free throw shooters  
            'statBeste3erWerferArchiv',      # Best 3-point shooters
        ]
    
    def discover_leagues_for_season(self, saison_id, bezirk_filter=5):
        """Step 1: Use Action=106 to discover leagues for a season"""
        
        print(f"\n🔍 DISCOVERING LEAGUES FOR SEASON {saison_id}")
        
        # Form parameters as specified by user
        params = {
            'Action': '106',
            'viewid': '',
            'saison_id': saison_id,
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '-3',  # Senioren (alle)
            'cbGeschlechtFilter': '0',
            'cbBezirkFilter': bezirk_filter,  # 5 = Oberfranken
            'cbKreisFilter': '0'
        }
        
        try:
            url = f"{self.base_url}/index.jsp"
            response = self.session.get(url, params=params, timeout=15)
            
            print(f"   URL: {response.url}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                return self.parse_league_discovery_page(response.text, saison_id)
            else:
                print(f"   ❌ Failed to get discovery page")
                return []
                
        except Exception as e:
            print(f"   ❌ Error discovering leagues: {e}")
            return []
    
    def parse_league_discovery_page(self, html_content, saison_id):
        """Parse the discovery page to extract league IDs and names"""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            leagues = []
            
            # Look for links with liga_id parameters
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                
                # Extract liga_id from various link patterns
                liga_id_match = re.search(r'liga_id=(\d+)', href)
                if liga_id_match:
                    liga_id = int(liga_id_match.group(1))
                    
                    # Get league name from link text
                    league_name = link.get_text(strip=True)
                    
                    # Skip empty or very short names
                    if league_name and len(league_name) > 3:
                        leagues.append({
                            'liga_id': liga_id,
                            'league_name': league_name,
                            'saison_id': saison_id,
                            'source_url': href
                        })
            
            # Remove duplicates based on liga_id
            unique_leagues = {}
            for league in leagues:
                liga_id = league['liga_id']
                if liga_id not in unique_leagues:
                    unique_leagues[liga_id] = league
            
            result_leagues = list(unique_leagues.values())
            print(f"   ✅ Found {len(result_leagues)} unique leagues")
            
            return result_leagues
            
        except Exception as e:
            print(f"   ❌ Error parsing discovery page: {e}")
            return []
    
    def crawl_league_statistics(self, liga_id, saison_id, league_name):
        """Step 2: Crawl all statistics endpoints for a specific league"""
        
        print(f"\n📊 CRAWLING STATISTICS: {league_name} (Liga {liga_id}, Season {saison_id})")
        
        all_data = {
            'liga_id': liga_id,
            'saison_id': saison_id,
            'league_name': league_name,
            'players': [],
            'teams': [],
            'matches': []
        }
        
        # Crawl each statistics endpoint
        for endpoint in self.stat_endpoints:
            print(f"   📈 {endpoint}...")
            
            try:
                data = self.crawl_statistics_endpoint(liga_id, saison_id, endpoint)
                
                if endpoint == 'statTeamArchiv':
                    all_data['teams'].extend(data)
                    print(f"      ✅ {len(data)} teams")
                else:
                    all_data['players'].extend(data)
                    print(f"      ✅ {len(data)} players")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
            
            time.sleep(random.uniform(1, 2))  # Rate limiting
        
        # Also crawl game results
        print(f"   🏀 Game results...")
        try:
            matches = self.crawl_game_results(liga_id, saison_id)
            all_data['matches'].extend(matches)
            print(f"      ✅ {len(matches)} matches")
        except Exception as e:
            print(f"      ❌ Error: {e}")
        
        return all_data
    
    def crawl_statistics_endpoint(self, liga_id, saison_id, endpoint):
        """Crawl a specific statistics endpoint"""
        
        # Build URL based on endpoint type
        if endpoint == 'statTeamArchiv':
            url = f"{self.base_url}/statistik.do?reqCode={endpoint}&liga_id={liga_id}&saison_id={saison_id}"
        else:
            url = f"{self.base_url}/statistik.do?reqCode={endpoint}&liga_id={liga_id}&saison_id={saison_id}&_top=-1"
        
        try:
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                return self.parse_statistics_page(response.text, endpoint, liga_id, saison_id)
            else:
                return []
                
        except Exception as e:
            print(f"        Error accessing {endpoint}: {e}")
            return []
    
    def parse_statistics_page(self, html_content, endpoint, liga_id, saison_id):
        """Parse statistics page and extract data"""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for main data table
            tables = soup.find_all('table')
            
            for table in tables:
                if self.is_data_table(table, endpoint):
                    return self.extract_data_from_table(table, endpoint, liga_id, saison_id)
            
            return []
            
        except Exception as e:
            print(f"        Error parsing {endpoint}: {e}")
            return []
    
    def is_data_table(self, table, endpoint):
        """Check if table contains the data we want"""
        
        table_text = table.get_text().lower()
        
        if endpoint == 'statTeamArchiv':
            # Team statistics table
            indicators = ['team', 'mannschaft', 'spiele', 'punkte', 'siege']
        else:
            # Player statistics table  
            indicators = ['spieler', 'name', 'punkte', 'spiele', 'minuten']
        
        found = sum(1 for indicator in indicators if indicator in table_text)
        return found >= 2
    
    def extract_data_from_table(self, table, endpoint, liga_id, saison_id):
        """Extract data from HTML table"""
        
        try:
            data = []
            rows = table.find_all('tr')
            
            if len(rows) < 2:
                return []
            
            # Get headers
            header_row = rows[0]
            headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
            
            # Process data rows
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 2:
                    row_data = {
                        'liga_id': liga_id,
                        'saison_id': saison_id,
                        'endpoint': endpoint,
                        'extracted_at': datetime.now().isoformat()
                    }
                    
                    # Map cell data to headers
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            header = headers[i]
                            cell_text = cell.get_text(strip=True)
                            
                            # Identify what this column contains
                            if any(term in header for term in ['name', 'spieler', 'team', 'mannschaft']):
                                if cell_text and len(cell_text) > 1:
                                    row_data['name'] = cell_text
                            
                            elif any(term in header for term in ['punkte', 'points']):
                                try:
                                    row_data['points'] = float(cell_text.replace(',', '.'))
                                except:
                                    pass
                            
                            elif any(term in header for term in ['spiele', 'games']):
                                try:
                                    row_data['games'] = int(cell_text)
                                except:
                                    pass
                            
                            elif any(term in header for term in ['minuten', 'minutes']):
                                try:
                                    row_data['minutes'] = float(cell_text.replace(',', '.'))
                                except:
                                    pass
                            
                            # Add raw cell data too
                            row_data[f'col_{i}_{header}'] = cell_text
                    
                    # Only add if we got a name and at least one other field
                    if 'name' in row_data and len(row_data) > 4:
                        data.append(row_data)
            
            return data
            
        except Exception as e:
            print(f"          Error extracting table data: {e}")
            return []
    
    def crawl_game_results(self, liga_id, saison_id):
        """Crawl game results using Action=108"""
        
        matches = []
        page = 0
        
        while page < 5:  # Limit to first 5 pages to avoid infinite loops
            try:
                url = f"{self.base_url}/index.jsp?Action=108&liga_id={liga_id}&saison_id={saison_id}"
                if page > 0:
                    url += f"&page={page}"
                
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    page_matches = self.parse_game_results_page(response.text, liga_id, saison_id)
                    
                    if not page_matches:
                        break  # No more matches on this page
                    
                    matches.extend(page_matches)
                    page += 1
                    time.sleep(1)
                else:
                    break
                    
            except Exception as e:
                print(f"          Error getting game results page {page}: {e}")
                break
        
        return matches
    
    def parse_game_results_page(self, html_content, liga_id, saison_id):
        """Parse game results from HTML page"""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            matches = []
            
            # Look for match results in tables
            tables = soup.find_all('table')
            
            for table in tables:
                table_text = table.get_text().lower()
                if any(term in table_text for term in ['spiel', 'ergebnis', 'heimmannschaft', 'gastmannschaft']):
                    
                    rows = table.find_all('tr')
                    for row in rows[1:]:  # Skip header
                        cells = row.find_all(['td', 'th'])
                        
                        if len(cells) >= 3:
                            match_data = {
                                'liga_id': liga_id,
                                'saison_id': saison_id,
                                'extracted_at': datetime.now().isoformat()
                            }
                            
                            # Extract basic match info
                            for i, cell in enumerate(cells):
                                text = cell.get_text(strip=True)
                                match_data[f'col_{i}'] = text
                            
                            matches.append(match_data)
            
            return matches
            
        except Exception as e:
            print(f"          Error parsing game results: {e}")
            return []
    
    def run_systematic_crawl(self):
        """Run the complete systematic crawl as specified by user"""
        
        print("=== SYSTEMATIC BASKETBALL-BUND.NET CRAWL ===")
        print("Following user's exact strategy:")
        print("1. Discovery page with form parameters")
        print("2. Extract league IDs for each season") 
        print("3. Hit all statistics endpoints for each league")
        print("4. Parse HTML tables for player/team data")
        print("5. Iterate over years and leagues")
        
        all_data = []
        
        # Test seasons (can be expanded)
        seasons = [2018, 2019, 2020, 2021, 2022]
        
        for saison_id in seasons:
            print(f"\n🗓️ PROCESSING SEASON {saison_id}")
            
            # Step 1: Discover leagues for this season
            leagues = self.discover_leagues_for_season(saison_id)
            
            if not leagues:
                print(f"   ❌ No leagues found for season {saison_id}")
                continue
            
            print(f"   📋 Found {len(leagues)} leagues to crawl")
            
            # Step 2: Crawl each league (limit to first 3 for testing)
            for i, league in enumerate(leagues[:3]):
                liga_id = league['liga_id']
                league_name = league['league_name']
                
                print(f"\n   {i+1}/{min(3, len(leagues))}: {league_name}")
                
                # Step 3: Crawl all statistics for this league
                league_data = self.crawl_league_statistics(liga_id, saison_id, league_name)
                
                if league_data['players'] or league_data['teams'] or league_data['matches']:
                    all_data.append(league_data)
                    print(f"      ✅ Total: {len(league_data['players'])} players, {len(league_data['teams'])} teams, {len(league_data['matches'])} matches")
                else:
                    print(f"      ❌ No data extracted")
                
                time.sleep(random.uniform(2, 4))  # Rate limiting between leagues
            
            time.sleep(3)  # Rate limiting between seasons
        
        # Save results
        self.save_results(all_data)
    
    def save_results(self, all_data):
        """Save all crawled data to JSON file"""
        
        total_players = sum(len(league['players']) for league in all_data)
        total_teams = sum(len(league['teams']) for league in all_data)
        total_matches = sum(len(league['matches']) for league in all_data)
        
        print(f"\n💾 SAVING RESULTS:")
        print(f"   📊 {len(all_data)} leagues crawled")
        print(f"   👤 {total_players} players extracted")
        print(f"   🏀 {total_teams} teams extracted") 
        print(f"   🎯 {total_matches} matches extracted")
        
        if all_data:
            output_data = {
                'source': 'basketball-bund.net systematic crawl',
                'strategy': 'User-specified: Action=106 discovery + statistics endpoints + game results',
                'extracted_at': datetime.now().isoformat(),
                'summary': {
                    'total_leagues': len(all_data),
                    'total_players': total_players,
                    'total_teams': total_teams,
                    'total_matches': total_matches
                },
                'leagues': all_data
            }
            
            filename = f'systematic_crawl_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Saved to {filename}")
        else:
            print("   ❌ No data to save")

if __name__ == "__main__":
    crawler = SystematicBasketballCrawler()
    crawler.run_systematic_crawl()
