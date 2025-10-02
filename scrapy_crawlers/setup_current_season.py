#!/usr/bin/env python3
"""
🔧 SETUP CURRENT SEASON SCRAPER 🔧
Install dependencies and test the current season data pipeline
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    
    packages = [
        'requests',
        'beautifulsoup4',
        'schedule'
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"   ✅ {package}")
        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to install {package}")

def test_api_access():
    """Test if we can access the basketball API"""
    print("🌐 Testing API access...")
    
    import requests
    
    cookies = {
        "__cmpcc": "1",
        "SESSION": "NDkzOWM2ZDktMzYyOS00MjlhLTk1OTEtNzFlYmNjZTZmNWNh"
    }
    
    try:
        # Test the WAM data endpoint
        response = requests.post(
            "https://www.basketball-bund.net/rest/wam/data",
            json={
                "token": 0,
                "verbandIds": [2],
                "gebietIds": ["5_"]
            },
            cookies=cookies,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ API access working")
            data = response.json()
            print(f"   📊 Received data: {len(str(data))} characters")
            return True
        else:
            print(f"   ⚠️ API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False

def create_database_schema():
    """Create database tables for current season data"""
    print("🗄️ Setting up database schema...")
    
    import sqlite3
    
    try:
        db_path = "../league_cache.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Current season leagues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS current_season_leagues (
                id INTEGER PRIMARY KEY,
                name TEXT,
                season TEXT,
                teams_count INTEGER,
                matches_count INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data JSON
            )
        """)
        
        # Current games table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS current_games (
                id TEXT PRIMARY KEY,
                league_id INTEGER,
                match_id TEXT,
                date TEXT,
                home_team TEXT,
                away_team TEXT,
                home_score INTEGER,
                away_score INTEGER,
                status TEXT,
                venue JSON,
                box_score JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Box scores table for detailed game stats
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS box_scores (
                id TEXT PRIMARY KEY,
                match_id TEXT,
                game_date TEXT,
                home_team TEXT,
                away_team TEXT,
                quarter_scores JSON,
                player_stats JSON,
                team_stats JSON,
                officials JSON,
                venue JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Player statistics table for current season
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS current_player_stats (
                id TEXT PRIMARY KEY,
                player_name TEXT,
                team_name TEXT,
                league_id INTEGER,
                games_played INTEGER,
                points_total INTEGER,
                points_avg REAL,
                rebounds_total INTEGER,
                assists_total INTEGER,
                season TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("   ✅ Database schema created")
        return True
        
    except Exception as e:
        print(f"   ❌ Database setup failed: {e}")
        return False

def run_test_scrape():
    """Run a test scrape to verify everything works"""
    print("🧪 Running test scrape...")
    
    try:
        # Import and test the scraper
        from current_season_scraper import CurrentSeasonScraper
        
        scraper = CurrentSeasonScraper()
        
        # Test league discovery
        print("   🔍 Testing league discovery...")
        test_leagues = scraper.discover_current_leagues()
        
        if test_leagues:
            print(f"   ✅ Found {len(test_leagues)} active leagues")
            
            # Test getting data for first league
            if test_leagues:
                test_league_id = test_leagues[0]
                print(f"   📊 Testing data fetch for league {test_league_id}...")
                league_data = scraper.get_league_data(test_league_id)
                
                if league_data:
                    print(f"   ✅ Successfully fetched league data")
                    print(f"      League: {league_data['name']}")
                    print(f"      Teams: {len(league_data.get('teams', []))}")
                    print(f"      Matches: {len(league_data.get('matches', []))}")
                    return True
        
        print("   ⚠️ No active leagues found - may need to update league IDs")
        return False
        
    except Exception as e:
        print(f"   ❌ Test scrape failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🏀 CURRENT SEASON SCRAPER SETUP")
    print("=" * 50)
    print("Setting up weekly basketball data pipeline...")
    print()
    
    # Step 1: Install dependencies
    install_dependencies()
    print()
    
    # Step 2: Test API access
    api_works = test_api_access()
    print()
    
    # Step 3: Setup database
    db_works = create_database_schema()
    print()
    
    # Step 4: Test scraping
    if api_works and db_works:
        scrape_works = run_test_scrape()
    else:
        scrape_works = False
        print("🚫 Skipping test scrape due to previous failures")
    
    print()
    print("🎯 SETUP SUMMARY")
    print("=" * 50)
    print(f"📦 Dependencies: {'✅' if True else '❌'}")
    print(f"🌐 API Access: {'✅' if api_works else '❌'}")
    print(f"🗄️ Database: {'✅' if db_works else '❌'}")
    print(f"🧪 Test Scrape: {'✅' if scrape_works else '❌'}")
    
    if all([api_works, db_works, scrape_works]):
        print()
        print("🎉 SETUP COMPLETE!")
        print("🚀 Ready to scrape current season data")
        print()
        print("💡 NEXT STEPS:")
        print("   1. Run: python current_season_scraper.py")
        print("   2. Schedule: python weekly_scheduler.py")
        print("   3. Test now: python weekly_scheduler.py --now")
        print()
        print("🔄 Remember to update cookies weekly!")
    else:
        print()
        print("⚠️ SETUP INCOMPLETE")
        print("Please fix the issues above before proceeding")

if __name__ == "__main__":
    main()
