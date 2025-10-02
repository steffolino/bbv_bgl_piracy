import scrapy
from datetime import datetime
import re

class HtmlAnalysisSpider(scrapy.Spider):
    name = 'html_analysis'
    allowed_domains = ['basketball-bund.net']
    
    start_urls = [
        'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow=10'
    ]
    
    def parse(self, response):
        """Analyze the HTML structure of the league overview page"""
        self.logger.info(f'🔍 Analyzing HTML structure: {response.url}')
        
        # Basic page info
        title = response.css('title::text').get()
        self.logger.info(f'📄 Page title: {title}')
        
        # Look for tables that might contain league information
        tables = response.css('table')
        self.logger.info(f'📊 Found {len(tables)} tables')
        
        for table_idx, table in enumerate(tables):
            self.analyze_table(table, table_idx, response)
        
        # Look for specific league-related links
        self.analyze_league_links(response)
        
        # Look for any forms that might be used for navigation
        self.analyze_forms(response)
        
        # Check for pagination or "next page" links
        self.analyze_pagination(response)
    
    def analyze_table(self, table, table_idx, response):
        """Analyze individual table structure"""
        rows = table.css('tr')
        
        if len(rows) < 2:
            return
            
        self.logger.info(f'🏀 Table {table_idx}: {len(rows)} rows')
        
        # Analyze headers
        header_row = rows[0]
        headers = []
        
        for cell in header_row.css('th, td'):
            header_text = cell.css('::text').get()
            if header_text:
                headers.append(header_text.strip())
        
        if headers:
            self.logger.info(f'   Headers: {headers}')
        
        # Analyze first few data rows
        for row_idx, row in enumerate(rows[1:6]):  # First 5 data rows
            cells = []
            links = []
            
            for cell in row.css('td'):
                # Get text content
                cell_text = ' '.join(cell.css('::text').getall()).strip()
                cells.append(cell_text)
                
                # Get any links in this cell
                cell_links = cell.css('a::attr(href)').getall()
                for link in cell_links:
                    link_text = cell.css('a::text').get() or ''
                    links.append({
                        'url': link,
                        'text': link_text.strip(),
                        'cell_index': len(cells) - 1
                    })
            
            if cells or links:
                self.logger.info(f'   Row {row_idx + 1}:')
                if cells:
                    self.logger.info(f'     Data: {cells[:5]}')  # First 5 cells
                if links:
                    link_summaries = []
                    for l in links[:3]:
                        link_summaries.append(f'{l["text"]} -> {l["url"]}')
                    self.logger.info(f'     Links: {link_summaries}')
                
                # Yield this as structured data
                yield {
                    'type': 'table_row',
                    'source': 'HTML_ANALYSIS',
                    'table_index': table_idx,
                    'row_index': row_idx,
                    'headers': headers,
                    'cells': cells,
                    'links': links,
                    'url': response.url,
                    'scraped_at': datetime.now().isoformat()
                }
    
    def analyze_league_links(self, response):
        """Look for specific patterns in league-related links"""
        self.logger.info('🔗 Analyzing league links...')
        
        # Look for various types of basketball-related links
        link_patterns = [
            ('Action=107', 'League Table'),
            ('Action=108', 'Fixtures'),
            ('statistik.do', 'Statistics'),
            ('scouting.do', 'Boxscores'),
            ('liga_id=', 'League ID'),
            ('saison_id=', 'Season ID'),
        ]
        
        for pattern, description in link_patterns:
            links = response.css(f'a[href*="{pattern}"]')
            
            if links:
                self.logger.info(f'   {description}: {len(links)} links found')
                
                for i, link in enumerate(links[:3]):  # First 3 examples
                    href = link.css('::attr(href)').get()
                    text = link.css('::text').get() or ''
                    self.logger.info(f'     {i+1}. {text.strip()} -> {href}')
                    
                    # Extract IDs from URLs
                    if 'liga_id=' in href:
                        liga_match = re.search(r'liga_id=(\d+)', href)
                        season_match = re.search(r'saison_id=(\d+)', href)
                        
                        yield {
                            'type': 'league_link',
                            'source': 'HTML_ANALYSIS',
                            'link_type': description,
                            'text': text.strip(),
                            'url': href,
                            'liga_id': liga_match.group(1) if liga_match else None,
                            'season_id': season_match.group(1) if season_match else None,
                            'scraped_at': datetime.now().isoformat()
                        }
    
    def analyze_forms(self, response):
        """Analyze forms that might be used for navigation"""
        forms = response.css('form')
        self.logger.info(f'📝 Found {len(forms)} forms')
        
        for form_idx, form in enumerate(forms):
            action = form.css('::attr(action)').get()
            method = form.css('::attr(method)').get() or 'GET'
            
            # Get form inputs
            inputs = []
            for input_elem in form.css('input, select'):
                input_name = input_elem.css('::attr(name)').get()
                input_type = input_elem.css('::attr(type)').get()
                input_value = input_elem.css('::attr(value)').get()
                
                if input_name:
                    inputs.append({
                        'name': input_name,
                        'type': input_type,
                        'value': input_value
                    })
            
            if action or inputs:
                self.logger.info(f'   Form {form_idx}: {method} {action}')
                for inp in inputs[:5]:  # First 5 inputs
                    self.logger.info(f'     {inp["name"]} ({inp["type"]}): {inp["value"]}')
    
    def analyze_pagination(self, response):
        """Look for pagination controls"""
        self.logger.info('📄 Analyzing pagination...')
        
        # Common pagination patterns
        pagination_selectors = [
            'a[href*="startrow"]',
            'a:contains("weiter")',
            'a:contains("nächste")',
            'a:contains(">")',
            '.pagination a',
            '[class*="pag"] a'
        ]
        
        for selector in pagination_selectors:
            links = response.css(selector)
            if links:
                self.logger.info(f'   Pagination ({selector}): {len(links)} links')
                
                for link in links[:3]:
                    href = link.css('::attr(href)').get()
                    text = link.css('::text').get() or ''
                    self.logger.info(f'     {text.strip()} -> {href}')
                    
                    # If this looks like a "next page" link, follow it
                    if href and ('startrow=' in href or 'weiter' in text.lower()):
                        yield response.follow(href, self.parse_next_page)
    
    def parse_next_page(self, response):
        """Parse additional pages to get more leagues"""
        self.logger.info(f'📄 Analyzing next page: {response.url}')
        
        # Reuse the same analysis logic
        yield from self.parse(response)
