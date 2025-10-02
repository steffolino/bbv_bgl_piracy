#!/usr/bin/env python3

import requests
from datetime import datetime
import time

def comprehensive_season_test():
    """
    Comprehensive test across multiple leagues and endpoints
    """
    
    print("🔍 COMPREHENSIVE SEASON AVAILABILITY TEST")
    print("Testing multiple leagues and checking REST API for current seasons")
    
    # Test multiple proven league IDs
    test_league_ids = [26212, 26211, 26225, 26196, 26197, 26198]  # Your best performing leagues
    test_seasons = list(range(2015, 2025))
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    }
    
    print(f"\n📋 TESTING ARCHIVE SYSTEM (statistik.do)")
    archive_results = {}
    
    for league_id in test_league_ids:
        print(f"\nTesting Liga {league_id}:")
        league_seasons = []
        
        for season in test_seasons:
            print(f"  {season}...", end=" ")
            
            test_url = f"https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id={league_id}&saison_id={season}&_top=-1"
            
            try:
                response = requests.get(test_url, headers=headers, timeout=8)
                
                if response.status_code == 200:
                    content = response.text.lower()
                    if ('spieler' in content and 'punkte' in content) and 'sportitem' in content:
                        league_seasons.append(season)
                        print("✅", end="")
                    else:
                        print("❌", end="")
                else:
                    print("❌", end="")
                    
            except:
                print("❌", end="")
            
            time.sleep(0.2)
        
        print(f"\n  Available: {league_seasons}")
        archive_results[league_id] = league_seasons
    
    print(f"\n📋 TESTING CURRENT REST API")
    # Test current season data from REST API
    current_leagues = []
    
    # Test some league IDs from your historical data to see if they have current season data
    rest_test_urls = [
        "https://www.basketball-bund.net/rest/competition/actual/id/49749",
        "https://www.basketball-bund.net/rest/competition/actual/id/49750", 
        "https://www.basketball-bund.net/rest/competition/actual/id/49854",
        "https://www.basketball-bund.net/rest/competition/actual/id/50799",
    ]
    
    for url in rest_test_urls:
        league_id = url.split('/')[-1]
        print(f"  Testing current league {league_id}...", end=" ")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                matches = data.get('matches', [])
                if matches:
                    current_leagues.append(league_id)
                    print(f"✅ {len(matches)} matches")
                else:
                    print("❌ No matches")
            else:
                print(f"❌ HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Error")
    
    print(f"\n📊 COMPREHENSIVE RESULTS:")
    
    # Archive results
    all_archive_seasons = set()
    for league_id, seasons in archive_results.items():
        all_archive_seasons.update(seasons)
    
    print(f"Archive System (statistik.do):")
    print(f"  Available seasons: {sorted(list(all_archive_seasons))}")
    print(f"  League coverage:")
    for league_id, seasons in archive_results.items():
        if seasons:
            print(f"    Liga {league_id}: {seasons}")
    
    print(f"\nCurrent API (rest/competition):")
    print(f"  Active leagues with current data: {current_leagues}")
    
    print(f"\n🎯 CRAWLING STRATEGY RECOMMENDATION:")
    
    if len(all_archive_seasons) > 1:
        missing_archive = [s for s in all_archive_seasons if s != 2018]
        if missing_archive:
            print(f"  📈 Can expand archive data: {missing_archive}")
        else:
            print(f"  ✅ Archive data complete (only 2018 available)")
    
    if current_leagues:
        print(f"  🔄 Can get current season data from {len(current_leagues)} leagues")
        print(f"  💡 Strategy: Combine archive (2018) + current API data for multi-season frontend")
    
    print(f"\n🏀 For your Basketball Reference frontend:")
    print(f"  1. Use existing 2018 archive data (historical)")
    print(f"  2. Add current 2024/2025 season from REST API")
    print(f"  3. This gives you historical comparison + current stats")
    
    return {
        'archive_seasons': sorted(list(all_archive_seasons)),
        'current_leagues': current_leagues,
        'total_seasons_possible': len(all_archive_seasons) + (1 if current_leagues else 0)
    }

if __name__ == "__main__":
    comprehensive_season_test()
