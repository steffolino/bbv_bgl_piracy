#!/usr/bin/env python3

import requests
from datetime import datetime
import time

def test_season_availability():
    """
    Quick test to see which seasons are available using your proven league
    """
    
    print("🔍 SEASON AVAILABILITY TEST")
    print("Testing which seasons are available for your Basketball Reference frontend")
    
    # Test with your best performing league from 2018
    test_league_id = 26212  # Your largest dataset league
    test_seasons = list(range(2015, 2025))  # Test wide range
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    }
    
    available_seasons = []
    
    print(f"Testing league {test_league_id} across seasons {test_seasons[0]}-{test_seasons[-1]}...")
    
    for season in test_seasons:
        print(f"  Testing {season}...", end=" ")
        
        # Test with your proven best endpoint
        test_url = f"https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id={test_league_id}&saison_id={season}&_top=-1"
        
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                content = response.text.lower()
                # Check for player data indicators
                if ('spieler' in content or 'punkte' in content) and 'basketball' in content:
                    # Additional check for actual data rows
                    if 'sportitem' in content or content.count('<tr') > 5:
                        available_seasons.append(season)
                        print("✅ Available")
                    else:
                        print("❌ No data")
                else:
                    print("❌ No data")
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"\n📊 RESULTS:")
    print(f"Available seasons: {available_seasons}")
    print(f"Total available: {len(available_seasons)} seasons")
    
    if available_seasons:
        print(f"\n🎯 RECOMMENDED CRAWLING STRATEGY:")
        current_seasons = [2018]  # Your existing data
        new_seasons = [s for s in available_seasons if s not in current_seasons]
        
        if new_seasons:
            print(f"  ✅ You have: {current_seasons}")
            print(f"  🆕 Can crawl: {new_seasons}")
            print(f"  📈 Total potential: {len(available_seasons)} seasons")
            
            print(f"\n💡 Priority order for your Basketball Reference frontend:")
            # Prioritize recent seasons first for most relevance
            recent_seasons = [s for s in new_seasons if s >= 2020]
            older_seasons = [s for s in new_seasons if s < 2020]
            
            if recent_seasons:
                print(f"  1. Recent seasons (high value): {recent_seasons}")
            if older_seasons:
                print(f"  2. Historical seasons: {older_seasons}")
        else:
            print(f"  ℹ️  All available seasons already crawled")
    else:
        print(f"\n❌ No additional seasons available")
    
    return available_seasons

if __name__ == "__main__":
    test_season_availability()
