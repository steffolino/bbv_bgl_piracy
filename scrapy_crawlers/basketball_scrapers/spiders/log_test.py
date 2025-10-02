#!/usr/bin/env python3

import scrapy
import json
import time
from datetime import datetime


class LogTestSpider(scrapy.Spider):
    """
    Test spider to demonstrate enhanced crawl logging capabilities
    """
    name = 'log_test'
    allowed_domains = ['basketball-bund.net']
    
    def start_requests(self):
        """Generate test requests with various scenarios"""
        base_url = 'https://www.basketball-bund.net/rest/competition/actual/id/'
        
        # Test scenarios for logging
        test_cases = [
            # Successful discovery (known working league)
            {'league_id': 47960, 'season': 2024, 'expected': 'success'},
            
            # Non-existent league (404 response)
            {'league_id': 99999, 'season': 2024, 'expected': 'not_found'},
            
            # Another successful case
            {'league_id': 47961, 'season': 2024, 'expected': 'success'},
            
            # Test historical data
            {'league_id': 47958, 'season': 2023, 'expected': 'success'},
        ]
        
        for i, test_case in enumerate(test_cases):
            league_id = test_case['league_id']
            season = test_case['season']
            
            url = f"{base_url}{league_id}"
            
            yield scrapy.Request(
                url=url,
                callback=self.parse_league_data,
                meta={
                    'league_id': league_id,
                    'season': season,
                    'test_case': i + 1,
                    'expected_result': test_case['expected'],
                    'start_time': time.time()
                }
            )
    
    def parse_league_data(self, response):
        """Parse league data and demonstrate logging"""
        league_id = response.meta['league_id']
        season = response.meta['season']
        test_case = response.meta['test_case']
        start_time = response.meta.get('start_time', time.time())
        
        response_time = (time.time() - start_time) * 1000
        
        # Log the response with enhanced details
        self.logger.info(
            f"🧪 TEST CASE {test_case}: League {league_id} ({season}) - "
            f"Status: {response.status}, Time: {response_time:.0f}ms",
            extra={
                'extra_data': {
                    'test_case': test_case,
                    'league_id': league_id,
                    'season_year': season,
                    'response_time_ms': int(response_time),
                    'response_status': response.status
                }
            }
        )
        
        try:
            data = json.loads(response.text)
            
            # Check if this is valid league data
            if self.is_valid_league_response(data):
                match_count = len(data.get('matchList', []))
                league_name = data.get('leagueName', 'Unknown')
                district = data.get('district', {}).get('name', 'Unknown')
                
                self.logger.info(
                    f"✅ DISCOVERY: League {league_id} ({season}) - "
                    f"{match_count} matches, '{league_name}', District: {district}",
                    extra={
                        'extra_data': {
                            'league_id': league_id,
                            'season_year': season,
                            'match_count': match_count,
                            'discovery_type': 'test_success'
                        }
                    }
                )
                
                # Yield structured data
                yield {
                    'league_id': league_id,
                    'season_year': season,
                    'league_name': league_name,
                    'district_name': district,
                    'match_count': match_count,
                    'matches': data.get('matchList', [])[:3],  # First 3 matches only
                    'table': data.get('table', {}),
                    'discovery_phase': 'test_scenario',
                    'data_quality': 'complete' if match_count > 10 else 'partial',
                    'team_count': len(data.get('table', {}).get('standings', [])),
                    'scraped_at': datetime.now().isoformat(),
                    'test_case': test_case,
                    'response_time_ms': int(response_time),
                    'url': response.url
                }
                
            else:
                self.logger.warning(
                    f"⚠️  Empty response for League {league_id} ({season}) - might not exist",
                    extra={
                        'extra_data': {
                            'league_id': league_id,
                            'season_year': season,
                            'discovery_type': 'empty_response'
                        }
                    }
                )
                
        except json.JSONDecodeError as e:
            self.logger.error(
                f"❌ JSON parsing failed for League {league_id} ({season}): {e}",
                extra={
                    'extra_data': {
                        'league_id': league_id,
                        'season_year': season,
                        'error_type': 'json_decode',
                        'response_preview': response.text[:200]
                    }
                }
            )
        
        except Exception as e:
            self.logger.error(
                f"❌ Unexpected error for League {league_id} ({season}): {e}",
                extra={
                    'extra_data': {
                        'league_id': league_id,
                        'season_year': season,
                        'error_type': 'unexpected',
                        'error_message': str(e)
                    }
                }
            )
    
    def is_valid_league_response(self, data):
        """Check if response contains valid league data"""
        if not isinstance(data, dict):
            return False
            
        # Must have matches or table data
        has_matches = bool(data.get('matchList'))
        has_table = bool(data.get('table', {}).get('standings'))
        
        return has_matches or has_table
    
    def closed(self, reason):
        """Log completion with summary"""
        self.logger.info(
            f"🏁 Log test spider completed: {reason}",
            extra={
                'extra_data': {
                    'completion_reason': reason,
                    'test_completed': True
                }
            }
        )
