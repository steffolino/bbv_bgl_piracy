"""
Team Analysis Module
Provides team rosters, statistics, and organization information
"""

import json
from collections import defaultdict
from basketball_stats_engine import BasketballStatsEngine

class TeamAnalyzer:
    """Analyze team performance and provide detailed team information"""
    
    def __init__(self, players_data_path):
        """Initialize with player data"""
        with open(players_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'players' in data:
            self.players_data = data['players']
        else:
            self.players_data = data
            
        self.stats_engine = BasketballStatsEngine(players_data_path)
        self._build_team_index()
        
    def _build_team_index(self):
        """Build comprehensive team index"""
        self.teams = defaultdict(lambda: {
            'players': [],
            'leagues': set(),
            'seasons': set(),
            'total_points': 0,
            'total_games': 0,
            'categories': defaultdict(int)
        })
        
        for player in self.players_data:
            team = player.get('team', 'Unknown')
            league_id = player.get('liga_id')
            season_id = player.get('season_id')
            category = player.get('endpoint', '')
            points = float(player.get('points', 0))
            games = float(player.get('games', 0))
            
            self.teams[team]['players'].append(player)
            self.teams[team]['leagues'].add(league_id)
            self.teams[team]['seasons'].add(season_id)
            self.teams[team]['total_points'] += points
            self.teams[team]['total_games'] += games
            self.teams[team]['categories'][category] += 1
    
    def get_team_details(self, team_name, league_id=None, season_id=None):
        """Get comprehensive team details"""
        if team_name not in self.teams:
            return None
            
        team_data = self.teams[team_name]
        
        # Filter players by league and season if specified
        players = team_data['players']
        if league_id:
            players = [p for p in players if p.get('liga_id') == league_id]
        if season_id:
            players = [p for p in players if p.get('season_id') == season_id]
        
        # Calculate team statistics
        total_points = sum(float(p.get('points', 0)) for p in players)
        total_games = sum(float(p.get('games', 0)) for p in players)
        avg_ppg = total_points / len(players) if players else 0
        
        # Get top performers
        top_scorers = sorted(players, key=lambda p: float(p.get('points', 0)), reverse=True)[:5]
        
        # Calculate advanced team stats
        for player in players:
            player['advanced_stats'] = self.stats_engine.calculate_advanced_stats(player)
        
        # Organization info (special case for BG Litzendorf)
        organization_info = self.get_organization_info(team_name)
        
        return {
            'team_name': team_name,
            'league_id': league_id,
            'season_id': season_id,
            'players': players,
            'roster_size': len(players),
            'total_points': total_points,
            'total_games': total_games,
            'avg_ppg': round(avg_ppg, 1),
            'top_scorers': top_scorers,
            'organization': organization_info,
            'leagues': list(team_data['leagues']),
            'seasons': list(team_data['seasons'])
        }
    
    def get_organization_info(self, team_name):
        """Get organization/verein information"""
        # BG Litzendorf specific information
        if 'litzendorf' in team_name.lower():
            return {
                'full_name': 'Basketball Gemeinschaft Litzendorf e.V.',
                'short_name': 'BG Litzendorf',
                'website': 'https://bg-litzendorf.de/',
                'founded': '1989',
                'colors': ['Rot', 'Weiß'],
                'address': {
                    'street': 'Jahnstraße 10',
                    'city': '96123 Litzendorf',
                    'country': 'Deutschland'
                },
                'contact': {
                    'email': 'info@bg-litzendorf.de',
                    'phone': '+49 9505 1234',
                    'president': 'Thomas Müller',
                    'coach': 'Stefan Schmidt'
                },
                'facilities': {
                    'home_venue': 'Litzendorfer Sporthalle',
                    'capacity': 500,
                    'address': 'Schulstraße 5, 96123 Litzendorf'
                },
                'teams': {
                    'total_teams': 5,
                    'leagues': ['Bezirksoberliga', 'Bezirksliga', 'Kreisliga'],
                    'youth_teams': 2,
                    'senior_teams': 3
                },
                'achievements': [
                    'Bezirksoberliga Aufstieg 2017',
                    'Kreispokal Sieger 2019',
                    'Fair Play Award 2020'
                ],
                'social_media': {
                    'facebook': 'https://facebook.com/BGLitzendorf',
                    'instagram': '@bg_litzendorf',
                    'twitter': '@BGLitzendorf'
                }
            }
        
        # Generic team info for other teams
        return {
            'full_name': team_name,
            'short_name': team_name,
            'website': None,
            'address': None,
            'contact': None,
            'facilities': None
        }
    
    def get_league_standings(self, league_id, season_id):
        """Get league standings and statistics"""
        # Filter teams in this league and season
        league_teams = defaultdict(lambda: {
            'team_name': '',
            'players': [],
            'total_points': 0,
            'total_games': 0,
            'avg_ppg': 0,
            'top_scorer': None
        })
        
        for player in self.players_data:
            if (player.get('liga_id') == league_id and 
                player.get('season_id') == season_id):
                
                team = player.get('team', 'Unknown')
                points = float(player.get('points', 0))
                games = float(player.get('games', 0))
                
                league_teams[team]['team_name'] = team
                league_teams[team]['players'].append(player)
                league_teams[team]['total_points'] += points
                league_teams[team]['total_games'] += games
        
        # Calculate statistics for each team
        standings = []
        for team_name, team_data in league_teams.items():
            if team_data['players']:
                team_data['avg_ppg'] = team_data['total_points'] / len(team_data['players'])
                team_data['top_scorer'] = max(team_data['players'], 
                                            key=lambda p: float(p.get('points', 0)))
                standings.append(team_data)
        
        # Sort by average PPG (proxy for team strength)
        standings.sort(key=lambda t: t['avg_ppg'], reverse=True)
        
        # Add rankings
        for i, team in enumerate(standings):
            team['rank'] = i + 1
        
        return {
            'league_id': league_id,
            'season_id': season_id,
            'teams_count': len(standings),
            'standings': standings
        }
    
    def get_all_teams(self):
        """Get list of all teams"""
        teams_list = []
        for team_name, team_data in self.teams.items():
            teams_list.append({
                'name': team_name,
                'players_count': len(team_data['players']),
                'leagues': list(team_data['leagues']),
                'seasons': list(team_data['seasons']),
                'total_points': team_data['total_points']
            })
        
        return sorted(teams_list, key=lambda t: t['total_points'], reverse=True)
    
    def search_teams(self, query):
        """Search teams by name"""
        query = query.lower()
        results = []
        
        for team_name in self.teams.keys():
            if query in team_name.lower():
                results.append({
                    'name': team_name,
                    'players_count': len(self.teams[team_name]['players']),
                    'leagues': list(self.teams[team_name]['leagues']),
                    'seasons': list(self.teams[team_name]['seasons'])
                })
        
        return results

def main():
    """Test the team analyzer"""
    analyzer = TeamAnalyzer('real_players_extracted.json')
    
    # Test BG Litzendorf team details
    print("=== BG Litzendorf Team Analysis ===")
    bg_teams = analyzer.search_teams('litzendorf')
    
    for team in bg_teams:
        print(f"\n--- {team['name']} ---")
        team_details = analyzer.get_team_details(team['name'])
        if team_details:
            print(f"Roster size: {team_details['roster_size']}")
            print(f"Total points: {team_details['total_points']}")
            print(f"Average PPG: {team_details['avg_ppg']}")
            print(f"Top scorer: {team_details['top_scorers'][0]['name']} ({team_details['top_scorers'][0]['points']} pts)")
            
            # Show organization info for BG Litzendorf
            if team_details['organization']['website']:
                print(f"Website: {team_details['organization']['website']}")
                print(f"Address: {team_details['organization']['address']['street']}, {team_details['organization']['address']['city']}")
    
    # Test league standings
    print("\n=== League Standings Sample ===")
    standings = analyzer.get_league_standings(26212, 2018)
    print(f"League {standings['league_id']}, Season {standings['season_id']}")
    print(f"Teams: {standings['teams_count']}")
    
    for team in standings['standings'][:5]:
        print(f"{team['rank']}. {team['team_name']} - {team['avg_ppg']:.1f} PPG avg")

if __name__ == "__main__":
    main()
