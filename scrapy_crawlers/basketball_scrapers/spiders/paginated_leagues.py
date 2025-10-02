import scrapy
import re
from urllib.parse import urljoin, parse_qs, urlparse


class PaginatedLeagueSpider(scrapy.Spider):
    name = 'paginated_leagues'
    allowed_domains = ['basketball-bund.net']
    
    def start_requests(self):
        """Start with the first page and auto-discover pagination"""
        start_url = 'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow=0'
        yield scrapy.Request(url=start_url, callback=self.parse)
    
    def parse(self, response):
        """Parse page and follow pagination automatically"""
        # Get current start row from URL
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url.query)
        current_start_row = int(query_params.get('startrow', [0])[0])
        
        self.logger.info(f'🔍 Processing page with startrow={current_start_row}')
        
        # Find all league links on this page
        league_links = self.extract_league_links(response)
        self.logger.info(f'📊 Found {len(league_links)} league links on this page')
        
        # Yield league data
        for link_data in league_links:
            yield {
                'type': 'league_link',
                'start_row': current_start_row,
                'page_url': response.url,
                **link_data
            }
        
        # Look for pagination - check if there are more results
        # Method 1: Look for "next" or pagination links
        next_links = response.css('a[href*="startrow="]')
        
        # Method 2: Check if current page has results, if so, try next batch
        if league_links:  # If we found results, there might be more
            next_start_row = current_start_row + 50  # Try next batch
            next_url = f'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow={next_start_row}'
            
            # Don't go beyond reasonable limits
            if next_start_row <= 2000:
                self.logger.info(f'➡️ Following pagination to startrow={next_start_row}')
                yield response.follow(
                    next_url, 
                    callback=self.parse,
                    dont_filter=True  # Allow duplicate URLs with different parameters
                )
        
        # Method 3: Look for specific pagination elements
        pagination_links = response.css('a[href*="startrow"]')
        for link in pagination_links:
            href = link.css('::attr(href)').get()
            if href and 'startrow=' in href:
                # Extract startrow value
                match = re.search(r'startrow=(\d+)', href)
                if match:
                    start_row = int(match.group(1))
                    if start_row > current_start_row and start_row <= 2000:
                        full_url = response.urljoin(href)
                        self.logger.info(f'🔗 Found pagination link to startrow={start_row}')
                        yield response.follow(full_url, callback=self.parse)
    
    def extract_league_links(self, response):
        """Extract all league/competition related links from the page"""
        league_links = []
        
        # Look in tables for league links
        tables = response.css('table')
        
        for table_idx, table in enumerate(tables):
            # Get all links in this table
            links = table.css('a')
            
            for link in links:
                href = link.css('::attr(href)').get()
                text = link.css('::text').get()
                
                if href and text:
                    text = text.strip()
                    full_url = response.urljoin(href)
                    
                    # Check if this looks like a league/competition link
                    is_league_link = self.is_league_link(href, text)
                    
                    if is_league_link:
                        # Extract additional context from the table row
                        row = link.xpath('./ancestor::tr[1]')
                        row_cells = []
                        if row:
                            cells = row.css('td::text').getall()
                            row_cells = [cell.strip() for cell in cells if cell.strip()]
                        
                        league_links.append({
                            'text': text,
                            'url': full_url,
                            'href': href,
                            'table_index': table_idx,
                            'row_context': row_cells,
                            'link_type': self.categorize_link(href, text)
                        })
        
        return league_links
    
    def is_league_link(self, href, text):
        """Determine if a link is related to leagues/competitions"""
        href_lower = href.lower()
        text_lower = text.lower()
        
        # URL patterns that indicate league/competition data
        url_patterns = [
            'action=100',  # League listings
            'action=200',  # Team/club info
            'action=300',  # Games/matches
            'spielklasse',  # Competition class
            'mannschaft',   # Team
            'tabelle',      # Table/standings
            'ergebnis'      # Results
        ]
        
        # Text patterns
        text_patterns = [
            'liga', 'spielklasse', 'championship', 'pokal', 'cup',
            'herren', 'damen', 'jugend', 'u19', 'u17', 'u15',
            'bezirk', 'kreis', 'landes', 'ober', 'regional'
        ]
        
        # Check URL patterns
        url_match = any(pattern in href_lower for pattern in url_patterns)
        
        # Check text patterns
        text_match = any(pattern in text_lower for pattern in text_patterns)
        
        # Also include numeric patterns that might be league codes
        numeric_match = re.search(r'\d+', text) and len(text) < 50
        
        return url_match or text_match or numeric_match
    
    def categorize_link(self, href, text):
        """Categorize the type of league-related link"""
        href_lower = href.lower()
        text_lower = text.lower()
        
        if 'action=100' in href_lower or 'spielklasse' in href_lower:
            return 'league_listing'
        elif 'action=200' in href_lower or 'mannschaft' in href_lower:
            return 'team'
        elif 'action=300' in href_lower:
            return 'games'
        elif 'tabelle' in href_lower or 'standings' in text_lower:
            return 'standings'
        elif 'ergebnis' in href_lower or 'result' in text_lower:
            return 'results'
        else:
            return 'other'
