#!/usr/bin/env python3
import sqlite3
import json
from datetime import datetime

def check_league_cache():
    """Check what data is actually in the league cache database"""
    
    try:
        conn = sqlite3.connect('league_cache.db')
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("🗃️  LEAGUE CACHE DATABASE TABLES:")
        print("=" * 50)
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   📊 {table_name}: {count} records")
        
        print("\n🏀 LEAGUE CACHE SAMPLE DATA:")
        print("=" * 50)
        cursor.execute("PRAGMA table_info(league_cache)")
        columns_info = cursor.fetchall()
        columns = [col[1] for col in columns_info]
        print(f"Columns: {', '.join(columns)}")
        print("-" * 50)
        
        cursor.execute("SELECT * FROM league_cache LIMIT 10")
        rows = cursor.fetchall()
        for i, row in enumerate(rows):
            print(f"Row {i+1}:")
            for j, col in enumerate(columns):
                print(f"  {col}: {row[j]}")
            print()
        
        # Check for game data
        try:
            cursor.execute("SELECT COUNT(*) FROM games WHERE 1=1")
            games_count = cursor.fetchone()[0]
            print(f"\n🎯 GAMES TABLE: {games_count} records")
            
            if games_count > 0:
                cursor.execute("SELECT * FROM games LIMIT 5")
                game_columns = [description[0] for description in cursor.description]
                print(f"Game columns: {', '.join(game_columns)}")
                game_rows = cursor.fetchall()
                for row in game_rows:
                    print(f"Game: {row}")
                    
        except sqlite3.OperationalError as e:
            print(f"❌ No games table: {e}")
        
        # Check season data
        try:
            cursor.execute("SELECT DISTINCT league_year FROM league_cache ORDER BY league_year")
            seasons = cursor.fetchall()
            print(f"\n📅 SEASONS AVAILABLE: {len(seasons)} seasons")
            for season in seasons[:10]:  # Show first 10
                print(f"   • Season: {season[0]}")
                
        except sqlite3.OperationalError as e:
            print(f"❌ No season data: {e}")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking league cache: {e}")

if __name__ == "__main__":
    check_league_cache()
