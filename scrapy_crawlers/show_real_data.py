#!/usr/bin/env python3
"""Show real basketball crawl data details"""

import sqlite3
from datetime import datetime

def show_real_basketball_data():
    """Show the actual basketball federation API data we crawled"""
    try:
        conn = sqlite3.connect('crawl_logs.db')
        cursor = conn.cursor()
        
        print("🏀 REAL BASKETBALL FEDERATION API DATA")
        print("=" * 50)
        
        # Show recent session stats
        cursor.execute("""
            SELECT spider_name, start_time, total_requests, successful_requests, leagues_discovered 
            FROM crawl_sessions 
            WHERE spider_name = 'extended_historical_crawler'
            ORDER BY start_time DESC LIMIT 1
        """)
        session = cursor.fetchone()
        if session:
            spider, start_time, total_req, success_req, leagues = session
            print(f"📊 Latest Real Crawl Session:")
            print(f"   Spider: {spider}")
            print(f"   Started: {start_time}")
            print(f"   Total Requests: {total_req}")
            print(f"   Successful: {success_req}")
            print(f"   Leagues Found: {leagues}")
            print()
        
        # Show real API requests with response data
        cursor.execute("""
            SELECT timestamp, url, response_status, response_time_ms, league_id, match_count
            FROM crawl_logs 
            WHERE url LIKE '%basketball-bund.net%' 
            AND response_status IS NOT NULL
            ORDER BY timestamp DESC LIMIT 15
        """)
        
        requests = cursor.fetchall()
        print(f"🌐 Recent Real Basketball API Requests ({len(requests)} shown):")
        print("-" * 80)
        
        for req in requests:
            timestamp, url, status, time_ms, league_id, matches = req
            league_part = league_id or url.split('/')[-1] if url else 'N/A'
            match_info = f" - {matches} matches" if matches else ""
            time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp[-8:]
            print(f"   {time_str} | League {league_part} | {status} | {time_ms}ms{match_info}")
        
        # Show performance stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_requests,
                AVG(response_time_ms) as avg_time,
                MIN(response_time_ms) as min_time,
                MAX(response_time_ms) as max_time,
                COUNT(DISTINCT league_id) as unique_leagues
            FROM crawl_logs 
            WHERE response_status IS NOT NULL
        """)
        
        stats = cursor.fetchone()
        if stats:
            total, avg_time, min_time, max_time, unique = stats
            print()
            print("⚡ Performance Statistics:")
            print(f"   Total API Requests: {total}")
            print(f"   Average Response Time: {avg_time:.1f}ms")
            print(f"   Fastest Response: {min_time}ms")
            print(f"   Slowest Response: {max_time}ms")
            print(f"   Unique Leagues Tested: {unique}")
        
        # Show league ID ranges tested
        cursor.execute("""
            SELECT MIN(CAST(league_id AS INTEGER)) as min_id, MAX(CAST(league_id AS INTEGER)) as max_id
            FROM crawl_logs 
            WHERE league_id IS NOT NULL AND league_id != ''
        """)
        
        ranges = cursor.fetchone()
        if ranges and ranges[0]:
            min_id, max_id = ranges
            print(f"   League ID Range: {min_id} - {max_id}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    show_real_basketball_data()
