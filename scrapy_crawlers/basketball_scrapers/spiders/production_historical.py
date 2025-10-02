import scrapy
import json
import sqlite3
import os
from datetime import datetime
from urllib.parse import urljoin


class ProductionHistoricalSpider(scrapy.Spider):
    name = 'production_historical'
    allowed_domains = ['basketball-bund.net']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1.0,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 8,
    }
    
    def __init__(self, *args, **kwargs):
        super(ProductionHistoricalSpider, self).__init__(*args, **kwargs)
        self.cache_db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'league_cache.db')
        
        # Only crawl leagues from 2. Regionalliga-Süd and below
        # Focus on confirmed existing leagues from cache
        self.min_matches_threshold = 3  # Only crawl leagues with meaningful data

    def get_cached_leagues(self):
        """Get all confirmed existing leagues from cache"""
        if not os.path.exists(self.cache_db_path):
            self.logger.error(f"Cache database not found at {self.cache_db_path}")
            self.logger.error("Run 'smart_historical_crawler' first to build the cache")
            return []
        
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT league_id, season_year, match_count, league_name, district_name
            FROM league_cache 
            WHERE league_exists = 1 AND match_count >= ?
            ORDER BY season_year DESC, match_count DESC
        ''', (self.min_matches_threshold,))
        
        results = cursor.fetchall()
        conn.close()
        
        self.logger.info(f"Found {len(results)} cached leagues with ≥{self.min_matches_threshold} matches")
        return results

    def start_requests(self):
        """Generate requests only for confirmed existing leagues"""
        cached_leagues = self.get_cached_leagues()
        
        if not cached_leagues:
            self.logger.error("No cached leagues found. Run discovery spider first.")
            return
        
        base_url = 'https://www.basketball-bund.net/rest/'
        request_count = 0
        
        for league_id, season_year, match_count, league_name, district_name in cached_leagues:
            url = urljoin(base_url, f'competition/actual/id/{league_id}')
            request_count += 1
            
            self.logger.info(
                f"Crawling: {league_name} ({district_name}) - "
                f"Season {season_year}, League ID {league_id}, {match_count} matches"
            )
            
            yield scrapy.Request(
                url=url,
                callback=self.parse_league_data,
                meta={
                    'league_id': league_id,
                    'season_year': season_year,
                    'expected_matches': match_count,
                    'league_name': league_name,
                    'district_name': district_name
                },
                dont_filter=True
            )
        
        self.logger.info(f"Generated {request_count} production requests")

    def parse_league_data(self, response):
        """Parse complete league data for confirmed leagues"""
        league_id = response.meta['league_id']
        season_year = response.meta['season_year']
        expected_matches = response.meta['expected_matches']
        league_name = response.meta['league_name']
        district_name = response.meta['district_name']
        
        if response.status != 200:
            self.logger.warning(f"Unexpected status {response.status} for league {league_id}")
            return
        
        try:
            json_data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON for league {league_id}")
            return
        
        data_section = json_data.get('data', {})
        if not isinstance(data_section, dict):
            self.logger.warning(f"No data section for league {league_id}")
            return
        
        league_data = data_section.get('league_data', {})
        matches = data_section.get('matches', [])
        table = data_section.get('table', {})
        
        # Extract comprehensive league information
        result = {
            'type': 'production_league_data',
            'crawled_at': datetime.now().isoformat(),
            'url': response.url,
            
            # League identification
            'league_id': league_id,
            'season_year': season_year,
            'cached_league_name': league_name,
            'cached_district_name': district_name,
            
            # League metadata from API
            'api_league_data': league_data,
            'found_league_name': league_data.get('league_name', '') if league_data else '',
            'found_district_name': league_data.get('district_name', '') if league_data else '',
            'found_season_id': league_data.get('season_id') if league_data else None,
            'found_season_name': league_data.get('season_name', '') if league_data else '',
            
            # Match data
            'matches': matches,
            'match_count': len(matches),
            'expected_match_count': expected_matches,
            
            # Table data
            'table': table,
            'team_count': len(table.get('entries', [])) if isinstance(table, dict) else 0,
            
            # Data quality metrics
            'data_completeness': {
                'has_league_data': bool(league_data),
                'has_matches': len(matches) > 0,
                'has_table': bool(table and table.get('entries')),
                'match_count_matches_cache': len(matches) == expected_matches,
            }
        }
        
        # Extract sample match details for verification
        if matches:
            sample_matches = []
            for match in matches[:3]:  # First 3 matches for sample
                if isinstance(match, dict):
                    sample_match = {
                        'match_id': match.get('match_id'),
                        'match_day': match.get('match_day'),
                        'kickoff_date': match.get('kickoff_date'),
                        'kickoff_time': match.get('kickoff_time'),
                        'home_team': match.get('home_team', {}).get('team_name') if match.get('home_team') else None,
                        'guest_team': match.get('guest_team', {}).get('team_name') if match.get('guest_team') else None,
                        'result': match.get('result'),
                        'has_result': bool(match.get('result'))
                    }
                    sample_matches.append(sample_match)
            result['sample_matches'] = sample_matches
        
        # Extract sample table entries
        if isinstance(table, dict) and 'entries' in table:
            sample_table = []
            for entry in table['entries'][:3]:  # First 3 teams for sample
                if isinstance(entry, dict):
                    team_entry = {
                        'rank': entry.get('rank'),
                        'team_name': entry.get('team', {}).get('team_name') if entry.get('team') else None,
                        'games_played': entry.get('games_played'),
                        'wins': entry.get('wins'),
                        'losses': entry.get('losses'),
                        'points_for': entry.get('points_for'),
                        'points_against': entry.get('points_against'),
                        'points_diff': entry.get('points_diff'),
                        'percentage': entry.get('percentage')
                    }
                    sample_table.append(team_entry)
            result['sample_table'] = sample_table
        
        # Log successful extraction
        self.logger.info(
            f"✅ {result['found_league_name'] or league_name} ({result['found_district_name'] or district_name}) - "
            f"Season {season_year}: {len(matches)} matches, {result['team_count']} teams"
        )
        
        yield result

    def closed(self, reason):
        """Log spider completion statistics"""
        self.logger.info(f"Production historical crawl completed: {reason}")
        
        # Could add statistics here if needed
        if hasattr(self, 'crawler'):
            stats = self.crawler.stats
            items_scraped = stats.get_value('item_scraped_count', 0)
            requests_made = stats.get_value('response_received_count', 0)
            self.logger.info(f"Scraped {items_scraped} leagues from {requests_made} requests")
