#!/usr/bin/env python3

import json

def check_existing_data():
    """
    Check what data we already have in real_players_extracted.json
    """
    
    print("🔍 CHECKING EXISTING DATA")
    
    try:
        with open('real_players_extracted.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        players = data.get('players', [])
        print(f"📊 Total players: {len(players):,}")
        
        # Check seasons
        seasons = sorted(set(p.get('season_id', 'unknown') for p in players))
        print(f"📅 Seasons: {seasons}")
        print(f"🗓️  Total seasons: {len([s for s in seasons if s != 'unknown'])}")
        
        # Check Litzendorf players
        litzendorf_players = []
        for p in players:
            if (p.get('is_litzendorf') or 
                'litzendorf' in str(p.get('team', '')).lower() or
                'litzendorf' in str(p.get('name', '')).lower()):
                litzendorf_players.append(p)
        
        print(f"🌟 Litzendorf players: {len(litzendorf_players)}")
        
        if litzendorf_players:
            print("🏆 Sample Litzendorf players:")
            for i, p in enumerate(litzendorf_players[:10]):
                name = p.get('name', 'Unknown')
                team = p.get('team', 'Unknown')
                season = p.get('season_id', 'Unknown')
                stat = p.get('primary_stat', 'N/A')
                print(f"  {i+1}. {name} ({team}) - Season {season} - {stat}")
        
        # Check by season breakdown
        print(f"\n📈 Players by season:")
        season_counts = {}
        litzendorf_by_season = {}
        
        for p in players:
            season = p.get('season_id', 'unknown')
            if season not in season_counts:
                season_counts[season] = 0
                litzendorf_by_season[season] = 0
            
            season_counts[season] += 1
            
            if (p.get('is_litzendorf') or 
                'litzendorf' in str(p.get('team', '')).lower()):
                litzendorf_by_season[season] += 1
        
        for season in sorted(season_counts.keys()):
            if season != 'unknown':
                litz_count = litzendorf_by_season.get(season, 0)
                litz_indicator = f" (🌟 {litz_count} Litzendorf)" if litz_count > 0 else ""
                print(f"  {season}: {season_counts[season]:,} players{litz_indicator}")
        
        # Check data sources
        sources = set()
        endpoints = set()
        for p in players:
            if 'source' in p:
                sources.add(p['source'])
            if 'endpoint' in p:
                endpoints.add(p['endpoint'])
        
        print(f"\n🔗 Data sources: {sources}")
        print(f"🎯 Endpoints used: {endpoints}")
        
        # Check if we have good coverage
        good_seasons = [s for s in seasons if s != 'unknown' and season_counts.get(s, 0) > 100]
        print(f"\n✅ Seasons with substantial data (>100 players): {len(good_seasons)}")
        print(f"📊 Coverage: {good_seasons}")
        
        if len(litzendorf_players) > 20:
            print(f"\n🎯 CONCLUSION: We already have excellent coverage!")
            print(f"   🌟 {len(litzendorf_players)} Litzendorf players across multiple seasons")
            print(f"   📊 {len(players):,} total players")
            print(f"   📅 {len(good_seasons)} seasons with substantial data")
        else:
            print(f"\n🎯 CONCLUSION: We could use more Litzendorf data")
            print(f"   🌟 Only {len(litzendorf_players)} Litzendorf players found")
        
    except FileNotFoundError:
        print("❌ real_players_extracted.json not found")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    check_existing_data()
