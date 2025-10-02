import scrapy
import json
from datetime import datetime

class DebugBasketballSpider(scrapy.Spider):
    name = 'debug_basketball'
    allowed_domains = ['basketball-bund.net']
    start_urls = ['https://www.basketball-bund.net/']
    
    def parse(self, response):
        """Debug the REST API structure"""
        self.logger.info('🔍 Starting API debug session...')
        
        # Test 1: Empty POST to see what parameters are expected
        yield scrapy.Request(
            url='https://www.basketball-bund.net/rest/wam/data',
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({}),
            callback=self.debug_empty_post,
            meta={'test': 'empty_post'}
        )
        
        # Test 2: Try different parameter combinations
        test_payloads = [
            {"verbandIds": []},
            {"gebietIds": []},
            {"verbandIds": [], "gebietIds": []},
            {"verbandIds": [1, 2, 3]},
            {"gebietIds": ["1_", "2_", "3_"]},
            {"verbandIds": [2], "gebietIds": ["5_"]},
            # Try without the underscore
            {"verbandIds": [2], "gebietIds": [5]},
            # Try string format
            {"verbandIds": ["2"], "gebietIds": ["5_"]},
        ]
        
        for i, payload in enumerate(test_payloads):
            yield scrapy.Request(
                url='https://www.basketball-bund.net/rest/wam/data',
                method='POST',
                headers={'Content-Type': 'application/json'},
                body=json.dumps(payload),
                callback=self.debug_payload_response,
                meta={'test': f'payload_{i}', 'payload': payload}
            )
    
    def debug_empty_post(self, response):
        """Debug empty POST response"""
        try:
            data = json.loads(response.text)
            self.logger.info(f'📋 Empty POST Response:')
            self.logger.info(f'   Status: {response.status}')
            self.logger.info(f'   Keys: {list(data.keys()) if isinstance(data, dict) else "Not dict"}')
            self.logger.info(f'   Message: {data.get("message", "No message")}')
            self.logger.info(f'   Data: {data.get("data", "No data")}')
            
            # Log first 500 chars of response for analysis
            self.logger.info(f'   Full Response (truncated): {response.text[:500]}...')
            
        except json.JSONDecodeError:
            self.logger.error(f'❌ Empty POST - Not JSON: {response.text[:200]}')
    
    def debug_payload_response(self, response):
        """Debug payload responses"""
        payload = response.meta['payload']
        test_name = response.meta['test']
        
        try:
            data = json.loads(response.text)
            
            # Check if this payload returned leagues
            leagues_count = 0
            if isinstance(data.get('data'), list):
                leagues_count = len(data['data'])
            elif isinstance(data.get('data'), dict) and 'leagues' in data['data']:
                leagues_count = len(data['data']['leagues'])
            elif 'leagues' in data:
                leagues_count = len(data['leagues'])
            
            self.logger.info(f'🧪 Test {test_name}:')
            self.logger.info(f'   Payload: {payload}')
            self.logger.info(f'   Status: {response.status}')
            self.logger.info(f'   Leagues found: {leagues_count}')
            self.logger.info(f'   Message: {data.get("message", "No message")}')
            
            # If we found leagues, log details
            if leagues_count > 0:
                self.logger.info(f'   🎉 SUCCESS! Found {leagues_count} leagues with payload: {payload}')
                
                # Extract some league details for verification
                leagues_data = data.get('data', [])
                if isinstance(leagues_data, dict) and 'leagues' in leagues_data:
                    leagues_data = leagues_data['leagues']
                elif not isinstance(leagues_data, list):
                    leagues_data = data.get('leagues', [])
                
                for i, league in enumerate(leagues_data[:3]):  # Show first 3 leagues
                    league_name = league.get('name') or league.get('title') or f'League {i}'
                    liga_id = league.get('ligaId') or league.get('id')
                    season_id = league.get('seasonId') or league.get('season')
                    self.logger.info(f'   League {i+1}: {league_name} (Liga: {liga_id}, Season: {season_id})')
            
        except json.JSONDecodeError:
            self.logger.error(f'❌ {test_name} - Not JSON: {response.text[:200]}')
    
    # Also test some direct URLs that might work
    def start_requests(self):
        """Override to add more test requests"""
        # First do the main parse
        yield scrapy.Request('https://www.basketball-bund.net/', self.parse)
        
        # Test some direct REST endpoints that might work
        test_urls = [
            'https://www.basketball-bund.net/rest/leagues',
            'https://www.basketball-bund.net/rest/seasons',
            'https://www.basketball-bund.net/rest/teams',
            'https://www.basketball-bund.net/rest/wam/leagues',
            'https://www.basketball-bund.net/rest/wam/data?verbandIds=2&gebietIds=5_',
            'https://www.basketball-bund.net/rest/wam/data?verbandIds=1',
        ]
        
        for url in test_urls:
            yield scrapy.Request(
                url=url,
                callback=self.debug_direct_url,
                meta={'test_url': url}
            )
