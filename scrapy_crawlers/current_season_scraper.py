#!/usr/bin/env python3
"""
🏀 CURRENT SEASON SCRAPER 2025/26 🏀
Weekly updated scraper for live basketball data

Features:
- Live games and box scores
- Current standings
- Player statistics
- Team rosters
- Weekly schedule updates

Run weekly to keep data fresh!
"""

import requests
import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib

class CurrentSeasonScraper:
    def __init__(self):
        self.base_url = "https://www.basketball-bund.net"
        self.api_url = "https://www.basketball-bund.net/rest/wam/data"
        self.league_base = "https://www.basketball-bund.net/static/#/liga"
        
        # Authentication cookies (update weekly!)
        self.cookies = {
            "__cmpcc": "1",
            "__cmpconsentx47082": "CQYqGvAQYqGvAAfQ6BENB-FgAP_AAEPAAAigJSkR5C5cDWFBeTp3QMskeYQX0cgBZgABAgaAASABCDAAcIQAkkESIAyAAAACAQAAIDSBAAAADAhAAEAAAIgBAADoAAAEgBAIIAAEABERQ0IAAAgKCIgAEAAIAAAxIkAAkAKAAILiQFAAgIAiAAABAAAAAIABAAMAAAAIAAACAAIAAAAAAAAAgAAAAAACABAIAAAAAAAAII3wPgAFgAVAAuABwADwAIAAVAAyABoADwAI4ATAAuABiADQAG8APwAhABDACaAE4AMAAYYA5wB3QD8AP0AhABFgCOAEiAJMASkAsQBigDXgG0AOIAdsA_oB_wEXgJWATEAmQBNIChwFHgKRAU2Ap8BboC5AF5gMhAZIAywBlwDTQHFgPHAhWBG8AAA.f_gACHgAAAA",
            "SESSION": "NDkzOWM2ZDktMzYyOS00MjlhLTk1OTEtNzFlYmNjZTZmNWNh",
            "_cc_id": "b616c325dc88e1ae505ba80bd46882fe"
        }
        
        # Payload for current season data
        self.payload = {
            "token": 0,
            "verbandIds": [2],  # Basketball federation
            "gebietIds": ["5_"]  # Gebiet 5 (likely Oberfranken region)
        }
        
        # Known current league IDs (update as needed)
        self.current_leagues = [
            47955,  # Example current league
            47956,  # Add more as discovered
            47957,
            47958,
            47959,
            47960
        ]
        
        self.session = requests.Session()
        self.session.cookies.update(self.cookies)
        
    def discover_current_leagues(self) -> List[int]:
        """Discover active 2025/26 leagues"""
        print("🔍 Discovering active 2025/26 leagues...")
        
        active_leagues = []
        
        # Test current year patterns (higher IDs for newer seasons)
        test_ranges = [
            (47950, 48000),  # Current season range
            (48000, 48050),  # Next range
            (49000, 49050),  # Future range
        ]
        
        for start_id, end_id in test_ranges:
            print(f"   Testing range {start_id}-{end_id}...")
            
            for league_id in range(start_id, end_id):
                try:
                    url = f"{self.base_url}/rest/competition/actual/id/{league_id}"
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            season = data.get('season', {})
                            season_name = season.get('name', '') if season else ''
                            
                            # Look for 2025/2026 season
                            if '2025' in season_name or '2026' in season_name:
                                league_name = data.get('name', 'Unknown')
                                matches = data.get('matches', [])
                                
                                active_leagues.append({
                                    'id': league_id,
                                    'name': league_name,
                                    'season': season_name,
                                    'matches': len(matches)
                                })
                                
                                print(f"✅ Found: {league_id} - {league_name} ({len(matches)} matches)")
                        
                        except json.JSONDecodeError:
                            pass
                    
                    time.sleep(0.1)  # Be polite
                    
                except requests.RequestException:
                    pass
        
        print(f"✅ Discovered {len(active_leagues)} active leagues")
        return [league['id'] for league in active_leagues]
    
    def get_league_data(self, league_id: int) -> Optional[Dict]:
        """Get complete league data including standings and games"""
        print(f"📊 Fetching league {league_id} data...")
        
        try:
            url = f"{self.base_url}/rest/competition/actual/id/{league_id}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                league_info = {
                    'id': league_id,
                    'name': data.get('name', ''),
                    'season': data.get('season', {}).get('name', ''),
                    'matches': data.get('matches', []),
                    'teams': data.get('teams', []),
                    'table': data.get('table', []),
                    'fetched_at': datetime.now().isoformat()
                }
                
                print(f"   ✅ {league_info['name']}: {len(league_info['matches'])} matches, {len(league_info['teams'])} teams")
                return league_info
            
        except Exception as e:
            print(f"   ❌ Error fetching league {league_id}: {e}")
        
        return None
    
    def get_current_week_games(self, leagues_data: List[Dict]) -> List[Dict]:
        """Extract games from current week"""
        print("📅 Extracting current week games...")
        
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)
        
        current_week_games = []
        
        for league in leagues_data:
            for match in league.get('matches', []):
                match_date_str = match.get('date', '')
                if match_date_str:
                    try:
                        # Parse date (adjust format as needed)
                        match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
                        
                        if week_start <= match_date <= week_end:
                            game_info = {
                                'league_id': league['id'],
                                'league_name': league['name'],
                                'match_id': match.get('id'),
                                'date': match_date_str,
                                'home_team': match.get('homeTeam', {}).get('name', ''),
                                'away_team': match.get('awayTeam', {}).get('name', ''),
                                'home_score': match.get('homeScore'),
                                'away_score': match.get('awayScore'),
                                'status': match.get('status', ''),
                                'venue': match.get('venue', {}),
                                'box_score_available': bool(match.get('boxScore'))
                            }
                            current_week_games.append(game_info)
                    
                    except (ValueError, TypeError):
                        continue
        
        print(f"   ✅ Found {len(current_week_games)} games this week")
        return current_week_games
    
    def get_box_score(self, match_id: str) -> Optional[Dict]:
        """Get detailed box score for a match"""
        if not match_id:
            return None
            
        try:
            url = f"{self.base_url}/rest/match/{match_id}/boxscore"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            print(f"   ⚠️ Box score error for {match_id}: {e}")
        
        return None
    
    def save_to_database(self, leagues_data: List[Dict], games_data: List[Dict]):
        """Save current season data to database"""
        print("💾 Saving to database...")
        
        try:
            db_path = "../league_cache.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create current_season table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS current_season_leagues (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    season TEXT,
                    teams_count INTEGER,
                    matches_count INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data JSON
                )
            """)
            
            # Create current_games table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS current_games (
                    id TEXT PRIMARY KEY,
                    league_id INTEGER,
                    match_id TEXT,
                    date TEXT,
                    home_team TEXT,
                    away_team TEXT,
                    home_score INTEGER,
                    away_score INTEGER,
                    status TEXT,
                    venue JSON,
                    box_score JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert league data
            for league in leagues_data:
                cursor.execute("""
                    INSERT OR REPLACE INTO current_season_leagues
                    (id, name, season, teams_count, matches_count, data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    league['id'],
                    league['name'],
                    league['season'],
                    len(league.get('teams', [])),
                    len(league.get('matches', [])),
                    json.dumps(league)
                ))
            
            # Insert games data
            for game in games_data:
                game_id = f"{game['league_id']}_{game['match_id']}"
                cursor.execute("""
                    INSERT OR REPLACE INTO current_games
                    (id, league_id, match_id, date, home_team, away_team, 
                     home_score, away_score, status, venue)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    game_id,
                    game['league_id'],
                    game['match_id'],
                    game['date'],
                    game['home_team'],
                    game['away_team'],
                    game['home_score'],
                    game['away_score'],
                    game['status'],
                    json.dumps(game.get('venue', {}))
                ))
            
            conn.commit()
            conn.close()
            
            print(f"   ✅ Saved {len(leagues_data)} leagues and {len(games_data)} games")
            
        except Exception as e:
            print(f"   ❌ Database error: {e}")
    
    def run_weekly_update(self):
        """Main function for weekly data update"""
        print("🏀 CURRENT SEASON WEEKLY UPDATE")
        print("=" * 50)
        print(f"📅 Update date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🏆 Season: 2025/26")
        print()
        
        # Discover current leagues
        active_league_ids = self.discover_current_leagues()
        if not active_league_ids:
            active_league_ids = self.current_leagues  # Fallback to known IDs
        
        # Get league data
        leagues_data = []
        for league_id in active_league_ids:
            league_data = self.get_league_data(league_id)
            if league_data:
                leagues_data.append(league_data)
            time.sleep(1)  # Rate limiting
        
        # Get current week games
        current_games = self.get_current_week_games(leagues_data)
        
        # Enhance games with box scores (for completed games)
        print("📋 Fetching box scores for completed games...")
        for i, game in enumerate(current_games):
            if game['status'] == 'FINISHED' and game['box_score_available']:
                box_score = self.get_box_score(game['match_id'])
                if box_score:
                    game['box_score'] = box_score
                    print(f"   ✅ Box score for {game['home_team']} vs {game['away_team']}")
                time.sleep(0.5)  # Rate limiting
        
        # Save to database
        self.save_to_database(leagues_data, current_games)
        
        # Save to files for backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        leagues_file = f"current_season_leagues_{timestamp}.json"
        with open(leagues_file, 'w', encoding='utf-8') as f:
            json.dump(leagues_data, f, indent=2, ensure_ascii=False)
        
        games_file = f"current_week_games_{timestamp}.json"
        with open(games_file, 'w', encoding='utf-8') as f:
            json.dump(current_games, f, indent=2, ensure_ascii=False)
        
        # Summary
        print("\\n🎉 WEEKLY UPDATE COMPLETE!")
        print("=" * 50)
        print(f"📊 Leagues updated: {len(leagues_data)}")
        print(f"🏀 Current week games: {len(current_games)}")
        completed_games = len([g for g in current_games if g['status'] == 'FINISHED'])
        print(f"✅ Completed games: {completed_games}")
        upcoming_games = len([g for g in current_games if g['status'] != 'FINISHED'])
        print(f"📅 Upcoming games: {upcoming_games}")
        print(f"💾 Files: {leagues_file}, {games_file}")
        
        # Show upcoming highlights
        if upcoming_games > 0:
            print("\\n🔥 UPCOMING GAMES THIS WEEK:")
            for game in current_games:
                if game['status'] != 'FINISHED':
                    print(f"   📅 {game['date'][:10]}: {game['home_team']} vs {game['away_team']}")
        
        print("\\n📈 Next update: Run this script again next week!")
        print("💡 Update cookies if authentication expires")

def main():
    """Main execution"""
    scraper = CurrentSeasonScraper()
    scraper.run_weekly_update()

if __name__ == "__main__":
    main()
