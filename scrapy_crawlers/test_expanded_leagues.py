#!/usr/bin/env python3
"""
Extended test script to check broader league ID patterns and verify our known working leagues
"""

import requests
import json
import time
from typing import List, Dict, Optional

def test_known_leagues():
    """Test our previously known working leagues"""
    
    print("🔍 Testing previously known working leagues...")
    print("=" * 60)
    
    # Known working leagues from our cache
    known_leagues = [47960, 47961, 47962, 47963, 47964, 47965]
    
    for league_id in known_leagues:
        try:
            url = f"https://www.basketball-bund.net/rest/competition/actual/id/{league_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if data and isinstance(data, dict):
                        league_name = data.get('name', 'Unknown')
                        season = data.get('season', {})
                        season_name = season.get('name', 'Unknown') if season else 'Unknown'
                        matches = data.get('matches', [])
                        match_count = len(matches) if matches else 0
                        
                        print(f"✅ League {league_id}: {league_name}")
                        print(f"   Season: {season_name}")
                        print(f"   Matches: {match_count}")
                        print(f"   Status: {'Active' if match_count > 0 else 'No matches'}")
                        print()
                        
                except json.JSONDecodeError:
                    print(f"❌ League {league_id}: Invalid JSON response")
            else:
                print(f"❌ League {league_id}: HTTP {response.status_code}")
                
        except requests.RequestException as e:
            print(f"❌ League {league_id}: Connection error - {e}")
        
        time.sleep(0.2)

def test_expanded_ranges():
    """Test expanded ranges to find current season patterns"""
    
    print("\n🔍 Testing expanded league ID ranges for current patterns...")
    print("=" * 60)
    
    # Much broader ranges
    test_ranges = [
        # Very recent IDs
        (52000, 52100),
        (51000, 51100), 
        (50500, 50600),
        
        # Previous known ranges
        (47000, 47100),
        (46000, 46100),
        (45000, 45100),
    ]
    
    active_leagues = []
    
    for start_id, end_id in test_ranges:
        print(f"\n🔍 Testing range {start_id}-{end_id}...")
        found_in_range = 0
        
        for league_id in range(start_id, end_id + 1):
            try:
                url = f"https://www.basketball-bund.net/rest/competition/actual/id/{league_id}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        if data and isinstance(data, dict) and data.get('name'):
                            league_name = data.get('name', 'Unknown')
                            season = data.get('season', {})
                            season_name = season.get('name', 'Unknown') if season else 'Unknown'
                            matches = data.get('matches', [])
                            match_count = len(matches) if matches else 0
                            
                            active_leagues.append({
                                'id': league_id,
                                'name': league_name,
                                'season': season_name,
                                'matches': match_count,
                                'url': url
                            })
                            
                            found_in_range += 1
                            print(f"   ✅ {league_id}: {league_name[:50]} | {season_name} | {match_count} matches")
                            
                    except json.JSONDecodeError:
                        pass
                
                # Shorter delay for broader search
                time.sleep(0.05)
                
            except requests.RequestException:
                pass
            
            # Show progress every 25 IDs
            if league_id % 25 == 0:
                print(f"   ... tested up to {league_id} (found {found_in_range} active)")
        
        print(f"   Range {start_id}-{end_id}: Found {found_in_range} active leagues")
    
    return active_leagues

def analyze_season_patterns(leagues: List[Dict]):
    """Analyze the season patterns we found"""
    
    if not leagues:
        print("\n❌ No leagues found to analyze")
        return
    
    print(f"\n📊 Analysis of {len(leagues)} discovered leagues:")
    print("=" * 60)
    
    # Group by season
    seasons = {}
    for league in leagues:
        season = league['season']
        if season not in seasons:
            seasons[season] = []
        seasons[season].append(league)
    
    print(f"🏆 Seasons found:")
    for season, season_leagues in seasons.items():
        total_matches = sum(l['matches'] for l in season_leagues)
        print(f"   • {season}: {len(season_leagues)} leagues, {total_matches} total matches")
    
    # Look for current season indicators
    current_seasons = []
    for season in seasons.keys():
        if any(year in str(season) for year in ['2024', '2025', '2026']):
            current_seasons.append(season)
    
    if current_seasons:
        print(f"\n🎯 Current season patterns found:")
        for season in current_seasons:
            season_leagues = seasons[season]
            print(f"\n   📅 {season}:")
            for league in sorted(season_leagues, key=lambda x: x['id']):
                print(f"      ID {league['id']:5d}: {league['name'][:60]:60} ({league['matches']} matches)")
    
    # Check for Oberfranken
    oberfranken_leagues = [l for l in leagues if 'oberfranken' in l['name'].lower()]
    if oberfranken_leagues:
        print(f"\n🎯 Bezirk Oberfranken leagues:")
        for league in oberfranken_leagues:
            print(f"   • ID {league['id']}: {league['name']} ({league['season']}, {league['matches']} matches)")

if __name__ == "__main__":
    # Test known leagues first
    test_known_leagues()
    
    # Then test expanded ranges
    active_leagues = test_expanded_ranges()
    
    # Analyze what we found
    analyze_season_patterns(active_leagues)
    
    print(f"\n🏁 Discovery complete. Found {len(active_leagues)} total active leagues.")
