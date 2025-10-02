#!/usr/bin/env python3

import scrapy
import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any

class ExtendedHistoricalCrawlerSpider(scrapy.Spider):
    """
    Extended historical crawler for basketball data from 2003-2024.
    Focuses on 2. Regionalliga-Süd and below with smart caching.
    """
    name = 'extended_historical_crawler'
    allowed_domains = ['basketball-bund.net']
    
    # Known working league IDs (from previous discovery)
    confirmed_leagues = {
        '49749': 'Top league with 73 matches',
        '49854': 'League with 33 matches', 
        '49750': 'League with 32 matches',
        '49849': 'League with 26 matches',
        '50799': 'League with 25 matches',
        '50852': 'League with 25 matches',
    }
    
    def __init__(self, *args, **kwargs):
        super(ExtendedHistoricalCrawlerSpider, self).__init__(*args, **kwargs)
        
        # Set up database path
        self.cache_db_path = 'extended_league_cache.db'
        self.setup_database()
        
        # Statistics
        self.leagues_discovered = 0
        self.leagues_cached_nonexistent = 0
        self.total_requests = 0
        
    def setup_database(self):
        """Set up SQLite database for extended caching"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extended_league_cache (
                league_id INTEGER,
                season_year INTEGER,
                league_exists BOOLEAN,
                match_count INTEGER,
                league_name TEXT,
                district_name TEXT,
                last_checked TIMESTAMP,
                data_quality TEXT,
                PRIMARY KEY (league_id, season_year)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extended_crawl_sessions (
                session_id TEXT PRIMARY KEY,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                years_covered TEXT,
                leagues_found INTEGER,
                leagues_tested INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info(f"Extended cache database ready: {self.cache_db_path}")

    def start_requests(self):
        """Generate requests for extended historical coverage (2003-2024)"""
        session_id = f"extended_crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_id = session_id
        
        # Log session start
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO extended_crawl_sessions 
            (session_id, started_at, years_covered, leagues_found, leagues_tested)
            VALUES (?, ?, ?, 0, 0)
        ''', (session_id, datetime.now().isoformat(), "2003-2024"))
        conn.commit()
        conn.close()
        
        self.logger.info(f"🚀 Starting extended historical crawl: {session_id}")
        self.logger.info("📅 Coverage: 2003-2024 (22 years of digitalized data)")
        
        # Extended season range: 2003-2024
        all_seasons = list(range(2003, 2025))
        base_url = 'https://www.basketball-bund.net/rest/'
        
        request_count = 0
        
        # Phase 1: Test confirmed working leagues across all years
        self.logger.info("🔍 Phase 1: Testing confirmed leagues across all seasons")
        for league_id, description in self.confirmed_leagues.items():
            for season in all_seasons:
                # Calculate historical league ID (subtract 1 per year from 2025)
                year_offset = 2025 - season
                historical_id = int(league_id) - year_offset
                
                if not self.is_league_cached(historical_id, season):
                    url = f"{base_url}competition/actual/id/{historical_id}"
                    request_count += 1
                    
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_league_data,
                        meta={
                            'league_id': historical_id,
                            'season': season,
                            'phase': 'confirmed_expansion',
                            'base_league_id': league_id
                        }
                    )
        
        # Phase 2: Systematic discovery in focused ranges for older years
        self.logger.info("🎯 Phase 2: Systematic discovery for older seasons")
        priority_seasons = [s for s in all_seasons if s < 2020]  # Focus on pre-2020
        
        # Focused ranges based on previous discoveries
        discovery_ranges = [
            (47500, 47600),  # Focused sub-range 1
            (48500, 48600),  # Focused sub-range 2
            (49700, 49900),  # Hot zone around 49749
            (50700, 50900),  # Hot zone around 50799/50852
        ]
        
        for start_id, end_id in discovery_ranges:
            for season in priority_seasons:
                for league_id in range(start_id, end_id, 5):  # Sample every 5th ID
                    if not self.is_league_cached(league_id, season):
                        url = f"{base_url}competition/actual/id/{league_id}"
                        request_count += 1
                        
                        yield scrapy.Request(
                            url=url,
                            callback=self.parse_league_data,
                            meta={
                                'league_id': league_id,
                                'season': season,
                                'phase': 'systematic_discovery',
                                'range': f"{start_id}-{end_id}"
                            }
                        )
        
        self.logger.info(f"📊 Total requests queued: {request_count}")
        self.total_requests = request_count

    def is_league_cached(self, league_id, season_year):
        """Check if league is already in extended cache"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT league_exists FROM extended_league_cache 
            WHERE league_id = ? AND season_year = ?
        ''', (league_id, season_year))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None

    def parse_league_data(self, response):
        """Parse league data and cache results"""
        league_id = response.meta['league_id']
        season = response.meta['season']
        phase = response.meta.get('phase', 'unknown')
        
        try:
            data = json.loads(response.text)
            
            # Check if league exists and has data
            if self.is_valid_league_response(data):
                self.leagues_discovered += 1
                match_count = len(data.get('matchList', []))
                league_name = data.get('leagueName', 'Unknown')
                district = data.get('district', {}).get('name', 'Unknown')
                
                # Cache successful discovery
                self.cache_league_result(
                    league_id=league_id,
                    season_year=season,
                    league_exists=True,
                    match_count=match_count,
                    league_name=league_name,
                    district_name=district,
                    data_quality='complete' if match_count > 10 else 'partial'
                )
                
                self.logger.info(
                    f"✅ {phase.upper()}: League {league_id} ({season}) - "
                    f"{match_count} matches, {league_name[:30]}{'...' if len(league_name) > 30 else ''}"
                )
                
                # Yield structured data
                yield {
                    'league_id': league_id,
                    'season_year': season,
                    'league_name': league_name,
                    'district_name': district,
                    'match_count': match_count,
                    'matches': data.get('matchList', []),
                    'table': data.get('table', {}),
                    'discovery_phase': phase,
                    'data_quality': 'complete' if match_count > 10 else 'partial',
                    'team_count': len(data.get('table', {}).get('standings', [])),
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Explore adjacent league IDs if this is a good find
                if match_count >= 15:  # High-quality league
                    yield from self.explore_adjacent_leagues(league_id, season, response.meta)
                    
            else:
                # Cache non-existent league
                self.leagues_cached_nonexistent += 1
                self.cache_league_result(
                    league_id=league_id,
                    season_year=season,
                    league_exists=False,
                    match_count=0,
                    league_name='',
                    district_name='',
                    data_quality='none'
                )
                
        except json.JSONDecodeError:
            self.logger.warning(f"❌ Invalid JSON for league {league_id} ({season})")
            self.cache_league_result(
                league_id=league_id,
                season_year=season, 
                league_exists=False,
                match_count=0,
                league_name='',
                district_name='',
                data_quality='error'
            )

    def is_valid_league_response(self, data):
        """Check if response contains valid league data"""
        if not isinstance(data, dict):
            return False
            
        # Must have matches or table data
        has_matches = bool(data.get('matchList'))
        has_table = bool(data.get('table', {}).get('standings'))
        
        return has_matches or has_table

    def explore_adjacent_leagues(self, base_league_id, season, original_meta):
        """Explore leagues adjacent to successful discoveries"""
        base_url = 'https://www.basketball-bund.net/rest/'
        adjacent_range = 3  # Check 3 IDs in each direction
        
        for offset in range(-adjacent_range, adjacent_range + 1):
            if offset == 0:  # Skip the original league
                continue
                
            adjacent_id = base_league_id + offset
            
            if not self.is_league_cached(adjacent_id, season):
                url = f"{base_url}competition/actual/id/{adjacent_id}"
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_league_data,
                    meta={
                        'league_id': adjacent_id,
                        'season': season,
                        'phase': 'adjacent_exploration',
                        'base_league': base_league_id
                    }
                )

    def cache_league_result(self, league_id, season_year, league_exists, match_count, 
                          league_name, district_name, data_quality):
        """Cache league result to avoid future duplicate requests"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO extended_league_cache 
            (league_id, season_year, league_exists, match_count, league_name, 
             district_name, last_checked, data_quality)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (league_id, season_year, league_exists, match_count, league_name,
              district_name, datetime.now().isoformat(), data_quality))
        
        conn.commit()
        conn.close()

    def close(self, reason):
        """Update final statistics when spider closes"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE extended_crawl_sessions 
            SET completed_at = ?, leagues_found = ?, leagues_tested = ?
            WHERE session_id = ?
        ''', (datetime.now().isoformat(), self.leagues_discovered, 
              self.total_requests, self.session_id))
        
        conn.commit()
        conn.close()
        
        self.logger.info("🎉 Extended historical crawl completed!")
        self.logger.info(f"📈 Final Statistics:")
        self.logger.info(f"   • Leagues discovered: {self.leagues_discovered}")
        self.logger.info(f"   • Leagues cached (non-existent): {self.leagues_cached_nonexistent}")
        self.logger.info(f"   • Total requests processed: {self.total_requests}")
        self.logger.info(f"   • Years covered: 2003-2024 (22 years)")
        self.logger.info(f"   • Cache database: {self.cache_db_path}")
