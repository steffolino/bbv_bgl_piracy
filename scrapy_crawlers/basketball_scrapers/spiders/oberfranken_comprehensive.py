import scrapy
import re
from urllib.parse import urljoin, parse_qs, urlparse


class OberfrankenLeagueSpider(scrapy.Spider):
    name = 'oberfranken_leagues'
    allowed_domains = ['basketball-bund.net']
    
    # This will crawl all pages systematically for Bezirk Oberfranken (Verband=2)
    custom_settings = {
        'DOWNLOAD_DELAY': 2,  # Be respectful with delays
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'FEEDS': {
            'oberfranken_leagues.json': {
                'format': 'json',
                'overwrite': True
            }
        }
    }
    
    def start_requests(self):
        """Generate requests for all pagination pages"""
        base_url = 'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow={}'
        
        # Start with a wider range to ensure we get everything
        start_rows = list(range(0, 1000, 10))  # 0, 10, 20, 30, ..., 990
        
        for start_row in start_rows:
            url = base_url.format(start_row)
            yield scrapy.Request(
                url=url,
                callback=self.parse_league_page,
                meta={'start_row': start_row},
                dont_filter=True  # Allow duplicate URLs with different parameters
            )
    
    def parse_league_page(self, response):
        """Parse each page to extract league data and export links"""
        start_row = response.meta['start_row']
        
        # Check if page has actual content
        if self.is_empty_page(response):
            self.logger.info(f'❌ Empty page at startrow={start_row}')
            return
        
        self.logger.info(f'🔍 Processing page startrow={start_row}')
        
        # 1. Look for export buttons first (most reliable)
        export_links = response.css('a[href*="presseExport.do"]')
        
        if export_links:
            for link in export_links:
                href = link.css('::attr(href)').get()
                if href:
                    self.logger.info(f'📤 Found export link: {href}')
                    yield response.follow(
                        href,
                        callback=self.parse_export_data,
                        meta={
                            'source_page': response.url,
                            'start_row': start_row,
                            'export_type': 'presse_export'
                        }
                    )
        
        # 2. Extract league links directly from the page
        league_data = self.extract_leagues_from_page(response, start_row)
        
        for league in league_data:
            yield league
        
        # 3. Look for individual league pages to follow
        league_detail_links = response.css('a[href*="Action=100"]')
        
        for link in league_detail_links:
            href = link.css('::attr(href)').get()
            text = link.css('::text').get() or ''
            
            if href and href != response.url:  # Avoid self-reference
                # Only follow if it looks like a specific league
                if any(keyword in text.lower() for keyword in ['liga', 'klasse', 'herren', 'damen', 'jugend']):
                    yield response.follow(
                        href,
                        callback=self.parse_league_detail,
                        meta={
                            'league_name': text.strip(),
                            'source_start_row': start_row
                        }
                    )
    
    def is_empty_page(self, response):
        """Check if the page has no results"""
        # Look for indicators of empty pages
        body_text = response.css('body').get('')
        
        empty_indicators = [
            'keine ergebnisse',
            'no results',
            'empty',
            'leer'
        ]
        
        if any(indicator in body_text.lower() for indicator in empty_indicators):
            return True
        
        # Check if there are very few tables or links
        tables = response.css('table')
        links = response.css('a[href*="Action="]')
        
        # If less than 2 tables and less than 5 action links, probably empty
        if len(tables) < 2 and len(links) < 5:
            return True
        
        return False
    
    def extract_leagues_from_page(self, response, start_row):
        """Extract league information directly from the HTML"""
        leagues = []
        
        # Look for tables that contain league information
        tables = response.css('table')
        
        for table_idx, table in enumerate(tables):
            rows = table.css('tr')
            
            if len(rows) < 2:  # Skip tables with no data rows
                continue
            
            # Check if this table contains league data
            table_text = ' '.join(table.css('::text').getall()).lower()
            league_keywords = ['liga', 'spielklasse', 'herren', 'damen', 'jugend', 'bezirk']
            
            if not any(keyword in table_text for keyword in league_keywords):
                continue
            
            self.logger.info(f'📊 Processing league table {table_idx} with {len(rows)} rows')
            
            # Extract data from each row
            for row_idx, row in enumerate(rows[1:], 1):  # Skip header row
                cells = row.css('td')
                if not cells:
                    continue
                
                row_data = {
                    'type': 'league_entry',
                    'source_url': response.url,
                    'start_row': start_row,
                    'table_index': table_idx,
                    'row_index': row_idx,
                    'cells': [],
                    'links': []
                }
                
                # Extract cell data
                for cell_idx, cell in enumerate(cells):
                    cell_text = cell.css('::text').get() or ''
                    cell_text = cell_text.strip()
                    
                    if cell_text:
                        row_data['cells'].append({
                            'index': cell_idx,
                            'text': cell_text
                        })
                    
                    # Extract links from cell
                    cell_links = cell.css('a')
                    for link in cell_links:
                        link_href = link.css('::attr(href)').get()
                        link_text = link.css('::text').get() or ''
                        
                        if link_href:
                            row_data['links'].append({
                                'href': link_href,
                                'text': link_text.strip(),
                                'full_url': response.urljoin(link_href),
                                'cell_index': cell_idx
                            })
                
                if row_data['cells'] or row_data['links']:
                    leagues.append(row_data)
        
        self.logger.info(f'✅ Extracted {len(leagues)} league entries from startrow={start_row}')
        return leagues
    
    def parse_league_detail(self, response):
        """Parse individual league detail pages"""
        league_name = response.meta['league_name']
        source_start_row = response.meta['source_start_row']
        
        self.logger.info(f'🏀 Processing league detail: {league_name}')
        
        # Look for export buttons on this page too
        export_links = response.css('a[href*="presseExport.do"]')
        
        for link in export_links:
            href = link.css('::attr(href)').get()
            if href:
                yield response.follow(
                    href,
                    callback=self.parse_export_data,
                    meta={
                        'source_page': response.url,
                        'league_name': league_name,
                        'source_start_row': source_start_row,
                        'export_type': 'league_detail_export'
                    }
                )
        
        # Extract any additional data from this detail page
        yield {
            'type': 'league_detail',
            'league_name': league_name,
            'url': response.url,
            'source_start_row': source_start_row,
            'title': response.css('title::text').get(),
            'has_export': len(export_links) > 0
        }
    
    def parse_export_data(self, response):
        """Parse exported data (CSV, HTML, etc.)"""
        source_page = response.meta['source_page']
        export_type = response.meta.get('export_type', 'unknown')
        start_row = response.meta.get('start_row')
        league_name = response.meta.get('league_name')
        
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        
        self.logger.info(f'📊 Processing export data:')
        self.logger.info(f'   Source: {source_page}')
        self.logger.info(f'   Type: {export_type}')
        self.logger.info(f'   Content-Type: {content_type}')
        self.logger.info(f'   Size: {len(response.body)} bytes')
        
        # Determine format and parse
        if 'csv' in content_type.lower():
            parsed_data = self.parse_csv_data(response.text)
        elif 'html' in content_type.lower():
            parsed_data = self.parse_html_data(response)
        else:
            # Try to auto-detect
            content_preview = response.body[:200]
            if b'<table' in content_preview or b'<html' in content_preview:
                parsed_data = self.parse_html_data(response)
            elif b',' in content_preview and (b'"' in content_preview or b';' in content_preview):
                parsed_data = self.parse_csv_data(response.text)
            else:
                parsed_data = {'raw_preview': response.text[:500]}
        
        yield {
            'type': 'export_data',
            'export_type': export_type,
            'source_page': source_page,
            'export_url': response.url,
            'start_row': start_row,
            'league_name': league_name,
            'content_type': content_type,
            'size': len(response.body),
            'parsed_data': parsed_data
        }
    
    def parse_csv_data(self, csv_text):
        """Parse CSV export data"""
        if not csv_text:
            return {}
        
        lines = csv_text.strip().split('\n')
        rows = []
        
        for line in lines[:50]:  # First 50 lines
            if line.strip():
                # Basic CSV parsing
                row = [field.strip().strip('"\'') for field in line.split(',')]
                rows.append(row)
        
        return {
            'format': 'csv',
            'total_lines': len(lines),
            'headers': rows[0] if rows else [],
            'sample_rows': rows[1:10] if len(rows) > 1 else [],
            'row_count': len(rows)
        }
    
    def parse_html_data(self, response):
        """Parse HTML export data"""
        tables = response.css('table')
        
        parsed_tables = []
        for i, table in enumerate(tables):
            rows = table.css('tr')
            
            table_rows = []
            for row in rows[:20]:  # First 20 rows
                cells = row.css('td::text, th::text').getall()
                cells = [cell.strip() for cell in cells if cell.strip()]
                if cells:
                    table_rows.append(cells)
            
            if table_rows:
                parsed_tables.append({
                    'table_index': i,
                    'row_count': len(rows),
                    'headers': table_rows[0] if table_rows else [],
                    'sample_rows': table_rows[1:10] if len(table_rows) > 1 else []
                })
        
        return {
            'format': 'html',
            'table_count': len(tables),
            'tables': parsed_tables
        }
