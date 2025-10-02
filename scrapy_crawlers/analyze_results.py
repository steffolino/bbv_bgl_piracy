#!/usr/bin/env python3

import json
from collections import Counter

def analyze_production_data():
    """Analyze the production data to understand what we collected."""
    data = json.load(open('historical_production_data.json'))
    
    print(f'Total leagues collected: {len(data)}')
    print('\nData quality analysis:')
    leagues_with_matches = [l for l in data if l.get('match_count', 0) > 0]
    print(f'Leagues with matches: {len(leagues_with_matches)}')
    print(f'Average matches per league: {sum(l.get("match_count", 0) for l in data) / len(data):.1f}')
    print(f'Max matches in a league: {max(l.get("match_count", 0) for l in data)}')

    print('\nSeason distribution:')
    season_counts = {}
    for league in data:
        season = league.get('season_year', 'Unknown')
        season_counts[season] = season_counts.get(season, 0) + 1
    for season in sorted(season_counts.keys()):
        print(f'  {season}: {season_counts[season]} leagues')

    print('\nMatch count distribution:')
    match_counts = {}
    for league in data:
        count = league.get('match_count', 0)
        if count == 0:
            bin_key = '0'
        elif count <= 10:
            bin_key = '1-10'
        elif count <= 20:
            bin_key = '11-20'
        elif count <= 30:
            bin_key = '21-30'
        elif count <= 50:
            bin_key = '31-50'
        else:
            bin_key = '50+'
        match_counts[bin_key] = match_counts.get(bin_key, 0) + 1
    
    for range_key in ['0', '1-10', '11-20', '21-30', '31-50', '50+']:
        if range_key in match_counts:
            print(f'  {range_key} matches: {match_counts[range_key]} leagues')

    print('\nTop 10 leagues by match count:')
    sorted_leagues = sorted(data, key=lambda x: x.get('match_count', 0), reverse=True)[:10]
    for i, league in enumerate(sorted_leagues, 1):
        league_id = league.get('league_id', 'Unknown')
        season = league.get('season_year', 'Unknown')
        matches = league.get('match_count', 0)
        print(f'  {i:2d}. League {league_id} ({season}): {matches} matches')

    print('\nData completeness overview:')
    leagues_with_results = 0
    leagues_with_teams = 0
    total_matches = 0
    
    for league in data:
        if league.get('sample_matches'):
            sample_has_results = any(match.get('has_result') for match in league['sample_matches'])
            if sample_has_results:
                leagues_with_results += 1
        
        team_count = league.get('team_count', 0)
        if team_count > 0:
            leagues_with_teams += 1
        
        total_matches += league.get('match_count', 0)
    
    print(f'  Total matches across all leagues: {total_matches:,}')
    print(f'  Leagues with match results: {leagues_with_results}')
    print(f'  Leagues with team data: {leagues_with_teams}')

if __name__ == '__main__':
    analyze_production_data()
