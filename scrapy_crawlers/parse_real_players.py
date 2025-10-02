#!/usr/bin/env python3
"""
Parse real player data from basketball-bund export
"""
import re

def parse_basketball_export(file_path):
    """Parse the real basketball federation export file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    players = []
    
    # Extract scoring leaders
    scorer_pattern = r'Beste Werfer/innen:\s+absolut\n(.*?)(?=\n\nBeste 3er-Werfer|$)'
    scorer_matches = re.findall(scorer_pattern, content, re.DOTALL)
    
    for scorer_section in scorer_matches:
        lines = scorer_section.strip().split('\n')
        for line in lines:
            if line.strip() and re.match(r'\d+\.', line):
                # Parse line like "1. Krauß (SpVgg Rattelsdorf) 42"
                match = re.search(r'\d+\.\s+(.+?)\s+\((.+?)\)\s+(\d+)', line)
                if match:
                    name = match.group(1).strip()
                    team = match.group(2).strip()
                    points = int(match.group(3))
                    
                    players.append({
                        'name': name,
                        'team': team,
                        'total_points': points,
                        'position': 'Unknown',  # Will need to infer
                        'league': 'Senioren Oberfranken'
                    })
    
    # Extract 3-point leaders
    three_point_pattern = r'Beste 3er-Werfer/innen:\s+absolut\n(.*?)(?=\n\nBeste Freiwerfer|$)'
    three_point_matches = re.findall(three_point_pattern, content, re.DOTALL)
    
    # Add 3-point stats to existing players
    for three_section in three_point_matches:
        lines = three_section.strip().split('\n')
        for line in lines:
            if line.strip() and re.match(r'\d+\.', line):
                # Parse line like "1. Müller (SC Kemmern) 3 1"
                match = re.search(r'\d+\.\s+(.+?)\s+\((.+?)\)\s+(\d+)\s+(\d+)', line)
                if match:
                    name = match.group(1).strip()
                    team = match.group(2).strip()
                    three_made = int(match.group(3))
                    three_attempts = int(match.group(4))
                    
                    # Find existing player or add new one
                    existing_player = None
                    for player in players:
                        if player['name'] == name and player['team'] == team:
                            existing_player = player
                            break
                    
                    if existing_player:
                        existing_player['three_pointers_made'] = three_made
                        existing_player['three_pointers_attempted'] = three_attempts
                    else:
                        players.append({
                            'name': name,
                            'team': team,
                            'total_points': 0,
                            'three_pointers_made': three_made,
                            'three_pointers_attempted': three_attempts,
                            'position': 'Unknown',
                            'league': 'Senioren Oberfranken'
                        })
    
    # Extract real match results and teams
    teams = set()
    match_pattern = r'(\d+)\s+(.+?)\s+-\s+(.+?)\s+(\d+)\s+:\s+(\d+)'
    matches = re.findall(match_pattern, content)
    
    for match in matches:
        home_team = match[1].strip()
        away_team = match[2].strip()
        teams.add(home_team)
        teams.add(away_team)
    
    return players, list(teams)

if __name__ == "__main__":
    file_path = r"c:\Users\StretzS\Downloads\ligaErgExtended (1).txt"
    players, teams = parse_basketball_export(file_path)
    
    print(f"🏀 REAL BASKETBALL FEDERATION DATA PARSED")
    print(f"📊 Found {len(players)} real players")
    print(f"🏟️ Found {len(teams)} real teams")
    
    print("\n🌟 Top Real Players:")
    # Sort by total points
    sorted_players = sorted([p for p in players if p.get('total_points', 0) > 0], 
                          key=lambda x: x.get('total_points', 0), reverse=True)
    
    for i, player in enumerate(sorted_players[:10]):
        three_info = ""
        if player.get('three_pointers_made'):
            pct = (player['three_pointers_made'] / player['three_pointers_attempted'] * 100) if player['three_pointers_attempted'] > 0 else 0
            three_info = f" | 3P: {player['three_pointers_made']}/{player['three_pointers_attempted']} ({pct:.1f}%)"
        
        print(f"{i+1:2d}. {player['name']:20s} ({player['team']:25s}) - {player['total_points']:3d} pts{three_info}")
    
    print(f"\n🏟️ Real Teams Found:")
    for team in sorted(teams):
        print(f"   • {team}")
