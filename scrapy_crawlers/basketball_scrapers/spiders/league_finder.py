import scrapy
import re
from urllib.parse import urljoin


class LeagueFinderSpider(scrapy.Spider):
    name = 'league_finder'
    allowed_domains = ['basketball-bund.net']
    
    def start_requests(self):
        """Generate requests for multiple pages to handle pagination"""
        base_url = 'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow={}'
        
        # Try multiple start rows to get all paginated results
        start_rows = [0, 10, 20, 50, 100, 200, 500, 1000]
        
        for start_row in start_rows:
            url = base_url.format(start_row)
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'start_row': start_row}
            )
    
    def parse(self, response):
        """Find and analyze league tables on the page"""
        start_row = response.meta.get('start_row', 0)
        self.logger.info(f'🔍 Analyzing page: {response.url} (startrow={start_row})')
        self.logger.info(f'📄 Page title: {response.css("title::text").get()}')
        
        # Check if this page has content (not empty)
        page_content = response.css('body').get()
        if not page_content or 'keine Ergebnisse' in page_content.lower():
            self.logger.info(f'❌ No results found for startrow={start_row}')
            return
        
        # Find all tables
        tables = response.css('table')
        self.logger.info(f'📊 Found {len(tables)} tables total')
        
        # Look for tables that contain league information
        league_tables = []
        
        for i, table in enumerate(tables):
            # Get all text content
            table_text = ' '.join(table.css('::text').getall()).lower()
            
            # Look for league-related keywords
            league_keywords = ['liga', 'spielklasse', 'championship', 'pokal', 'cup', 'herren', 'damen', 'jugend']
            has_league_content = any(keyword in table_text for keyword in league_keywords)
            
            # Count links in the table
            links = table.css('a')
            link_count = len(links)
            
            # Count rows
            rows = table.css('tr')
            row_count = len(rows)
            
            if has_league_content and link_count > 0 and row_count > 1:
                league_tables.append({
                    'index': i,
                    'table': table,
                    'row_count': row_count,
                    'link_count': link_count,
                    'keywords_found': [kw for kw in league_keywords if kw in table_text]
                })
                
                self.logger.info(f'🏀 Found potential league table {i}: {row_count} rows, {link_count} links')
                self.logger.info(f'   Keywords found: {[kw for kw in league_keywords if kw in table_text]}')
        
        self.logger.info(f'🎯 Found {len(league_tables)} potential league tables')
        
        # Analyze the most promising tables
        for table_info in league_tables[:3]:  # Top 3 tables
            yield from self.analyze_league_table(table_info, response)
    
    def analyze_league_table(self, table_info, response):
        """Analyze a specific table that appears to contain league information"""
        table = table_info['table']
        index = table_info['index']
        
        self.logger.info(f'\n📋 Analyzing League Table {index}:')
        
        # Get all links from this table
        links = []
        for link in table.css('a'):
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            
            if href and text:
                full_url = response.urljoin(href)
                links.append({
                    'text': text.strip(),
                    'url': full_url,
                    'href': href
                })
        
        # Group links by type (based on URL patterns)
        link_types = {
            'leagues': [],
            'teams': [],
            'games': [],
            'results': [],
            'other': []
        }
        
        for link in links:
            href = link['href'].lower()
            text = link['text'].lower()
            
            # Categorize links
            if 'action=100' in href or 'spielklasse' in href or 'liga' in text:
                link_types['leagues'].append(link)
            elif 'action=200' in href or 'mannschaft' in href or 'team' in text:
                link_types['teams'].append(link)
            elif 'action=300' in href or 'spiel' in href or 'game' in text:
                link_types['games'].append(link)
            elif 'result' in href or 'ergebnis' in href or 'tabelle' in href:
                link_types['results'].append(link)
            else:
                link_types['other'].append(link)
        
        # Report findings
        for link_type, type_links in link_types.items():
            if type_links:
                self.logger.info(f'   {link_type.upper()} ({len(type_links)} links):')
                for link in type_links[:5]:  # Show first 5 of each type
                    self.logger.info(f'     "{link["text"]}" -> {link["url"]}')
        
        # Look for table structure
        rows = table.css('tr')
        if len(rows) > 1:
            self.logger.info(f'   📊 Table structure:')
            
            # Analyze first row (headers)
            first_row = rows[0]
            headers = [cell.css('::text').get() or '' for cell in first_row.css('th, td')]
            headers = [h.strip() for h in headers if h.strip()]
            
            if headers:
                self.logger.info(f'     Headers: {headers}')
            
            # Analyze a few data rows
            for i, row in enumerate(rows[1:4]):  # First 3 data rows
                cells = []
                row_links = []
                
                for cell in row.css('td'):
                    # Get cell text
                    cell_text = cell.css('::text').get()
                    if cell_text:
                        cells.append(cell_text.strip())
                    
                    # Get cell links
                    cell_link = cell.css('a')
                    if cell_link:
                        href = cell_link.css('::attr(href)').get()
                        link_text = cell_link.css('::text').get()
                        if href and link_text:
                            row_links.append(f'"{link_text.strip()}" -> {response.urljoin(href)}')
                
                if cells or row_links:
                    self.logger.info(f'     Row {i+1}: {cells}')
                    if row_links:
                        self.logger.info(f'       Links: {row_links}')
        
        # Yield structured data
        yield {
            'type': 'league_table',
            'table_index': index,
            'url': response.url,
            'start_row': response.meta.get('start_row', 0),
            'row_count': table_info['row_count'],
            'link_count': table_info['link_count'],
            'keywords_found': table_info['keywords_found'],
            'links': links,
            'link_types': {k: len(v) for k, v in link_types.items()}
        }
