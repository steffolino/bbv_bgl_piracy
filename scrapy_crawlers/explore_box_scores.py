#!/usr/bin/env python3
"""
📊 BOX SCORE EXPLORER 📊
Test fetching real box scores from current 2025/26 season
"""

import requests
import json
from datetime import datetime
import time

class BoxScoreExplorer:
    def __init__(self):
        self.base_url = "https://www.basketball-bund.net"
        
        # Authentication cookies
        self.cookies = {
            "__cmpcc": "1",
            "__cmpconsentx47082": "CQYqGvAQYqGvAAfQ6BENB-FgAP_AAEPAAAigJSkR5C5cDWFBeTp3QMskeYQX0cgBZgABAgaAASABCDAAcIQAkkESIAyAAAACAQAAIDSBAAAADAhAAEAAAIgBAADoAAAEgBAIIAAEABERQ0IAAAgKCIgAEAAIAAAxIkAAkAKAAILiQFAAgIAiAAABAAAAAIABAAMAAAAIAAACAAIAAAAAAAAAgAAAAAACABAIAAAAAAAAII3wPgAFgAVAAuABwADwAIAAVAAyABoADwAI4ATAAuABiADQAG8APwAhABDACaAE4AMAAYYA5wB3QD8AP0AhABFgCOAEiAJMASkAsQBigDXgG0AOIAdsA_oB_wEXgJWATEAmQBNIChwFHgKRAU2Ap8BboC5AF5gMhAZIAywBlwDTQHFgPHAhWBG8AAA.f_gACHgAAAA",
            "SESSION": "NDkzOWM2ZDktMzYyOS00MjlhLTk1OTEtNzFlYmNjZTZmNWNh",
            "_cc_id": "b616c325dc88e1ae505ba80bd46882fe"
        }
        
        self.session = requests.Session()
        self.session.cookies.update(self.cookies)
        
        # Current league IDs
        self.current_leagues = [47817, 47818, 47955, 47956, 50779, 50824, 51790, 52098, 52102, 52106]
    
    def get_league_matches(self, league_id: int):
        """Get all matches for a league"""
        print(f"🔍 Fetching matches for league {league_id}...")
        
        try:
            url = f"{self.base_url}/rest/competition/actual/id/{league_id}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('matches', [])
                league_name = data.get('name', f'League {league_id}')
                
                print(f"   ✅ {league_name}: {len(matches)} matches")
                return matches, league_name
            else:
                print(f"   ❌ HTTP {response.status_code}")
                return [], f"League {league_id}"
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return [], f"League {league_id}"
    
    def get_box_score(self, match_id: str, match_info: dict = None):
        """Get detailed box score for a match"""
        try:
            url = f"{self.base_url}/rest/match/{match_id}/boxscore"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                box_score = response.json()
                
                if match_info:
                    home_team = match_info.get('homeTeam', {}).get('name', 'Home')
                    away_team = match_info.get('awayTeam', {}).get('name', 'Away')
                    date = match_info.get('date', '')[:10]
                    print(f"   📊 Box score: {home_team} vs {away_team} ({date})")
                
                return box_score
            else:
                print(f"   ⚠️ No box score data (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            print(f"   ❌ Box score error: {e}")
            return None
    
    def analyze_box_score_structure(self, box_score: dict):
        """Analyze what data is in a box score"""
        print("\\n📊 BOX SCORE DATA STRUCTURE:")
        print("=" * 60)
        
        if not box_score:
            print("❌ No box score data to analyze")
            return
        
        # Top-level keys
        print("🔍 Top-level data:")
        for key, value in box_score.items():
            if isinstance(value, list):
                print(f"   • {key}: {len(value)} items")
            elif isinstance(value, dict):
                print(f"   • {key}: {len(value)} keys")
            else:
                print(f"   • {key}: {type(value).__name__}")
        
        # Game info
        if 'game' in box_score:
            game = box_score['game']
            print(f"\\n🏀 Game Info:")
            print(f"   Date: {game.get('date', 'N/A')}")
            print(f"   Home: {game.get('homeTeam', {}).get('name', 'N/A')}")
            print(f"   Away: {game.get('awayTeam', {}).get('name', 'N/A')}")
            print(f"   Score: {game.get('homeScore', 'N/A')}:{game.get('awayScore', 'N/A')}")
        
        # Quarter scores
        if 'periods' in box_score:
            periods = box_score['periods']
            print(f"\\n📈 Quarter Scores: {len(periods)} periods")
            for i, period in enumerate(periods, 1):
                home_score = period.get('homeScore', 0)
                away_score = period.get('awayScore', 0)
                period_name = period.get('name', f'Q{i}')
                print(f"   {period_name}: {home_score}-{away_score}")
        
        # Player statistics
        if 'playerStats' in box_score:
            player_stats = box_score['playerStats']
            if 'home' in player_stats and 'away' in player_stats:
                home_players = player_stats['home']
                away_players = player_stats['away']
                print(f"\\n👥 Player Stats:")
                print(f"   Home team: {len(home_players)} players")
                print(f"   Away team: {len(away_players)} players")
                
                # Show sample player stats
                if home_players:
                    sample_player = home_players[0]
                    print(f"\\n📊 Sample Player Stats (Keys Available):")
                    for key in sample_player.keys():
                        print(f"   • {key}")
        
        # Team statistics
        if 'teamStats' in box_score:
            team_stats = box_score['teamStats']
            print(f"\\n🏀 Team Stats:")
            if 'home' in team_stats:
                print(f"   Home team stats: {len(team_stats['home'])} categories")
            if 'away' in team_stats:
                print(f"   Away team stats: {len(team_stats['away'])} categories")
    
    def find_completed_games(self):
        """Find completed games with box scores"""
        print("🎯 SEARCHING FOR COMPLETED GAMES WITH BOX SCORES")
        print("=" * 60)
        
        completed_games = []
        
        # Check top leagues first (men's and women's senior)
        priority_leagues = [47955, 47956]  # Bezirksoberliga Herren & Damen
        
        for league_id in priority_leagues:
            matches, league_name = self.get_league_matches(league_id)
            
            for match in matches:
                status = match.get('status', '')
                match_id = match.get('id')
                
                # Look for finished games
                if status == 'FINISHED' and match_id:
                    home_team = match.get('homeTeam', {}).get('name', 'Home')
                    away_team = match.get('awayTeam', {}).get('name', 'Away')
                    date = match.get('date', '')[:10]
                    home_score = match.get('homeScore')
                    away_score = match.get('awayScore')
                    
                    if home_score is not None and away_score is not None:
                        game_info = {
                            'league_id': league_id,
                            'league_name': league_name,
                            'match_id': match_id,
                            'date': date,
                            'home_team': home_team,
                            'away_team': away_team,
                            'home_score': home_score,
                            'away_score': away_score,
                            'match_data': match
                        }
                        completed_games.append(game_info)
                        
                        print(f"   ✅ {date}: {home_team} {home_score}:{away_score} {away_team}")
            
            time.sleep(1)  # Rate limiting
        
        print(f"\\n🎯 Found {len(completed_games)} completed games")
        return completed_games
    
    def explore_box_scores(self):
        """Main exploration function"""
        print("📊 BOX SCORE EXPLORATION - SEASON 2025/26")
        print("=" * 60)
        print("Searching for real box score data...")
        print()
        
        # Find completed games
        completed_games = self.find_completed_games()
        
        if not completed_games:
            print("⚠️ No completed games found yet (early in season)")
            print("📅 Check back after some games have been played")
            return
        
        # Try to get box scores for the first few games
        print(f"\\n📊 TESTING BOX SCORE ACCESS:")
        print("=" * 60)
        
        successful_box_scores = []
        
        for i, game in enumerate(completed_games[:3], 1):  # Test first 3 games
            print(f"\\n🎯 Game {i}: {game['home_team']} vs {game['away_team']} ({game['date']})")
            
            box_score = self.get_box_score(game['match_id'], game)
            
            if box_score:
                successful_box_scores.append({
                    'game_info': game,
                    'box_score': box_score
                })
                
                # Save for inspection
                filename = f"box_score_{game['match_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'game_info': game,
                        'box_score': box_score
                    }, f, indent=2, ensure_ascii=False)
                
                print(f"   💾 Saved to: {filename}")
                
                # Analyze the structure
                self.analyze_box_score_structure(box_score)
                break  # Analyze just the first successful one
            
            time.sleep(1)  # Rate limiting
        
        # Summary
        print(f"\\n🎉 BOX SCORE EXPLORATION COMPLETE!")
        print("=" * 60)
        print(f"📊 Completed games found: {len(completed_games)}")
        print(f"✅ Box scores retrieved: {len(successful_box_scores)}")
        
        if successful_box_scores:
            print("\\n🚀 BOX SCORE FEATURES AVAILABLE:")
            print("   • Player statistics (points, rebounds, assists, etc.)")
            print("   • Quarter-by-quarter scoring")
            print("   • Team statistics")
            print("   • Game details and timing")
            print("   • Individual performance tracking")
            print("\\n💡 WEEKLY UPDATE POTENTIAL:")
            print("   • Fresh box scores every week")
            print("   • Player performance trends")
            print("   • Team statistics evolution")
            print("   • League standings with detailed stats")
        else:
            print("\\n📅 Season may be too early for box score data")
            print("   Games need to be completed and processed first")

def main():
    """Main execution"""
    explorer = BoxScoreExplorer()
    explorer.explore_box_scores()

if __name__ == "__main__":
    main()
