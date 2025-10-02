#!/usr/bin/env python3
import sqlite3

def analyze_basketball_data():
    """Analyze the actual basketball data in the cache"""
    
    conn = sqlite3.connect('league_cache.db')
    cursor = conn.cursor()
    
    # Overall summary
    cursor.execute('''
        SELECT 
            COUNT(*) as total_leagues,
            SUM(match_count) as total_matches,
            COUNT(CASE WHEN league_exists = 1 THEN 1 END) as existing_leagues,
            COUNT(CASE WHEN league_exists = 0 THEN 1 END) as non_existing_leagues
        FROM league_cache
    ''')
    summary = cursor.fetchone()
    
    print("🏀 BASKETBALL DATA ANALYSIS")
    print("=" * 60)
    print(f"📊 Total Leagues: {summary[0]}")
    print(f"🎯 Total Matches: {summary[1]}")
    print(f"✅ Existing Leagues: {summary[2]}")
    print(f"❌ Non-Existing Leagues: {summary[3]}")
    
    # By season
    cursor.execute('''
        SELECT 
            season_year, 
            COUNT(*) as leagues, 
            SUM(match_count) as matches,
            COUNT(CASE WHEN league_exists = 1 THEN 1 END) as existing
        FROM league_cache 
        GROUP BY season_year 
        ORDER BY season_year
    ''')
    seasons = cursor.fetchall()
    
    print("\n📅 DATA BY SEASON:")
    print("=" * 60)
    print("Year    | Leagues | Matches | Existing")
    print("-" * 40)
    
    for season in seasons:
        year, leagues, matches, existing = season
        print(f"{year:<8} | {leagues:<7} | {matches:<7} | {existing}")
    
    # Top leagues by match count
    cursor.execute('''
        SELECT league_id, season_year, match_count, league_exists
        FROM league_cache 
        WHERE match_count > 0
        ORDER BY match_count DESC
        LIMIT 10
    ''')
    top_leagues = cursor.fetchall()
    
    print(f"\n🏆 TOP LEAGUES BY MATCH COUNT:")
    print("=" * 60)
    print("League ID | Season | Matches | Exists")
    print("-" * 40)
    
    for league in top_leagues:
        league_id, season, matches, exists = league
        status = "✅" if exists else "❌"
        print(f"{league_id:<9} | {season:<6} | {matches:<7} | {status}")
    
    # Historical coverage
    cursor.execute('SELECT MIN(season_year), MAX(season_year) FROM league_cache')
    min_year, max_year = cursor.fetchone()
    
    print(f"\n📊 HISTORICAL COVERAGE:")
    print("=" * 60)
    print(f"📅 Years: {min_year} - {max_year} ({max_year - min_year + 1} years)")
    
    # Check for actual game details (if games table exists)
    try:
        cursor.execute("SELECT COUNT(*) FROM games")
        games_count = cursor.fetchone()[0]
        print(f"🎯 Individual Games: {games_count}")
    except sqlite3.OperationalError:
        print("❌ No individual games table found")
    
    conn.close()

if __name__ == "__main__":
    analyze_basketball_data()
