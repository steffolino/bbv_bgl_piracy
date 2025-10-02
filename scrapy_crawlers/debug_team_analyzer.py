#!/usr/bin/env python3
from team_analyzer import TeamAnalyzer
import json

try:
    analyzer = TeamAnalyzer('real_players_extracted.json')
    
    print("=== TEAM ANALYZER DEBUG ===")
    print(f"Total teams in index: {len(analyzer.teams)}")
    
    # Find all Litzendorf teams
    litzendorf_teams = []
    for team_name in analyzer.teams.keys():
        if 'litzendorf' in team_name.lower():
            litzendorf_teams.append(team_name)
    
    print(f"\nLitzendorf teams found in index:")
    for team in litzendorf_teams:
        print(f"  '{team}'")
        team_info = analyzer.teams[team]
        print(f"    Players: {len(team_info['players'])}")
        print(f"    Leagues: {team_info['leagues']}")
        print(f"    Seasons: {team_info['seasons']}")
    
    # Test exact lookup
    print(f"\n=== EXACT LOOKUP TESTS ===")
    test_names = ['BG Litzendorf 2', 'BG Litzendorf']
    
    for test_name in test_names:
        print(f"\nTesting: '{test_name}'")
        print(f"  In teams index: {test_name in analyzer.teams}")
        
        # Try getting team details
        details = analyzer.get_team_details(test_name, 26211, 2018)
        if details:
            print(f"  ✅ Found team details: {details['roster_size']} players")
        else:
            print(f"  ❌ No team details returned")
    
    # Show all teams starting with 'BG'
    print(f"\n=== ALL BG TEAMS ===")
    bg_teams = [name for name in analyzer.teams.keys() if name.startswith('BG')]
    for team in sorted(bg_teams)[:10]:
        print(f"  '{team}'")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
