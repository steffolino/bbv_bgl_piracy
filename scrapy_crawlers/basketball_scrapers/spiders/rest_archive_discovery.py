import scrapy
import json


class RestArchiveDiscoverySpider(scrapy.Spider):
    name = 'rest_archive_discovery'
    allowed_domains = ['basketball-bund.net']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.3,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.1,
    }
    
    def start_requests(self):
        """Test systematic ranges to find historical league IDs"""
        
        # Current season IDs we know work: 47959, 47960, 47961
        # Let's test ranges around these and in different thousands
        
        base_ranges = [
            # Around current season (47xxx)
            range(47900, 48000, 5),  # Every 5th ID around current
            
            # Previous thousands (might be previous seasons)
            range(46900, 47000, 10),  # 2024 season?
            range(45900, 46000, 10),  # 2023 season?
            range(44900, 45000, 10),  # 2022 season?
            
            # Much lower ranges (older data)
            range(17000, 17500, 25),  # Around the original 17248
            range(51000, 51100, 10),  # Around the original 51819
        ]
        
        # Test all these IDs
        for range_set in base_ranges:
            for liga_id in range_set:
                url = f'https://www.basketball-bund.net/rest/competition/actual/id/{liga_id}'
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_league_response,
                    meta={'liga_id': liga_id, 'endpoint_type': 'current'},
                    dont_filter=True,
                    errback=self.handle_error
                )
    
    def parse_league_response(self, response):
        """Parse successful league responses"""
        liga_id = response.meta['liga_id']
        endpoint_type = response.meta['endpoint_type']
        
        if response.status != 200:
            return
            
        try:
            data = json.loads(response.text)
            
            if 'data' in data and 'ligaData' in data['data']:
                liga_data = data['data']['ligaData']
                
                # Extract key information
                season_id = liga_data.get('seasonId')
                season_name = liga_data.get('seasonName')
                liga_name = liga_data.get('liganame')
                bezirk_name = liga_data.get('bezirkName')
                
                # Count data
                matches = data['data'].get('matches', [])
                tabelle = data['data'].get('tabelle', {})
                table_entries = len(tabelle.get('entries', [])) if tabelle else 0
                
                result = {
                    'type': 'working_league',
                    'liga_id': liga_id,
                    'season_id': season_id,
                    'season_name': season_name,
                    'liga_name': liga_name,
                    'bezirk_name': bezirk_name,
                    'matches_count': len(matches),
                    'teams_count': table_entries,
                    'url': response.url,
                    'endpoint_type': endpoint_type
                }
                
                # Log discovery
                self.logger.info(
                    f'✅ FOUND: ID {liga_id} - {liga_name} ({bezirk_name}) - '
                    f'Season: {season_name} - Matches: {len(matches)} - Teams: {table_entries}'
                )
                
                yield result
                
                # If this is Oberfranken (our target region), explore more
                if bezirk_name and 'oberfranken' in bezirk_name.lower():
                    self.logger.info(f'🎯 Oberfranken league found: {liga_id}')
                    
                    # Try to find historical versions of this league
                    # Maybe they use different patterns for historical data
                    historical_patterns = [
                        f'competition/season/2024/id/{liga_id}',
                        f'competition/history/{liga_id}',
                        f'competition/archive/{liga_id}',
                        f'competition/{liga_id}/seasons',
                    ]
                    
                    for pattern in historical_patterns:
                        historical_url = f'https://www.basketball-bund.net/rest/{pattern}'
                        yield scrapy.Request(
                            url=historical_url,
                            callback=self.parse_historical_response,
                            meta={
                                'liga_id': liga_id,
                                'liga_name': liga_name,
                                'pattern': pattern
                            },
                            dont_filter=True
                        )
                
        except json.JSONDecodeError:
            pass  # Skip invalid JSON
    
    def parse_historical_response(self, response):
        """Parse potential historical data endpoints"""
        liga_id = response.meta['liga_id']
        liga_name = response.meta['liga_name']
        pattern = response.meta['pattern']
        
        if response.status == 200:
            try:
                data = json.loads(response.text)
                
                result = {
                    'type': 'historical_endpoint',
                    'liga_id': liga_id,
                    'liga_name': liga_name,
                    'pattern': pattern,
                    'url': response.url,
                    'status_code': response.status,
                    'data_keys': list(data.keys()) if isinstance(data, dict) else [],
                    'content_length': len(response.text)
                }
                
                self.logger.info(f'🏛️ Historical endpoint works: {pattern} for league {liga_id}')
                yield result
                
            except json.JSONDecodeError:
                pass
    
    def handle_error(self, failure):
        """Handle request failures silently"""
        pass  # Most will be 404s, which is expected
