#!/usr/bin/env python3

import json

def analyze_historical_data():
    """Analyze historical data structure to find league names"""
    
    print('=== HISTORICAL DATA LEAGUE ANALYSIS ===')

    with open('historical_production_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f'Data type: {type(data)}')

    if isinstance(data, list):
        print(f'List with {len(data)} items')
        
        leagues_found = {}
        
        for i, item in enumerate(data):
            if isinstance(item, dict):
                # Look for league names in various fields
                league_name = None
                league_id = None
                
                # Check for found_league_name
                if 'found_league_name' in item:
                    league_name = item['found_league_name']
                
                # Check for league_id
                if 'league_id' in item:
                    league_id = item['league_id']
                
                # Check for cached_league_name
                if 'cached_league_name' in item:
                    cached_name = item['cached_league_name']
                    if cached_name and cached_name.strip():
                        league_name = cached_name
                
                # Check nested structures
                if 'api_league_data' in item and isinstance(item['api_league_data'], dict):
                    api_data = item['api_league_data']
                    if 'name' in api_data:
                        league_name = api_data['name']
                    elif 'league_name' in api_data:
                        league_name = api_data['league_name']
                
                # Store found leagues
                if league_name and league_name.strip():
                    leagues_found[league_id or f'unknown_{i}'] = league_name.strip()
        
        print(f'\n=== FOUND LEAGUES ({len(leagues_found)}) ===')
        
        if leagues_found:
            for i, (league_id, name) in enumerate(sorted(leagues_found.items(), key=lambda x: str(x[1])), 1):
                print(f'{i:3d}. {name} (ID: {league_id})')
        else:
            print('No league names found in historical data')
            
            # Show sample structure
            print('\n=== SAMPLE DATA STRUCTURE ===')
            for i, item in enumerate(data[:3]):
                print(f'\nItem {i+1} keys:')
                if isinstance(item, dict):
                    for key in item.keys():
                        value = item[key]
                        if isinstance(value, str) and len(value) < 50:
                            print(f'  {key}: "{value}"')
                        else:
                            print(f'  {key}: {type(value)}')

if __name__ == "__main__":
    analyze_historical_data()
