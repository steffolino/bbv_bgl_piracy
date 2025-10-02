#!/usr/bin/env python3
import json

def examine_match_structure():
    """Examine the actual structure of match data to understand how to extract players"""
    
    print("🔍 EXAMINING MATCH DATA STRUCTURE")
    print("=" * 60)
    
    # Load and examine historical data
    with open('historical_production_data.json', 'r', encoding='utf-8') as f:
        historical_data = json.load(f)
    
    print(f"📊 Total league seasons: {len(historical_data)}")
    
    # Find a league with matches and examine structure
    for i, league_season in enumerate(historical_data[:5]):
        print(f"\n🏀 League Season {i+1}:")
        print(f"   League ID: {league_season.get('league_id')}")
        print(f"   Season: {league_season.get('season_year')}")
        print(f"   League Name: {league_season.get('found_league_name', 'N/A')}")
        
        matches = league_season.get('matches', [])
        print(f"   Matches: {len(matches)}")
        
        if matches:
            sample_match = matches[0]
            print(f"   Sample match type: {type(sample_match)}")
            print(f"   Sample match: {sample_match}")
            
            if isinstance(sample_match, dict):
                print(f"   Match keys: {list(sample_match.keys())}")
                
                # Look for any data that might contain player info
                for key, value in sample_match.items():
                    if isinstance(value, (list, dict)) and len(str(value)) > 50:
                        print(f"   {key}: {type(value)} - {str(value)[:100]}...")
                    else:
                        print(f"   {key}: {value}")
            
        # Check if there's a 'table' or 'sample_matches' for this league
        if 'table' in league_season:
            table = league_season['table']
            print(f"   Table type: {type(table)}")
            if isinstance(table, list) and table:
                print(f"   Table sample: {table[0]}")
        
        if 'sample_matches' in league_season:
            sample_matches = league_season['sample_matches']
            print(f"   Sample matches type: {type(sample_matches)}")
            if isinstance(sample_matches, list) and sample_matches:
                print(f"   Sample match structure: {sample_matches[0]}")
                
        print("-" * 40)
        
        if i >= 2:  # Only check first few
            break
    
    # Also check if there are other files with player data
    other_files = ['rest_api_results.json', 'archive_results.json']
    
    for filename in other_files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"\n📄 {filename}:")
                print(f"   Type: {type(data)}")
                if isinstance(data, list) and data:
                    print(f"   Items: {len(data)}")
                    sample = data[0]
                    print(f"   Sample keys: {list(sample.keys()) if isinstance(sample, dict) else 'Not dict'}")
                elif isinstance(data, dict):
                    print(f"   Keys: {list(data.keys())}")
        except FileNotFoundError:
            print(f"   {filename}: Not found")
        except Exception as e:
            print(f"   {filename}: Error - {e}")

if __name__ == "__main__":
    examine_match_structure()
