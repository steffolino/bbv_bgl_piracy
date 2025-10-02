#!/usr/bin/env python3
import json

try:
    with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    players = data if isinstance(data, list) else data.get('players', [])
    
    # Find teams in League 26212, Season 2018
    target_teams = {}
    litzendorf_variations = []
    
    for player in players:
        liga_id = player.get('liga_id')
        season_id = player.get('season_id')
        team = player.get('team', '')
        
        # Look for League 26212, Season 2018
        if liga_id == 26212 and season_id == 2018:
            if team in target_teams:
                target_teams[team] += 1
            else:
                target_teams[team] = 1
        
        # Look for any Litzendorf variations
        if 'litzendorf' in team.lower():
            litzendorf_variations.append({
                'team': team,
                'liga_id': liga_id,
                'season_id': season_id,
                'name': player.get('name', 'Unknown')
            })
    
    print(f"=== TEAMS IN LEAGUE 26212, SEASON 2018 ===")
    print(f"Total teams found: {len(target_teams)}")
    
    for team, count in sorted(target_teams.items(), key=lambda x: x[1], reverse=True):
        print(f"  {team}: {count} players")
    
    print(f"\n=== ALL LITZENDORF VARIATIONS ===")
    print(f"Total Litzendorf entries: {len(litzendorf_variations)}")
    
    # Group by team name and league/season
    litz_grouped = {}
    for entry in litzendorf_variations:
        key = f"{entry['team']} (Liga {entry['liga_id']}, Season {entry['season_id']})"
        if key in litz_grouped:
            litz_grouped[key] += 1
        else:
            litz_grouped[key] = 1
    
    for key, count in sorted(litz_grouped.items()):
        print(f"  {key}: {count} players")
    
    # Sample Litzendorf player
    if litzendorf_variations:
        sample = litzendorf_variations[0]
        print(f"\nSample Litzendorf player:")
        print(f"  Name: {sample['name']}")
        print(f"  Team: {sample['team']}")
        print(f"  Liga: {sample['liga_id']}")
        print(f"  Season: {sample['season_id']}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
