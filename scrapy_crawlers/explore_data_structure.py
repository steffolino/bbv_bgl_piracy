#!/usr/bin/env python3
import sqlite3
import json
import os
from pathlib import Path

def explore_basketball_data():
    """Explore all basketball data to understand structure for player extraction"""
    
    print("🏀 EXPLORING BASKETBALL DATA STRUCTURE")
    print("=" * 60)
    
    # Check league cache
    if os.path.exists('league_cache.db'):
        conn = sqlite3.connect('league_cache.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 LEAGUE_CACHE.DB TABLES: {[t[0] for t in tables]}")
        
        cursor.execute("PRAGMA table_info(league_cache)")
        columns = cursor.fetchall()
        print(f"🗂️ League cache columns: {[col[1] for col in columns]}")
        
        cursor.execute("SELECT * FROM league_cache WHERE match_count > 0 LIMIT 3")
        rows = cursor.fetchall()
        print("\n📝 Sample league data with matches:")
        for row in rows:
            print(f"  League {row[0]}: {row[5]} matches in {row[1]}")
            
        conn.close()
    
    # Check extended cache
    if os.path.exists('extended_league_cache.db'):
        print(f"\n📊 EXTENDED_LEAGUE_CACHE.DB exists")
        conn = sqlite3.connect('extended_league_cache.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        conn.close()
    
    # Check crawl logs for actual match data
    if os.path.exists('crawl_logs.db'):
        conn = sqlite3.connect('crawl_logs.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n📊 CRAWL_LOGS.DB TABLES: {[t[0] for t in tables]}")
        
        # Look for any tables that might contain match details
        for table_name in [t[0] for t in tables]:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"🗂️ {table_name} columns: {[col[1] for col in columns]}")
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   📈 {count} records")
            
            if count > 0 and count < 20:  # Show sample for small tables
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print(f"   Sample data: {rows}")
            print()
            
        conn.close()
    
    # Check JSON files for actual match/player data
    json_files = [
        'historical_production_data.json',
        'extended_historical_data.json', 
        'rest_api_results.json',
        'rest_historical_results.json',
        'discovery_results.json'
    ]
    
    print("🔍 CHECKING JSON DATA FILES:")
    print("=" * 40)
    
    for filename in json_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                print(f"📄 {filename}:")
                if isinstance(data, dict):
                    print(f"   Keys: {list(data.keys())}")
                    if 'matches' in data:
                        matches = data['matches']
                        print(f"   🎯 {len(matches)} matches found")
                        if matches:
                            sample_match = matches[0]
                            print(f"   Sample match keys: {list(sample_match.keys())}")
                            if 'players' in sample_match or 'boxscore' in sample_match:
                                print("   ✅ Contains player data!")
                elif isinstance(data, list):
                    print(f"   📊 {len(data)} items")
                    if data:
                        sample = data[0]
                        if isinstance(sample, dict):
                            print(f"   Sample keys: {list(sample.keys())}")
                print()
            except Exception as e:
                print(f"   ❌ Error reading {filename}: {e}")
    
    print("🎯 NEXT STEPS:")
    print("=" * 40)
    print("1. Identify where actual match/player data is stored")
    print("2. Extract player statistics from match data")
    print("3. Build player profiles and career timelines")
    print("4. Create advanced stats explorer")

if __name__ == "__main__":
    explore_basketball_data()
