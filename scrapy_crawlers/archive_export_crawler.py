#!/usr/bin/env python3

import requests
import json
import time
import random
from datetime import datetime
import sqlite3

class ArchiveExportCrawler:
    """Crawl basketball-bund.net archive pages and use export buttons to get player data"""
    
    def __init__(self):
        self.base_url = "https://www.basketball-bund.net"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def load_working_leagues(self):
        """Load leagues that we know are working from discovery"""
        try:
            with open('rest_archive_discovery.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            leagues = []
            for item in data:
                if item.get('type') == 'working_league':
                    leagues.append({
                        'liga_id': item['liga_id'],
                        'liga_name': item['liga_name'],
                        'bezirk_name': item.get('bezirk_name'),
                        'season_name': item['season_name'],
                        'matches_count': item['matches_count'],
                        'teams_count': item['teams_count']
                    })
            
            print(f"Loaded {len(leagues)} working leagues")
            return leagues
            
        except Exception as e:
            print(f"Error loading leagues: {e}")
            return []
    
    def try_archive_export(self, liga_id, liga_name):
        """Try to access archive page and find export buttons"""
        try:
            # Try different archive URL patterns
            archive_urls = [
                f"{self.base_url}/index.jsp?Action=101&liga_id={liga_id}",
                f"{self.base_url}/index.jsp?Action=100&liga_id={liga_id}",
                f"{self.base_url}/index.jsp?Action=106&liga_id={liga_id}",
                f"{self.base_url}/index.jsp?Action=102&liga_id={liga_id}",  # Tabelle
                f"{self.base_url}/index.jsp?Action=103&liga_id={liga_id}",  # Spieler
            ]
            
            for url in archive_urls:
                print(f"  Trying: {url}")
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Look for export buttons or player data
                    if self.has_export_functionality(content):
                        print(f"  ✅ Found export functionality!")
                        return self.extract_export_data(url, content, liga_name)
                    elif self.has_player_data(content):
                        print(f"  ✅ Found player data in page!")
                        return self.extract_player_data_from_html(content, liga_name)
                    else:
                        print(f"  ❌ No player data found")
                
                time.sleep(random.uniform(1, 2))
            
            return []
            
        except Exception as e:
            print(f"  Error accessing archive for {liga_name}: {e}")
            return []
    
    def has_export_functionality(self, html_content):
        """Check if page has export buttons or download links"""
        export_indicators = [
            'export', 'download', 'excel', 'csv', 'xls',
            'herunterladen', 'exportieren', 'Action=104',
            'Action=105', 'statistik', 'spielerstatistik'
        ]
        
        content_lower = html_content.lower()
        return any(indicator in content_lower for indicator in export_indicators)
    
    def has_player_data(self, html_content):
        """Check if page contains player names or statistics"""
        player_indicators = [
            'spieler', 'punkte', 'rebounds', 'assists',
            'player', 'points', 'statistics', 'stats',
            'minuten', 'minutes', 'dreier', 'freiwurf'
        ]
        
        content_lower = html_content.lower()
        return any(indicator in content_lower for indicator in player_indicators)
    
    def extract_export_data(self, url, content, liga_name):
        """Try to extract data from export functionality"""
        try:
            # Look for export URLs in the HTML
            import re
            
            # Find export/download links
            export_patterns = [
                r'href="([^"]*Action=104[^"]*)"',  # Export action
                r'href="([^"]*Action=105[^"]*)"',  # Statistics action
                r'href="([^"]*excel[^"]*)"',       # Excel export
                r'href="([^"]*csv[^"]*)"',         # CSV export
                r'href="([^"]*download[^"]*)"',    # Download links
            ]
            
            export_urls = []
            for pattern in export_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                export_urls.extend(matches)
            
            # Try each export URL
            players = []
            for export_url in export_urls[:3]:  # Limit to first 3 to avoid spam
                if not export_url.startswith('http'):
                    export_url = f"{self.base_url}/{export_url.lstrip('/')}"
                
                print(f"    Trying export URL: {export_url}")
                
                try:
                    export_response = self.session.get(export_url, timeout=10)
                    if export_response.status_code == 200:
                        export_players = self.parse_export_response(export_response, liga_name)
                        players.extend(export_players)
                        if export_players:
                            print(f"    ✅ Got {len(export_players)} players from export")
                            break
                except:
                    continue
                
                time.sleep(1)
            
            return players
            
        except Exception as e:
            print(f"    Error extracting export data: {e}")
            return []
    
    def extract_player_data_from_html(self, content, liga_name):
        """Extract player data directly from HTML table"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            players = []
            
            # Look for tables with player data
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if table looks like player statistics
                if self.is_player_table(table):
                    table_players = self.parse_player_table(table, liga_name)
                    players.extend(table_players)
            
            return players
            
        except Exception as e:
            print(f"    Error parsing HTML player data: {e}")
            return []
    
    def is_player_table(self, table):
        """Check if HTML table contains player data"""
        try:
            # Look at headers to see if it's a player table
            headers = table.find_all(['th', 'td'])
            header_text = ' '.join([h.get_text().lower() for h in headers[:10]])
            
            player_header_indicators = [
                'spieler', 'name', 'punkte', 'rebounds', 'assists',
                'player', 'points', 'minutes', 'spiele', 'games'
            ]
            
            return any(indicator in header_text for indicator in player_header_indicators)
            
        except:
            return False
    
    def parse_player_table(self, table, liga_name):
        """Parse player data from HTML table"""
        try:
            players = []
            rows = table.find_all('tr')
            
            # Skip header row, process data rows
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:  # Need at least name and some stats
                    
                    # Extract player name (usually first or second column)
                    player_name = None
                    for cell in cells[:3]:
                        text = cell.get_text(strip=True)
                        if text and len(text) > 2 and not text.isdigit():
                            player_name = text
                            break
                    
                    if player_name:
                        # Extract statistics from remaining cells
                        stats = {}
                        cell_values = [cell.get_text(strip=True) for cell in cells]
                        
                        # Try to identify statistics columns
                        for i, value in enumerate(cell_values):
                            if value.replace('.', '').replace(',', '').isdigit():
                                if i == 1:
                                    stats['games'] = float(value.replace(',', '.'))
                                elif i == 2:
                                    stats['points'] = float(value.replace(',', '.'))
                                elif i == 3:
                                    stats['rebounds'] = float(value.replace(',', '.'))
                                elif i == 4:
                                    stats['assists'] = float(value.replace(',', '.'))
                        
                        player = {
                            'name': player_name,
                            'league': liga_name,
                            'source': 'archive_html_table',
                            'extracted_at': datetime.now().isoformat(),
                            **stats
                        }
                        
                        players.append(player)
            
            return players
            
        except Exception as e:
            print(f"      Error parsing player table: {e}")
            return []
    
    def parse_export_response(self, response, liga_name):
        """Parse player data from export response (CSV, Excel, etc.)"""
        try:
            content_type = response.headers.get('content-type', '').lower()
            players = []
            
            if 'csv' in content_type or 'text' in content_type:
                # Parse CSV data
                lines = response.text.split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 2:
                            player = {
                                'name': parts[0].strip().strip('"'),
                                'league': liga_name,
                                'source': 'archive_csv_export',
                                'extracted_at': datetime.now().isoformat()
                            }
                            # Add stats if available
                            for i, part in enumerate(parts[1:]):
                                if part.strip().replace('.', '').isdigit():
                                    stat_names = ['games', 'points', 'rebounds', 'assists', 'minutes']
                                    if i < len(stat_names):
                                        player[stat_names[i]] = float(part.strip())
                            
                            players.append(player)
            
            elif 'json' in content_type:
                # Parse JSON data
                data = response.json()
                # Process JSON structure to extract player data
                players = self.extract_players_from_json(data, liga_name)
            
            return players
            
        except Exception as e:
            print(f"      Error parsing export response: {e}")
            return []
    
    def extract_players_from_json(self, data, liga_name):
        """Extract player data from JSON response"""
        players = []
        
        def find_players_recursive(obj):
            if isinstance(obj, dict):
                # Look for player arrays
                for key, value in obj.items():
                    if 'player' in key.lower() and isinstance(value, list):
                        for player_data in value:
                            if isinstance(player_data, dict) and 'name' in player_data:
                                player = {
                                    'name': player_data['name'],
                                    'league': liga_name,
                                    'source': 'archive_json_export',
                                    'extracted_at': datetime.now().isoformat(),
                                    **{k: v for k, v in player_data.items() if k != 'name'}
                                }
                                players.append(player)
                    else:
                        find_players_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    find_players_recursive(item)
        
        find_players_recursive(data)
        return players
    
    def run_archive_export_crawl(self):
        """Run comprehensive archive export crawling"""
        print("=== BASKETBALL-BUND.NET ARCHIVE EXPORT CRAWLING ===")
        
        # Load working leagues
        leagues = self.load_working_leagues()
        if not leagues:
            print("❌ No working leagues found")
            return
        
        print(f"\n📋 Found {len(leagues)} leagues to crawl:")
        for league in leagues:
            print(f"  - {league['liga_name']} ({league['bezirk_name']}) - {league['teams_count']} teams")
        
        all_players = []
        
        # Process each league
        for i, league in enumerate(leagues[:10], 1):  # Limit to first 10 to start
            liga_id = league['liga_id']
            liga_name = league['liga_name']
            bezirk = league['bezirk_name'] or 'Unknown'
            
            print(f"\n{i:2d}/{min(10, len(leagues))}: {liga_name} ({bezirk})")
            
            # Try archive export for this league
            league_players = self.try_archive_export(liga_id, f"{liga_name} {bezirk}")
            
            if league_players:
                print(f"     ✅ Extracted {len(league_players)} players")
                all_players.extend(league_players)
            else:
                print(f"     ❌ No players extracted")
            
            # Rate limiting
            time.sleep(random.uniform(2, 4))
        
        # Save results
        print(f"\n💾 SAVING RESULTS: {len(all_players)} total players")
        
        if all_players:
            output_data = {
                'source': 'basketball-bund.net archive export crawling',
                'extracted_at': datetime.now().isoformat(),
                'total_players': len(all_players),
                'leagues_crawled': min(10, len(leagues)),
                'players': all_players
            }
            
            with open('archive_export_players.json', 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved to archive_export_players.json")
            
            # Summary by league
            leagues_summary = {}
            for player in all_players:
                league = player.get('league', 'Unknown')
                leagues_summary[league] = leagues_summary.get(league, 0) + 1
            
            print(f"\nPlayers by league:")
            for league, count in sorted(leagues_summary.items(), key=lambda x: x[1], reverse=True):
                print(f"  {league}: {count} players")
        else:
            print("❌ No players extracted from any league")

if __name__ == "__main__":
    # Install BeautifulSoup if not available
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Installing BeautifulSoup...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'beautifulsoup4'])
        from bs4 import BeautifulSoup
    
    crawler = ArchiveExportCrawler()
    crawler.run_archive_export_crawl()
