import scrapy
import re
from urllib.parse import urljoin, parse_qs, urlparse


class ArchiveDebugSpider(scrapy.Spider):
    name = 'archive_debug'
    allowed_domains = ['basketball-bund.net']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
    }
    
    def start_requests(self):
        """Start with the main archive form page"""
        yield scrapy.Request(
            url='https://www.basketball-bund.net/index.jsp?Action=106',
            callback=self.parse_archive_form
        )
    
    def parse_archive_form(self, response):
        """Parse the main archive page and submit one POST request for debugging"""
        self.logger.info('🔍 Processing main archive form page')
        
        # Save the original form page for debugging
        with open('debug_form_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        self.logger.info('💾 Saved form page as debug_form_page.html')
        
        # Find the form
        form = response.css('form').get()
        if not form:
            self.logger.warning('❌ No form found on archive page')
            return
            
        # Submit one request for season 2020 to debug
        self.logger.info('📅 Submitting debug archive request for season 2020')
        
        formdata = {
            'saison_id': '2020',
            'cbSpielklasseFilter': '0',
            'cbAltersklasseFilter': '0',  
            'cbGeschlechtFilter': '0',
            'cbBezirkFilter': '0',
            'cbKreisFilter': '0'
        }
        
        yield scrapy.FormRequest.from_response(
            response,
            formdata=formdata,
            callback=self.parse_archive_results_debug,
            meta={'season': '2020'}
        )

    def parse_archive_results_debug(self, response):
        """Parse the results and save for debugging"""
        season = response.meta['season']
        
        self.logger.info(f'🗃️ Processing archive results for season {season}')
        self.logger.info(f'   URL: {response.url}')
        self.logger.info(f'   Status: {response.status}')
        self.logger.info(f'   Content length: {len(response.text)} characters')
        
        # Save the response for debugging
        with open(f'debug_archive_response_{season}.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        self.logger.info(f'💾 Saved response as debug_archive_response_{season}.html')
        
        # Check if this looks like the same form page
        has_form = len(response.css('form')) > 0
        has_season_select = 'saison_id' in response.text
        
        self.logger.info(f'   Has form: {has_form}')
        self.logger.info(f'   Has season select: {has_season_select}')
        
        # Count different elements for debugging
        tables = response.css('table')
        links = response.css('a[href]')
        
        self.logger.info(f'   Tables found: {len(tables)}')
        self.logger.info(f'   Links found: {len(links)}')
        
        # Look for specific patterns that indicate archive results
        archive_indicators = []
        if 'archiv' in response.text.lower():
            archive_indicators.append('archiv_text_found')
        if 'saison' in response.text.lower():
            archive_indicators.append('saison_text_found')
        if '2020' in response.text:
            archive_indicators.append('season_2020_found')
        
        self.logger.info(f'   Archive indicators: {archive_indicators}')
        
        # Sample some links to see their patterns
        sample_links = []
        for link in links[:10]:
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            if href and text:
                sample_links.append({'href': href, 'text': text.strip()})
        
        for i, link in enumerate(sample_links):
            self.logger.info(f'   Link {i+1}: {link["text"]} -> {link["href"][:50]}...')
        
        yield {
            'type': 'debug_response',
            'season': season,
            'url': response.url,
            'status': response.status,
            'content_length': len(response.text),
            'has_form': has_form,
            'has_season_select': has_season_select,
            'tables_found': len(tables),
            'links_found': len(links),
            'archive_indicators': archive_indicators,
            'sample_links': sample_links
        }
