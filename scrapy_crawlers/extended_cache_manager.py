#!/usr/bin/env python3

import sqlite3
import argparse
import json
from tabulate import tabulate
from datetime import datetime

class ExtendedCacheManager:
    """Management utility for extended historical cache database"""
    
    def __init__(self, db_path='extended_league_cache.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def show_stats(self):
        """Display comprehensive statistics about the extended cache"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        print("📊 EXTENDED CACHE STATISTICS (2003-2024)")
        print("=" * 60)
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) FROM extended_league_cache")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM extended_league_cache WHERE league_exists = 1")
        existing_leagues = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM extended_league_cache WHERE league_exists = 0")
        nonexistent_leagues = cursor.fetchone()[0]
        
        print(f"Total records: {total_records:,}")
        print(f"Existing leagues: {existing_leagues:,}")
        print(f"Non-existent leagues: {nonexistent_leagues:,}")
        
        if total_records > 0:
            success_rate = (existing_leagues / total_records) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        print()
        
        # Year distribution
        cursor.execute('''
            SELECT season_year, COUNT(*) as total,
                   COUNT(CASE WHEN league_exists = 1 THEN 1 END) as existing
            FROM extended_league_cache 
            GROUP BY season_year 
            ORDER BY season_year DESC
        ''')
        
        year_data = cursor.fetchall()
        if year_data:
            print("📅 YEAR DISTRIBUTION:")
            headers = ["Year", "Total Tested", "Found", "Success Rate"]
            table_data = []
            
            for year, total, found in year_data:
                success_rate = (found / total * 100) if total > 0 else 0
                table_data.append([year, total, found, f"{success_rate:.1f}%"])
            
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            print()
        
        # Match count distribution
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN match_count = 0 THEN '0'
                    WHEN match_count <= 5 THEN '1-5'
                    WHEN match_count <= 10 THEN '6-10'
                    WHEN match_count <= 20 THEN '11-20'
                    WHEN match_count <= 30 THEN '21-30'
                    WHEN match_count <= 50 THEN '31-50'
                    ELSE '50+'
                END as range,
                COUNT(*) as count
            FROM extended_league_cache 
            WHERE league_exists = 1
            GROUP BY range
            ORDER BY MIN(match_count)
        ''')
        
        match_distribution = cursor.fetchall()
        if match_distribution:
            print("🏀 MATCH COUNT DISTRIBUTION:")
            headers = ["Match Range", "League Count"]
            print(tabulate(match_distribution, headers=headers, tablefmt="grid"))
            print()
        
        # Data quality overview
        cursor.execute('''
            SELECT data_quality, COUNT(*) 
            FROM extended_league_cache 
            WHERE league_exists = 1
            GROUP BY data_quality
        ''')
        
        quality_data = cursor.fetchall()
        if quality_data:
            print("⭐ DATA QUALITY:")
            headers = ["Quality", "Count"]
            print(tabulate(quality_data, headers=headers, tablefmt="grid"))
            print()
        
        # Crawl sessions
        cursor.execute('''
            SELECT session_id, started_at, completed_at, years_covered, 
                   leagues_found, leagues_tested
            FROM extended_crawl_sessions 
            ORDER BY started_at DESC
            LIMIT 5
        ''')
        
        sessions = cursor.fetchall()
        if sessions:
            print("🕐 RECENT CRAWL SESSIONS:")
            headers = ["Session ID", "Started", "Completed", "Years", "Found", "Tested"]
            session_data = []
            
            for session in sessions:
                session_id, started, completed, years, found, tested = session
                started_short = started[:19] if started else "N/A"
                completed_short = completed[:19] if completed else "Running"
                session_data.append([
                    session_id[-12:],  # Last 12 chars
                    started_short,
                    completed_short,
                    years,
                    found or 0,
                    tested or 0
                ])
            
            print(tabulate(session_data, headers=headers, tablefmt="grid"))
        
        conn.close()
    
    def list_top_leagues(self, limit=20):
        """List top leagues by match count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT league_id, season_year, league_name, district_name, 
                   match_count, data_quality
            FROM extended_league_cache 
            WHERE league_exists = 1 
            ORDER BY match_count DESC, season_year DESC
            LIMIT ?
        ''', (limit,))
        
        leagues = cursor.fetchall()
        
        if leagues:
            print(f"🏆 TOP {limit} LEAGUES BY MATCH COUNT:")
            print("=" * 80)
            
            headers = ["League ID", "Season", "Name", "District", "Matches", "Quality"]
            table_data = []
            
            for league_id, season, name, district, matches, quality in leagues:
                name_short = (name[:25] + "...") if name and len(name) > 28 else (name or "Unknown")
                district_short = (district[:15] + "...") if district and len(district) > 18 else (district or "Unknown")
                
                table_data.append([
                    league_id,
                    season,
                    name_short,
                    district_short,
                    matches,
                    quality
                ])
            
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            print("No leagues found in cache.")
        
        conn.close()
    
    def search_leagues(self, search_term):
        """Search leagues by name or district"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT league_id, season_year, league_name, district_name, match_count
            FROM extended_league_cache 
            WHERE league_exists = 1 
            AND (league_name LIKE ? OR district_name LIKE ?)
            ORDER BY match_count DESC
        ''', (f'%{search_term}%', f'%{search_term}%'))
        
        results = cursor.fetchall()
        
        if results:
            print(f"🔍 SEARCH RESULTS FOR '{search_term}':")
            print("=" * 60)
            
            headers = ["League ID", "Season", "Name", "District", "Matches"]
            print(tabulate(results, headers=headers, tablefmt="grid"))
        else:
            print(f"No leagues found matching '{search_term}'")
        
        conn.close()
    
    def export_data(self, filename=None):
        """Export all existing leagues to JSON"""
        if not filename:
            filename = f"extended_historical_leagues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT league_id, season_year, league_name, district_name, 
                   match_count, data_quality, last_checked
            FROM extended_league_cache 
            WHERE league_exists = 1 
            ORDER BY season_year DESC, match_count DESC
        ''')
        
        leagues = cursor.fetchall()
        
        data = []
        for league in leagues:
            league_id, season, name, district, matches, quality, checked = league
            data.append({
                'league_id': league_id,
                'season_year': season,
                'league_name': name,
                'district_name': district,
                'match_count': matches,
                'data_quality': quality,
                'last_checked': checked
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported {len(data)} leagues to {filename}")
        conn.close()
    
    def clean_cache(self, older_than_days=7):
        """Clean old cache entries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM extended_league_cache 
            WHERE last_checked < datetime('now', '-{} days')
            AND league_exists = 0
        '''.format(older_than_days))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"🧹 Cleaned {deleted} old non-existent league entries")

def main():
    parser = argparse.ArgumentParser(description='Extended Historical Basketball Cache Manager')
    parser.add_argument('command', choices=['stats', 'list', 'search', 'export', 'clean'], 
                       help='Command to execute')
    parser.add_argument('--term', help='Search term for search command')
    parser.add_argument('--limit', type=int, default=20, help='Limit for list command')
    parser.add_argument('--file', help='Output filename for export command')
    parser.add_argument('--days', type=int, default=7, help='Days for clean command')
    
    args = parser.parse_args()
    
    manager = ExtendedCacheManager()
    
    if args.command == 'stats':
        manager.show_stats()
    elif args.command == 'list':
        manager.list_top_leagues(args.limit)
    elif args.command == 'search':
        if not args.term:
            print("Error: --term required for search command")
            return
        manager.search_leagues(args.term)
    elif args.command == 'export':
        manager.export_data(args.file)
    elif args.command == 'clean':
        manager.clean_cache(args.days)

if __name__ == '__main__':
    main()
