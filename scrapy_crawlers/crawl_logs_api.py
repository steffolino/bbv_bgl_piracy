#!/usr/bin/env python3

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class CrawlSession:
    id: str
    session_name: str
    spider_name: str
    start_time: str
    end_time: Optional[str]
    status: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    items_scraped: int
    leagues_discovered: int
    error_message: Optional[str]
    duration_minutes: Optional[int]


@dataclass
class CrawlLogEntry:
    id: str
    timestamp: str
    level: str
    logger_name: str
    message: str
    url: Optional[str]
    response_status: Optional[int]
    response_time_ms: Optional[int]
    league_id: Optional[str]
    season_year: Optional[int]
    match_count: Optional[int]
    metadata: Optional[Dict]


@dataclass
class CrawlDiscovery:
    id: str
    league_id: str
    season_year: int
    league_name: Optional[str]
    district_name: Optional[str]
    match_count: int
    team_count: int
    data_quality: Optional[str]
    discovery_phase: Optional[str]
    url: str
    discovered_at: str


class CrawlLogsAPI:
    """API for searching and managing crawl logs from the backend"""
    
    def __init__(self, db_path: str = 'crawl_logs.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_recent_sessions(self, limit: int = 20) -> List[CrawlSession]:
        """Get recent crawl sessions with summary statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                cs.id, cs.session_name, cs.spider_name, cs.start_time, cs.end_time,
                cs.status, cs.total_requests, cs.successful_requests, cs.failed_requests,
                cs.items_scraped, cs.leagues_discovered, cs.error_message,
                CAST((julianday(COALESCE(cs.end_time, datetime('now'))) - julianday(cs.start_time)) * 24 * 60 AS INTEGER) as duration_minutes
            FROM crawl_sessions cs
            ORDER BY cs.start_time DESC
            LIMIT ?
        ''', (limit,))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append(CrawlSession(*row))
        
        conn.close()
        return sessions
    
    def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific crawl session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute('''
            SELECT * FROM crawl_sessions WHERE id = ?
        ''', (session_id,))
        
        session_row = cursor.fetchone()
        if not session_row:
            conn.close()
            return None
        
        # Get column names
        session_columns = [desc[0] for desc in cursor.description]
        session_data = dict(zip(session_columns, session_row))
        
        # Get log count by level
        cursor.execute('''
            SELECT level, COUNT(*) as count
            FROM crawl_logs 
            WHERE session_id = ?
            GROUP BY level
            ORDER BY 
                CASE level
                    WHEN 'ERROR' THEN 1
                    WHEN 'WARNING' THEN 2
                    WHEN 'INFO' THEN 3
                    WHEN 'DEBUG' THEN 4
                    ELSE 5
                END
        ''', (session_id,))
        
        log_levels = dict(cursor.fetchall())
        
        # Get discoveries count
        cursor.execute('''
            SELECT COUNT(*) FROM crawl_discoveries WHERE session_id = ?
        ''', (session_id,))
        
        discoveries_count = cursor.fetchone()[0]
        
        # Get errors count  
        cursor.execute('''
            SELECT COUNT(*) FROM crawl_errors WHERE session_id = ?
        ''', (session_id,))
        
        errors_count = cursor.fetchone()[0]
        
        # Get top discovered leagues
        cursor.execute('''
            SELECT league_id, season_year, league_name, match_count, data_quality
            FROM crawl_discoveries 
            WHERE session_id = ?
            ORDER BY match_count DESC
            LIMIT 10
        ''', (session_id,))
        
        top_discoveries = []
        for row in cursor.fetchall():
            top_discoveries.append({
                'league_id': row[0],
                'season_year': row[1],
                'league_name': row[2],
                'match_count': row[3],
                'data_quality': row[4]
            })
        
        conn.close()
        
        return {
            'session': session_data,
            'log_levels': log_levels,
            'discoveries_count': discoveries_count,
            'errors_count': errors_count,
            'top_discoveries': top_discoveries
        }
    
    def search_logs(self, session_id: Optional[str] = None, level: Optional[str] = None,
                   search_term: Optional[str] = None, league_id: Optional[str] = None,
                   start_date: Optional[str] = None, end_date: Optional[str] = None,
                   limit: int = 100, offset: int = 0) -> List[CrawlLogEntry]:
        """Search crawl logs with multiple filter options"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, timestamp, level, logger_name, message, url, response_status,
                   response_time_ms, league_id, season_year, match_count, metadata
            FROM crawl_logs
            WHERE 1=1
        '''
        params = []
        
        if session_id:
            query += ' AND session_id = ?'
            params.append(session_id)
        
        if level:
            query += ' AND level = ?'
            params.append(level)
        
        if search_term:
            query += ' AND (message LIKE ? OR url LIKE ?)'
            params.extend([f'%{search_term}%', f'%{search_term}%'])
        
        if league_id:
            query += ' AND league_id = ?'
            params.append(league_id)
        
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date)
        
        query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        logs = []
        for row in cursor.fetchall():
            metadata = json.loads(row[11]) if row[11] else None
            logs.append(CrawlLogEntry(*row[:11], metadata))
        
        conn.close()
        return logs
    
    def search_discoveries(self, session_id: Optional[str] = None, 
                          league_name: Optional[str] = None,
                          district_name: Optional[str] = None,
                          min_matches: Optional[int] = None,
                          season_year: Optional[int] = None,
                          data_quality: Optional[str] = None,
                          limit: int = 100) -> List[CrawlDiscovery]:
        """Search crawl discoveries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, league_id, season_year, league_name, district_name,
                   match_count, team_count, data_quality, discovery_phase, url, discovered_at
            FROM crawl_discoveries
            WHERE 1=1
        '''
        params = []
        
        if session_id:
            query += ' AND session_id = ?'
            params.append(session_id)
        
        if league_name:
            query += ' AND league_name LIKE ?'
            params.append(f'%{league_name}%')
        
        if district_name:
            query += ' AND district_name LIKE ?'
            params.append(f'%{district_name}%')
        
        if min_matches:
            query += ' AND match_count >= ?'
            params.append(min_matches)
        
        if season_year:
            query += ' AND season_year = ?'
            params.append(season_year)
        
        if data_quality:
            query += ' AND data_quality = ?'
            params.append(data_quality)
        
        query += ' ORDER BY discovered_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        
        discoveries = []
        for row in cursor.fetchall():
            discoveries.append(CrawlDiscovery(*row))
        
        conn.close()
        return discoveries
    
    def get_crawl_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get crawl statistics for the last N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Session statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_sessions,
                COUNT(CASE WHEN status = 'running' THEN 1 END) as running_sessions,
                SUM(total_requests) as total_requests,
                SUM(successful_requests) as successful_requests,
                SUM(failed_requests) as failed_requests,
                SUM(items_scraped) as total_items,
                SUM(leagues_discovered) as total_discoveries
            FROM crawl_sessions
            WHERE start_time >= ?
        ''', (since_date,))
        
        stats_row = cursor.fetchone()
        session_stats = {
            'total_sessions': stats_row[0] or 0,
            'completed_sessions': stats_row[1] or 0,
            'failed_sessions': stats_row[2] or 0,
            'running_sessions': stats_row[3] or 0,
            'total_requests': stats_row[4] or 0,
            'successful_requests': stats_row[5] or 0,
            'failed_requests': stats_row[6] or 0,
            'total_items': stats_row[7] or 0,
            'total_discoveries': stats_row[8] or 0,
        }
        
        # Log level distribution
        cursor.execute('''
            SELECT cl.level, COUNT(*) as count
            FROM crawl_logs cl
            JOIN crawl_sessions cs ON cl.session_id = cs.id
            WHERE cs.start_time >= ?
            GROUP BY cl.level
        ''', (since_date,))
        
        log_levels = dict(cursor.fetchall())
        
        # Top discovered leagues
        cursor.execute('''
            SELECT cd.league_id, cd.season_year, cd.league_name, cd.match_count
            FROM crawl_discoveries cd
            JOIN crawl_sessions cs ON cd.session_id = cs.id
            WHERE cs.start_time >= ?
            ORDER BY cd.match_count DESC
            LIMIT 10
        ''', (since_date,))
        
        top_leagues = []
        for row in cursor.fetchall():
            top_leagues.append({
                'league_id': row[0],
                'season_year': row[1],
                'league_name': row[2],
                'match_count': row[3]
            })
        
        # Error analysis
        cursor.execute('''
            SELECT ce.error_type, COUNT(*) as count
            FROM crawl_errors ce
            JOIN crawl_sessions cs ON ce.session_id = cs.id
            WHERE cs.start_time >= ?
            GROUP BY ce.error_type
            ORDER BY count DESC
        ''', (since_date,))
        
        error_types = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'period_days': days,
            'session_stats': session_stats,
            'log_levels': log_levels,
            'top_leagues': top_leagues,
            'error_types': error_types,
            'success_rate': (session_stats['successful_requests'] / max(1, session_stats['total_requests'])) * 100
        }
    
    def get_league_discovery_history(self, league_id: str) -> List[Dict[str, Any]]:
        """Get discovery history for a specific league across seasons"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cd.season_year, cd.league_name, cd.district_name, cd.match_count,
                   cd.team_count, cd.data_quality, cd.discovered_at, cs.session_name
            FROM crawl_discoveries cd
            JOIN crawl_sessions cs ON cd.session_id = cs.id
            WHERE cd.league_id = ?
            ORDER BY cd.season_year DESC, cd.discovered_at DESC
        ''', (league_id,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'season_year': row[0],
                'league_name': row[1],
                'district_name': row[2],
                'match_count': row[3],
                'team_count': row[4],
                'data_quality': row[5],
                'discovered_at': row[6],
                'session_name': row[7]
            })
        
        conn.close()
        return history
    
    def export_session_report(self, session_id: str) -> Dict[str, Any]:
        """Export comprehensive session report"""
        session_details = self.get_session_details(session_id)
        if not session_details:
            return {}
        
        # Get all discoveries for this session
        discoveries = self.search_discoveries(session_id=session_id, limit=1000)
        
        # Get critical errors
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT url, error_type, error_message, occurred_at
            FROM crawl_errors
            WHERE session_id = ?
            ORDER BY occurred_at DESC
            LIMIT 50
        ''', (session_id,))
        
        errors = []
        for row in cursor.fetchall():
            errors.append({
                'url': row[0],
                'error_type': row[1],
                'error_message': row[2],
                'occurred_at': row[3]
            })
        
        conn.close()
        
        return {
            'session_details': session_details,
            'discoveries': [
                {
                    'league_id': d.league_id,
                    'season_year': d.season_year,
                    'league_name': d.league_name,
                    'match_count': d.match_count,
                    'data_quality': d.data_quality
                }
                for d in discoveries
            ],
            'errors': errors,
            'generated_at': datetime.now().isoformat()
        }
