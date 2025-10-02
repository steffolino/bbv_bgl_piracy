import scrapy
import re
from urllib.parse import urljoin, parse_qs, urlparse


class PresseExportSpider(scrapy.Spider):
    name = 'presse_export'
    allowed_domains = ['basketball-bund.net']
    
    def start_requests(self):
        """Start with key pages that should have export buttons"""
        start_urls = [
            'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow=0',
            'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow=10',
            'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow=50',
            'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow=100',
        ]
        
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_page)
    
    def parse_page(self, response):
        """Find presseExport.do links on the page"""
        self.logger.info(f'🔍 Looking for export buttons on: {response.url}')
        
        # Look for the specific export pattern
        export_links = response.css('a[href*="presseExport.do"]')
        self.logger.info(f'📤 Found {len(export_links)} presseExport links')
        
        for i, link in enumerate(export_links):
            href = link.css('::attr(href)').get()
            text = link.css('::text').get() or ''
            class_attr = link.css('::attr(class)').get() or ''
            
            if href:
                full_url = response.urljoin(href)
                
                self.logger.info(f'   Export {i+1}: "{text.strip()}" -> {href}')
                self.logger.info(f'     Class: {class_attr}')
                self.logger.info(f'     Full URL: {full_url}')
                
                # Follow the export link
                yield response.follow(
                    href,
                    callback=self.parse_export,
                    meta={
                        'source_page': response.url,
                        'export_text': text.strip(),
                        'export_href': href
                    }
                )
        
        # Also look for any other export-related links
        other_export_links = response.css('a[href*="export"], a[href*="Export"], a[class*="export"], a[class*="Export"]')
        other_export_links = [link for link in other_export_links if 'presseExport.do' not in link.css('::attr(href)').get('')]
        
        if other_export_links:
            self.logger.info(f'📋 Found {len(other_export_links)} other export-related links')
            for link in other_export_links:
                href = link.css('::attr(href)').get()
                text = link.css('::text').get() or ''
                if href:
                    self.logger.info(f'   Other export: "{text.strip()}" -> {href}')
        
        # Look for forms that might be export forms
        forms = response.css('form')
        for form in forms:
            action = form.css('::attr(action)').get() or ''
            if 'export' in action.lower() or any('export' in input.css('::attr(value)').get('').lower() 
                                                for input in form.css('input')):
                self.logger.info(f'📝 Found export form: action={action}')
        
        # Yield page info
        yield {
            'type': 'page_analysis',
            'url': response.url,
            'presse_export_count': len(export_links),
            'other_export_count': len(other_export_links),
            'presse_export_links': [
                {
                    'text': link.css('::text').get('').strip(),
                    'href': link.css('::attr(href)').get(),
                    'class': link.css('::attr(class)').get('')
                }
                for link in export_links
            ]
        }
    
    def parse_export(self, response):
        """Parse the export data from presseExport.do"""
        source_page = response.meta['source_page']
        export_text = response.meta['export_text']
        export_href = response.meta['export_href']
        
        self.logger.info(f'📊 Processing export from: {source_page}')
        self.logger.info(f'   Export URL: {response.url}')
        self.logger.info(f'   Status: {response.status}')
        
        # Get content info
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        content_length = len(response.body)
        
        self.logger.info(f'   Content-Type: {content_type}')
        self.logger.info(f'   Content-Length: {content_length} bytes')
        
        # Determine the format
        file_format = 'unknown'
        if 'text/csv' in content_type or 'application/csv' in content_type:
            file_format = 'csv'
        elif 'text/html' in content_type:
            file_format = 'html'
        elif 'application/json' in content_type:
            file_format = 'json'
        elif 'text/xml' in content_type or 'application/xml' in content_type:
            file_format = 'xml'
        else:
            # Try to detect from content
            content_start = response.body[:200].lower()
            if b'<html' in content_start or b'<table' in content_start:
                file_format = 'html'
            elif content_start.startswith(b'"') or b',' in content_start:
                file_format = 'csv'
            elif content_start.strip().startswith(b'{') or content_start.strip().startswith(b'['):
                file_format = 'json'
        
        self.logger.info(f'   Detected format: {file_format}')
        
        # Get content preview
        if response.text:
            preview = response.text[:500]
        else:
            preview = response.body[:500].decode('utf-8', errors='ignore')
        
        self.logger.info(f'   Content preview:\n{preview}')
        
        # Parse based on format
        parsed_data = None
        if file_format == 'csv':
            parsed_data = self.parse_csv_export(response.text)
        elif file_format == 'html':
            parsed_data = self.parse_html_export(response)
        elif file_format == 'json':
            try:
                import json
                parsed_data = json.loads(response.text)
            except:
                parsed_data = {'error': 'Invalid JSON'}
        
        # Yield the export data
        yield {
            'type': 'export_data',
            'source_page': source_page,
            'export_url': response.url,
            'export_text': export_text,
            'export_href': export_href,
            'content_type': content_type,
            'file_format': file_format,
            'size': content_length,
            'preview': preview[:200],
            'parsed_data': parsed_data
        }
    
    def parse_csv_export(self, csv_content):
        """Parse CSV export content"""
        if not csv_content:
            return None
            
        lines = csv_content.strip().split('\n')
        if not lines:
            return None
            
        # Try to parse as CSV
        rows = []
        for line in lines[:20]:  # First 20 rows
            if line.strip():
                # Simple CSV parsing (might need improvement for quoted fields)
                row = [field.strip().strip('"') for field in line.split(',')]
                rows.append(row)
        
        return {
            'total_lines': len(lines),
            'sample_rows': rows,
            'headers': rows[0] if rows else None
        }
    
    def parse_html_export(self, response):
        """Parse HTML export content"""
        tables = response.css('table')
        
        parsed_tables = []
        for i, table in enumerate(tables):
            rows = table.css('tr')
            
            table_data = {
                'table_index': i,
                'row_count': len(rows),
                'sample_rows': []
            }
            
            # Get first few rows
            for j, row in enumerate(rows[:10]):
                cells = row.css('td::text, th::text').getall()
                cells = [cell.strip() for cell in cells if cell.strip()]
                if cells:
                    table_data['sample_rows'].append({
                        'row_index': j,
                        'cells': cells
                    })
            
            parsed_tables.append(table_data)
        
        return {
            'table_count': len(tables),
            'tables': parsed_tables
        }
