import scrapy
import json
import sqlite3
import os
from datetime import datetime, timedelta
from urllib.parse import urljoin


class SmartHistoricalCrawlerSpider(scrapy.Spider):
    name = 'smart_historical_crawler'
    allowed_domains = ['basketball-bund.net']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.8,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.3,
    }
    
    def __init__(self, *args, **kwargs):
        super(SmartHistoricalCrawlerSpider, self).__init__(*args, **kwargs)
        self.cache_db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'league_cache.db')
        self.setup_cache_database()
        
        # Focus on 2. Regionalliga-Süd and below (lower tier leagues)
        # These typically have IDs in ranges: 47xxx, 48xxx, 49xxx, 50xxx, 51xxx
        self.target_league_ranges = [
            (47000, 48000),  # Oberliga/Regionalliga level
            (48000, 49000),  # District leagues
            (49000, 50000),  # Lower district leagues  
            (50000, 52000),  # Youth leagues and others
        ]
        
        # Known working leagues from our previous tests
        self.confirmed_leagues = {
            '47960': 'Oberfranken District League Men',
            '47961': 'Oberfranken District League Women', 
            '47959': 'Oberfranken District Cup Women',
            '51020': 'NBBL A'
        }

    def setup_cache_database(self):
        """Initialize SQLite database for caching league existence"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS league_cache (
                league_id TEXT,
                season_year INTEGER,
                league_exists BOOLEAN,
                last_checked TIMESTAMP,
                match_count INTEGER,
                league_name TEXT,
                district_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (league_id, season_year)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawl_sessions (
                session_id TEXT PRIMARY KEY,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                leagues_found INTEGER,
                leagues_failed INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Cache database initialized at: {self.cache_db_path}")

    def is_league_cached(self, league_id, season_year):
        """Check if league data is already cached and recent"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT league_exists, last_checked, match_count 
            FROM league_cache 
            WHERE league_id = ? AND season_year = ?
        ''', (league_id, season_year))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            league_exists, last_checked_str, match_count = result
            last_checked = datetime.fromisoformat(last_checked_str)
            
            # Consider cached for 7 days for non-existing leagues, 1 day for existing
            cache_duration = timedelta(days=7) if not league_exists else timedelta(days=1)
            
            if datetime.now() - last_checked < cache_duration:
                self.logger.info(f"Using cached result for {league_id}/{season_year}: exists={league_exists}")
                return True, league_exists
        
        return False, None

    def cache_league_result(self, league_id, season_year, league_exists, match_count=0, league_name="", district_name=""):
        """Cache the result of league existence check"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO league_cache 
            (league_id, season_year, league_exists, last_checked, match_count, league_name, district_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (league_id, season_year, league_exists, datetime.now().isoformat(), match_count, league_name, district_name))
        
        conn.commit()
        conn.close()

    def start_requests(self):
        """Generate requests focusing on likely historical data sources"""
        session_id = f"crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_id = session_id
        
        # Log crawl session start
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO crawl_sessions (session_id, started_at, leagues_found, leagues_failed)
            VALUES (?, ?, 0, 0)
        ''', (session_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        self.logger.info(f"Starting smart crawl session: {session_id}")
        
        # Test seasons from 2003 to 2024 (22 years of digitalized data)
        test_seasons = list(range(2003, 2025))
        base_url = 'https://www.basketball-bund.net/rest/'
        
        request_count = 0
        
        # First, check confirmed working leagues
        for league_id, league_name in self.confirmed_leagues.items():
            for season in test_seasons:
                # Calculate expected historical league ID (subtract 1 per year from 2025)
                year_offset = 2025 - season
                historical_id = int(league_id) - year_offset
                
                # Check cache first
                is_cached, cached_exists = self.is_league_cached(str(historical_id), season)
                if is_cached:
                    if cached_exists:
                        self.logger.info(f"✅ Cached: League {historical_id} exists for {season}")
                    continue
                
                url = urljoin(base_url, f'competition/actual/id/{historical_id}')
                request_count += 1
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_league_response,
                    meta={
                        'original_league_id': league_id,
                        'original_league_name': league_name,
                        'historical_league_id': str(historical_id),
                        'season_year': season,
                        'test_type': 'confirmed_league_historical'
                    },
                    dont_filter=True
                )
        
        # Then, systematically check league ranges for unknown leagues
        for start_range, end_range in self.target_league_ranges:
            for base_league_id in range(start_range, end_range, 50):  # Sample every 50 IDs
                for season in test_seasons[:2]:  # Only check recent 2 seasons for discovery
                    year_offset = 2025 - season
                    historical_id = base_league_id - year_offset
                    
                    # Skip if already tested or cached
                    is_cached, cached_exists = self.is_league_cached(str(historical_id), season)
                    if is_cached:
                        continue
                    
                    # Skip if too many requests already
                    if request_count >= 200:
                        self.logger.info(f"Limiting discovery requests to 200 for this session")
                        break
                    
                    url = urljoin(base_url, f'competition/actual/id/{historical_id}')
                    request_count += 1
                    
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_league_response,
                        meta={
                            'original_league_id': str(base_league_id),
                            'original_league_name': 'Unknown',
                            'historical_league_id': str(historical_id),
                            'season_year': season,
                            'test_type': 'discovery'
                        },
                        dont_filter=True
                    )
                    
                if request_count >= 200:
                    break
            if request_count >= 200:
                break

        self.logger.info(f"Generated {request_count} discovery requests")

    def parse_league_response(self, response):
        """Parse league response and cache results"""
        historical_league_id = response.meta['historical_league_id']
        season_year = response.meta['season_year']
        original_league_id = response.meta['original_league_id']
        original_league_name = response.meta['original_league_name']
        test_type = response.meta['test_type']
        
        status_code = response.status
        
        if status_code != 200:
            # Cache non-existing league
            self.cache_league_result(historical_league_id, season_year, False)
            self.logger.debug(f"❌ League {historical_league_id} not found (HTTP {status_code})")
            return
        
        try:
            json_data = json.loads(response.text)
        except json.JSONDecodeError:
            self.cache_league_result(historical_league_id, season_year, False)
            return
        
        # Check if response indicates league doesn't exist
        if json_data.get('status') == '1' and 'no competition found' in json_data.get('message', '').lower():
            self.cache_league_result(historical_league_id, season_year, False)
            self.logger.debug(f"❌ League {historical_league_id} not found for {season_year}")
            return
        
        # Check if we have actual basketball data
        data_section = json_data.get('data', {})
        if not isinstance(data_section, dict):
            self.cache_league_result(historical_league_id, season_year, False)
            return
        
        league_data = data_section.get('league_data', {})
        matches = data_section.get('matches', [])
        table = data_section.get('table', {})
        
        if not (league_data or matches or table):
            self.cache_league_result(historical_league_id, season_year, False)
            return
        
        # Extract league information
        found_league_name = league_data.get('league_name', '') if league_data else ''
        found_district = league_data.get('district_name', '') if league_data else ''
        found_season_id = league_data.get('season_id') if league_data else None
        found_season_name = league_data.get('season_name', '') if league_data else ''
        match_count = len(matches) if matches else 0
        table_count = len(table.get('entries', [])) if isinstance(table, dict) else 0
        
        # Cache successful result
        self.cache_league_result(
            historical_league_id, 
            season_year, 
            True, 
            match_count, 
            found_league_name, 
            found_district
        )
        
        # Log discovery
        if test_type == 'confirmed_league_historical':
            self.logger.info(
                f"✅ CONFIRMED: {found_league_name} ({found_district}) - "
                f"Season: {season_year} - League ID: {historical_league_id} - "
                f"Matches: {match_count}, Teams: {table_count}"
            )
        else:
            self.logger.info(
                f"🆕 DISCOVERED: {found_league_name} ({found_district}) - "
                f"Season: {season_year} - League ID: {historical_league_id} - " 
                f"Matches: {match_count}, Teams: {table_count}"
            )
        
        # Yield detailed result
        result = {
            'type': 'historical_league_data',
            'url': response.url,
            'original_league_id': original_league_id,
            'original_league_name': original_league_name,
            'historical_league_id': historical_league_id,
            'season_year': season_year,
            'test_type': test_type,
            'found_league_name': found_league_name,
            'found_district': found_district,
            'found_season_id': found_season_id,
            'found_season_name': found_season_name,
            'match_count': match_count,
            'table_count': table_count,
            'content_length': len(response.text),
            'discovery_timestamp': datetime.now().isoformat()
        }
        
        yield result
        
        # If this is a new discovery, also try adjacent league IDs
        if test_type == 'discovery' and match_count > 0:
            self.logger.info(f"🔍 Exploring adjacent IDs around successful {historical_league_id}")
            yield from self.explore_adjacent_leagues(historical_league_id, season_year, response.url)

    def explore_adjacent_leagues(self, successful_league_id, season_year, base_url):
        """Explore league IDs adjacent to a successful discovery"""
        base_id = int(successful_league_id)
        base_url_template = base_url.replace(f'id/{successful_league_id}', 'id/{}')
        
        # Check ±5 IDs around the successful one
        for offset in [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]:
            adjacent_id = base_id + offset
            adjacent_id_str = str(adjacent_id)
            
            # Skip if already cached
            is_cached, _ = self.is_league_cached(adjacent_id_str, season_year)
            if is_cached:
                continue
            
            url = base_url_template.format(adjacent_id)
            
            yield scrapy.Request(
                url=url,
                callback=self.parse_league_response,
                meta={
                    'original_league_id': str(base_id),
                    'original_league_name': 'Adjacent Discovery',
                    'historical_league_id': adjacent_id_str,
                    'season_year': season_year,
                    'test_type': 'adjacent_exploration'
                },
                dont_filter=True
            )

    def closed(self, reason):
        """Update crawl session completion"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        # Count results
        cursor.execute('''
            SELECT COUNT(*) FROM league_cache 
            WHERE league_exists = 1 AND datetime(last_checked) > datetime('now', '-1 hour')
        ''')
        leagues_found = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM league_cache 
            WHERE league_exists = 0 AND datetime(last_checked) > datetime('now', '-1 hour')
        ''')
        leagues_failed = cursor.fetchone()[0]
        
        # Update session
        cursor.execute('''
            UPDATE crawl_sessions 
            SET completed_at = ?, leagues_found = ?, leagues_failed = ?
            WHERE session_id = ?
        ''', (datetime.now().isoformat(), leagues_found, leagues_failed, self.session_id))
        
        conn.commit()
        conn.close()
        
        self.logger.info(
            f"Crawl session completed: {leagues_found} leagues found, "
            f"{leagues_failed} leagues confirmed non-existent"
        )
