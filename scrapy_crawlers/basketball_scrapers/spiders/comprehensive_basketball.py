import scrapy
import json
from datetime import datetime
import re

class ComprehensiveBasketballSpider(scrapy.Spider):
    name = 'comprehensive_basketball'
    allowed_domains = ['basketball-bund.net']
    
    # Start with REST API discovery
    start_urls = ['https://www.basketball-bund.net/']
    
    # Configuration - can be set via spider arguments
    target_verband_ids = [2]  # Bayern
    target_gebiet_ids = ["5_"]  # Oberfranken
    max_leagues_to_process = 3  # Limit for testing
    max_matches_per_league = 5  # Limit for testing
    
    def parse(self, response):
        """Start with REST API discovery for current seasons"""
        self.logger.info('🏀 Starting comprehensive basketball stats crawling...')
        
        # Step 1: Discover leagues via REST API
        yield scrapy.Request(
            url='https://www.basketball-bund.net/rest/wam/data',
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({
                "verbandIds": self.target_verband_ids,
                "gebietIds": self.target_gebiet_ids
            }),
            callback=self.parse_rest_discovery,
            errback=self.handle_rest_error,
            meta={'step': 'discovery'}
        )
        
        # Step 2: Also try HTML discovery as fallback
        yield scrapy.Request(
            url='https://www.basketball-bund.net/',
            callback=self.parse_html_discovery,
            meta={'step': 'html_discovery'}
        )
    
    def parse_rest_discovery(self, response):
        """Parse REST API discovery response"""
        try:
            data = json.loads(response.text)
            self.logger.info(f'✅ REST Discovery: found data with keys: {list(data.keys())}')
            
            # Extract league information from the correct API structure
            leagues = []
            if 'data' in data and isinstance(data['data'], dict):
                liga_liste = data['data'].get('ligaListe', {})
                if 'ligen' in liga_liste:
                    leagues = liga_liste['ligen']
                    self.logger.info(f'📊 Found {len(leagues)} leagues in data.ligaListe.ligen')
                else:
                    self.logger.info(f'📊 No ligaListe.ligen found. Available keys in data: {list(data["data"].keys())}')
            
            if not leagues:
                self.logger.warning('❌ No leagues found in expected structure')
                return
            
            processed_count = 0
            for league in leagues:
                if processed_count >= self.max_leagues_to_process:
                    break
                    
                liga_id = league.get('ligaId')
                # For current API, we need to determine season - let's use current year as default
                season_id = league.get('seasonId') or '2025'  # Default to current year
                league_name = league.get('liganame') or f'League {liga_id}'
                
                if liga_id:
                    self.logger.info(f'🏆 Processing: {league_name} (Liga: {liga_id}, Season: {season_id})')
                    
                    # Current season: Use REST API
                    yield from self.crawl_current_season_rest(liga_id, season_id, league_name)
                    
                    # Archive: Use HTML endpoints
                    yield from self.crawl_archive_html(liga_id, season_id, league_name)
                    
                    processed_count += 1
                        
        except json.JSONDecodeError as e:
            self.logger.error(f'❌ Failed to parse REST discovery JSON: {e}')
            self.logger.info(f'Response text: {response.text[:500]}')
    
    def crawl_current_season_rest(self, liga_id, season_id, league_name):
        """Crawl current season data using REST API"""
        
        # Get matches list
        matches_url = f'https://www.basketball-bund.net/rest/liga/id/{liga_id}/season/{season_id}/matches'
        yield scrapy.Request(
            url=matches_url,
            callback=self.parse_rest_matches,
            meta={
                'liga_id': liga_id,
                'season_id': season_id,
                'league_name': league_name,
                'source': 'REST_CURRENT',
                'step': 'matches'
            },
            errback=self.handle_rest_error
        )
    
    def crawl_archive_html(self, liga_id, season_id, league_name):
        """Crawl archive data using HTML endpoints"""
        
        # Team statistics (season aggregates)
        yield scrapy.Request(
            url=f'https://www.basketball-bund.net/statistik.do?reqCode=statTeamArchiv&liga_id={liga_id}&saison_id={season_id}',
            callback=self.parse_team_statistics,
            meta={
                'liga_id': liga_id,
                'season_id': season_id,
                'league_name': league_name,
                'source': 'HTML_ARCHIVE',
                'step': 'team_stats'
            }
        )
        
        # Player statistics (various types)
        stats_configs = [
            ('statBesteWerferArchiv', 'top_scorers'),
            ('statBesteFreiWerferArchiv', 'top_free_throw'),
            ('statBeste3erWerferArchiv', 'top_three_point')
        ]
        
        for req_code, stat_type in stats_configs:
            yield scrapy.Request(
                url=f'https://www.basketball-bund.net/statistik.do?reqCode={req_code}&liga_id={liga_id}&saison_id={season_id}&_top=-1',
                callback=self.parse_player_statistics,
                meta={
                    'liga_id': liga_id,
                    'season_id': season_id,
                    'league_name': league_name,
                    'stat_type': stat_type,
                    'source': 'HTML_ARCHIVE',
                    'step': 'player_stats'
                }
            )
        
        # League table
        yield scrapy.Request(
            url=f'https://www.basketball-bund.net/index.jsp?Action=107&liga_id={liga_id}&saison_id={season_id}',
            callback=self.parse_league_table,
            meta={
                'liga_id': liga_id,
                'season_id': season_id,
                'league_name': league_name,
                'source': 'HTML_ARCHIVE',
                'step': 'league_table'
            }
        )
    
    def parse_rest_matches(self, response):
        """Parse matches from REST API"""
        try:
            matches_data = json.loads(response.text)
            matches = matches_data if isinstance(matches_data, list) else matches_data.get('matches', [])
            
            meta = response.meta
            self.logger.info(f'🏀 Found {len(matches)} matches for {meta["league_name"]}')
            
            processed_matches = 0
            for match in matches:
                if processed_matches >= self.max_matches_per_league:
                    break
                    
                match_id = match.get('matchId') or match.get('id')
                if match_id:
                    # Get detailed match info
                    match_url = f'https://www.basketball-bund.net/rest/match/id/{match_id}/matchInfo'
                    yield scrapy.Request(
                        url=match_url,
                        callback=self.parse_rest_match_details,
                        meta={
                            **meta,
                            'match_id': match_id,
                            'match_basic_data': match,
                            'step': 'match_details'
                        }
                    )
                    processed_matches += 1
                    
        except json.JSONDecodeError as e:
            self.logger.error(f'❌ Failed to parse matches JSON: {e}')
    
    def parse_rest_match_details(self, response):
        """Parse detailed match info from REST API"""
        try:
            match_info = json.loads(response.text)
            meta = response.meta
            
            # Extract basic match data
            match_item = {
                'type': 'match',
                'source': meta['source'],
                'match_id': meta['match_id'],
                'liga_id': meta['liga_id'],
                'season_id': meta['season_id'],
                'league_name': meta['league_name'],
                'date': match_info.get('date'),
                'home_team': self.extract_team_name(match_info.get('homeTeam')),
                'guest_team': self.extract_team_name(match_info.get('guestTeam')),
                'home_score': match_info.get('homeScore'),
                'guest_score': match_info.get('guestScore'),
                'status': match_info.get('status'),
                'has_boxscore': match_info.get('matchBoxscore') is not None,
                'scraped_at': datetime.now().isoformat()
            }
            
            yield match_item
            
            # Extract boxscore if available
            if match_info.get('matchBoxscore'):
                yield from self.extract_boxscore_data(match_info['matchBoxscore'], meta)
                
            # Try to get legacy boxscore via HTML if we can find spielplan_id
            yield from self.try_legacy_boxscore(match_info, meta)
                
        except json.JSONDecodeError as e:
            self.logger.error(f'❌ Failed to parse match details: {e}')
    
    def extract_team_name(self, team_data):
        """Extract team name from various possible structures"""
        if not team_data:
            return None
        if isinstance(team_data, str):
            return team_data
        return team_data.get('name') or team_data.get('title') or str(team_data)
    
    def extract_boxscore_data(self, boxscore, meta):
        """Extract player statistics from REST boxscore"""
        for team_key in ['homeTeam', 'guestTeam']:
            team_stats = boxscore.get(team_key, {})
            players = team_stats.get('players', [])
            
            for player in players:
                player_item = {
                    'type': 'player_boxscore',
                    'source': meta['source'],
                    'match_id': meta['match_id'],
                    'liga_id': meta['liga_id'],
                    'season_id': meta['season_id'],
                    'league_name': meta['league_name'],
                    'team_side': team_key,
                    'player_name': player.get('name'),
                    'player_id': player.get('playerId'),
                    'jersey_number': player.get('jerseyNumber'),
                    'position': player.get('position'),
                    'points': self.safe_int(player.get('points')),
                    'rebounds': self.safe_int(player.get('rebounds')),
                    'assists': self.safe_int(player.get('assists')),
                    'field_goals_made': self.safe_int(player.get('fieldGoalsMade')),
                    'field_goals_attempted': self.safe_int(player.get('fieldGoalsAttempted')),
                    'three_pointers_made': self.safe_int(player.get('threePointersMade')),
                    'three_pointers_attempted': self.safe_int(player.get('threePointersAttempted')),
                    'free_throws_made': self.safe_int(player.get('freeThrowsMade')),
                    'free_throws_attempted': self.safe_int(player.get('freeThrowsAttempted')),
                    'minutes_played': player.get('minutesPlayed'),
                    'fouls': self.safe_int(player.get('fouls')),
                    'turnovers': self.safe_int(player.get('turnovers')),
                    'steals': self.safe_int(player.get('steals')),
                    'blocks': self.safe_int(player.get('blocks')),
                    'scraped_at': datetime.now().isoformat()
                }
                yield player_item
    
    def try_legacy_boxscore(self, match_info, meta):
        """Try to find and scrape legacy boxscore data"""
        # Look for spielplan_id in match_info
        spielplan_id = match_info.get('spielplan_id') or match_info.get('legacyId')
        
        if spielplan_id:
            legacy_url = f'https://www.basketball-bund.net/scouting.do?reqCode=spielStatistik&spielplan_id={spielplan_id}'
            yield scrapy.Request(
                url=legacy_url,
                callback=self.parse_legacy_boxscore,
                meta={
                    **meta,
                    'spielplan_id': spielplan_id,
                    'step': 'legacy_boxscore'
                }
            )
    
    def parse_legacy_boxscore(self, response):
        """Parse legacy HTML boxscore"""
        meta = response.meta
        
        # Extract tables from legacy boxscore page
        tables = response.css('table')
        
        for table_idx, table in enumerate(tables):
            rows = table.css('tr')
            if len(rows) < 2:
                continue
                
            # Try to identify if this is a player stats table
            headers = [h.strip() for h in rows[0].css('th::text, td::text').getall() if h.strip()]
            
            # Look for typical basketball stat headers
            if any(keyword in ' '.join(headers).lower() for keyword in ['punkte', 'points', 'rebounds', 'assists']):
                for row_idx, row in enumerate(rows[1:]):
                    cells = [c.strip() for c in row.css('td::text').getall() if c.strip()]
                    
                    if len(cells) >= 3:  # At least player name + some stats
                        legacy_player_item = {
                            'type': 'legacy_player_boxscore',
                            'source': 'HTML_LEGACY',
                            'spielplan_id': meta.get('spielplan_id'),
                            'match_id': meta.get('match_id'),
                            'liga_id': meta['liga_id'],
                            'season_id': meta['season_id'],
                            'league_name': meta['league_name'],
                            'table_index': table_idx,
                            'row_index': row_idx,
                            'headers': headers,
                            'data': cells,
                            'scraped_at': datetime.now().isoformat()
                        }
                        yield legacy_player_item
    
    def parse_team_statistics(self, response):
        """Parse team statistics from HTML archive"""
        meta = response.meta
        self.logger.info(f'📊 Parsing team statistics: {meta["league_name"]}')
        
        tables = response.css('table')
        
        for table_idx, table in enumerate(tables):
            yield from self.parse_statistics_table(
                table, meta, 'team_statistics', table_idx
            )
    
    def parse_player_statistics(self, response):
        """Parse player statistics from HTML archive"""
        meta = response.meta
        stat_type = meta['stat_type']
        self.logger.info(f'🏀 Parsing {stat_type}: {meta["league_name"]}')
        
        tables = response.css('table')
        
        for table_idx, table in enumerate(tables):
            yield from self.parse_statistics_table(
                table, meta, 'player_statistics', table_idx
            )
    
    def parse_league_table(self, response):
        """Parse league standings table"""
        meta = response.meta
        self.logger.info(f'🏆 Parsing league table: {meta["league_name"]}')
        
        tables = response.css('table')
        
        for table_idx, table in enumerate(tables):
            yield from self.parse_statistics_table(
                table, meta, 'league_standings', table_idx
            )
    
    def parse_statistics_table(self, table, meta, data_type, table_idx):
        """Generic table parser for statistics"""
        rows = table.css('tr')
        if len(rows) < 2:
            return
            
        # Extract headers
        headers = [h.strip() for h in rows[0].css('th::text, td::text').getall() if h.strip()]
        
        if not headers:
            return
            
        # Extract data rows
        for row_idx, row in enumerate(rows[1:]):
            cells = [c.strip() for c in row.css('td::text').getall() if c.strip()]
            
            if len(cells) >= len(headers) * 0.5:  # At least half the headers have data
                item = {
                    'type': data_type,
                    'source': meta['source'],
                    'liga_id': meta['liga_id'],
                    'season_id': meta['season_id'],
                    'league_name': meta['league_name'],
                    'table_index': table_idx,
                    'row_index': row_idx,
                    'headers': headers,
                    'data': cells,
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Add stat_type if available
                if 'stat_type' in meta:
                    item['stat_type'] = meta['stat_type']
                    
                yield item
    
    def parse_html_discovery(self, response):
        """Fallback HTML discovery"""
        self.logger.info('🔍 HTML Discovery fallback...')
        
        # Look for league links
        league_links = response.css('a[href*="liga"], a[href*="Action=107"]')
        
        for link in league_links[:5]:  # Limit for testing
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            
            if href:
                self.logger.info(f'Found league link: {text} -> {href}')
                
                # Try to extract liga_id and saison_id from URL
                liga_match = re.search(r'liga_id=(\d+)', href)
                season_match = re.search(r'saison_id=(\d+)', href)
                
                if liga_match and season_match:
                    liga_id = liga_match.group(1)
                    season_id = season_match.group(1)
                    league_name = text or f'League {liga_id}'
                    
                    self.logger.info(f'Discovered via HTML: {league_name} (Liga: {liga_id}, Season: {season_id})')
                    
                    # Crawl this league
                    yield from self.crawl_archive_html(liga_id, season_id, league_name)
    
    def handle_rest_error(self, failure):
        """Handle REST API errors"""
        self.logger.error(f'❌ REST API Error: {failure}')
        
        # Log the actual HTTP response if available
        if hasattr(failure.value, 'response'):
            response = failure.value.response
            self.logger.error(f'HTTP {response.status}: {response.url}')
            if response.text:
                self.logger.error(f'Response: {response.text[:200]}')
    
    def safe_int(self, value):
        """Safely convert value to int"""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
