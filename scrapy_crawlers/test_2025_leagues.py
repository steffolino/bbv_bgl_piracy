#!/usr/bin/env python3
"""
Test script to check current league ID patterns for 2025 season data
"""

import requests
import json
import time
from typing import List, Dict, Optional

# Test a range of league IDs to see what's active for 2025
def test_league_patterns():
    """Test various league ID patterns to find active 2025 leagues"""
    
    print("🔍 Testing current league ID patterns for 2025 season...")
    print("=" * 60)
    
    # Known active ranges from our previous discoveries
    test_ranges = [
        # Current year patterns - typically higher IDs
        (50000, 50050),  # Recent high-range IDs
        (49000, 49050),  # Previous pattern range
        (48000, 48050),  # Earlier pattern range
        (47900, 48000),  # Around our known working ID 47960
        
        # Test some specific patterns
        (47950, 47980),  # Close to our known working league
    ]
    
    active_leagues = []
    
    for start_id, end_id in test_ranges:
        print(f"\n🔍 Testing range {start_id}-{end_id}...")
        
        for league_id in range(start_id, end_id + 1):
            try:
                url = f"https://www.basketball-bund.net/rest/competition/actual/id/{league_id}"
                
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Check if we have meaningful data
                        if data and isinstance(data, dict):
                            league_name = data.get('name', 'Unknown')
                            season = data.get('season', {})
                            season_name = season.get('name', 'Unknown') if season else 'Unknown'
                            
                            # Look for 2024/2025 or 2025/2026 season patterns
                            if any(year in str(season_name) for year in ['2024', '2025', '2026']):
                                matches = data.get('matches', [])
                                match_count = len(matches) if matches else 0
                                
                                active_leagues.append({
                                    'id': league_id,
                                    'name': league_name,
                                    'season': season_name,
                                    'matches': match_count,
                                    'url': url
                                })
                                
                                print(f"✅ Found active league {league_id}: {league_name}")
                                print(f"   Season: {season_name}, Matches: {match_count}")
                                
                    except json.JSONDecodeError:
                        # Not JSON, skip
                        pass
                
                # Small delay to be polite
                time.sleep(0.1)
                
            except requests.RequestException:
                # Connection issues, skip
                pass
            
            # Show progress every 10 IDs
            if league_id % 10 == 0:
                print(f"   ... tested up to {league_id}")
    
    print("\n" + "=" * 60)
    print(f"🏆 Discovery Summary: Found {len(active_leagues)} active leagues")
    
    if active_leagues:
        print("\n📊 Active Leagues for Current Season:")
        print("-" * 60)
        
        for league in sorted(active_leagues, key=lambda x: x['id']):
            print(f"ID {league['id']:5d} | {league['name'][:40]:40} | {league['season'][:20]:20} | {league['matches']:3d} matches")
        
        # Analyze patterns
        print(f"\n🔍 Pattern Analysis:")
        print(f"   ID Range: {min(l['id'] for l in active_leagues)} - {max(l['id'] for l in active_leagues)}")
        print(f"   Total Matches: {sum(l['matches'] for l in active_leagues)}")
        
        # Check for Bezirk Oberfranken specifically
        oberfranken_leagues = [l for l in active_leagues if 'oberfranken' in l['name'].lower()]
        if oberfranken_leagues:
            print(f"\n🎯 Bezirk Oberfranken Leagues Found: {len(oberfranken_leagues)}")
            for league in oberfranken_leagues:
                print(f"   • {league['name']} (ID: {league['id']}, {league['matches']} matches)")
        else:
            print(f"\n⚠️  No 'Oberfranken' leagues found in current test range")
            
    else:
        print("\n❌ No active leagues found in tested ranges")
        print("   Consider expanding the search range or checking for new patterns")
    
    return active_leagues

if __name__ == "__main__":
    test_league_patterns()
