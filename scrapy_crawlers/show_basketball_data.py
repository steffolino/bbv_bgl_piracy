#!/usr/bin/env python3
"""Display real basketball federation crawl data"""

import sqlite3
import re

def show_basketball_api_data():
    """Show actual basketball federation API requests from logs"""
    try:
        conn = sqlite3.connect('crawl_logs.db')
        cursor = conn.cursor()
        
        print("🏀 REAL BASKETBALL FEDERATION API CRAWL DATA")
        print("=" * 60)
        
        # Get session info
        cursor.execute("""
            SELECT session_name, spider_name, start_time, 
                   (julianday(end_time) - julianday(start_time)) * 24 * 60 as duration_minutes
            FROM crawl_sessions 
            WHERE spider_name = 'extended_historical_crawler'
            ORDER BY start_time DESC LIMIT 1
        """)
        session = cursor.fetchone()
        if session:
            name, spider, start, duration = session
            print(f"📊 Session: {name}")
            print(f"   Spider: {spider}")
            print(f"   Started: {start}")
            print(f"   Duration: {duration:.2f} minutes")
            print()
        
        # Extract real API requests from log messages
        cursor.execute("""
            SELECT message, timestamp 
            FROM crawl_logs 
            WHERE message LIKE '%✅ 200 https://www.basketball-bund.net%'
            ORDER BY timestamp DESC
            LIMIT 20
        """)
        
        api_requests = cursor.fetchall()
        print(f"🌐 Recent Basketball Federation API Requests:")
        print(f"   Found {len(api_requests)} successful API calls")
        print("-" * 60)
        
        # Parse the log messages to extract league IDs and response times
        league_times = []
        for message, timestamp in api_requests:
            # Extract league ID and response time from message like:
            # "✅ 200 https://www.basketball-bund.net/rest/competition/actual/id/49743 (22562ms)"
            match = re.search(r'/id/(\d+).*\((\d+)ms\)', message)
            if match:
                league_id = match.group(1)
                response_time = int(match.group(2))
                league_times.append((league_id, response_time))
                time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp[-8:]
                print(f"   {time_str} | League {league_id} | {response_time}ms")
        
        if league_times:
            # Calculate statistics
            times = [t[1] for t in league_times]
            leagues = [t[0] for t in league_times]
            
            print()
            print("⚡ Real API Performance:")
            print(f"   Requests Made: {len(times)}")
            print(f"   Avg Response Time: {sum(times)/len(times):.1f}ms")
            print(f"   Fastest: {min(times)}ms")
            print(f"   Slowest: {max(times)}ms")
            print(f"   League Range: {min(leagues)} - {max(leagues)}")
        
        # Show total log counts
        cursor.execute("SELECT level, COUNT(*) FROM crawl_logs GROUP BY level")
        log_counts = cursor.fetchall()
        print()
        print("📝 Log Summary:")
        total_logs = 0
        for level, count in log_counts:
            print(f"   {level}: {count} entries")
            total_logs += count
        print(f"   TOTAL: {total_logs} log entries")
        
        # Show request patterns
        cursor.execute("""
            SELECT message FROM crawl_logs 
            WHERE message LIKE '%requests processed%' 
            OR message LIKE '%Leagues cached%'
            OR message LIKE '%Years covered%'
            LIMIT 5
        """)
        patterns = cursor.fetchall()
        if patterns:
            print()
            print("🎯 Crawl Results:")
            for (msg,) in patterns:
                if 'requests processed' in msg:
                    print(f"   {msg}")
                elif 'Leagues cached' in msg:
                    print(f"   {msg}")
                elif 'Years covered' in msg:
                    print(f"   {msg}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    show_basketball_api_data()
