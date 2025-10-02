import scrapy
import re
from urllib.parse import urljoin, parse_qs, urlparse


class ArchiveSpider(scrapy.Spider):
    name = 'archive_crawler'
    allowed_domains = ['basketball-bund.net']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,  # Be more respectful with archive pages
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
    }
    
    # Seasons to crawl (recent years)
    seasons_to_crawl = ['2023', '2022', '2021', '2020', '2019', '2018', '2017']
    
    def start_requests(self):
        """Start with the main archive form page"""
        yield scrapy.Request(
            url='https://www.basketball-bund.net/index.jsp?Action=106',
            callback=self.parse_archive_form
        )
    
    def parse_archive_form(self, response):
        """Parse the main archive page and submit POST requests for different seasons"""
        self.logger.info('🔍 Processing main archive form page')
        
        # Find the form
        form = response.css('form').get()
        if not form:
            self.logger.warning('❌ No form found on archive page')
            return
            
        # Submit requests for each season we want to crawl
        for season in self.seasons_to_crawl:
            self.logger.info(f'📅 Submitting archive request for season {season}')
            
            # POST form data for this season
            formdata = {
                'saison_id': season,
                'cbSpielklasseFilter': '0',  # alle Spielklassen
                'cbAltersklasseFilter': '0',  # alle Altersklassen  
                'cbGeschlechtFilter': '0',    # alle Bereiche
                'cbBezirkFilter': '0',        # alle Bezirke
                'cbKreisFilter': '0'          # alle Kreise
            }
            
            yield scrapy.FormRequest.from_response(
                response,
                formdata=formdata,
                callback=self.parse_archive_results,
                meta={'season': season}
            )
    
    def parse_archive_results(self, response):
        """Parse the results of a POST request to the archive form"""
        season = response.meta['season']
        
        self.logger.info(f'🗃️ Processing archive results for season {season}')
        self.logger.info(f'   Content length: {len(response.text)} characters')
        
        # Check if page has content
        if len(response.text) < 1000:
            self.logger.warning(f'❌ Very short content for season {season}')
            return
            
        # Look for historical leagues in the results
        historical_leagues = self.extract_historical_leagues(response, season)
        
        if historical_leagues:
            self.logger.info(f'🏀 Found {len(historical_leagues)} historical leagues for season {season}')
            
            # Create summary item for this season
            yield {
                'type': 'archive_season_summary',
                'season': season,
                'url': response.url,
                'historical_leagues_found': len(historical_leagues),
                'historical_leagues': historical_leagues[:10]  # First 10 for summary
            }
            
            # Process each historical league found
            for league in historical_leagues:
                yield scrapy.Request(
                    url=league['url'],
                    callback=self.parse_historical_league,
                    meta={
                        'season': season,
                        'league_info': league
                    }
                )
        else:
            self.logger.warning(f'❌ No historical leagues found for season {season}')
            
            # Still yield a summary showing what we found
            yield {
                'type': 'archive_season_summary', 
                'season': season,
                'url': response.url,
                'historical_leagues_found': 0,
                'content_sample': response.text[:500]  # Sample for debugging
            }

    def extract_historical_leagues(self, response, season):
        """Extract historical league links from archive results"""
        leagues = []
        
        # Look for links with liga_id parameters
        for link in response.css('a[href*="liga_id"]'):
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            
            if href and text:
                # Parse the URL to extract parameters
                parsed_url = urlparse(href)
                params = parse_qs(parsed_url.query)
                
                liga_id = params.get('liga_id', [None])[0]
                action = params.get('Action', [None])[0]
                
                if liga_id:
                    league_info = {
                        'url': urljoin(response.url, href),
                        'text': text.strip(),
                        'href': href,
                        'liga_id': liga_id,
                        'saison': season,
                        'action': action,
                        'category': self.categorize_league(text.strip())
                    }
                    leagues.append(league_info)
        
        return leagues
        export_buttons = self.find_archive_exports(response)
        
        if export_buttons:
            self.logger.info(f'📤 Found {len(export_buttons)} archive export options')
            for export_info in export_buttons:
                yield response.follow(
                    export_info['url'],
                    callback=self.parse_archive_export,
                    meta={
                        'export_info': export_info,
                        'source_url': response.url,
                        'start_row': start_row,
                        'page_type': page_type
                    }
                )
        
        # Extract historical league information
        historical_leagues = self.extract_historical_leagues(response)
        
        if historical_leagues:
            self.logger.info(f'🏀 Found {len(historical_leagues)} historical leagues')
            
            # Follow links to individual historical league pages
            for league_info in historical_leagues:
                yield response.follow(
                    league_info['url'],
                    callback=self.parse_historical_league,
                    meta={
                        'league_info': league_info,
                        'source_url': response.url,
                        'start_row': start_row
                    }
                )
        
        # Look for season/year navigation
        season_links = self.extract_season_navigation(response)
        
        if season_links:
            self.logger.info(f'📅 Found {len(season_links)} season navigation links')
            for season_link in season_links[:3]:  # Limit to 3 seasons to avoid going too far back
                yield response.follow(
                    season_link['url'],
                    callback=self.parse_archive_listing,
                    meta={
                        'start_row': 0,
                        'page_type': f'archive_season_{season_link["season"]}',
                        'season_info': season_link
                    }
                )
        
        # Yield summary of this archive page
        yield {
            'type': 'archive_listing_summary',
            'url': response.url,
            'start_row': start_row,
            'page_type': page_type,
            'export_buttons_found': len(export_buttons),
            'historical_leagues_found': len(historical_leagues),
            'season_links_found': len(season_links),
            'historical_leagues': historical_leagues
        }
    
    def is_empty_archive_page(self, response):
        """Check if archive page is empty"""
        empty_indicators = [
            'keine ergebnisse',
            'no results',
            'keine archive',
            'empty archive'
        ]
        
        body_text = response.text.lower()
        if any(indicator in body_text for indicator in empty_indicators):
            return True
        
        # Check if very few tables/links
        tables = response.css('table')
        archive_links = response.css('a[href*="Action="]')
        
        return len(tables) < 1 and len(archive_links) < 3
    
    def find_archive_exports(self, response):
        """Find export buttons on archive pages"""
        export_buttons = []
        
        # Look for presseExport.do links
        presse_exports = response.css('a[href*="presseExport.do"]')
        for link in presse_exports:
            href = link.css('::attr(href)').get()
            text = link.css('::text').get() or ''
            
            if href:
                export_buttons.append({
                    'type': 'presse_export_archive',
                    'text': text.strip(),
                    'url': href,
                    'full_url': response.urljoin(href)
                })
        
        # Look for other export patterns common in archives
        export_patterns = ['export', 'download', 'ausdrucken', 'liste', 'excel', 'csv']
        
        for pattern in export_patterns:
            links = response.css(f'a:contains("{pattern}"), a[href*="{pattern}"]')
            for link in links:
                href = link.css('::attr(href)').get()
                text = link.css('::text').get() or ''
                
                if href and href not in [eb['url'] for eb in export_buttons]:
                    export_buttons.append({
                        'type': f'archive_export_{pattern}',
                        'text': text.strip(),
                        'url': href,
                        'full_url': response.urljoin(href)
                    })
        
        return export_buttons
    
    def extract_historical_leagues(self, response):
        """Extract historical league information from archive pages"""
        historical_leagues = []
        
        # Look for different action patterns that might be used in archives
        archive_league_patterns = [
            'a[href*="Action=100"]',  # Standard league view
            'a[href*="Action=102"]',  # Individual league
            'a[href*="Action=103"]',  # Boxscores
            'a[href*="Action=107"]',  # Possible archive-specific action
            'a[href*="Action=108"]',  # Possible archive-specific action
            'a[href*="liga_id="]',    # Any link with liga_id
            'a[href*="saison"]',      # Season-specific links
            'a[href*="archiv"]',      # Archive-specific links
        ]
        
        for pattern in archive_league_patterns:
            links = response.css(pattern)
            
            for link in links:
                href = link.css('::attr(href)').get()
                text = link.css('::text').get() or ''
                
                if href and text:
                    # Extract IDs and season info
                    liga_id_match = re.search(r'liga_id=(\d+)', href)
                    saison_match = re.search(r'saison=([^&]+)', href)
                    action_match = re.search(r'Action=(\d+)', href)
                    
                    liga_id = liga_id_match.group(1) if liga_id_match else None
                    saison = saison_match.group(1) if saison_match else 'unknown'
                    action = action_match.group(1) if action_match else 'unknown'
                    
                    # Determine league category
                    category = self.categorize_historical_league(text, href)
                    
                    historical_leagues.append({
                        'url': response.urljoin(href),
                        'text': text.strip(),
                        'href': href,
                        'liga_id': liga_id,
                        'saison': saison,
                        'action': action,
                        'category': category
                    })
        
        return historical_leagues
    
    def categorize_historical_league(self, text, href):
        """Categorize historical league entries"""
        text_lower = text.lower()
        href_lower = href.lower()
        
        if any(keyword in text_lower for keyword in ['herren', 'men']):
            return 'men'
        elif any(keyword in text_lower for keyword in ['damen', 'women']):
            return 'women'
        elif any(keyword in text_lower for keyword in ['jugend', 'youth', 'u19', 'u17', 'u15']):
            return 'youth'
        elif any(keyword in text_lower for keyword in ['bezirk', 'kreis', 'regional']):
            return 'regional'
        else:
            return 'general'
    
    def extract_season_navigation(self, response):
        """Extract links to different seasons/years"""
        season_links = []
        
        # Look for season/year navigation
        season_patterns = [
            r'(\d{4}[-/]\d{4})',  # 2023-2024, 2023/2024
            r'(\d{4}[-/]\d{2})',  # 2023-24, 2023/24
            r'(Saison\s+\d{4})',  # Saison 2023
        ]
        
        page_text = response.text
        
        # Find season references in links
        season_links_css = response.css('a[href*="saison"], a[href*="jahr"], a:contains("2023"), a:contains("2024")')
        
        for link in season_links_css:
            href = link.css('::attr(href)').get()
            text = link.css('::text').get() or ''
            
            if href:
                # Try to extract season year
                for pattern in season_patterns:
                    match = re.search(pattern, text)
                    if match:
                        season = match.group(1)
                        season_links.append({
                            'url': response.urljoin(href),
                            'text': text.strip(),
                            'season': season,
                            'href': href
                        })
                        break
        
        return season_links
    
    def parse_historical_league(self, response):
        """Parse individual historical league pages"""
        league_info = response.meta['league_info']
        source_url = response.meta['source_url']
        start_row = response.meta.get('start_row')
        
        self.logger.info(f'🏀 Processing historical league: {league_info["text"]} (ID: {league_info.get("liga_id")})')
        
        # Look for export buttons on historical league pages
        export_buttons = self.find_archive_exports(response)
        
        for export_info in export_buttons:
            yield response.follow(
                export_info['url'],
                callback=self.parse_archive_export,
                meta={
                    'export_info': export_info,
                    'source_url': response.url,
                    'league_info': league_info,
                    'context': 'historical_league'
                }
            )
        
        # Try to follow historical statistical views if available
        if league_info.get('liga_id'):
            yield from self.create_historical_stat_requests(
                league_info['liga_id'],
                league_info['text'],
                league_info.get('saison', 'unknown')
            )
        
        # Extract data from this historical league page
        league_data = self.extract_historical_league_data(response)
        
        yield {
            'type': 'historical_league',
            'url': response.url,
            'source_url': source_url,
            'league_info': league_info,
            'export_buttons_found': len(export_buttons),
            'league_data': league_data
        }
    
    def create_historical_stat_requests(self, liga_id, league_name, saison):
        """Create requests for historical statistical views using archive-specific patterns"""
        # Archive-specific statistical views with 'Archiv' suffix
        historical_views = [
            {
                'reqCode': 'statTeamArchiv',
                'name': 'Historical Team Stats (Archive)',
                'url_template': 'statistik.do?reqCode=statTeamArchiv&liga_id={}&saison_id={}'
            },
            {
                'reqCode': 'statBesteWerferArchiv', 
                'name': 'Historical Top Scorers (Archive)',
                'url_template': 'statistik.do?reqCode=statBesteWerferArchiv&liga_id={}&saison_id={}&_top=-1'
            },
            {
                'reqCode': 'statBesteFreiWerferArchiv',
                'name': 'Historical Free Throws (Archive)', 
                'url_template': 'statistik.do?reqCode=statBesteFreiWerferArchiv&liga_id={}&saison_id={}&_top=-1'
            },
            {
                'reqCode': 'statBeste3erWerferArchiv',
                'name': 'Historical 3-Pointers (Archive)',
                'url_template': 'statistik.do?reqCode=statBeste3erWerferArchiv&liga_id={}&saison_id={}&_top=-1'
            },
        ]
        
        base_url = 'https://www.basketball-bund.net/'
        
        # Try different saison_id formats
        saison_ids = self.generate_saison_ids(saison)
        
        for view in historical_views:
            for saison_id in saison_ids:
                url = base_url + view['url_template'].format(liga_id, saison_id)
                
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_historical_stats,
                    meta={
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'saison': saison,
                        'saison_id': saison_id,
                        'view_info': view
                    }
                )
        
        # Also try the archive standings page (Action=107)
        for saison_id in saison_ids:
            standings_url = f'https://www.basketball-bund.net/index.jsp?Action=107&liga_id={liga_id}&saison_id={saison_id}'
            
            yield scrapy.Request(
                url=standings_url,
                callback=self.parse_historical_standings,
                meta={
                    'liga_id': liga_id,
                    'league_name': league_name,
                    'saison': saison,
                    'saison_id': saison_id
                }
            )
        
        # Try to find boxscores even without direct links
        yield from self.create_boxscore_discovery_requests(liga_id, league_name, saison_ids)
    
    def generate_saison_ids(self, saison):
        """Generate possible saison_id values from season string"""
        saison_ids = []
        
        # If we have a specific saison string, try to parse it
        if saison and saison != 'unknown':
            # Extract years from formats like "2023-2024", "2023/24", etc.
            year_match = re.search(r'(\d{4})', saison)
            if year_match:
                year = int(year_match.group(1))
                saison_ids.extend([str(year), str(year + 1), str(year - 1)])
        
        # Add common recent years
        current_year = 2024
        for year in range(current_year, current_year - 5, -1):  # Last 5 years
            saison_ids.append(str(year))
        
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in saison_ids if not (x in seen or seen.add(x))]
    
    def create_boxscore_discovery_requests(self, liga_id, league_name, saison_ids):
        """Create requests to discover boxscores even without direct HTML links"""
        
        # Try different boxscore action patterns for archives
        boxscore_actions = [103, 108, 109, 110]  # Possible archive boxscore actions
        
        for action in boxscore_actions:
            for saison_id in saison_ids[:3]:  # Limit to first 3 saison_ids
                boxscore_url = f'https://www.basketball-bund.net/index.jsp?Action={action}&liga_id={liga_id}&saison_id={saison_id}'
                
                yield scrapy.Request(
                    url=boxscore_url,
                    callback=self.parse_discovered_boxscores,
                    meta={
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'saison_id': saison_id,
                        'action': action,
                        'discovery_type': 'boxscore_discovery'
                    }
                )
        
        # Also try to discover individual games by constructing URLs
        # This is speculative - try common spiel_id patterns
        yield from self.create_speculative_game_requests(liga_id, league_name, saison_ids[0] if saison_ids else '2024')
    
    def parse_historical_stats(self, response):
        """Parse historical statistical views"""
        liga_id = response.meta['liga_id']
        league_name = response.meta['league_name']
        saison = response.meta['saison']
        saison_id = response.meta.get('saison_id', 'unknown')
        view_info = response.meta['view_info']
        
        self.logger.info(f'📊 Processing historical {view_info["name"]} for {league_name} (saison_id: {saison_id})')
        
        # Check if this page has valid data
        if self.is_valid_archive_stats_page(response):
            self.logger.info(f'   ✅ Found valid archive stats data')
            
            # Look for export buttons
            export_buttons = self.find_archive_exports(response)
            
            for export_info in export_buttons:
                yield response.follow(
                    export_info['url'],
                    callback=self.parse_archive_export,
                    meta={
                        'export_info': export_info,
                        'source_url': response.url,
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'saison': saison,
                        'saison_id': saison_id,
                        'view_info': view_info,
                        'context': 'historical_stats_archive'
                    }
                )
            
            # Extract historical stats data
            stats_data = self.extract_archive_stats_data(response, view_info)
            
            yield {
                'type': 'historical_stats_archive',
                'url': response.url,
                'liga_id': liga_id,
                'league_name': league_name,
                'saison': saison,
                'saison_id': saison_id,
                'view_name': view_info['name'],
                'view_reqCode': view_info['reqCode'],
                'export_buttons_found': len(export_buttons),
                'stats_data': stats_data
            }
        else:
            self.logger.info(f'   ❌ No valid data for saison_id: {saison_id}')
    
    def parse_historical_standings(self, response):
        """Parse historical standings pages (Action=107)"""
        liga_id = response.meta['liga_id']
        league_name = response.meta['league_name']
        saison = response.meta['saison']
        saison_id = response.meta['saison_id']
        
        self.logger.info(f'🏆 Processing historical standings for {league_name} (saison_id: {saison_id})')
        
        if self.is_valid_archive_page(response):
            self.logger.info(f'   ✅ Found valid standings data')
            
            # Look for export buttons
            export_buttons = self.find_archive_exports(response)
            
            for export_info in export_buttons:
                yield response.follow(
                    export_info['url'],
                    callback=self.parse_archive_export,
                    meta={
                        'export_info': export_info,
                        'source_url': response.url,
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'saison_id': saison_id,
                        'context': 'historical_standings'
                    }
                )
            
            # Extract standings data
            standings_data = self.extract_standings_data(response)
            
            yield {
                'type': 'historical_standings',
                'url': response.url,
                'liga_id': liga_id,
                'league_name': league_name,
                'saison_id': saison_id,
                'export_buttons_found': len(export_buttons),
                'standings_data': standings_data
            }
        else:
            self.logger.info(f'   ❌ No valid standings for saison_id: {saison_id}')
    
    def parse_discovered_boxscores(self, response):
        """Parse boxscore pages discovered through URL construction"""
        liga_id = response.meta['liga_id']
        league_name = response.meta['league_name']
        saison_id = response.meta['saison_id']
        action = response.meta['action']
        
        self.logger.info(f'🔍 Testing boxscore discovery: Action={action}, liga_id={liga_id}, saison_id={saison_id}')
        
        if self.is_valid_archive_page(response) and self.has_boxscore_content(response):
            self.logger.info(f'   ✅ FOUND VALID BOXSCORE PAGE! Action={action}')
            
            # Look for export buttons
            export_buttons = self.find_archive_exports(response)
            
            # Look for individual game links
            game_links = self.extract_boxscore_game_links(response)
            
            for export_info in export_buttons:
                yield response.follow(
                    export_info['url'],
                    callback=self.parse_archive_export,
                    meta={
                        'export_info': export_info,
                        'source_url': response.url,
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'saison_id': saison_id,
                        'action': action,
                        'context': 'discovered_boxscore'
                    }
                )
            
            # Try to follow some game links
            for game_link in game_links[:3]:  # First 3 games
                yield response.follow(
                    game_link['url'],
                    callback=self.parse_discovered_game,
                    meta={
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'saison_id': saison_id,
                        'game_info': game_link
                    }
                )
            
            yield {
                'type': 'discovered_boxscore_page',
                'url': response.url,
                'liga_id': liga_id,
                'league_name': league_name,
                'saison_id': saison_id,
                'action': action,
                'export_buttons_found': len(export_buttons),
                'game_links_found': len(game_links),
                'discovery_successful': True
            }
        else:
            # This action/saison_id combination didn't work
            yield {
                'type': 'failed_boxscore_discovery',
                'url': response.url,
                'liga_id': liga_id,
                'saison_id': saison_id,
                'action': action,
                'discovery_successful': False
            }
    
    def create_speculative_game_requests(self, liga_id, league_name, saison_id):
        """Create speculative requests for individual games by guessing spiel_id patterns"""
        
        # Try different game detail actions
        game_actions = [104, 105]  # Common game detail actions
        
        # Try some spiel_id ranges (this is speculative)
        # Game IDs are often sequential within a season
        base_spiel_ids = [100000, 200000, 300000, 400000]  # Different ranges to try
        
        for action in game_actions:
            for base_id in base_spiel_ids[:2]:  # Try first 2 ranges
                for offset in range(0, 50, 10):  # Try every 10th ID in range
                    spiel_id = base_id + offset
                    
                    game_url = f'https://www.basketball-bund.net/index.jsp?Action={action}&spiel_id={spiel_id}&saison_id={saison_id}'
                    
                    yield scrapy.Request(
                        url=game_url,
                        callback=self.parse_speculative_game,
                        meta={
                            'liga_id': liga_id,
                            'league_name': league_name,
                            'saison_id': saison_id,
                            'spiel_id': spiel_id,
                            'action': action,
                            'discovery_type': 'speculative_game'
                        }
                    )
    
    def is_valid_archive_stats_page(self, response):
        """Check if an archive stats page has valid data"""
        # Look for indicators of valid stats data
        page_text = response.text.lower()
        
        # Positive indicators
        valid_indicators = [
            'punkte', 'points', 'treffer', 'wurf', 'shot',
            'tabelle', 'statistik', 'ranking', 'platz'
        ]
        
        # Negative indicators  
        invalid_indicators = [
            'keine daten', 'no data', 'empty', 'fehler',
            'nicht gefunden', 'not found', 'error'
        ]
        
        has_valid_content = any(indicator in page_text for indicator in valid_indicators)
        has_invalid_content = any(indicator in page_text for indicator in invalid_indicators)
        
        # Must have tables and not be empty
        tables = response.css('table')
        has_tables = len(tables) > 0
        
        return has_valid_content and not has_invalid_content and has_tables
    
    def is_valid_archive_page(self, response):
        """Check if any archive page has valid data"""
        # Check response status
        if response.status != 200:
            return False
        
        # Check for error indicators
        error_indicators = [
            'error', 'fehler', 'not found', 'nicht gefunden',
            'keine daten', 'no data', 'empty page'
        ]
        
        page_text = response.text.lower()
        has_errors = any(indicator in page_text for indicator in error_indicators)
        
        # Check for content indicators
        has_tables = len(response.css('table')) > 0
        has_content = len(response.text.strip()) > 1000  # Reasonable content length
        
        return not has_errors and (has_tables or has_content)
    
    def has_boxscore_content(self, response):
        """Check if a page contains boxscore-related content"""
        page_text = response.text.lower()
        
        boxscore_indicators = [
            'spiel', 'game', 'ergebnis', 'result', 'score',
            'heimmannschaft', 'gastmannschaft', 'home', 'away',
            'datum', 'date', 'uhrzeit', 'time'
        ]
        
        return any(indicator in page_text for indicator in boxscore_indicators)
    
    def extract_boxscore_game_links(self, response):
        """Extract game links from boxscore pages"""
        game_links = []
        
        # Look for various game link patterns
        game_patterns = [
            'a[href*="Action=104"]',  # Individual game details
            'a[href*="Action=105"]',  # Alternative game action
            'a[href*="spiel_id="]',   # Game ID links
            'a[href*="spielbericht"]', # Game report links
        ]
        
        for pattern in game_patterns:
            links = response.css(pattern)
            for link in links:
                href = link.css('::attr(href)').get()
                text = link.css('::text').get() or ''
                
                if href:
                    # Extract spiel_id if present
                    spiel_id_match = re.search(r'spiel_id=(\d+)', href)
                    spiel_id = spiel_id_match.group(1) if spiel_id_match else None
                    
                    game_links.append({
                        'url': response.urljoin(href),
                        'text': text.strip(),
                        'href': href,
                        'spiel_id': spiel_id
                    })
        
        return game_links
    
    def parse_discovered_game(self, response):
        """Parse individual games discovered from boxscore pages"""
        liga_id = response.meta['liga_id']
        league_name = response.meta['league_name']
        saison_id = response.meta['saison_id']
        game_info = response.meta['game_info']
        
        self.logger.info(f'🏀 Processing discovered game: {game_info["text"]} (spiel_id: {game_info.get("spiel_id")})')
        
        if self.is_valid_archive_page(response):
            # Look for export buttons on game pages
            export_buttons = self.find_archive_exports(response)
            
            for export_info in export_buttons:
                yield response.follow(
                    export_info['url'],
                    callback=self.parse_archive_export,
                    meta={
                        'export_info': export_info,
                        'source_url': response.url,
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'saison_id': saison_id,
                        'game_info': game_info,
                        'context': 'discovered_game'
                    }
                )
            
            # Extract game data
            game_data = self.extract_detailed_game_data(response)
            
            yield {
                'type': 'discovered_individual_game',
                'url': response.url,
                'liga_id': liga_id,
                'league_name': league_name,
                'saison_id': saison_id,
                'game_info': game_info,
                'export_buttons_found': len(export_buttons),
                'game_data': game_data
            }
    
    def parse_speculative_game(self, response):
        """Parse games found through speculative spiel_id construction"""
        liga_id = response.meta['liga_id']
        saison_id = response.meta['saison_id']
        spiel_id = response.meta['spiel_id']
        action = response.meta['action']
        
        if self.is_valid_archive_page(response) and self.has_boxscore_content(response):
            self.logger.info(f'   ✅ FOUND VALID GAME! Action={action}, spiel_id={spiel_id}')
            
            game_data = self.extract_detailed_game_data(response)
            
            yield {
                'type': 'speculative_game_success',
                'url': response.url,
                'liga_id': liga_id,
                'saison_id': saison_id,
                'spiel_id': spiel_id,
                'action': action,
                'game_data': game_data,
                'discovery_method': 'speculative'
            }
    
    def extract_archive_stats_data(self, response, view_info):
        """Extract data from archive statistics pages"""
        data = {
            'title': response.css('title::text').get(),
            'tables_count': len(response.css('table')),
            'view_type': view_info['reqCode']
        }
        
        # Extract sample data from tables
        tables = response.css('table')
        if tables:
            # Get data from first main table
            main_table = tables[0]
            rows = main_table.css('tr')
            
            if len(rows) > 1:
                # Extract headers
                headers = []
                header_cells = rows[0].css('th, td')
                for cell in header_cells:
                    text = cell.css('::text').get()
                    if text:
                        headers.append(text.strip())
                
                # Extract sample data rows
                sample_data = []
                for row in rows[1:6]:  # First 5 data rows
                    row_cells = []
                    cells = row.css('td')
                    for cell in cells:
                        text = ' '.join(cell.css('::text').getall()).strip()
                        if text:
                            row_cells.append(text)
                    
                    if row_cells:
                        sample_data.append(row_cells)
                
                data['headers'] = headers
                data['sample_data'] = sample_data
                data['total_data_rows'] = len(rows) - 1
        
        return data
    
    def extract_standings_data(self, response):
        """Extract standings data from Action=107 pages"""
        data = {
            'title': response.css('title::text').get(),
            'tables_count': len(response.css('table'))
        }
        
        # Look for standings table
        tables = response.css('table')
        for i, table in enumerate(tables):
            rows = table.css('tr')
            
            if len(rows) > 3:  # Likely a standings table
                # Extract team standings
                teams = []
                for row in rows[1:]:  # Skip header
                    cells = row.css('td')
                    if len(cells) >= 3:  # At least rank, team, points
                        team_data = []
                        for cell in cells[:6]:  # First 6 columns
                            text = ' '.join(cell.css('::text').getall()).strip()
                            team_data.append(text)
                        
                        if any(team_data):  # Has some data
                            teams.append(team_data)
                
                if teams:
                    data[f'standings_table_{i}'] = teams[:10]  # Top 10 teams
        
        return data
    
    def extract_detailed_game_data(self, response):
        """Extract detailed data from individual game pages"""
        data = {
            'title': response.css('title::text').get(),
            'tables_count': len(response.css('table'))
        }
        
        # Look for boxscore tables
        tables = response.css('table')
        
        for i, table in enumerate(tables[:3]):  # First 3 tables
            rows = table.css('tr')
            
            if len(rows) > 1:
                # Try to identify table type
                table_text = ' '.join(table.css('::text').getall()).lower()
                
                if 'punkte' in table_text or 'points' in table_text:
                    data[f'table_{i}_type'] = 'scoring'
                elif 'rebounds' in table_text:
                    data[f'table_{i}_type'] = 'rebounds'
                elif 'assist' in table_text:
                    data[f'table_{i}_type'] = 'assists'
                else:
                    data[f'table_{i}_type'] = 'general'
                
                # Extract sample data
                sample_rows = []
                for row in rows[:5]:  # First 5 rows
                    cells = row.css('td::text, th::text').getall()
                    cells = [cell.strip() for cell in cells if cell.strip()]
                    if cells:
                        sample_rows.append(cells)
                
                data[f'table_{i}_sample'] = sample_rows
        
        return data
    
    def parse_historical_boxscores(self, response):
        """Parse historical boxscore pages"""
        liga_id = response.meta['liga_id']
        league_name = response.meta['league_name']
        saison = response.meta['saison']
        
        self.logger.info(f'🏀 Processing historical boxscores for {league_name} ({saison})')
        
        # Look for export buttons and game links
        export_buttons = self.find_archive_exports(response)
        game_links = self.extract_historical_game_links(response)
        
        for export_info in export_buttons:
            yield response.follow(
                export_info['url'],
                callback=self.parse_archive_export,
                meta={
                    'export_info': export_info,
                    'source_url': response.url,
                    'liga_id': liga_id,
                    'league_name': league_name,
                    'saison': saison,
                    'context': 'historical_boxscores'
                }
            )
        
        # Follow a sample of historical games
        for game_link in game_links[:3]:  # First 3 games
            yield response.follow(
                game_link['url'],
                callback=self.parse_historical_game,
                meta={
                    'liga_id': liga_id,
                    'league_name': league_name,
                    'saison': saison,
                    'game_info': game_link
                }
            )
        
        yield {
            'type': 'historical_boxscores',
            'url': response.url,
            'liga_id': liga_id,
            'league_name': league_name,
            'saison': saison,
            'export_buttons_found': len(export_buttons),
            'game_links_found': len(game_links)
        }
    
    def extract_historical_game_links(self, response):
        """Extract game links from historical boxscore pages"""
        game_links = []
        
        # Look for historical game patterns
        game_patterns = [
            'a[href*="Action=104"]',
            'a[href*="spiel_id="]',
            'a[href*="game_id="]',
            'a[href*="spielbericht"]'
        ]
        
        for pattern in game_patterns:
            links = response.css(pattern)
            for link in links:
                href = link.css('::attr(href)').get()
                text = link.css('::text').get() or ''
                
                if href:
                    game_links.append({
                        'url': response.urljoin(href),
                        'text': text.strip(),
                        'href': href
                    })
        
        return game_links
    
    def parse_historical_game(self, response):
        """Parse individual historical game pages"""
        liga_id = response.meta['liga_id']
        league_name = response.meta['league_name']
        saison = response.meta['saison']
        game_info = response.meta['game_info']
        
        self.logger.info(f'🏀 Processing historical game: {game_info["text"]} ({saison})')
        
        game_data = self.extract_game_data(response)
        
        yield {
            'type': 'historical_game',
            'url': response.url,
            'liga_id': liga_id,
            'league_name': league_name,
            'saison': saison,
            'game_info': game_info,
            'game_data': game_data
        }
    
    def extract_historical_league_data(self, response):
        """Extract data from historical league pages"""
        return {
            'title': response.css('title::text').get(),
            'tables_count': len(response.css('table')),
            'links_count': len(response.css('a[href*="Action="]')),
        }
    
    def extract_stats_data(self, response, view_info):
        """Extract statistical data from pages"""
        return {
            'title': response.css('title::text').get(),
            'tables_count': len(response.css('table')),
            'view_type': view_info['reqCode']
        }
    
    def extract_game_data(self, response):
        """Extract game data"""
        return {
            'title': response.css('title::text').get(),
            'tables_count': len(response.css('table'))
        }
    
    def parse_archive_export(self, response):
        """Parse all types of archive export data"""
        export_info = response.meta['export_info']
        source_url = response.meta['source_url']
        context = response.meta.get('context', 'archive')
        
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        
        self.logger.info(f'📊 Processing archive export: {export_info["text"]}')
        self.logger.info(f'   Context: {context}')
        self.logger.info(f'   Content-Type: {content_type}')
        self.logger.info(f'   Size: {len(response.body)} bytes')
        
        # Detect format and get preview
        file_format = self.detect_format(response, content_type)
        preview = (response.text[:300] if response.text else 
                  response.body[:300].decode('utf-8', errors='ignore'))
        
        yield {
            'type': 'archive_export_data',
            'context': context,
            'export_info': export_info,
            'source_url': source_url,
            'export_url': response.url,
            'content_type': content_type,
            'file_format': file_format,
            'size': len(response.body),
            'preview': preview,
            **{k: v for k, v in response.meta.items() if k not in ['export_info', 'source_url', 'context']}
        }
    
    def detect_format(self, response, content_type):
        """Detect file format"""
        if 'html' in content_type.lower():
            return 'html'
        elif 'csv' in content_type.lower():
            return 'csv'
        elif 'excel' in content_type.lower():
            return 'excel'
        else:
            content_start = response.body[:200].lower()
            if b'<html' in content_start or b'<table' in content_start:
                return 'html'
            elif b',' in content_start and b'"' in content_start:
                return 'csv'
            else:
                return 'text'
    
    def parse_historical_standings(self, response):
        """Parse historical standings pages (Action=107)"""
        liga_id = response.meta['liga_id']
        league_name = response.meta['league_name']
        saison = response.meta['saison']
        saison_id = response.meta['saison_id']
        
        self.logger.info(f'🏆 Processing historical standings: {league_name} ({saison_id})')
        
        # Check if this page has valid standings data
        if self.is_valid_standings_page(response):
            self.logger.info(f'   ✅ Valid standings data found')
            
            # Look for export buttons
            export_buttons = self.find_archive_exports(response)
            
            for export_info in export_buttons:
                yield response.follow(
                    export_info['url'],
                    callback=self.parse_archive_export,
                    meta={
                        'export_info': export_info,
                        'source_url': response.url,
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'saison_id': saison_id,
                        'context': 'historical_standings'
                    }
                )
            
            # Extract standings data
            standings_data = self.extract_standings_data(response)
            
            yield {
                'type': 'historical_standings',
                'url': response.url,
                'liga_id': liga_id,
                'league_name': league_name,
                'saison': saison,
                'saison_id': saison_id,
                'export_buttons_found': len(export_buttons),
                'standings_data': standings_data
            }
        else:
            self.logger.info(f'   ❌ No valid standings data found')
    
    def parse_discovered_boxscores(self, response):
        """Parse discovered boxscore pages"""
        liga_id = response.meta['liga_id']
        league_name = response.meta['league_name']
        saison_id = response.meta['saison_id']
        action = response.meta['action']
        
        self.logger.info(f'🏀 Testing boxscore discovery: Action={action}, Liga={liga_id}, Saison={saison_id}')
        
        # Check if this page has valid boxscore data
        if self.is_valid_boxscore_page(response):
            self.logger.info(f'   ✅ Valid boxscore data found!')
            
            # Look for export buttons
            export_buttons = self.find_archive_exports(response)
            
            for export_info in export_buttons:
                yield response.follow(
                    export_info['url'],
                    callback=self.parse_archive_export,
                    meta={
                        'export_info': export_info,
                        'source_url': response.url,
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'saison_id': saison_id,
                        'context': 'discovered_boxscores'
                    }
                )
            
            # Look for individual game links
            game_links = self.extract_historical_game_links(response)
            
            # Follow a few sample games
            for game_link in game_links[:3]:
                yield response.follow(
                    game_link['url'],
                    callback=self.parse_historical_game,
                    meta={
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'saison_id': saison_id,
                        'game_info': game_link
                    }
                )
            
            yield {
                'type': 'discovered_boxscores',
                'url': response.url,
                'liga_id': liga_id,
                'league_name': league_name,
                'saison_id': saison_id,
                'action': action,
                'export_buttons_found': len(export_buttons),
                'game_links_found': len(game_links)
            }
        else:
            self.logger.info(f'   ❌ No valid boxscore data (Action={action})')
    
    def is_valid_standings_page(self, response):
        """Check if a page contains valid standings data"""
        # Look for basketball-specific terms and table structures
        page_text = response.text.lower()
        
        # Indicators of valid standings
        standings_indicators = [
            'tabelle', 'standings', 'platz', 'punkte', 'spiele',
            'siege', 'wins', 'niederlagen', 'losses'
        ]
        
        has_indicators = any(indicator in page_text for indicator in standings_indicators)
        
        # Check for table structure
        tables = response.css('table')
        has_tables = len(tables) > 0
        
        # Check for team-like entries
        has_team_data = bool(response.css('td, th'))
        
        return has_indicators and has_tables and has_team_data
    
    def is_valid_boxscore_page(self, response):
        """Check if a page contains valid boxscore data"""
        page_text = response.text.lower()
        
        # Indicators of valid boxscore data
        boxscore_indicators = [
            'spiel', 'game', 'datum', 'date', 'ergebnis', 'result',
            'mannschaft', 'team', 'punkte', 'points'
        ]
        
        has_indicators = any(indicator in page_text for indicator in boxscore_indicators)
        
        # Check for meaningful content structure
        tables = response.css('table')
        links = response.css('a[href*="Action="]')
        
        # Avoid error pages or empty responses
        error_indicators = ['fehler', 'error', '404', 'not found', 'keine daten']
        has_errors = any(indicator in page_text for indicator in error_indicators)
        
        return has_indicators and len(tables) > 0 and not has_errors
    
    def extract_standings_data(self, response):
        """Extract standings data from page"""
        data = {
            'title': response.css('title::text').get(),
            'tables_count': len(response.css('table')),
        }
        
        # Extract team standings if available
        tables = response.css('table')
        
        for i, table in enumerate(tables[:2]):  # First 2 tables
            rows = table.css('tr')
            
            if len(rows) > 1:
                # Try to extract standings information
                headers = []
                for cell in rows[0].css('th, td'):
                    cell_text = cell.css('::text').get()
                    if cell_text:
                        headers.append(cell_text.strip())
                
                sample_teams = []
                for row in rows[1:6]:  # First 5 teams
                    team_cells = []
                    for cell in row.css('td'):
                        cell_text = ' '.join(cell.css('::text').getall()).strip()
                        if cell_text:
                            team_cells.append(cell_text)
                    
                    if team_cells:
                        sample_teams.append(team_cells)
                
                data[f'table_{i}'] = {
                    'headers': headers,
                    'sample_teams': sample_teams,
                    'total_rows': len(rows)
                }
        
        return data
