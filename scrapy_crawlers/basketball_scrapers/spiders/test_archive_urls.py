import scrapy
from datetime import datetime
import re
from urllib.parse import urlparse, parse_qs, urljoin


class TestArchiveUrlsSpider(scrapy.Spider):
    name = "test_archive_urls"
    allowed_domains = ["basketball-bund.net"]
    
    # Test the specific URLs provided by the user
    start_urls = [
        # Current season for comparison
        "https://www.basketball-bund.net/index.jsp?Action=102&liga_id=51819",
        
        # Archive URLs from user examples
        "https://www.basketball-bund.net/index.jsp?Action=107&liga_id=17248&saison_id=2020&reqCode=statTeamArchiv",
        "https://www.basketball-bund.net/index.jsp?Action=107&liga_id=17248&saison_id=2019&reqCode=statTeamArchiv", 
        "https://www.basketball-bund.net/index.jsp?Action=107&liga_id=17248&saison_id=2018&reqCode=statTeamArchiv",
        "https://www.basketball-bund.net/index.jsp?Action=107&liga_id=17248&saison_id=2017&reqCode=statTeamArchiv",
        
        # Different archive reqCodes
        "https://www.basketball-bund.net/index.jsp?Action=107&liga_id=17248&saison_id=2020&reqCode=statBesteWerferArchiv",
        "https://www.basketball-bund.net/index.jsp?Action=107&liga_id=17248&saison_id=2020&reqCode=statBesteFreiWerferArchiv",
        "https://www.basketball-bund.net/index.jsp?Action=107&liga_id=17248&saison_id=2020&reqCode=statBeste3erWerferArchiv",
        
        # Archive main pages
        "https://www.basketball-bund.net/index.jsp?Action=106&reqCode=bglArchiv&",
        "https://www.basketball-bund.net/index.jsp?Action=106",
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'ITEM_PIPELINES': {
            'basketball_scrapers.pipelines.JsonWriterPipeline': 300,
        },
        'FEEDS': {
            'test_archive_results.json': {
                'format': 'json',
                'encoding': 'utf8',
            }
        }
    }

    def parse(self, response):
        """Parse any response and analyze its structure"""
        url = response.url
        
        self.logger.info(f"🔍 Testing URL: {url}")
        self.logger.info(f"   Status: {response.status}")
        self.logger.info(f"   Content-Type: {response.headers.get('Content-Type', b'unknown').decode()}")
        self.logger.info(f"   Content length: {len(response.text)} characters")
        
        # Parse URL parameters
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        
        action = params.get('Action', [None])[0]
        liga_id = params.get('liga_id', [None])[0] 
        saison_id = params.get('saison_id', [None])[0]
        req_code = params.get('reqCode', [None])[0]
        
        # Analyze page structure
        analysis = {
            'type': 'url_test',
            'url': url,
            'action': action,
            'liga_id': liga_id,
            'saison_id': saison_id,
            'req_code': req_code,
            'status_code': response.status,
            'content_length': len(response.text),
            'analysis': {}
        }
        
        # Count different elements
        tables = response.css('table')
        analysis['analysis']['tables_found'] = len(tables)
        
        # Look for export buttons/links
        export_links = []
        for link in response.css('a[href*="export" i], a[href*="Export" i], a:contains("Export"), a:contains("export")'):
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            if href:
                export_links.append({'text': text, 'href': href})
        analysis['analysis']['export_links'] = export_links
        analysis['analysis']['export_links_count'] = len(export_links)
        
        # Look for boxscore links (Action=108)
        boxscore_links = []
        for link in response.css('a[href*="Action=108"]'):
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            if href:
                boxscore_links.append({'text': text, 'href': href})
        analysis['analysis']['boxscore_links'] = boxscore_links
        analysis['analysis']['boxscore_links_count'] = len(boxscore_links)
        
        # Look for league links
        league_links = []
        for link in response.css('a[href*="liga_id"]'):
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            if href and text:
                league_links.append({'text': text.strip(), 'href': href})
        analysis['analysis']['league_links'] = league_links[:5]  # First 5 only
        analysis['analysis']['league_links_count'] = len(league_links)
        
        # Check for error indicators
        error_indicators = []
        if "fehler" in response.text.lower() or "error" in response.text.lower():
            error_indicators.append("error_text_found")
        if len(response.text) < 1000:
            error_indicators.append("very_short_content")
        if response.status != 200:
            error_indicators.append(f"non_200_status_{response.status}")
        
        analysis['analysis']['error_indicators'] = error_indicators
        analysis['analysis']['has_errors'] = len(error_indicators) > 0
        
        # Sample of the page content (first 500 chars)
        analysis['analysis']['content_sample'] = response.text[:500]
        
        self.logger.info(f"   📊 Tables: {len(tables)}")
        self.logger.info(f"   📤 Export links: {len(export_links)}")
        self.logger.info(f"   🏀 Boxscore links: {len(boxscore_links)}")
        self.logger.info(f"   🔗 League links: {len(league_links)}")
        self.logger.info(f"   ⚠️ Error indicators: {error_indicators}")
        
        yield analysis
