#!/usr/bin/env python3
"""Simple script to check crawl logs database"""

import sqlite3
from datetime import datetime
import json

def check_crawl_logs():
    """Check the crawl logs database contents"""
    try:
        conn = sqlite3.connect('crawl_logs.db')
        cursor = conn.cursor()
        
        # Check sessions
        cursor.execute("SELECT id, session_name, spider_name, start_time, status FROM crawl_sessions ORDER BY start_time DESC LIMIT 5")
        sessions = cursor.fetchall()
        print(f"📊 Found {len(sessions)} recent sessions:")
        for session in sessions:
            session_id, session_name, spider_name, start_time, status = session
            print(f"  🔹 {session_id} - {spider_name} - {start_time} - {status}")
        
        # Check logs
        cursor.execute("SELECT COUNT(*) FROM crawl_logs")
        log_count = cursor.fetchone()[0]
        print(f"\n📝 Total logs: {log_count}")
        
        if log_count > 0:
            cursor.execute("SELECT timestamp, level, logger_name, message FROM crawl_logs ORDER BY timestamp DESC LIMIT 10")
            logs = cursor.fetchall()
            print("\n🔍 Recent logs:")
            for log in logs:
                timestamp, level, logger_name, message = log
                print(f"  {timestamp} [{level}] {logger_name}: {message[:60]}...")
        
        # Check discoveries
        cursor.execute("SELECT COUNT(*) FROM crawl_discoveries")
        discovery_count = cursor.fetchone()[0]
        print(f"\n🎯 Total discoveries: {discovery_count}")
        
        if discovery_count > 0:
            cursor.execute("SELECT session_id, league_id, year, response_time FROM crawl_discoveries ORDER BY timestamp DESC LIMIT 5")
            discoveries = cursor.fetchall()
            print("\n🏆 Recent discoveries:")
            for discovery in discoveries:
                print(f"  League {discovery[1]} ({discovery[2]}) - {discovery[3]}ms")
        
        # Check errors
        cursor.execute("SELECT COUNT(*) FROM crawl_errors")
        error_count = cursor.fetchone()[0]
        print(f"\n⚠️  Total errors: {error_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_crawl_logs()
