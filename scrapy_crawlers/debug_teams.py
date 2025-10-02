#!/usr/bin/env python3
import json

try:
    with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get unique team names
    teams = set()
    litzendorf_players = []
    
    players = data if isinstance(data, list) else data.get('players', [])
    
    for player in players:
        team = player.get('team', '')
        teams.add(team)
        
        # Look for Litzendorf specifically
        if 'litzendorf' in team.lower():
            litzendorf_players.append(player)
    
    print(f"Total teams found: {len(teams)}")
    print("\nFirst 20 teams:")
    for i, team in enumerate(sorted(teams)[:20]):
        print(f"  {i+1}. {team}")
    
    print(f"\nLitzendorf players found: {len(litzendorf_players)}")
    if litzendorf_players:
        sample = litzendorf_players[0]
        print(f"Sample Litzendorf player: {sample.get('name')} - Team: {sample.get('team')}")
        print(f"Liga ID: {sample.get('liga_id')}, Season: {sample.get('season_id')}")
    
    # Check for exact match
    bg_litzendorf_players = [p for p in players if p.get('team') == 'BG Litzendorf']
    print(f"\nExact 'BG Litzendorf' matches: {len(bg_litzendorf_players)}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
