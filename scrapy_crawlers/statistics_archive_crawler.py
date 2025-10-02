#!/usr/bin/env python3

import requests
import json
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup

class StatisticsArchiveCrawler:
    """Crawl basketball-bund.net statistics archive pages for player data"""
    
    def __init__(self):
        self.base_url = "https://www.basketball-bund.net"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Referer': 'https://www.basketball-bund.net/',
        })
    
    def test_statistics_url(self, liga_id, saison_id):
        """Test the statistics URL pattern provided by user"""
        
        print(f"=== TESTING STATISTICS URL ===")
        print(f"Liga ID: {liga_id}, Season ID: {saison_id}")
        
        # Different statistics endpoints to try
        stat_endpoints = [
            f"statistik.do?reqCode=statBesteWerferArchiv&liga_id={liga_id}&saison_id={saison_id}&_top=-1",  # Best shooters
            f"statistik.do?reqCode=statBesteSpielerArchiv&liga_id={liga_id}&saison_id={saison_id}&_top=-1",  # Best players
            f"statistik.do?reqCode=statTeamArchiv&liga_id={liga_id}&saison_id={saison_id}",  # Team stats
            f"statistik.do?reqCode=statSpielerArchiv&liga_id={liga_id}&saison_id={saison_id}&_top=-1",  # Player stats
        ]
        
        all_players = []
        
        for endpoint in stat_endpoints:
            url = f"{self.base_url}/{endpoint}"
            print(f"\n🔍 Testing: {url}")
            
            try:
                response = self.session.get(url, timeout=15)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Check if we got player data
                    if self.has_player_statistics(content):
                        print(f"   ✅ Found player statistics!")
                        players = self.parse_statistics_page(content, liga_id, saison_id, endpoint)
                        print(f"   📊 Extracted {len(players)} players")
                        all_players.extend(players)
                        
                        # Save sample HTML for analysis
                        with open(f'sample_stats_{endpoint.split("=")[1]}.html', 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"   💾 Saved sample HTML")
                    else:
                        print(f"   ❌ No player statistics found")
                else:
                    print(f"   ❌ Failed to access")
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return all_players
    
    def has_player_statistics(self, html_content):
        """Check if page contains player statistics"""
        indicators = [
            'spieler', 'punkte', 'rebounds', 'assists', 'würfe',
            'player', 'points', 'statistics', 'werfer', 'statistik',
            'name', 'minuten', 'spiele', 'dreier', 'freiwurf'
        ]
        
        content_lower = html_content.lower()
        
        # Must have multiple indicators to be a real stats page
        found_indicators = sum(1 for indicator in indicators if indicator in content_lower)
        return found_indicators >= 3
    
    def parse_statistics_page(self, html_content, liga_id, saison_id, endpoint):
        """Parse player statistics from HTML page"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            players = []
            
            # Look for statistics tables
            tables = soup.find_all('table')
            
            for table in tables:
                if self.is_statistics_table(table):
                    table_players = self.extract_players_from_table(table, liga_id, saison_id, endpoint)
                    players.extend(table_players)
            
            return players
            
        except Exception as e:
            print(f"      Error parsing statistics page: {e}")
            return []
    
    def is_statistics_table(self, table):
        """Check if table contains player statistics"""
        try:
            # Get all text from table
            table_text = table.get_text().lower()
            
            # Look for statistical headers
            stat_indicators = [
                'spieler', 'name', 'punkte', 'rebounds', 'assists',
                'spiele', 'minuten', 'würfe', 'quote', 'dreier'
            ]
            
            found = sum(1 for indicator in stat_indicators if indicator in table_text)
            return found >= 3
            
        except:
            return False
    
    def extract_players_from_table(self, table, liga_id, saison_id, endpoint):
        """Extract player data from statistics table"""
        try:
            players = []
            rows = table.find_all('tr')
            
            if len(rows) < 2:  # Need header + data rows
                return []
            
            # Analyze header row to understand column structure
            header_row = rows[0]
            headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
            
            print(f"      Table headers: {headers}")
            
            # Map columns to statistics
            column_map = self.map_columns(headers)
            
            # Process data rows
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:  # Need at least name + some stats
                    
                    player_data = {}
                    
                    # Extract data based on column mapping
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            cell_text = cell.get_text(strip=True)
                            
                            if i in column_map:
                                stat_name = column_map[i]
                                
                                if stat_name == 'name':
                                    if cell_text and len(cell_text) > 1 and not cell_text.isdigit():
                                        player_data['name'] = cell_text
                                else:
                                    # Try to convert to number
                                    try:
                                        if ',' in cell_text:
                                            value = float(cell_text.replace(',', '.'))
                                        elif '.' in cell_text or cell_text.isdigit():
                                            value = float(cell_text)
                                        else:
                                            continue
                                        player_data[stat_name] = value
                                    except:
                                        continue
                    
                    # Only add if we have a name and at least one statistic
                    if 'name' in player_data and len(player_data) > 1:
                        player_data.update({
                            'liga_id': liga_id,
                            'saison_id': saison_id,
                            'source_endpoint': endpoint,
                            'source': 'basketball-bund.net statistics archive',
                            'extracted_at': datetime.now().isoformat()
                        })
                        
                        players.append(player_data)
            
            return players
            
        except Exception as e:
            print(f"        Error extracting players from table: {e}")
            return []
    
    def map_columns(self, headers):
        """Map table column headers to statistic names"""
        column_map = {}
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            
            # Name columns
            if any(term in header_lower for term in ['name', 'spieler', 'player']):
                column_map[i] = 'name'
            
            # Points
            elif any(term in header_lower for term in ['punkte', 'points', 'pts']):
                column_map[i] = 'points'
            
            # Games
            elif any(term in header_lower for term in ['spiele', 'games', 'sp']):
                column_map[i] = 'games'
            
            # Minutes
            elif any(term in header_lower for term in ['minuten', 'minutes', 'min']):
                column_map[i] = 'minutes'
            
            # Rebounds
            elif any(term in header_lower for term in ['rebounds', 'reb']):
                column_map[i] = 'rebounds'
            
            # Assists
            elif any(term in header_lower for term in ['assists', 'ass', 'vorlagen']):
                column_map[i] = 'assists'
            
            # Field goals
            elif any(term in header_lower for term in ['feldwurf', 'fg', 'würfe']):
                if 'quote' in header_lower or '%' in header_lower:
                    column_map[i] = 'field_goal_percentage'
                else:
                    column_map[i] = 'field_goals'
            
            # Three pointers
            elif any(term in header_lower for term in ['dreier', '3p', 'drei']):
                if 'quote' in header_lower or '%' in header_lower:
                    column_map[i] = 'three_point_percentage'
                else:
                    column_map[i] = 'three_pointers'
            
            # Free throws
            elif any(term in header_lower for term in ['freiwurf', 'ft', 'frei']):
                if 'quote' in header_lower or '%' in header_lower:
                    column_map[i] = 'free_throw_percentage'
                else:
                    column_map[i] = 'free_throws'
        
        return column_map
    
    def crawl_multiple_leagues_and_seasons(self):
        """Crawl multiple leagues and seasons systematically"""
        
        print("=== SYSTEMATIC STATISTICS ARCHIVE CRAWLING ===")
        
        # Test with the provided example first
        print("\n1. Testing provided URL pattern...")
        test_players = self.test_statistics_url(28217, 2019)
        
        all_players = list(test_players)
        
        # Try other league IDs and seasons
        print("\n2. Testing other league/season combinations...")
        
        # Sample league IDs (from our discovery data)
        league_ids = [47950, 47960, 47940, 47955, 28217, 47965, 47985]
        seasons = [2019, 2020, 2021, 2022, 2023, 2024]
        
        for liga_id in league_ids[:3]:  # Limit to first 3 leagues
            for saison_id in seasons[:2]:  # Limit to first 2 seasons
                print(f"\n   Testing Liga {liga_id}, Season {saison_id}...")
                
                try:
                    league_players = self.test_statistics_url(liga_id, saison_id)
                    if league_players:
                        print(f"   ✅ Got {len(league_players)} players")
                        all_players.extend(league_players)
                    else:
                        print(f"   ❌ No players found")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                time.sleep(random.uniform(2, 4))  # Rate limiting
        
        # Save results
        print(f"\n💾 TOTAL RESULTS: {len(all_players)} players")
        
        if all_players:
            output_data = {
                'source': 'basketball-bund.net statistics archive',
                'extraction_method': 'statistik.do endpoints',
                'extracted_at': datetime.now().isoformat(),
                'total_players': len(all_players),
                'players': all_players
            }
            
            with open('statistics_archive_players.json', 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved to statistics_archive_players.json")
            
            # Summary
            leagues_summary = {}
            for player in all_players:
                liga_id = player.get('liga_id', 'Unknown')
                leagues_summary[liga_id] = leagues_summary.get(liga_id, 0) + 1
            
            print(f"\nPlayers by league ID:")
            for liga_id, count in sorted(leagues_summary.items(), key=lambda x: x[1], reverse=True):
                print(f"  Liga {liga_id}: {count} players")
        else:
            print("❌ No players extracted")

if __name__ == "__main__":
    crawler = StatisticsArchiveCrawler()
    crawler.crawl_multiple_leagues_and_seasons()
