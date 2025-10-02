#!/usr/bin/env python3
import json
from team_analyzer import TeamAnalyzer

# Test the team analyzer directly
try:
    analyzer = TeamAnalyzer('real_players_extracted.json')
    
    # Test BG Litzendorf specifically
    team_details = analyzer.get_team_details('BG Litzendorf', 26212, 2018)
    
    print("=== TEAM ANALYZER TEST ===")
    print(f"Team found: {team_details is not None}")
    
    if team_details:
        print(f"Team name: {team_details.get('team_name')}")
        print(f"Players: {team_details.get('roster_size')}")
        print(f"Total points: {team_details.get('total_points')}")
        print(f"Organization: {team_details.get('organization') is not None}")
        
        # Show first few players
        players = team_details.get('players', [])
        print(f"Sample players ({len(players)} total):")
        for i, player in enumerate(players[:3]):
            print(f"  {i+1}. {player.get('name')} - {player.get('team')} - {player.get('points')} pts")
    else:
        print("❌ No team details returned")
        
        # Let's see what teams ARE available
        print("\nAvailable teams:")
        for team_name in list(analyzer.teams.keys())[:10]:
            print(f"  - {team_name}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
