#!/usr/bin/env python3

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import traceback
import time


class CrawlLoggerPipeline:
    """
    Enhanced logging pipeline that captures comprehensive crawl information
    and stores it in a searchable database format.
    """
    
    def __init__(self):
        self.db_path = 'crawl_logs.db'
        self.session_id = None
        self.session_start_time = None
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0, 
            'failed_requests': 0,
            'items_scraped': 0,
            'leagues_discovered': 0
        }
        
    def open_spider(self, spider):
        """Initialize logging session when spider starts"""
        self.setup_database()
        
        # Create crawl session
        self.session_id = f"{spider.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_start_time = datetime.now()
        
        spider_config = {
            'name': spider.name,
            'allowed_domains': getattr(spider, 'allowed_domains', []),
            'custom_settings': getattr(spider, 'custom_settings', {}),
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO crawl_sessions 
            (id, session_name, spider_name, start_time, status, configuration)
            VALUES (?, ?, ?, ?, 'running', ?)
        ''', (
            self.session_id,
            f"{spider.name} - {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            spider.name,
            self.session_start_time.isoformat(),
            json.dumps(spider_config, indent=2)
        ))
        
        conn.commit()
        conn.close()
        
        spider.logger.info(f"🚀 Crawl logging session started: {self.session_id}")
        
        # Set up custom log handler
        self.setup_log_handler(spider)
    
    def setup_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Read and execute migration SQL
        try:
            with open('crawl_logging_migration.sql', 'r') as f:
                migration_sql = f.read()
                # Split by semicolon and execute each statement
                statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
                for statement in statements:
                    if statement and not statement.startswith('--'):
                        cursor.execute(statement)
        except FileNotFoundError:
            # Fallback: create basic tables
            cursor.executescript('''
                CREATE TABLE IF NOT EXISTS crawl_sessions (
                    id TEXT PRIMARY KEY,
                    session_name TEXT NOT NULL,
                    spider_name TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    status TEXT NOT NULL DEFAULT 'running',
                    total_requests INTEGER DEFAULT 0,
                    successful_requests INTEGER DEFAULT 0,
                    failed_requests INTEGER DEFAULT 0,
                    items_scraped INTEGER DEFAULT 0,
                    leagues_discovered INTEGER DEFAULT 0,
                    error_message TEXT,
                    configuration TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS crawl_logs (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    level TEXT NOT NULL,
                    logger_name TEXT NOT NULL,
                    message TEXT NOT NULL,
                    url TEXT,
                    response_status INTEGER,
                    response_time_ms INTEGER,
                    league_id TEXT,
                    season_year INTEGER,
                    match_count INTEGER,
                    error_details TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS crawl_discoveries (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    league_id TEXT NOT NULL,
                    season_year INTEGER NOT NULL,
                    league_name TEXT,
                    district_name TEXT,
                    match_count INTEGER DEFAULT 0,
                    team_count INTEGER DEFAULT 0,
                    data_quality TEXT,
                    discovery_phase TEXT,
                    url TEXT NOT NULL,
                    response_time_ms INTEGER,
                    discovered_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS crawl_errors (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    error_code INTEGER,
                    league_id TEXT,
                    season_year INTEGER,
                    retry_count INTEGER DEFAULT 0,
                    stack_trace TEXT,
                    request_headers TEXT,
                    response_headers TEXT,
                    response_body TEXT,
                    occurred_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            ''')
        
        conn.commit()
        conn.close()
    
    def setup_log_handler(self, spider):
        """Set up custom log handler to capture all log messages"""
        handler = CrawlDatabaseLogHandler(self.db_path, self.session_id)
        handler.setLevel(logging.DEBUG)
        
        # Add handler to root logger instead of spider logger
        logging.getLogger().addHandler(handler)
        
        spider.logger.info(f"📝 Enhanced logging enabled for session: {self.session_id}")
    
    def process_item(self, item, spider):
        """Process scraped items and log discoveries"""
        self.stats['items_scraped'] += 1
        
        # Log league discovery
        if 'league_id' in item and 'season_year' in item:
            self.log_discovery(item, spider)
            self.stats['leagues_discovered'] += 1
        
        return item
    
    def log_discovery(self, item: Dict[str, Any], spider):
        """Log a league discovery with detailed information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        discovery_id = f"disc_{int(time.time() * 1000000)}"
        
        cursor.execute('''
            INSERT INTO crawl_discoveries (
                id, session_id, league_id, season_year, league_name, district_name,
                match_count, team_count, data_quality, discovery_phase, url,
                response_time_ms, discovered_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            discovery_id,
            self.session_id,
            str(item.get('league_id', '')),
            int(item.get('season_year', 0)),
            item.get('league_name', ''),
            item.get('district_name', ''),
            int(item.get('match_count', 0)),
            int(item.get('team_count', 0)),
            item.get('data_quality', ''),
            item.get('discovery_phase', ''),
            item.get('url', ''),
            item.get('response_time_ms'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        spider.logger.info(
            f"🎯 DISCOVERY: League {item.get('league_id')} ({item.get('season_year')}) - "
            f"{item.get('match_count', 0)} matches, {item.get('data_quality', 'unknown')} quality"
        )
    
    def log_error(self, failure, request, spider):
        """Log detailed error information"""
        self.stats['failed_requests'] += 1
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        error_id = f"err_{int(time.time() * 1000000)}"
        
        # Extract error details
        error_type = failure.type.__name__ if failure.type else 'UnknownError'
        error_message = str(failure.value) if failure.value else 'No error message'
        
        # Extract league info from request meta if available
        league_id = request.meta.get('league_id')
        season_year = request.meta.get('season')
        
        cursor.execute('''
            INSERT INTO crawl_errors (
                id, session_id, url, error_type, error_message, error_code,
                league_id, season_year, retry_count, stack_trace,
                request_headers, response_headers, response_body, occurred_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            error_id,
            self.session_id,
            request.url,
            error_type,
            error_message,
            getattr(failure.value, 'response', {}).get('status') if hasattr(failure.value, 'response') else None,
            str(league_id) if league_id else None,
            int(season_year) if season_year else None,
            request.meta.get('retry_times', 0),
            failure.getTraceback(),
            json.dumps(dict(request.headers)) if request.headers else None,
            json.dumps(dict(getattr(failure.value, 'response', {}).get('headers', {}))) if hasattr(failure.value, 'response') else None,
            getattr(failure.value, 'response', {}).get('text', '')[:5000] if hasattr(failure.value, 'response') else None,  # Limit to 5KB
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        spider.logger.error(
            f"❌ ERROR: {request.url} - {error_type}: {error_message}"
        )
    
    def close_spider(self, spider):
        """Finalize logging session when spider closes"""
        end_time = datetime.now()
        duration = end_time - self.session_start_time
        
        # Update session with final statistics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE crawl_sessions SET
                end_time = ?,
                status = 'completed',
                total_requests = ?,
                successful_requests = ?,
                failed_requests = ?,
                items_scraped = ?,
                leagues_discovered = ?
            WHERE id = ?
        ''', (
            end_time.isoformat(),
            self.stats['total_requests'],
            self.stats['successful_requests'],
            self.stats['failed_requests'],
            self.stats['items_scraped'],
            self.stats['leagues_discovered'],
            self.session_id
        ))
        
        conn.commit()
        conn.close()
        
        spider.logger.info(f"🏁 Crawl session completed: {self.session_id}")
        spider.logger.info(f"📊 Final Statistics:")
        spider.logger.info(f"   Duration: {duration}")
        spider.logger.info(f"   Items scraped: {self.stats['items_scraped']}")
        spider.logger.info(f"   Leagues discovered: {self.stats['leagues_discovered']}")
        spider.logger.info(f"   Success rate: {(self.stats['successful_requests'] / max(1, self.stats['total_requests']) * 100):.1f}%")


class CrawlDatabaseLogHandler(logging.Handler):
    """Custom log handler that writes to crawl_logs database table"""
    
    def __init__(self, db_path: str, session_id: str):
        super().__init__()
        self.db_path = db_path
        self.session_id = session_id
    
    def emit(self, record: logging.LogRecord):
        """Emit log record to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            log_id = f"log_{int(time.time() * 1000000)}"
            
            # Extract additional context from record
            url = getattr(record, 'url', None)
            response_status = getattr(record, 'response_status', None)
            response_time = getattr(record, 'response_time_ms', None)
            league_id = getattr(record, 'league_id', None)
            season_year = getattr(record, 'season_year', None)
            match_count = getattr(record, 'match_count', None)
            
            # Build metadata
            metadata = {}
            if hasattr(record, 'extra_data'):
                metadata.update(record.extra_data)
            
            cursor.execute('''
                INSERT INTO crawl_logs (
                    id, session_id, timestamp, level, logger_name, message,
                    url, response_status, response_time_ms, league_id, season_year,
                    match_count, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_id,
                self.session_id,
                datetime.fromtimestamp(record.created).isoformat(),
                record.levelname,
                record.name,
                record.getMessage(),
                url,
                response_status,
                response_time,
                league_id,
                season_year,
                match_count,
                json.dumps(metadata) if metadata else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            # Don't let logging errors crash the spider
            print(f"Log handler error: {e}")


class EnhancedRequestMiddleware:
    """Middleware to track request/response timing and enhance logging"""
    
    def process_request(self, request, spider):
        """Track request start time"""
        request.meta['start_time'] = time.time()
        spider.crawler.stats.inc_value('crawl_logger/total_requests')
        return None
    
    def process_response(self, request, response, spider):
        """Log successful response with timing"""
        if 'start_time' in request.meta:
            response_time = (time.time() - request.meta['start_time']) * 1000
            
            spider.crawler.stats.inc_value('crawl_logger/successful_requests')
            
            # Create enhanced log record
            extra_data = {
                'url': request.url,
                'response_status': response.status,
                'response_time_ms': int(response_time),
                'league_id': request.meta.get('league_id'),
                'season_year': request.meta.get('season'),
            }
            
            spider.logger.info(
                f"✅ {response.status} {request.url} ({response_time:.0f}ms)",
                extra={'extra_data': extra_data}
            )
        
        return response
    
    def process_exception(self, request, exception, spider):
        """Log request exceptions"""
        spider.crawler.stats.inc_value('crawl_logger/failed_requests')
        
        extra_data = {
            'url': request.url,
            'league_id': request.meta.get('league_id'),
            'season_year': request.meta.get('season'),
            'exception_type': exception.__class__.__name__,
        }
        
        spider.logger.error(
            f"❌ Exception for {request.url}: {exception}",
            extra={'extra_data': extra_data}
        )
        
        return None
