import scrapy
import json
from urllib.parse import urljoin


class RestHistoricalTestSpider(scrapy.Spider):
    name = 'rest_historical_test'
    allowed_domains = ['basketball-bund.net']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.2,
    }
    
    def start_requests(self):
        """Test REST API for historical season data"""
        
        # Known working current league IDs
        working_league_ids = [
            '47960',  # Oberfranken District League Men  
            '47961',  # Oberfranken District League Women
            '47959',  # Oberfranken District Cup Women
            '51020',  # NBBL A
        ]
        
        # Test different historical season patterns
        season_patterns = [
            # Direct season endpoints (most likely)
            'competition/season/{season}/id/{league_id}',
            
            # League with season parameter
            'competition/id/{league_id}/season/{season}', 
            'competition/{league_id}/season/{season}',
            
            # Archive endpoints
            'competition/archive/{league_id}/season/{season}',
            'archive/competition/{league_id}/season/{season}',
            
            # Historical endpoints
            'competition/historical/{league_id}/{season}',
            'historical/competition/{season}/id/{league_id}',
            
            # Season-specific competition IDs (maybe they increment by season)
            'competition/actual/id/{adjusted_league_id}',
        ]
        
        # Test seasons (going back from current 2025)
        test_seasons = ['2024', '2023', '2022', '2021', '2020']
        
        base_url = 'https://www.basketball-bund.net/rest/'
        
        for league_id in working_league_ids:
            for season in test_seasons:
                for pattern in season_patterns:
                    
                    # For adjusted league IDs, try different calculations
                    if 'adjusted_league_id' in pattern:
                        # Try subtracting increments (maybe each season is -1000?)
                        season_offset = 2025 - int(season)
                        adjustments = [
                            int(league_id) - (season_offset * 1000),  # -1000 per season
                            int(league_id) - (season_offset * 100),   # -100 per season  
                            int(league_id) - (season_offset * 10),    # -10 per season
                            int(league_id) - season_offset,           # -1 per season
                        ]
                        
                        for adjusted_id in adjustments:
                            if adjusted_id > 0:  # Only positive IDs
                                endpoint = pattern.format(adjusted_league_id=adjusted_id)
                                url = urljoin(base_url, endpoint)
                                
                                yield scrapy.Request(
                                    url=url,
                                    callback=self.parse_historical_response,
                                    meta={
                                        'original_league_id': league_id,
                                        'season': season,
                                        'pattern': pattern,
                                        'adjusted_id': adjusted_id,
                                        'test_type': 'adjusted_id'
                                    },
                                    dont_filter=True
                                )
                    else:
                        # Normal pattern substitution
                        endpoint = pattern.format(league_id=league_id, season=season)
                        url = urljoin(base_url, endpoint)
                        
                        yield scrapy.Request(
                            url=url,
                            callback=self.parse_historical_response,
                            meta={
                                'original_league_id': league_id,
                                'season': season, 
                                'pattern': pattern,
                                'test_type': 'direct_pattern'
                            },
                            dont_filter=True
                        )

    def parse_historical_response(self, response):
        """Parse responses from historical API tests"""
        original_league_id = response.meta['original_league_id']
        season = response.meta['season']
        pattern = response.meta['pattern']
        test_type = response.meta['test_type']
        
        status_code = response.status
        content_length = len(response.text)
        
        # Try to parse JSON
        json_data = None
        is_valid_json = False
        basketball_data_found = False
        
        if status_code == 200:
            try:
                json_data = json.loads(response.text)
                is_valid_json = True
                
                # Check if it contains basketball data
                if isinstance(json_data, dict):
                    data_section = json_data.get('data', {})
                    
                    if isinstance(data_section, dict):
                        league_data = data_section.get('league_data', {})
                        matches = data_section.get('matches', [])
                        table = data_section.get('table', {})
                        
                        # Check if this looks like real basketball data
                        if league_data or matches or table:
                            basketball_data_found = True
                            
                            # Extract season info from the data
                            found_season_id = league_data.get('season_id') if league_data else None
                            found_season_name = league_data.get('season_name') if league_data else None
                            found_league_name = league_data.get('league_name', '')
                            found_district = league_data.get('district_name', '')
                            
                            result = {
                                'type': 'historical_data_found',
                                'url': response.url,
                                'original_league_id': original_league_id,
                                'requested_season': season,
                                'pattern': pattern,
                                'test_type': test_type,
                                'found_season_id': found_season_id,
                                'found_season_name': found_season_name,
                                'found_league_name': found_league_name,
                                'found_district': found_district,
                                'matches_count': len(matches) if matches else 0,
                                'table_entries_count': len(table.get('entries', [])) if isinstance(table, dict) else 0,
                                'content_length': content_length
                            }
                            
                            # Log successful discovery
                            self.logger.info(
                                f'🎯 HISTORICAL DATA FOUND: {found_league_name} ({found_district}) - '
                                f'Season: {found_season_name} (ID: {found_season_id}) - '
                                f'Pattern: {pattern} - Matches: {len(matches) if matches else 0}'
                            )
                            
                            yield result
                            
                            # If this is historical data, also try to get detailed information
                            if found_season_id and int(found_season_id) < 2025:
                                detailed_data = self.extract_detailed_data(response, result)
                                if detailed_data:
                                    yield detailed_data
                            
            except json.JSONDecodeError:
                pass  # Not valid JSON, skip
        
        # Always log unsuccessful attempts for debugging  
        if not basketball_data_found:
            result = {
                'type': 'historical_test_result',
                'url': response.url,
                'original_league_id': original_league_id,
                'requested_season': season,
                'pattern': pattern,
                'test_type': test_type,
                'status_code': status_code,
                'content_length': content_length,
                'is_valid_json': is_valid_json,
                'basketball_data_found': False
            }
            
            # Only log interesting failures (200 responses that don't have data)
            if status_code == 200 and is_valid_json:
                self.logger.info(f'❌ No basketball data: {pattern} - Season: {season} - League: {original_league_id}')
            
            yield result

    def extract_detailed_data(self, response, basic_info):
        """Extract detailed information from confirmed historical data"""
        try:
            json_data = json.loads(response.text)
            data_section = json_data.get('data', {})
            
            # Extract comprehensive match data
            matches = data_section.get('matches', [])
            match_details = []
            
            for match in matches[:5]:  # Sample first 5 matches
                if isinstance(match, dict):
                    match_detail = {
                        'match_id': match.get('match_id'),
                        'match_day': match.get('match_day'),
                        'kickoff_date': match.get('kickoff_date'),
                        'kickoff_time': match.get('kickoff_time'),
                        'home_team': match.get('home_team', {}).get('team_name') if match.get('home_team') else None,
                        'guest_team': match.get('guest_team', {}).get('team_name') if match.get('guest_team') else None,
                        'result': match.get('result'),
                        'has_result': bool(match.get('result'))
                    }
                    match_details.append(match_detail)
            
            # Extract table data
            table = data_section.get('table', {})
            table_entries = []
            
            if isinstance(table, dict) and 'entries' in table:
                for entry in table['entries'][:5]:  # Sample first 5 teams
                    if isinstance(entry, dict):
                        team_entry = {
                            'rank': entry.get('rank'),
                            'team_name': entry.get('team', {}).get('team_name') if entry.get('team') else None,
                            'games_played': entry.get('games_played'),
                            'wins': entry.get('wins'),
                            'losses': entry.get('losses'),
                            'points_for': entry.get('points_for'),
                            'points_against': entry.get('points_against')
                        }
                        table_entries.append(team_entry)
            
            return {
                'type': 'detailed_historical_data',
                'basic_info': basic_info,
                'match_sample': match_details,
                'table_sample': table_entries,
                'total_matches': len(matches),
                'total_teams': len(table.get('entries', [])) if isinstance(table, dict) else 0
            }
            
        except (json.JSONDecodeError, KeyError, AttributeError):
            return None
