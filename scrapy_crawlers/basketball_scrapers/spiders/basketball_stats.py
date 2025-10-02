import scrapy
import json
from datetime import datetime
from ..items import PlayerStatsItem, MatchItem, TeamItem


class BasketballStatsSpider(scrapy.Spider):
    name = 'basketball_stats'
    allowed_domains = ['www.basketball-bund.net']
    
    # Base URLs based on your COPILOT.md
    base_urls = {
        'api': 'https://www.basketball-bund.net/rest/wam/data',
        'matches': 'https://www.basketball-bund.net/rest/liga/id/{liga_id}/season/{season_id}/matches',
        'stats': 'https://www.basketball-bund.net/statistik.do',
        'scouting': 'https://www.basketball-bund.net/scouting.do'
    }
    
    def start_requests(self):
        """Generate initial requests"""
        # Start with discovering available leagues/seasons
        discovery_urls = [
            'https://www.basketball-bund.net/rest/wam/data',
            'https://www.basketball-bund.net/',
        ]
        
        for url in discovery_urls:
            yield scrapy.Request(
                url=url, 
                callback=self.parse_discovery,
                meta={'source': 'discovery'}
            )
    
    def parse_discovery(self, response):
        """Parse main pages to discover available data"""
        self.logger.info(f"Parsing discovery page: {response.url}")
        
        if response.status != 200:
            self.logger.warning(f"Failed to fetch {response.url}: {response.status}")
            return
            
        # Try to find league/season information
        # Look for links or data that might contain league IDs
        
        # Check if it's JSON response
        try:
            data = json.loads(response.text)
            self.logger.info(f"Found JSON data structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            
            # Process JSON data here if needed
            if isinstance(data, dict) and 'leagues' in data:
                for league in data.get('leagues', []):
                    yield self.request_league_data(league)
                    
        except json.JSONDecodeError:
            # It's HTML, parse for links and information
            self.parse_html_discovery(response)
    
    def parse_html_discovery(self, response):
        """Parse HTML to find basketball data links"""
        self.logger.info(f"Parsing HTML discovery for: {response.url}")
        
        # Look for league links or match links
        league_links = response.css('a[href*="liga"]::attr(href)').getall()
        match_links = response.css('a[href*="spiel"]::attr(href)').getall()
        stats_links = response.css('a[href*="statistik"]::attr(href)').getall()
        
        self.logger.info(f"Found {len(league_links)} league links, {len(match_links)} match links, {len(stats_links)} stats links")
        
        # Follow promising links
        for link in league_links[:5]:  # Limit to first 5 to avoid overwhelming
            if link.startswith('/'):
                link = response.urljoin(link)
            yield scrapy.Request(url=link, callback=self.parse_league_page)
            
        for link in stats_links[:3]:  # Follow some stats links
            if link.startswith('/'):
                link = response.urljoin(link)
            yield scrapy.Request(url=link, callback=self.parse_stats_page)
    
    def request_league_data(self, league_info):
        """Generate request for specific league data"""
        if isinstance(league_info, dict):
            liga_id = league_info.get('id')
            season_id = league_info.get('season_id', '2024')
        else:
            liga_id = league_info
            season_id = '2024'
            
        if liga_id:
            url = self.base_urls['matches'].format(liga_id=liga_id, season_id=season_id)
            return scrapy.Request(
                url=url,
                callback=self.parse_matches,
                meta={'liga_id': liga_id, 'season_id': season_id}
            )
    
    def parse_league_page(self, response):
        """Parse individual league pages"""
        self.logger.info(f"Parsing league page: {response.url}")
        
        # Extract team information
        team_names = response.css('.team-name::text').getall()
        team_links = response.css('a[href*="team"]::attr(href)').getall()
        
        for i, name in enumerate(team_names):
            team_item = TeamItem()
            team_item['name'] = name.strip()
            team_item['source_url'] = response.url
            if i < len(team_links):
                team_item['team_id'] = self.extract_id_from_url(team_links[i])
            yield team_item
            
        # Look for match links on this page
        match_links = response.css('a[href*="spiel"]::attr(href)').getall()
        for link in match_links[:10]:  # Limit to avoid too many requests
            if link.startswith('/'):
                link = response.urljoin(link)
            yield scrapy.Request(url=link, callback=self.parse_match_page)
    
    def parse_matches(self, response):
        """Parse match data from API or HTML"""
        self.logger.info(f"Parsing matches: {response.url}")
        
        try:
            # Try JSON first
            matches_data = json.loads(response.text)
            if isinstance(matches_data, list):
                for match_data in matches_data:
                    yield self.create_match_item(match_data, response)
            elif isinstance(matches_data, dict) and 'matches' in matches_data:
                for match_data in matches_data['matches']:
                    yield self.create_match_item(match_data, response)
        except json.JSONDecodeError:
            # Parse HTML matches
            yield from self.parse_html_matches(response)
    
    def parse_html_matches(self, response):
        """Parse match data from HTML"""
        match_rows = response.css('.match-row, .game-row, tr[class*="match"], tr[class*="game"]')
        
        for row in match_rows:
            match_item = MatchItem()
            
            # Extract match data from HTML structure
            # This will need to be adapted based on actual HTML structure
            match_item['home_team'] = row.css('.home-team::text, .team-home::text').get()
            match_item['away_team'] = row.css('.away-team::text, .team-away::text').get()
            match_item['home_score'] = row.css('.home-score::text, .score-home::text').get()
            match_item['away_score'] = row.css('.away-score::text, .score-away::text').get()
            match_item['date'] = row.css('.match-date::text, .game-date::text').get()
            match_item['source_url'] = response.url
            
            if match_item['home_team'] and match_item['away_team']:
                yield match_item
    
    def create_match_item(self, match_data, response):
        """Create MatchItem from JSON data"""
        match_item = MatchItem()
        match_item['match_id'] = match_data.get('id', match_data.get('match_id'))
        match_item['home_team'] = match_data.get('home_team', match_data.get('homeTeam'))
        match_item['away_team'] = match_data.get('away_team', match_data.get('awayTeam'))
        match_item['home_score'] = match_data.get('home_score', match_data.get('homeScore'))
        match_item['away_score'] = match_data.get('away_score', match_data.get('awayScore'))
        match_item['date'] = match_data.get('date', match_data.get('gameDate'))
        match_item['source_url'] = response.url
        match_item['league_id'] = response.meta.get('liga_id')
        match_item['season'] = response.meta.get('season_id')
        
        return match_item
    
    def parse_match_page(self, response):
        """Parse individual match pages for detailed stats"""
        self.logger.info(f"Parsing match page: {response.url}")
        
        # Extract player statistics from match page
        player_stats = response.css('.player-stats tr, .boxscore tr, table[class*="stat"] tr')
        
        for row in player_stats[1:]:  # Skip header row
            player_item = PlayerStatsItem()
            
            # Extract player data - adapt selectors based on actual HTML
            player_item['name'] = row.css('td:nth-child(1)::text, .player-name::text').get()
            player_item['points'] = self.safe_int(row.css('td:nth-child(2)::text, .points::text').get())
            player_item['rebounds'] = self.safe_int(row.css('td:nth-child(3)::text, .rebounds::text').get())
            player_item['assists'] = self.safe_int(row.css('td:nth-child(4)::text, .assists::text').get())
            player_item['source_url'] = response.url
            player_item['match_id'] = self.extract_id_from_url(response.url)
            
            if player_item['name']:
                yield player_item
    
    def parse_stats_page(self, response):
        """Parse statistics pages"""
        self.logger.info(f"Parsing stats page: {response.url}")
        
        # Look for player statistics tables
        stats_tables = response.css('table[class*="stat"], .stats-table, .player-stats')
        
        for table in stats_tables:
            headers = table.css('th::text, thead td::text').getall()
            rows = table.css('tbody tr, tr[class*="player"]')
            
            for row in rows:
                cells = row.css('td::text').getall()
                if len(cells) >= 3:  # Ensure we have enough data
                    player_item = PlayerStatsItem()
                    player_item['name'] = cells[0].strip() if cells[0] else None
                    player_item['source_url'] = response.url
                    
                    # Map other fields based on headers if available
                    for i, header in enumerate(headers):
                        if i < len(cells) and header:
                            self.map_stat_field(player_item, header.lower(), cells[i])
                    
                    if player_item['name']:
                        yield player_item
    
    def map_stat_field(self, item, header, value):
        """Map table headers to item fields"""
        header = header.lower().strip()
        mapping = {
            'punkte': 'points',
            'points': 'points',
            'pts': 'points',
            'rebounds': 'rebounds',
            'reb': 'rebounds',
            'assists': 'assists',
            'ast': 'assists',
            'steals': 'steals',
            'blocks': 'blocks',
            'turnovers': 'turnovers',
        }
        
        if header in mapping:
            item[mapping[header]] = self.safe_int(value)
    
    def safe_int(self, value):
        """Safely convert value to integer"""
        if not value:
            return None
        try:
            return int(str(value).strip())
        except (ValueError, TypeError):
            return None
    
    def extract_id_from_url(self, url):
        """Extract ID from URL"""
        if not url:
            return None
        parts = url.split('/')
        for part in reversed(parts):
            if part.isdigit():
                return part
        return None
