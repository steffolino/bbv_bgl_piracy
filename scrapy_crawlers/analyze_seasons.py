#!/usr/bin/env python3
import json

try:
    with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    players = data if isinstance(data, list) else data.get('players', [])
    
    # Find all unique seasons and leagues
    seasons = set()
    leagues = set()
    season_league_combos = set()
    
    for player in players:
        season_id = player.get('season_id')
        liga_id = player.get('liga_id')
        
        if season_id is not None:
            seasons.add(season_id)
        if liga_id is not None:
            leagues.add(liga_id)
        if season_id is not None and liga_id is not None:
            season_league_combos.add((season_id, liga_id))
    
    print(f"=== DATASET OVERVIEW ===")
    print(f"Total players: {len(players)}")
    print(f"Unique seasons: {sorted(seasons)}")
    print(f"Unique leagues: {sorted(leagues)}")
    print(f"Season/League combinations: {len(season_league_combos)}")
    
    print(f"\n=== AVAILABLE SEASON/LEAGUE COMBINATIONS ===")
    for season, league in sorted(season_league_combos):
        # Count players in this combination
        count = sum(1 for p in players if p.get('season_id') == season and p.get('liga_id') == league)
        print(f"Season {season}, Liga {league}: {count} players")
    
    # Check if BG Litzendorf exists in any combination
    print(f"\n=== BG LITZENDORF AVAILABILITY ===")
    litzendorf_combos = set()
    for player in players:
        team = player.get('team', '')
        if 'litzendorf' in team.lower():
            season_id = player.get('season_id')
            liga_id = player.get('liga_id')
            litzendorf_combos.add((team, season_id, liga_id))
    
    if litzendorf_combos:
        for team, season, league in sorted(litzendorf_combos):
            count = sum(1 for p in players if p.get('team') == team and p.get('season_id') == season and p.get('liga_id') == league)
            print(f"'{team}' in Season {season}, Liga {league}: {count} players")
    else:
        print("No Litzendorf teams found in dataset")
    
    # Find the most common season/league combination
    print(f"\n=== RECOMMENDED DEFAULT PARAMETERS ===")
    combo_counts = {}
    for season, league in season_league_combos:
        count = sum(1 for p in players if p.get('season_id') == season and p.get('liga_id') == league)
        combo_counts[(season, league)] = count
    
    if combo_counts:
        best_combo = max(combo_counts.items(), key=lambda x: x[1])
        season, league = best_combo[0]
        count = best_combo[1]
        print(f"Largest dataset: Season {season}, Liga {league} with {count} players")
        
        # Find teams in this combination
        teams_in_best = {}
        for player in players:
            if player.get('season_id') == season and player.get('liga_id') == league:
                team = player.get('team', '')
                teams_in_best[team] = teams_in_best.get(team, 0) + 1
        
        print(f"Top 10 teams in Season {season}, Liga {league}:")
        for i, (team, count) in enumerate(sorted(teams_in_best.items(), key=lambda x: x[1], reverse=True)[:10]):
            print(f"  {i+1}. {team}: {count} players")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
