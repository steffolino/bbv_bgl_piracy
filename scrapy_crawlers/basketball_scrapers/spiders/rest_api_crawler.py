import scrapy
import json
from urllib.parse import urljoin


class RestApiSpider(scrapy.Spider):
    name = 'rest_api_crawler'
    allowed_domains = ['basketball-bund.net']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.2,
    }
    
    def start_requests(self):
        """Test the REST API with different parameters"""
        
        # Test current league from your example
        current_liga_id = '47960'
        
        # Test different API endpoints
        api_endpoints = [
            # Current season data
            f'competition/actual/id/{current_liga_id}',
            
            # Try historical seasons (guessing the pattern)
            f'competition/season/2024/id/{current_liga_id}',
            f'competition/season/2023/id/{current_liga_id}', 
            f'competition/season/2022/id/{current_liga_id}',
            
            # Try different competition IDs (variants around 47960)
            'competition/actual/id/47961',
            'competition/actual/id/47959',
            'competition/actual/id/47950',
            
            # Try to find league listings or hierarchies
            'competition/list',
            'competition/hierarchy',
            'leagues',
            'competitions',
            'season/2024',
            'season/2023',
            
            # Try team-specific endpoints
            'team/142980',  # BBC Bayreuth 3 from the data
            'team/143008',  # TSV Hof
            
            # Try match-specific endpoints  
            'match/2718253',  # A match ID from the data
            
            # Try statistics endpoints
            f'statistics/competition/{current_liga_id}',
            f'statistics/season/2024/competition/{current_liga_id}',
            
            # Try different data types
            f'competition/{current_liga_id}/matches',
            f'competition/{current_liga_id}/table', 
            f'competition/{current_liga_id}/statistics',
        ]
        
        base_url = 'https://www.basketball-bund.net/rest/'
        
        for endpoint in api_endpoints:
            url = urljoin(base_url, endpoint)
            yield scrapy.Request(
                url=url,
                callback=self.parse_api_response,
                meta={
                    'endpoint': endpoint,
                    'expected_json': True
                }
            )
    
    def parse_api_response(self, response):
        """Parse API responses and analyze the data structure"""
        endpoint = response.meta['endpoint']
        
        self.logger.info(f'🔍 Testing endpoint: {endpoint}')
        self.logger.info(f'   Status: {response.status}')
        self.logger.info(f'   Content-Type: {response.headers.get("Content-Type", b"unknown").decode()}')
        self.logger.info(f'   Content length: {len(response.text)} characters')
        
        # Try to parse as JSON
        data = None
        is_json = False
        
        try:
            if response.text.strip():
                data = json.loads(response.text)
                is_json = True
                self.logger.info(f'   ✅ Valid JSON response')
            else:
                self.logger.info(f'   ❌ Empty response')
                
        except json.JSONDecodeError as e:
            self.logger.info(f'   ❌ Invalid JSON: {str(e)[:100]}')
            # Maybe it's HTML or error page
            if '<html' in response.text.lower():
                self.logger.info(f'   📄 HTML response (possibly error page)')
        
        result = {
            'type': 'api_endpoint_test',
            'endpoint': endpoint,
            'url': response.url,
            'status_code': response.status,
            'content_length': len(response.text),
            'is_json': is_json,
            'content_type': response.headers.get('Content-Type', b'unknown').decode()
        }
        
        if is_json and data:
            # Analyze JSON structure
            result.update({
                'json_keys': list(data.keys()) if isinstance(data, dict) else [],
                'json_type': type(data).__name__,
            })
            
            # Look for interesting data patterns
            if isinstance(data, dict):
                # Check for basketball-specific data
                basketball_indicators = []
                
                if 'ligaData' in data:
                    basketball_indicators.append('ligaData')
                if 'matches' in data:
                    basketball_indicators.append('matches')  
                if 'tabelle' in data:
                    basketball_indicators.append('tabelle')
                if 'seasonId' in str(data):
                    basketball_indicators.append('seasonId')
                if 'teamname' in str(data):
                    basketball_indicators.append('teamname')
                    
                result['basketball_indicators'] = basketball_indicators
                
                # Extract key information
                if 'data' in data and isinstance(data['data'], dict):
                    liga_data = data['data'].get('ligaData', {})
                    if liga_data:
                        result['liga_info'] = {
                            'seasonId': liga_data.get('seasonId'),
                            'seasonName': liga_data.get('seasonName'),
                            'ligaId': liga_data.get('ligaId'), 
                            'liganame': liga_data.get('liganame'),
                            'bezirkName': liga_data.get('bezirkName')
                        }
                        
                    # Count matches and teams
                    matches = data['data'].get('matches', [])
                    tabelle = data['data'].get('tabelle', {})
                    
                    result['data_counts'] = {
                        'matches': len(matches) if matches else 0,
                        'table_entries': len(tabelle.get('entries', [])) if tabelle else 0
                    }
                    
                # Sample some data for inspection
                result['data_sample'] = str(data)[:500] + '...' if len(str(data)) > 500 else str(data)
        
        else:
            # For non-JSON responses, sample the content
            result['content_sample'] = response.text[:500] + '...' if len(response.text) > 500 else response.text
        
        # Log successful endpoints
        if response.status == 200 and is_json and data:
            self.logger.info(f'   🎯 SUCCESS: {endpoint} returned valid basketball data!')
            
        yield result
