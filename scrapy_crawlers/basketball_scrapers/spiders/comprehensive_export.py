import scrapy
import re
from urllib.parse import urljoin, parse_qs, urlparse


class ComprehensiveExportSpider(scrapy.Spider):
    name = 'comprehensive_export'
    allowed_domains = ['basketball-bund.net']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
    }
    
    def start_requests(self):
        """Start with comprehensive pagination + individual league pages"""
        # 1. Main league listing pages with different startrow values
        base_url = 'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow={}'
        start_rows = [0, 10, 20, 30, 50, 75, 100, 125, 150, 200, 250, 300, 400, 500]
        
        for start_row in start_rows:
            url = base_url.format(start_row)
            yield scrapy.Request(
                url=url,
                callback=self.parse_listing_page,
                meta={'start_row': start_row, 'page_type': 'listing'}
            )
        
        # 2. Example individual league page (Action=102) that we know has ExcelExport
        example_league_url = 'https://www.basketball-bund.net/index.jsp?Action=102&liga_id=47960'
        yield scrapy.Request(
            url=example_league_url,
            callback=self.parse_individual_league,
            meta={'page_type': 'individual_league', 'liga_id': '47960'}
        )
    
    def parse_listing_page(self, response):
        """Parse league listing pages to find export buttons and individual league links"""
        start_row = response.meta['start_row']
        self.logger.info(f'🔍 Processing listing page: startrow={start_row}')
        
        # Check if page has content
        if self.is_empty_page(response):
            self.logger.info(f'❌ Empty page at startrow={start_row}')
            return
        
        # 1. Look for presseExport.do links
        presse_exports = response.css('a[href*="presseExport.do"]')
        self.logger.info(f'📤 Found {len(presse_exports)} presseExport links')
        
        for export_link in presse_exports:
            href = export_link.css('::attr(href)').get()
            text = export_link.css('::text').get() or ''
            
            if href:
                self.logger.info(f'   presseExport: "{text.strip()}" -> {href}')
                yield response.follow(
                    href,
                    callback=self.parse_export_data,
                    meta={
                        'export_type': 'presse_export',
                        'source_url': response.url,
                        'start_row': start_row,
                        'export_text': text.strip()
                    }
                )
        
        # 2. Find individual league links (Action=102) to follow
        league_links = response.css('a[href*="Action=102"]')
        self.logger.info(f'🏀 Found {len(league_links)} individual league links')
        
        for league_link in league_links:
            href = league_link.css('::attr(href)').get()
            text = league_link.css('::text').get() or ''
            
            if href:
                # Extract liga_id
                liga_id_match = re.search(r'liga_id=(\d+)', href)
                liga_id = liga_id_match.group(1) if liga_id_match else None
                
                self.logger.info(f'   League: "{text.strip()}" -> liga_id={liga_id}')
                yield response.follow(
                    href,
                    callback=self.parse_individual_league,
                    meta={
                        'page_type': 'individual_league',
                        'liga_id': liga_id,
                        'league_name': text.strip(),
                        'source_start_row': start_row
                    }
                )
        
        # Yield summary of this page
        yield {
            'type': 'listing_page_summary',
            'url': response.url,
            'start_row': start_row,
            'presse_exports_found': len(presse_exports),
            'league_links_found': len(league_links)
        }
    
    def parse_individual_league(self, response):
        """Parse individual league pages for JavaScript exports and other data"""
        liga_id = response.meta.get('liga_id')
        league_name = response.meta.get('league_name', 'Unknown')
        
        self.logger.info(f'🏆 Processing individual league: {league_name} (ID: {liga_id})')
        
        # 1. Look for presseExport.do links
        presse_exports = response.css('a[href*="presseExport.do"]')
        for export_link in presse_exports:
            href = export_link.css('::attr(href)').get()
            text = export_link.css('::text').get() or ''
            
            if href:
                yield response.follow(
                    href,
                    callback=self.parse_export_data,
                    meta={
                        'export_type': 'presse_export_individual',
                        'source_url': response.url,
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'export_text': text.strip()
                    }
                )
        
        # 2. Look for JavaScript export buttons (like ExcelExport)
        js_exports = response.css('a[href*="javascript:"], a[onclick]')
        excel_exports = []
        
        for js_link in js_exports:
            href = js_link.css('::attr(href)').get() or ''
            onclick = js_link.css('::attr(onclick)').get() or ''
            text = js_link.css('::text').get() or ''
            
            # Check if it's an Excel/Export function
            if 'excel' in (href + onclick + text).lower() or 'export' in (href + onclick + text).lower():
                excel_exports.append({
                    'href': href,
                    'onclick': onclick,
                    'text': text.strip()
                })
                
                self.logger.info(f'🔧 Found JS export: "{text.strip()}" - {href}{onclick}')
                
                # Try to construct the actual export URL
                export_url = self.construct_excel_export_url(response.url, liga_id)
                if export_url:
                    yield response.follow(
                        export_url,
                        callback=self.parse_export_data,
                        meta={
                            'export_type': 'excel_export',
                            'source_url': response.url,
                            'liga_id': liga_id,
                            'league_name': league_name,
                            'export_text': text.strip(),
                            'js_function': href + onclick
                        }
                    )
        
        # 3. Look for other potential export URLs in the page source
        self.find_hidden_exports(response, liga_id, league_name)
        
        # Yield summary of individual league
        yield {
            'type': 'individual_league_summary',
            'url': response.url,
            'liga_id': liga_id,
            'league_name': league_name,
            'presse_exports_found': len(presse_exports),
            'js_exports_found': len(excel_exports)
        }
    
    def construct_excel_export_url(self, current_url, liga_id):
        """Try to construct Excel export URL based on common patterns"""
        if not liga_id:
            return None
        
        # Common patterns for Excel exports
        possible_urls = [
            f'https://www.basketball-bund.net/excelExport.do?liga_id={liga_id}',
            f'https://www.basketball-bund.net/excelExport.do?liga_id={liga_id}&format=excel',
            f'https://www.basketball-bund.net/presseExport.do?reqCode=excelExport&liga_id={liga_id}',
            f'https://www.basketball-bund.net/export.do?action=excel&liga_id={liga_id}',
        ]
        
        # Return the most likely one first
        return possible_urls[0]
    
    def find_hidden_exports(self, response, liga_id, league_name):
        """Look for export URLs hidden in JavaScript or page source"""
        page_source = response.text
        
        # Patterns to look for export URLs
        export_patterns = [
            r'(excelExport\.do[^"\'\s<>]*)',
            r'(presseExport\.do[^"\'\s<>]*)',
            r'([^"\'\s<>]*Action=\d+[^"\'\s<>]*format=[^"\'\s<>]*)',
        ]
        
        found_urls = set()
        for pattern in export_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            for match in matches:
                if match not in found_urls and 'liga_id' in match:
                    found_urls.add(match)
                    full_url = response.urljoin(match)
                    
                    self.logger.info(f'🔍 Found hidden export: {match}')
                    yield response.follow(
                        full_url,
                        callback=self.parse_export_data,
                        meta={
                            'export_type': 'hidden_export',
                            'source_url': response.url,
                            'liga_id': liga_id,
                            'league_name': league_name,
                            'export_text': f'Hidden: {match[:30]}...',
                            'hidden_url': match
                        }
                    )
    
    def is_empty_page(self, response):
        """Check if page has no results"""
        indicators = ['keine ergebnisse', 'no results', 'empty']
        body_text = response.text.lower()
        return any(indicator in body_text for indicator in indicators)
    
    def parse_export_data(self, response):
        """Parse all types of export data"""
        export_type = response.meta['export_type']
        source_url = response.meta['source_url']
        liga_id = response.meta.get('liga_id')
        league_name = response.meta.get('league_name')
        export_text = response.meta.get('export_text', 'Unknown')
        
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        content_length = len(response.body)
        
        self.logger.info(f'📊 Processing {export_type}: "{export_text}"')
        self.logger.info(f'   From: {source_url}')
        self.logger.info(f'   Liga ID: {liga_id}')
        self.logger.info(f'   Content-Type: {content_type}')
        self.logger.info(f'   Size: {content_length} bytes')
        
        # Detect format
        file_format = self.detect_format(response, content_type)
        self.logger.info(f'   Format: {file_format}')
        
        # Get preview
        preview = self.get_content_preview(response)
        self.logger.info(f'   Preview: {preview[:100]}...')
        
        # Parse based on format
        parsed_data = None
        if file_format == 'csv':
            parsed_data = self.parse_csv_data(response.text)
        elif file_format == 'html':
            parsed_data = self.parse_html_data(response)
        elif file_format == 'json':
            parsed_data = self.parse_json_data(response.text)
        elif file_format == 'excel':
            parsed_data = {'note': 'Excel file detected - would need special handling'}
        
        yield {
            'type': 'export_data',
            'export_type': export_type,
            'export_text': export_text,
            'source_url': source_url,
            'export_url': response.url,
            'liga_id': liga_id,
            'league_name': league_name,
            'content_type': content_type,
            'file_format': file_format,
            'size': content_length,
            'preview': preview[:200],
            'parsed_data': parsed_data
        }
    
    def detect_format(self, response, content_type):
        """Detect export data format"""
        if 'csv' in content_type.lower():
            return 'csv'
        elif 'html' in content_type.lower():
            return 'html'
        elif 'json' in content_type.lower():
            return 'json'
        elif 'excel' in content_type.lower() or 'spreadsheet' in content_type.lower():
            return 'excel'
        else:
            # Auto-detect from content
            content_start = response.body[:300].lower()
            if b'<html' in content_start or b'<table' in content_start:
                return 'html'
            elif b',' in content_start and (b'"' in content_start or b';' in content_start):
                return 'csv'
            elif content_start.strip().startswith(b'{'):
                return 'json'
            else:
                return 'text'
    
    def get_content_preview(self, response):
        """Get content preview"""
        if response.text:
            return response.text[:300]
        else:
            return response.body[:300].decode('utf-8', errors='ignore')
    
    def parse_csv_data(self, content):
        """Parse CSV content"""
        if not content:
            return {'error': 'Empty content'}
        
        lines = content.strip().split('\n')
        rows = []
        
        for line in lines[:20]:  # First 20 lines
            if line.strip():
                row = [field.strip().strip('"\'') for field in line.split(',')]
                rows.append(row)
        
        return {
            'format': 'csv',
            'total_lines': len(lines),
            'headers': rows[0] if rows else [],
            'sample_rows': rows[1:10] if len(rows) > 1 else []
        }
    
    def parse_html_data(self, response):
        """Parse HTML content"""
        tables = response.css('table')
        
        parsed_tables = []
        for i, table in enumerate(tables[:3]):  # First 3 tables
            rows = table.css('tr')
            
            sample_rows = []
            for row in rows[:10]:  # First 10 rows per table
                cells = row.css('td::text, th::text').getall()
                cells = [cell.strip() for cell in cells if cell.strip()]
                if cells:
                    sample_rows.append(cells)
            
            parsed_tables.append({
                'table_index': i,
                'row_count': len(rows),
                'sample_rows': sample_rows
            })
        
        return {
            'format': 'html',
            'table_count': len(tables),
            'tables': parsed_tables
        }
    
    def parse_json_data(self, content):
        """Parse JSON content"""
        try:
            import json
            data = json.loads(content)
            return {
                'format': 'json',
                'data': data if len(str(data)) < 500 else str(data)[:500]
            }
        except:
            return {
                'format': 'json',
                'error': 'Invalid JSON'
            }
