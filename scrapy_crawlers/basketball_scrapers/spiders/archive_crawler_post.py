import scrapy
import re
from urllib.parse import urljoin, parse_qs, urlparse


class ArchiveSpider(scrapy.Spider):
    name = 'archive_crawler_post'
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
            # Still yield something for debugging
            yield {
                'type': 'archive_season_debug',
                'season': season,
                'url': response.url,
                'content_length': len(response.text),
                'content_sample': response.text[:500]
            }
            return
            
        # Look for historical leagues in the results
        historical_leagues = self.extract_historical_leagues(response, season)
        
        # Look for export buttons
        export_buttons = self.find_export_buttons(response)
        
        # Count tables on the page
        tables = response.css('table')
        table_count = len(tables)
        
        self.logger.info(f'🏀 Found {len(historical_leagues)} historical leagues for season {season}')
        self.logger.info(f'📤 Found {len(export_buttons)} export buttons')
        self.logger.info(f'📊 Found {table_count} tables')
        
        # Create summary item for this season
        yield {
            'type': 'archive_season_summary',
            'season': season,
            'url': response.url,
            'content_length': len(response.text),
            'historical_leagues_found': len(historical_leagues),
            'export_buttons_found': len(export_buttons),
            'tables_found': table_count,
            'historical_leagues': historical_leagues[:10],  # First 10 for summary
            'export_buttons': export_buttons[:5]  # First 5 for summary
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
            
        # Process export buttons
        for export in export_buttons:
            if export.get('url'):
                yield scrapy.Request(
                    url=export['url'],
                    callback=self.parse_export,
                    meta={
                        'season': season,
                        'export_info': export
                    }
                )

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
    
    def find_export_buttons(self, response):
        """Find export buttons and links on the page"""
        exports = []
        
        # Look for links with 'export' in href or text
        for link in response.css('a'):
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            
            if href and text:
                text = text.strip()
                if ('export' in href.lower() or 'export' in text.lower() or 
                    'Export' in text or 'presseExport' in href):
                    exports.append({
                        'url': urljoin(response.url, href),
                        'text': text,
                        'href': href
                    })
        
        return exports
    
    def categorize_league(self, text):
        """Categorize a league based on its text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['herren', 'männer', 'men']):
            return 'men'
        elif any(word in text_lower for word in ['damen', 'frauen', 'women']):
            return 'women'
        elif any(word in text_lower for word in ['jugend', 'youth', 'u18', 'u16', 'u14']):
            return 'youth'
        else:
            return 'general'
    
    def parse_historical_league(self, response):
        """Parse a specific historical league page"""
        season = response.meta['season']
        league_info = response.meta['league_info']
        
        self.logger.info(f'🏀 Processing historical league: {league_info["text"]} (Season: {season})')
        
        # Look for statistical views and boxscore links
        stat_links = []
        boxscore_links = []
        
        for link in response.css('a[href]'):
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            
            if href and text:
                text = text.strip()
                
                # Statistical views
                if any(stat in href for stat in ['statTeam', 'statBeste', 'statSpieler']):
                    stat_links.append({
                        'url': urljoin(response.url, href),
                        'text': text,
                        'type': 'statistics'
                    })
                
                # Boxscore links (Action=108)
                elif 'Action=108' in href:
                    boxscore_links.append({
                        'url': urljoin(response.url, href),
                        'text': text,
                        'type': 'boxscore'
                    })
        
        # Yield the league data
        yield {
            'type': 'historical_league',
            'season': season,
            'league_name': league_info['text'],
            'liga_id': league_info['liga_id'],
            'url': response.url,
            'stat_links_found': len(stat_links),
            'boxscore_links_found': len(boxscore_links),
            'content_length': len(response.text)
        }
        
        # Follow statistical links
        for stat_link in stat_links:
            yield scrapy.Request(
                url=stat_link['url'],
                callback=self.parse_historical_stats,
                meta={
                    'season': season,
                    'league_info': league_info,
                    'stat_type': stat_link.get('text', 'unknown')
                }
            )
        
        # Follow boxscore links
        for boxscore_link in boxscore_links[:5]:  # Limit boxscores
            yield scrapy.Request(
                url=boxscore_link['url'],
                callback=self.parse_boxscore,
                meta={
                    'season': season,
                    'league_info': league_info
                }
            )
    
    def parse_historical_stats(self, response):
        """Parse historical statistics page"""
        season = response.meta['season']
        league_info = response.meta['league_info']
        stat_type = response.meta['stat_type']
        
        # Look for tables with statistical data
        tables = response.css('table')
        
        yield {
            'type': 'historical_statistics',
            'season': season,
            'league_name': league_info['text'],
            'liga_id': league_info['liga_id'],
            'stat_type': stat_type,
            'url': response.url,
            'tables_found': len(tables),
            'content_length': len(response.text)
        }
    
    def parse_boxscore(self, response):
        """Parse boxscore page"""
        season = response.meta['season']
        league_info = response.meta['league_info']
        
        yield {
            'type': 'historical_boxscore',
            'season': season,
            'league_name': league_info['text'],
            'liga_id': league_info['liga_id'],
            'url': response.url,
            'content_length': len(response.text)
        }
    
    def parse_export(self, response):
        """Parse export page/response"""
        season = response.meta['season']
        export_info = response.meta['export_info']
        
        yield {
            'type': 'historical_export',
            'season': season,
            'export_name': export_info.get('text', 'Unknown'),
            'url': response.url,
            'content_type': response.headers.get('Content-Type', b'unknown').decode(),
            'content_length': len(response.text)
        }
