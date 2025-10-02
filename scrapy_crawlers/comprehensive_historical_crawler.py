#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random

class ComprehensiveHistoricalCrawler:
    """
    Crawl basketball-bund.net using the Action=106 endpoint
    Going back to 2003 - perfect for Basketball Reference-style multi-season analysis!
    """
    
    def __init__(self):
        self.base_url = "https://www.basketball-bund.net/index.jsp"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        
    def crawl_historical_seasons(self, start_year=2003, end_year=2025):
        """
        Crawl all seasons from 2003 to current using Action=106 endpoint
        Perfect for your Basketball Reference frontend!
        """
        
        print("🏀 COMPREHENSIVE HISTORICAL BASKETBALL CRAWLER")
        print(f"📅 Crawling seasons {start_year} to {end_year} (22+ years of data!)")
        print("🎯 Building ultimate dataset for Basketball Reference-style frontend")
        
        # Define Oberfranken parameters (adjust based on your needs)
        oberfranken_params = {
            'Action': '106',
            'cbSpielklasseFilter': '0',  # All league levels
            'cbAltersklasseFilter': '1',  # Senioren (Adults) - adjust if needed
            'cbGeschlechtFilter': '0',   # All genders
            'cbBezirkFilter': 'OBERFRANKEN_ID',  # Need to find Oberfranken ID
            'cbKreisFilter': '0'         # All Kreis
        }
        
        all_seasons_data = []
        working_seasons = []
        total_players = 0
        
        # Test each season
        for season in range(start_year, end_year + 1):
            print(f"\n📊 CRAWLING SEASON {season}")
            
            season_data = self.crawl_season(season, oberfranken_params)
            
            if season_data and season_data['players']:
                working_seasons.append(season)
                all_seasons_data.append(season_data)
                total_players += len(season_data['players'])
                
                print(f"  ✅ Season {season}: {len(season_data['players'])} players from {season_data.get('leagues_count', 0)} leagues")
                
                # Save individual season immediately
                self.save_season_data(season_data)
            else:
                print(f"  ❌ Season {season}: No data")
            
            # Rate limiting
            time.sleep(random.uniform(1, 3))
        
        # Save comprehensive multi-season dataset
        if all_seasons_data:
            self.save_comprehensive_dataset(all_seasons_data, working_seasons, total_players)
            
            print(f"\n🎯 HISTORICAL CRAWL COMPLETE!")
            print(f"📊 Successful seasons: {working_seasons}")
            print(f"👤 Total players: {total_players:,}")
            print(f"📅 Season range: {min(working_seasons)}-{max(working_seasons)}")
            print(f"🏀 Perfect for Basketball Reference frontend with {len(working_seasons)} seasons!")
        else:
            print(f"\n❌ No data found - may need to adjust parameters")
        
        return all_seasons_data
    
    def crawl_season(self, season, base_params):
        """
        Crawl a specific season using Action=106 endpoint
        """
        
        # Prepare form data for POST request
        form_data = base_params.copy()
        form_data['saison_id'] = str(season)
        
        try:
            print(f"  🔍 Requesting season {season}...")
            
            # Make POST request to Action=106 endpoint
            response = self.session.post(
                self.base_url,
                data=form_data,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"  ✅ Response received ({len(response.text)} chars)")
                
                # Parse the response
                season_data = self.parse_season_response(response.text, season)
                return season_data
            else:
                print(f"  ❌ HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def parse_season_response(self, html_content, season):
        """
        Parse the HTML response to extract basketball data
        """
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for different data structures that might be present
            players = []
            leagues = []
            teams = set()
            
            # Method 1: Look for player statistics tables
            players.extend(self.extract_player_statistics(soup, season))
            
            # Method 2: Look for league/team listings
            leagues.extend(self.extract_league_data(soup, season))
            
            # Method 3: Look for match data
            matches = self.extract_match_data(soup, season)
            
            # Collect all teams
            for player in players:
                if player.get('team'):
                    teams.add(player['team'])
            
            return {
                'season': season,
                'extraction_timestamp': datetime.now().isoformat(),
                'source': f'Action=106 endpoint - Season {season}',
                'players': players,
                'leagues': leagues,
                'matches': matches,
                'teams': sorted(list(teams)),
                'players_count': len(players),
                'leagues_count': len(leagues),
                'teams_count': len(teams),
                'matches_count': len(matches)
            }
            
        except Exception as e:
            print(f"    ❌ Parse error: {e}")
            return None
    
    def extract_player_statistics(self, soup, season):
        """
        Extract player statistics from various table formats
        """
        
        players = []
        
        # Look for tables that might contain player data
        tables = soup.find_all('table')
        
        for table in tables:
            # Check if this looks like a player statistics table
            if self.is_player_statistics_table(table):
                table_players = self.parse_player_table(table, season)
                players.extend(table_players)
        
        return players
    
    def is_player_statistics_table(self, table):
        """
        Determine if a table contains player statistics
        """
        
        try:
            # Look at table headers and content
            headers = table.find_all(['th', 'td'])
            header_text = ' '.join([h.get_text().lower() for h in headers[:20]])
            
            # Check for basketball/player indicators
            basketball_indicators = [
                'spieler', 'name', 'punkte', 'rebounds', 'assists',
                'player', 'points', 'games', 'spiele', 'mannschaft',
                'team', 'verein', 'korb', 'wurf', 'statistik'
            ]
            
            indicator_count = sum(1 for indicator in basketball_indicators if indicator in header_text)
            
            # Also check table size (should have reasonable number of rows/columns)
            rows = table.find_all('tr')
            
            return indicator_count >= 2 and len(rows) >= 3
            
        except:
            return False
    
    def parse_player_table(self, table, season):
        """
        Parse a player statistics table
        """
        
        players = []
        
        try:
            rows = table.find_all('tr')
            
            # Skip header row(s), process data rows
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 3:  # Minimum: name, team, some stat
                    
                    cell_texts = []
                    for cell in cells:
                        text = cell.get_text(strip=True).replace('\u00a0', ' ')
                        cell_texts.append(text)
                    
                    # Try to identify player data structure
                    player = self.identify_player_from_cells(cell_texts, season)
                    
                    if player and player.get('name'):
                        players.append(player)
                        
        except Exception as e:
            print(f"      Parse error in player table: {e}")
        
        return players
    
    def identify_player_from_cells(self, cells, season):
        """
        Identify player information from table cells
        """
        
        if len(cells) < 3:
            return None
        
        player = {
            'season_id': season,
            'source': 'Action=106',
            'extracted_at': datetime.now().isoformat()
        }
        
        # Try different cell arrangements
        # Common patterns: [rank, name, team, stats...] or [name, team, stats...]
        
        try:
            # Look for name patterns (usually contains letters, not just numbers)
            name_candidates = []
            team_candidates = []
            stat_candidates = []
            
            for i, cell in enumerate(cells):
                if cell and len(cell) > 1:
                    # Check if it looks like a name (contains letters, reasonable length)
                    if any(c.isalpha() for c in cell) and 2 <= len(cell) <= 50:
                        if any(keyword in cell.lower() for keyword in ['fc', 'sg', 'bg', 'tv', 'tsv', 'sc', 'bc']):
                            team_candidates.append((i, cell))
                        else:
                            name_candidates.append((i, cell))
                    
                    # Check if it looks like a stat (number)
                    if cell.replace('.', '').replace(',', '').isdigit():
                        stat_candidates.append((i, int(cell.replace(',', '.'))))
            
            # Assign based on patterns
            if name_candidates:
                player['name'] = name_candidates[0][1]
            
            if team_candidates:
                player['team'] = team_candidates[0][1]
            
            # Add statistics if available
            if stat_candidates:
                # Assume first numeric value is points or games
                if len(stat_candidates) >= 1:
                    player['stat_1'] = stat_candidates[0][1]
                if len(stat_candidates) >= 2:
                    player['stat_2'] = stat_candidates[1][1]
                if len(stat_candidates) >= 3:
                    player['stat_3'] = stat_candidates[2][1]
            
            return player if player.get('name') else None
            
        except:
            return None
    
    def extract_league_data(self, soup, season):
        """
        Extract league information
        """
        
        leagues = []
        
        # Look for league listings, dropdown options, etc.
        # This would depend on the specific HTML structure returned
        
        return leagues
    
    def extract_match_data(self, soup, season):
        """
        Extract match information
        """
        
        matches = []
        
        # Look for match listings, scoreboards, etc.
        # This would depend on the specific HTML structure returned
        
        return matches
    
    def save_season_data(self, season_data):
        """
        Save individual season data
        """
        
        season = season_data['season']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f'historical_season_{season}_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(season_data, f, indent=2, ensure_ascii=False)
        
        print(f"    💾 Saved: {filename}")
    
    def save_comprehensive_dataset(self, all_seasons_data, working_seasons, total_players):
        """
        Save comprehensive multi-season dataset for Basketball Reference frontend
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Combine all players from all seasons
        all_players = []
        for season_data in all_seasons_data:
            all_players.extend(season_data['players'])
        
        # Create frontend-ready dataset
        comprehensive_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'source': 'Comprehensive historical crawl using Action=106 endpoint',
            'seasons_available': sorted(working_seasons),
            'season_range': f"{min(working_seasons)}-{max(working_seasons)}",
            'total_seasons': len(working_seasons),
            'total_players': total_players,
            'total_teams': len(set(p.get('team') for p in all_players if p.get('team'))),
            'seasons_data': all_seasons_data,
            'players': all_players
        }
        
        # Save main comprehensive file
        main_filename = f'comprehensive_historical_basketball_{timestamp}.json'
        with open(main_filename, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
        
        # Update frontend data file (merge with existing)
        try:
            # Try to merge with existing real_players_extracted.json
            existing_players = []
            try:
                with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_players = existing_data.get('players', [])
            except:
                pass
            
            # Combine existing + new data
            combined_players = existing_players + all_players
            existing_seasons = [2018]  # Your known existing seasons
            all_available_seasons = sorted(list(set(existing_seasons + working_seasons)))
            
            frontend_data = {
                'extraction_timestamp': datetime.now().isoformat(),
                'source': 'Combined historical data (2018 archive + Action=106 multi-season)',
                'seasons_available': all_available_seasons,
                'total_seasons': len(all_available_seasons),
                'total_players': len(combined_players),
                'historical_coverage': f"{min(all_available_seasons)}-{max(all_available_seasons)}",
                'players': combined_players
            }
            
            with open('real_players_extracted.json', 'w', encoding='utf-8') as f:
                json.dump(frontend_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Updated real_players_extracted.json")
            print(f"📊 Combined dataset: {len(combined_players):,} players across {len(all_available_seasons)} seasons")
            
        except Exception as e:
            print(f"⚠️  Could not merge with existing data: {e}")
        
        print(f"\n💾 Saved comprehensive dataset: {main_filename}")
        print(f"🏀 Perfect for Basketball Reference frontend with {len(working_seasons)} historical seasons!")

def test_action_106_endpoint():
    """
    Quick test of the Action=106 endpoint to understand its response format
    """
    
    print("🧪 TESTING ACTION=106 ENDPOINT")
    
    crawler = ComprehensiveHistoricalCrawler()
    
    # Test with a single recent season first
    test_params = {
        'Action': '106',
        'saison_id': '2018',  # Start with known working season
        'cbSpielklasseFilter': '0',
        'cbAltersklasseFilter': '1',  # Senioren
        'cbGeschlechtFilter': '0',
        'cbBezirkFilter': '0',  # All districts for now
        'cbKreisFilter': '0'
    }
    
    try:
        response = crawler.session.post(
            crawler.base_url,
            data=test_params,
            timeout=15
        )
        
        if response.status_code == 200:
            print(f"✅ Response received: {len(response.text)} characters")
            
            # Save raw response for analysis
            with open('action_106_test_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print("💾 Raw response saved to action_106_test_response.html")
            
            # Quick analysis
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')
            forms = soup.find_all('form')
            
            print(f"📊 Found {len(tables)} tables, {len(forms)} forms")
            
            # Look for basketball-related content
            content = response.text.lower()
            basketball_keywords = ['basketball', 'liga', 'saison', 'spieler', 'mannschaft', 'verein']
            found_keywords = [kw for kw in basketball_keywords if kw in content]
            
            print(f"🏀 Basketball keywords found: {found_keywords}")
            
            return True
            
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # First test the endpoint
    print("Step 1: Testing Action=106 endpoint...")
    if test_action_106_endpoint():
        print("\nStep 2: Ready to crawl multiple seasons!")
        
        # Uncomment to run full historical crawl
        # crawler = ComprehensiveHistoricalCrawler()
        # crawler.crawl_historical_seasons(start_year=2015, end_year=2023)
    else:
        print("❌ Endpoint test failed - need to adjust parameters")
