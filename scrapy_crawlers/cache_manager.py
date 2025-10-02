#!/usr/bin/env python3
"""
League Cache Management Utility

This script helps manage the SQLite cache database for basketball league discovery.
It provides commands to query, analyze, and maintain the cached league data.
"""

import sqlite3
import argparse
import sys
import os
from datetime import datetime, timedelta
from tabulate import tabulate


class LeagueCacheManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'league_cache.db')
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Create database if it doesn't exist"""
        if not os.path.exists(self.db_path):
            print(f"Database not found at {self.db_path}")
            print("Run the smart_historical_crawler spider first to create the database.")
            return False
        return True
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def list_existing_leagues(self, limit=50):
        """List all leagues that exist in cache"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT league_id, season_year, match_count, league_name, district_name, last_checked
            FROM league_cache 
            WHERE league_exists = 1 
            ORDER BY season_year DESC, match_count DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            print("No existing leagues found in cache.")
            return
        
        headers = ['League ID', 'Season', 'Matches', 'League Name', 'District', 'Last Checked']
        table_data = []
        
        for row in results:
            league_id, season_year, match_count, league_name, district_name, last_checked = row
            last_checked_dt = datetime.fromisoformat(last_checked).strftime('%Y-%m-%d %H:%M')
            table_data.append([league_id, season_year, match_count, league_name[:30], district_name[:20], last_checked_dt])
        
        print(f"\n📊 Found {len(results)} existing leagues:")
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    def get_statistics(self):
        """Show cache statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total leagues checked
        cursor.execute('SELECT COUNT(*) FROM league_cache')
        total_checked = cursor.fetchone()[0]
        
        # Existing leagues
        cursor.execute('SELECT COUNT(*) FROM league_cache WHERE league_exists = 1')
        existing_count = cursor.fetchone()[0]
        
        # Non-existing leagues  
        cursor.execute('SELECT COUNT(*) FROM league_cache WHERE league_exists = 0')
        non_existing_count = cursor.fetchone()[0]
        
        # Leagues by season
        cursor.execute('''
            SELECT season_year, COUNT(*) as count, SUM(CASE WHEN league_exists = 1 THEN 1 ELSE 0 END) as existing
            FROM league_cache 
            GROUP BY season_year 
            ORDER BY season_year DESC
        ''')
        season_stats = cursor.fetchall()
        
        # Recent crawl sessions
        cursor.execute('''
            SELECT session_id, started_at, completed_at, leagues_found, leagues_failed
            FROM crawl_sessions 
            ORDER BY started_at DESC 
            LIMIT 5
        ''')
        recent_sessions = cursor.fetchall()
        
        conn.close()
        
        print(f"\n📈 League Cache Statistics:")
        print(f"=" * 50)
        print(f"Total leagues checked: {total_checked}")
        print(f"Leagues found: {existing_count} ({existing_count/total_checked*100:.1f}%)")
        print(f"Leagues not found: {non_existing_count} ({non_existing_count/total_checked*100:.1f}%)")
        
        if season_stats:
            print(f"\n📅 By Season:")
            season_headers = ['Season', 'Total Checked', 'Found', 'Success Rate']
            season_table = []
            for season_year, count, existing in season_stats:
                success_rate = f"{existing/count*100:.1f}%" if count > 0 else "0%"
                season_table.append([season_year, count, existing, success_rate])
            print(tabulate(season_table, headers=season_headers, tablefmt='simple'))
        
        if recent_sessions:
            print(f"\n🕐 Recent Crawl Sessions:")
            session_headers = ['Session ID', 'Started', 'Found', 'Failed']
            session_table = []
            for session_id, started_at, completed_at, found, failed in recent_sessions:
                started_dt = datetime.fromisoformat(started_at).strftime('%m-%d %H:%M')
                session_table.append([session_id[-15:], started_dt, found or 0, failed or 0])
            print(tabulate(session_table, headers=session_headers, tablefmt='simple'))
    
    def search_leagues(self, search_term, limit=20):
        """Search leagues by name or district"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT league_id, season_year, match_count, league_name, district_name, last_checked
            FROM league_cache 
            WHERE league_exists = 1 AND (league_name LIKE ? OR district_name LIKE ?)
            ORDER BY match_count DESC
            LIMIT ?
        ''', (f'%{search_term}%', f'%{search_term}%', limit))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            print(f"No leagues found matching '{search_term}'")
            return
        
        headers = ['League ID', 'Season', 'Matches', 'League Name', 'District']
        table_data = []
        
        for row in results:
            league_id, season_year, match_count, league_name, district_name, _ = row
            table_data.append([league_id, season_year, match_count, league_name[:40], district_name[:25]])
        
        print(f"\n🔍 Leagues matching '{search_term}':")
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    def clean_old_cache(self, days_old=30):
        """Remove cache entries older than specified days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        cursor.execute('''
            DELETE FROM league_cache 
            WHERE datetime(last_checked) < datetime(?)
        ''', (cutoff_date.isoformat(),))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"🗑️ Cleaned {deleted_count} cache entries older than {days_old} days")
    
    def export_existing_leagues(self, output_file):
        """Export existing leagues to JSON file"""
        import json
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT league_id, season_year, match_count, league_name, district_name, last_checked
            FROM league_cache 
            WHERE league_exists = 1 
            ORDER BY season_year DESC, match_count DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        export_data = []
        for row in results:
            league_id, season_year, match_count, league_name, district_name, last_checked = row
            export_data.append({
                'league_id': league_id,
                'season_year': season_year,
                'match_count': match_count,
                'league_name': league_name,
                'district_name': district_name,
                'last_checked': last_checked,
                'api_url': f'https://www.basketball-bund.net/rest/competition/actual/id/{league_id}'
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Exported {len(export_data)} existing leagues to {output_file}")


def main():
    parser = argparse.ArgumentParser(description='League Cache Management Utility')
    parser.add_argument('--db-path', help='Path to SQLite database file')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List existing leagues')
    list_parser.add_argument('--limit', type=int, default=50, help='Limit number of results')
    
    # Stats command
    subparsers.add_parser('stats', help='Show cache statistics')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search leagues by name or district')
    search_parser.add_argument('term', help='Search term')
    search_parser.add_argument('--limit', type=int, default=20, help='Limit number of results')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean old cache entries')
    clean_parser.add_argument('--days', type=int, default=30, help='Remove entries older than N days')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export existing leagues to JSON')
    export_parser.add_argument('output', help='Output JSON file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        manager = LeagueCacheManager(args.db_path)
        
        if args.command == 'list':
            manager.list_existing_leagues(args.limit)
        elif args.command == 'stats':
            manager.get_statistics()
        elif args.command == 'search':
            manager.search_leagues(args.term, args.limit)
        elif args.command == 'clean':
            manager.clean_old_cache(args.days)
        elif args.command == 'export':
            manager.export_existing_leagues(args.output)
    
    except ImportError as e:
        if 'tabulate' in str(e):
            print("Error: tabulate package required. Install with: pip install tabulate")
        else:
            print(f"Import error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
