import scrapy
import json


class RestHistoricalSpider(scrapy.Spider):
    name = 'rest_historical_crawler'
    allowed_domains = ['basketball-bund.net']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.3,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.1,
    }
    
    def start_requests(self):
        """Test patterns to find historical season data in the REST API"""
        
        # Current working league ID from Oberfranken
        current_league_id = '47960'
        
        # Test different historical patterns
        historical_patterns = [
            # Pattern 1: Different endpoints for seasons
            'competition/season/2024/id/47960',
            'competition/season/2023/id/47960', 
            'competition/season/2022/id/47960',
            'competition/history/47960',
            'competition/archive/47960',
            'competition/47960/seasons',
            'competition/47960/history',
            
            # Pattern 2: Maybe league IDs shift by thousands per season
            # If 47960 is 2025, maybe 46960 is 2024?
            'competition/actual/id/46960',  # 2024?
            'competition/actual/id/45960',  # 2023?
            'competition/actual/id/44960',  # 2022?
            
            # Pattern 3: Maybe they increment by hundreds
            'competition/actual/id/47860',  # Previous season?
            'competition/actual/id/47760',  # Earlier season?
            'competition/actual/id/47660',  # Even earlier?
            
            # Pattern 4: Test broader ranges around known working IDs
            # We know 47960, 47961, 47959 work for current season
            'competition/actual/id/46959',
            'competition/actual/id/46960', 
            'competition/actual/id/46961',
            'competition/actual/id/45959',
            'competition/actual/id/45960',
            'competition/actual/id/45961',
            
            # Pattern 5: Test if there are season-specific base APIs
            'seasons',
            'seasons/2024',
            'seasons/2023', 
            'seasons/2022',
            'competitions/season/2024',
            'competitions/season/2023',
            'competitions/season/2022',
            
            # Pattern 6: Test if there are region-specific historical APIs
            'region/oberfranken/seasons',
            'bezirk/oberfranken/2024',
            'bezirk/oberfranken/2023',
        ]
        
        base_url = 'https://www.basketball-bund.net/rest/'
        
        for pattern in historical_patterns:
            url = f"{base_url}{pattern}"
            yield scrapy.Request(
                url=url,
                callback=self.parse_historical_response,
                meta={
                    'pattern': pattern,
                    'test_type': 'historical_pattern'
                },
                dont_filter=True
            )

    def parse_historical_response(self, response):
        """Parse responses to find historical data patterns"""
        pattern = response.meta['pattern']
        test_type = response.meta['test_type']
        
        self.logger.info(f'🔍 Testing pattern: {pattern}')
        self.logger.info(f'   Status: {response.status}')
        self.logger.info(f'   Content length: {len(response.text)} characters')
        
        result = {
            'type': 'historical_test',
            'pattern': pattern,
            'url': response.url,
            'status_code': response.status,
            'content_length': len(response.text),
            'is_json': False,
            'season_data': None,
            'league_data': None
        }
        
        # Try to parse as JSON
        if response.status == 200:
            try:
                data = json.loads(response.text)
                result['is_json'] = True
                result['json_keys'] = list(data.keys()) if isinstance(data, dict) else []
                
                # Look for basketball/season specific data
                if isinstance(data, dict):
                    # Check for season information
                    if 'data' in data and isinstance(data['data'], dict):
                        league_data = data['data'].get('ligaData', {})
                        if league_data:
                            result['season_data'] = {
                                'season_id': league_data.get('seasonId'),
                                'season_name': league_data.get('seasonName'),
                                'league_id': league_data.get('ligaId'), 
                                'league_name': league_data.get('liganame'),
                                'region_name': league_data.get('bezirkName')
                            }
                            
                            season_id = league_data.get('seasonId')
                            season_name = league_data.get('seasonName', '')
                            league_name = league_data.get('liganame', '')
                            region_name = league_data.get('bezirkName', '')
                            
                            self.logger.info(
                                f'✅ HISTORICAL DATA FOUND: {pattern} -> '
                                f'Season: {season_name} (ID: {season_id}) - '
                                f'League: {league_name} - Region: {region_name}'
                            )
                            
                            # Check if this is a different season than 2025
                            if season_id and season_id != 2025:
                                self.logger.info(f'🎯 DIFFERENT SEASON FOUND: {season_id}!')
                    
                    # Check for arrays of competitions/seasons
                    elif isinstance(data, list):
                        result['array_length'] = len(data)
                        if len(data) > 0 and isinstance(data[0], dict):
                            result['sample_item'] = data[0]
                            self.logger.info(f'📋 Array response with {len(data)} items')
                
                # Sample the data for inspection
                result['data_sample'] = str(data)[:300] + '...' if len(str(data)) > 300 else str(data)
                
            except json.JSONDecodeError:
                # Not JSON, maybe HTML error page
                if '<html' in response.text.lower():
                    result['content_type'] = 'html'
                else:
                    result['content_type'] = 'text'
                    result['content_sample'] = response.text[:200]
        
        yield result
