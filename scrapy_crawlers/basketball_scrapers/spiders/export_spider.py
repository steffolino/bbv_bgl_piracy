import scrapy
import re
from urllib.parse import urljoin, parse_qs, urlparse


class ExportButtonSpider(scrapy.Spider):
    name = 'export_spider'
    allowed_domains = ['basketball-bund.net']
    
    def start_requests(self):
        """Start with a few key pages to find export buttons"""
        start_urls = [
            'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow=0',
            'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow=10',
            'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow=50',
        ]
        
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        """Find export buttons and forms on the page"""
        self.logger.info(f'🔍 Analyzing exports on: {response.url}')
        
        # Look for export buttons, links, and forms
        export_elements = self.find_export_elements(response)
        
        for export_info in export_elements:
            self.logger.info(f'📤 Found export: {export_info["type"]} - {export_info["text"]} -> {export_info["url"]}')
            
            # Try to download the export
            if export_info['url']:
                yield response.follow(
                    export_info['url'],
                    callback=self.parse_export,
                    meta={
                        'export_info': export_info,
                        'source_url': response.url
                    }
                )
        
        # Also yield info about what we found
        yield {
            'type': 'export_discovery',
            'page_url': response.url,
            'exports_found': export_elements
        }
    
    def find_export_elements(self, response):
        """Find all export-related elements on the page"""
        export_elements = []
        
        # 1. Look for explicit export buttons/links
        export_patterns = [
            'export', 'csv', 'excel', 'download', 'save', 
            'html', 'pdf', 'print', 'ausgabe'
        ]
        
        # Check all links
        for link in response.css('a'):
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            
            if href and text:
                text = text.strip().lower()
                href_lower = href.lower()
                
                # Check if this looks like an export link
                is_export = any(pattern in text for pattern in export_patterns) or \
                           any(pattern in href_lower for pattern in export_patterns) or \
                           'format=' in href_lower or 'type=' in href_lower
                
                if is_export:
                    export_elements.append({
                        'type': 'link',
                        'text': text,
                        'url': response.urljoin(href),
                        'href': href
                    })
        
        # 2. Look for forms that might be export forms
        for form in response.css('form'):
            # Check form inputs and buttons
            form_text = ' '.join(form.css('::text').getall()).lower()
            
            # Look for export-related words in form
            if any(pattern in form_text for pattern in export_patterns):
                action = form.css('::attr(action)').get() or response.url
                method = form.css('::attr(method)').get() or 'get'
                
                # Get form inputs
                inputs = {}
                for input_elem in form.css('input, select'):
                    name = input_elem.css('::attr(name)').get()
                    value = input_elem.css('::attr(value)').get()
                    input_type = input_elem.css('::attr(type)').get()
                    
                    if name:
                        inputs[name] = {
                            'value': value,
                            'type': input_type
                        }
                
                export_elements.append({
                    'type': 'form',
                    'text': form_text[:100],  # First 100 chars
                    'url': response.urljoin(action),
                    'method': method,
                    'inputs': inputs
                })
        
        # 3. Look for JavaScript links that might trigger exports
        js_links = response.css('a[href*="javascript:"], a[onclick]')
        for link in js_links:
            onclick = link.css('::attr(onclick)').get() or ''
            href = link.css('::attr(href)').get() or ''
            text = link.css('::text').get() or ''
            
            if any(pattern in (onclick + href + text).lower() for pattern in export_patterns):
                export_elements.append({
                    'type': 'javascript',
                    'text': text.strip(),
                    'url': None,  # Can't follow JS directly
                    'onclick': onclick,
                    'href': href
                })
        
        # 4. Look for specific export URL patterns in page source
        page_source = response.text
        export_url_patterns = [
            r'Action=\d+[^"\']*format=[^"\']*',
            r'export[^"\']*\.jsp[^"\']*',
            r'download[^"\']*\.jsp[^"\']*'
        ]
        
        for pattern in export_url_patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            for match in matches[:5]:  # Limit to first 5 matches
                if 'http' not in match:  # Relative URL
                    full_url = response.urljoin(match)
                else:
                    full_url = match
                    
                export_elements.append({
                    'type': 'url_pattern',
                    'text': f'Found in source: {match[:50]}...',
                    'url': full_url,
                    'pattern': match
                })
        
        return export_elements
    
    def parse_export(self, response):
        """Parse the downloaded export data"""
        export_info = response.meta['export_info']
        source_url = response.meta['source_url']
        
        content_type = response.headers.get('Content-Type', b'').decode('utf-8').lower()
        
        self.logger.info(f'📊 Downloaded export: {export_info["text"]}')
        self.logger.info(f'   Content-Type: {content_type}')
        self.logger.info(f'   Size: {len(response.body)} bytes')
        
        # Determine format based on content type and content
        file_format = 'unknown'
        if 'csv' in content_type or response.body.startswith(b'"') or b',' in response.body[:100]:
            file_format = 'csv'
        elif 'html' in content_type or b'<html' in response.body[:200].lower():
            file_format = 'html'
        elif 'xml' in content_type or b'<?xml' in response.body[:100]:
            file_format = 'xml'
        elif 'json' in content_type or response.body.strip().startswith(b'{'):
            file_format = 'json'
        
        # Preview content
        preview = response.text[:500] if response.text else response.body[:500].decode('utf-8', errors='ignore')
        
        self.logger.info(f'   Detected format: {file_format}')
        self.logger.info(f'   Preview: {preview[:200]}...')
        
        # For CSV files, try to parse structure
        if file_format == 'csv':
            lines = response.text.split('\n')[:10]  # First 10 lines
            self.logger.info(f'   CSV structure:')
            for i, line in enumerate(lines):
                if line.strip():
                    self.logger.info(f'     Line {i+1}: {line[:100]}')
        
        # For HTML, look for tables
        elif file_format == 'html':
            tables = response.css('table')
            self.logger.info(f'   HTML contains {len(tables)} tables')
            for i, table in enumerate(tables[:3]):
                rows = table.css('tr')
                self.logger.info(f'     Table {i+1}: {len(rows)} rows')
                if rows:
                    first_row = rows[0].css('td::text, th::text').getall()
                    self.logger.info(f'       Headers/First row: {first_row[:5]}')
        
        yield {
            'type': 'export_data',
            'source_url': source_url,
            'export_url': response.url,
            'export_info': export_info,
            'content_type': content_type,
            'file_format': file_format,
            'size': len(response.body),
            'preview': preview[:200]
        }
