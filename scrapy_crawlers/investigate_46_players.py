#!/usr/bin/env python3

import json

def investigate_46_players_issue():
    """
    Investigate why we're seeing exactly 46 players for each historical season
    """
    
    print("🔍 INVESTIGATING THE 46-PLAYERS-PER-SEASON ISSUE")
    
    try:
        with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        players = data.get('players', [])
        print(f"📊 Total players: {len(players):,}")
        
        # Group by season and analyze
        by_season = {}
        for p in players:
            season = p.get('season_id', 'unknown')
            if season not in by_season:
                by_season[season] = []
            by_season[season].append(p)
        
        print(f"\n📅 DETAILED SEASON ANALYSIS:")
        
        for season in sorted(by_season.keys()):
            if season == 'unknown':
                continue
                
            season_players = by_season[season]
            count = len(season_players)
            
            print(f"\n🗓️  SEASON {season}: {count} players")
            
            # Sample first few players from this season
            print(f"   📋 Sample players:")
            for i, p in enumerate(season_players[:3]):
                name = p.get('name', 'Unknown')
                team = p.get('team', 'Unknown')
                source = p.get('source', 'Unknown')
                endpoint = p.get('endpoint', 'Unknown')
                liga_id = p.get('liga_id', 'Unknown')
                print(f"      {i+1}. {name} ({team}) - Liga: {liga_id}, Source: {source}")
            
            # Check if all players are identical or similar
            if count > 1:
                # Check data sources
                sources = set(p.get('source', 'Unknown') for p in season_players)
                endpoints = set(p.get('endpoint', 'Unknown') for p in season_players)
                liga_ids = set(p.get('liga_id', 'Unknown') for p in season_players)
                teams = set(p.get('team', 'Unknown') for p in season_players)
                
                print(f"   🔗 Sources: {sources}")
                print(f"   🎯 Endpoints: {endpoints}")
                print(f"   🏀 Liga IDs: {liga_ids}")
                print(f"   👥 Unique teams: {len(teams)}")
                
                # If it's exactly 46, check if they're all the same
                if count == 46:
                    names = [p.get('name', 'Unknown') for p in season_players]
                    unique_names = set(names)
                    print(f"   ⚠️  SUSPICIOUS: Exactly 46 players!")
                    print(f"   🔍 Unique names: {len(unique_names)}")
                    if len(unique_names) < 10:
                        print(f"   🚨 LIKELY DUPLICATE DATA!")
                        print(f"   📝 Names: {list(unique_names)[:5]}")
        
        # Check 2018 vs others
        if 2018 in by_season:
            players_2018 = by_season[2018]
            print(f"\n🎯 2018 ANALYSIS (our good season):")
            print(f"   📊 Players: {len(players_2018):,}")
            
            sources_2018 = set(p.get('source', 'Unknown') for p in players_2018)
            endpoints_2018 = set(p.get('endpoint', 'Unknown') for p in players_2018)
            liga_ids_2018 = set(p.get('liga_id', 'Unknown') for p in players_2018)
            
            print(f"   🔗 Sources: {sources_2018}")
            print(f"   🎯 Endpoints: {endpoints_2018}")
            print(f"   🏀 Liga IDs count: {len(liga_ids_2018)}")
            
            # Compare with historical seasons
            if 2010 in by_season:
                players_2010 = by_season[2010]
                sources_2010 = set(p.get('source', 'Unknown') for p in players_2010)
                endpoints_2010 = set(p.get('endpoint', 'Unknown') for p in players_2010)
                
                print(f"\n🔍 COMPARISON 2018 vs 2010:")
                print(f"   2018: {len(players_2018):,} players, sources: {sources_2018}")
                print(f"   2010: {len(players_2010)} players, sources: {sources_2010}")
                
                if sources_2018 != sources_2010:
                    print(f"   ⚠️  Different data sources used!")
        
        print(f"\n🎯 CONCLUSION:")
        historical_seasons = [s for s in by_season.keys() if s != 'unknown' and s != 2018]
        problematic_seasons = [s for s in historical_seasons if len(by_season[s]) == 46]
        
        print(f"   📅 Historical seasons: {len(historical_seasons)}")
        print(f"   🚨 Seasons with exactly 46 players: {len(problematic_seasons)}")
        
        if len(problematic_seasons) == len(historical_seasons):
            print(f"   💡 THEORY: Historical data was extracted differently than 2018")
            print(f"   💡 SOLUTION: Re-extract using working statistik.do endpoints!")
        
    except FileNotFoundError:
        print("❌ real_players_extracted.json not found")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    investigate_46_players_issue()
