#!/usr/bin/env python3

import sqlite3
import requests
import json
import time
import random
from datetime import datetime

class ComprehensivePlayerExtractor:
    """Extract player data from multiple sources and leagues"""
    
    def __init__(self):
        self.base_url = "https://www.basketball-bund.net"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_teams_with_most_matches(self, limit=50):
        """Get teams that have played the most matches (likely to have player data)"""
        conn = sqlite3.connect('basketball_analytics.db')
        cursor = conn.cursor()
        
        # Get teams with most completed matches
        cursor.execute('''
            SELECT t.team_name, t.team_permanent_id, COUNT(*) as match_count
            FROM teams t
            JOIN matches m ON (t.team_permanent_id = m.home_team_id OR t.team_permanent_id = m.guest_team_id)
            WHERE m.home_score IS NOT NULL AND m.guest_score IS NOT NULL
            GROUP BY t.team_permanent_id, t.team_name
            ORDER BY match_count DESC
            LIMIT ?
        ''', (limit,))
        
        teams = cursor.fetchall()
        conn.close()
        return teams
    
    def extract_team_roster(self, team_id, team_name):
        """Try to extract team roster from basketball-bund.net"""
        try:
            # Try different URL patterns for team pages
            potential_urls = [
                f"{self.base_url}/team/{team_id}",
                f"{self.base_url}/teams/{team_id}",
                f"{self.base_url}/rest/team/{team_id}",
                f"{self.base_url}/club/team/{team_id}",
            ]
            
            for url in potential_urls:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                    if data and self.contains_player_data(data):
                        return self.parse_team_roster(data, team_name)
                        
            print(f"No accessible team page found for {team_name} (ID: {team_id})")
            return []
            
        except Exception as e:
            print(f"Error extracting roster for {team_name}: {e}")
            return []
    
    def contains_player_data(self, data):
        """Check if response contains player data"""
        if isinstance(data, dict):
            # Look for common player data indicators
            indicators = ['players', 'roster', 'squad', 'team_members', 'athlete']
            return any(indicator in str(data).lower() for indicator in indicators)
        return False
    
    def parse_team_roster(self, data, team_name):
        """Parse player data from team roster response"""
        players = []
        
        # Handle different response structures
        if isinstance(data, dict):
            # Look for player arrays in different locations
            player_arrays = []
            
            def find_player_arrays(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key.lower() in ['players', 'roster', 'squad', 'athletes', 'members']:
                            if isinstance(value, list):
                                player_arrays.append((value, f"{path}.{key}"))
                        else:
                            find_player_arrays(value, f"{path}.{key}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        find_player_arrays(item, f"{path}[{i}]")
            
            find_player_arrays(data)
            
            # Process found player arrays
            for player_list, path in player_arrays:
                for player_data in player_list:
                    if isinstance(player_data, dict):
                        player = self.extract_player_info(player_data, team_name)
                        if player:
                            players.append(player)
        
        return players
    
    def extract_player_info(self, player_data, team_name):
        """Extract individual player information"""
        try:
            # Common field mappings
            name_fields = ['name', 'player_name', 'full_name', 'displayName', 'firstName', 'lastName']
            position_fields = ['position', 'pos', 'role']
            age_fields = ['age', 'birth_year', 'birthYear']
            number_fields = ['number', 'jersey_number', 'shirt_number']
            
            # Extract name
            name = None
            for field in name_fields:
                if field in player_data:
                    name = player_data[field]
                    break
            
            # Try to construct name from first/last name
            if not name and 'firstName' in player_data and 'lastName' in player_data:
                name = f"{player_data['firstName']} {player_data['lastName']}"
            
            if not name:
                return None
            
            # Extract other fields
            position = next((player_data.get(field) for field in position_fields if field in player_data), None)
            age = next((player_data.get(field) for field in age_fields if field in player_data), None)
            number = next((player_data.get(field) for field in number_fields if field in player_data), None)
            
            return {
                'name': name,
                'team': team_name,
                'position': position,
                'age': age,
                'jersey_number': number,
                'source': 'basketball-bund.net team roster',
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting player info: {e}")
            return None
    
    def extract_players_from_matches(self, limit=100):
        """Extract player names from match results and statistics"""
        conn = sqlite3.connect('basketball_analytics.db')
        cursor = conn.cursor()
        
        # Get recent matches with results
        cursor.execute('''
            SELECT DISTINCT m.match_id, m.home_team_name, m.guest_team_name, m.result
            FROM matches m
            WHERE m.home_score IS NOT NULL AND m.guest_score IS NOT NULL
            AND m.match_id IS NOT NULL
            ORDER BY m.id DESC
            LIMIT ?
        ''', (limit,))
        
        matches = cursor.fetchall()
        conn.close()
        
        players = []
        
        for match_id, home_team, guest_team, result in matches:
            # Try to get match details with potential player statistics
            match_players = self.extract_match_player_data(match_id, home_team, guest_team)
            players.extend(match_players)
            
            # Rate limiting
            time.sleep(random.uniform(0.5, 1.5))
        
        return players
    
    def extract_match_player_data(self, match_id, home_team, guest_team):
        """Try to extract player data from match details"""
        try:
            # Try different match detail endpoints
            potential_urls = [
                f"{self.base_url}/rest/match/{match_id}",
                f"{self.base_url}/match/{match_id}",
                f"{self.base_url}/rest/match/{match_id}/details",
                f"{self.base_url}/rest/match/{match_id}/boxscore",
                f"{self.base_url}/rest/match/{match_id}/statistics",
            ]
            
            for url in potential_urls:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                        if data:
                            players = self.parse_match_players(data, home_team, guest_team)
                            if players:
                                return players
                except:
                    continue
            
            return []
            
        except Exception as e:
            print(f"Error extracting match players for match {match_id}: {e}")
            return []
    
    def parse_match_players(self, match_data, home_team, guest_team):
        """Parse player data from match details"""
        players = []
        
        # Look for player statistics in match data
        def find_player_stats(obj, current_team=None):
            if isinstance(obj, dict):
                # Check for team-specific player data
                if 'homeTeam' in obj or 'home_team' in obj:
                    home_data = obj.get('homeTeam') or obj.get('home_team')
                    if isinstance(home_data, dict):
                        find_player_stats(home_data, home_team)
                
                if 'guestTeam' in obj or 'guest_team' in obj or 'awayTeam' in obj:
                    guest_data = obj.get('guestTeam') or obj.get('guest_team') or obj.get('awayTeam')
                    if isinstance(guest_data, dict):
                        find_player_stats(guest_data, guest_team)
                
                # Look for player arrays
                for key, value in obj.items():
                    if key.lower() in ['players', 'statistics', 'stats', 'boxscore']:
                        if isinstance(value, list):
                            for player_stat in value:
                                if isinstance(player_stat, dict):
                                    player = self.extract_match_player_info(player_stat, current_team or home_team)
                                    if player:
                                        players.append(player)
                    else:
                        find_player_stats(value, current_team)
            
            elif isinstance(obj, list):
                for item in obj:
                    find_player_stats(item, current_team)
        
        find_player_stats(match_data)
        return players
    
    def extract_match_player_info(self, player_stat, team_name):
        """Extract player info from match statistics"""
        try:
            # Look for player name in statistics
            name_fields = ['name', 'player_name', 'playerName', 'full_name']
            stat_fields = ['points', 'pts', 'rebounds', 'reb', 'assists', 'ast']
            
            name = None
            for field in name_fields:
                if field in player_stat:
                    name = player_stat[field]
                    break
            
            if not name:
                return None
            
            # Extract statistics
            stats = {}
            for field in stat_fields:
                if field in player_stat:
                    stats[field] = player_stat[field]
            
            return {
                'name': name,
                'team': team_name,
                'match_stats': stats,
                'source': 'match statistics',
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting match player info: {e}")
            return None
    
    def run_comprehensive_extraction(self):
        """Run comprehensive player data extraction"""
        print("=== COMPREHENSIVE PLAYER DATA EXTRACTION ===")
        
        all_players = []
        
        # 1. Get teams with most matches
        print("\n1. Getting teams with most completed matches...")
        top_teams = self.get_teams_with_most_matches(30)
        print(f"Found {len(top_teams)} teams to process")
        
        # 2. Extract team rosters
        print("\n2. Extracting team rosters...")
        for i, (team_name, team_id, match_count) in enumerate(top_teams[:10], 1):
            print(f"  {i}/10: {team_name} ({match_count} matches)")
            roster_players = self.extract_team_roster(team_id, team_name)
            all_players.extend(roster_players)
            time.sleep(random.uniform(1, 2))  # Rate limiting
        
        # 3. Extract from match statistics
        print("\n3. Extracting players from match statistics...")
        match_players = self.extract_players_from_matches(50)
        all_players.extend(match_players)
        
        # 4. Save results
        print(f"\n4. Saving {len(all_players)} extracted players...")
        
        if all_players:
            output_data = {
                'source': 'Comprehensive basketball-bund.net extraction',
                'extracted_at': datetime.now().isoformat(),
                'total_players': len(all_players),
                'extraction_methods': ['team rosters', 'match statistics'],
                'players': all_players
            }
            
            with open('comprehensive_players_extracted.json', 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(all_players)} players to comprehensive_players_extracted.json")
            
            # Summary by team
            teams = {}
            for player in all_players:
                team = player.get('team', 'Unknown')
                teams[team] = teams.get(team, 0) + 1
            
            print(f"\nPlayers by team:")
            for team, count in sorted(teams.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {team}: {count} players")
        else:
            print("❌ No players extracted")

if __name__ == "__main__":
    extractor = ComprehensivePlayerExtractor()
    extractor.run_comprehensive_extraction()
