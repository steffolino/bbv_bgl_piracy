import scrapy
import re
from urllib.parse import urljoin, parse_qs, urlparse
from itertools import product


class DiscoverArchiveSpider(scrapy.Spider):
    name = 'discover_archive'
    allowed_domains = ['basketball-bund.net']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.3,
    }
    
    # Historical seasons to test
    test_seasons = ['2024', '2023', '2022', '2021', '2020']
    
    # Archive reqCodes to test
    archive_req_codes = [
        'statTeamArchiv',
        'statBesteWerferArchiv', 
        'statBesteFreiWerferArchiv',
        'statBeste3erWerferArchiv'
    ]
    
    def start_requests(self):
        """Start by discovering current league IDs from current season data"""
        # Start with the current season Oberfranken leagues
        yield scrapy.Request(
            url='https://www.basketball-bund.net/index.jsp?Action=100&viewid=187&startrow=0',
            callback=self.discover_current_leagues,
            meta={'discovery_phase': 'current_leagues'}
        )

    def discover_current_leagues(self, response):
        """Extract current league IDs that we can then test with archive seasons"""
        self.logger.info('🔍 Discovering current league IDs...')
        
        current_leagues = []
        
        # Look for links with liga_id parameters
        for link in response.css('a[href*="liga_id"]'):
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            
            if href and text:
                # Parse the URL to extract liga_id
                parsed_url = urlparse(href)
                params = parse_qs(parsed_url.query)
                liga_id = params.get('liga_id', [None])[0]
                
                if liga_id and text.strip():
                    current_leagues.append({
                        'liga_id': liga_id,
                        'league_name': text.strip(),
                        'current_url': urljoin(response.url, href)
                    })
        
        self.logger.info(f'🏀 Found {len(current_leagues)} current leagues with IDs')
        
        # Yield summary of discovered leagues
        yield {
            'type': 'discovery_summary',
            'phase': 'current_leagues',
            'leagues_found': len(current_leagues),
            'leagues': current_leagues[:10]  # First 10 for summary
        }
        
        # Now test these league IDs with archive seasons
        for league in current_leagues[:5]:  # Test first 5 leagues to start
            for season in self.test_seasons:
                for req_code in self.archive_req_codes:
                    archive_url = (
                        f'https://www.basketball-bund.net/index.jsp?'
                        f'Action=107&liga_id={league["liga_id"]}&'
                        f'saison_id={season}&reqCode={req_code}'
                    )
                    
                    yield scrapy.Request(
                        url=archive_url,
                        callback=self.test_archive_url,
                        meta={
                            'league_info': league,
                            'season': season,
                            'req_code': req_code,
                            'test_url': archive_url
                        },
                        dont_filter=True
                    )

    def test_archive_url(self, response):
        """Test if an archive URL returns actual data"""
        league_info = response.meta['league_info']
        season = response.meta['season']
        req_code = response.meta['req_code']
        test_url = response.meta['test_url']
        
        # Analyze the response
        content_length = len(response.text)
        tables = response.css('table')
        table_count = len(tables)
        
        # Check for data indicators
        has_data = False
        data_indicators = []
        
        # Look for actual table data (not just empty tables)
        non_empty_tables = 0
        for table in tables:
            table_text = table.get_text(strip=True)
            if len(table_text) > 50 and any(word in table_text.lower() for word in 
                ['platz', 'team', 'punkte', 'spiele', 'tore', 'körbe', 'spieler']):
                non_empty_tables += 1
                has_data = True
                data_indicators.append('meaningful_table_data')
        
        # Look for error indicators
        error_indicators = []
        if 'fehler' in response.text.lower():
            error_indicators.append('error_text')
        if content_length < 1000:
            error_indicators.append('very_short_content')
        if response.status != 200:
            error_indicators.append(f'http_{response.status}')
            
        # Look for "no data" indicators
        no_data_indicators = []
        if 'keine daten' in response.text.lower():
            no_data_indicators.append('keine_daten_text')
        if 'nicht gefunden' in response.text.lower():
            no_data_indicators.append('nicht_gefunden_text')
        
        # Determine if this URL has useful data
        has_useful_data = (
            has_data and 
            len(error_indicators) == 0 and 
            len(no_data_indicators) == 0 and
            non_empty_tables > 0
        )
        
        result = {
            'type': 'archive_test_result',
            'league_name': league_info['league_name'],
            'liga_id': league_info['liga_id'], 
            'season': season,
            'req_code': req_code,
            'url': test_url,
            'status_code': response.status,
            'content_length': content_length,
            'tables_found': table_count,
            'non_empty_tables': non_empty_tables,
            'has_useful_data': has_useful_data,
            'data_indicators': data_indicators,
            'error_indicators': error_indicators,
            'no_data_indicators': no_data_indicators
        }
        
        # Log interesting results
        if has_useful_data:
            self.logger.info(
                f'✅ FOUND DATA: {league_info["league_name"]} (ID: {league_info["liga_id"]}) '
                f'- Season: {season} - Type: {req_code} - Tables: {non_empty_tables}'
            )
        elif error_indicators or no_data_indicators:
            self.logger.info(
                f'❌ NO DATA: {league_info["league_name"]} - {season} - {req_code} '
                f'- Errors: {error_indicators} - NoData: {no_data_indicators}'
            )
        
        yield result
        
        # If we found useful data, also get the actual content
        if has_useful_data:
            yield scrapy.Request(
                url=test_url,
                callback=self.extract_archive_data,
                meta={
                    'league_info': league_info,
                    'season': season,
                    'req_code': req_code,
                    'confirmed_working_url': True
                }
            )

    def extract_archive_data(self, response):
        """Extract actual data from confirmed working archive URLs"""
        league_info = response.meta['league_info']
        season = response.meta['season']
        req_code = response.meta['req_code']
        
        self.logger.info(f'📊 Extracting data: {league_info["league_name"]} - {season} - {req_code}')
        
        # Extract table data
        tables_data = []
        for i, table in enumerate(response.css('table')):
            rows = []
            for row in table.css('tr'):
                cells = [cell.get_text(strip=True) for cell in row.css('td, th')]
                if cells and any(cell for cell in cells):  # Non-empty row
                    rows.append(cells)
            
            if len(rows) > 1:  # Has header + data rows
                tables_data.append({
                    'table_index': i,
                    'row_count': len(rows),
                    'header': rows[0] if rows else [],
                    'sample_data': rows[1:4] if len(rows) > 1 else []  # First 3 data rows
                })
        
        # Look for export links
        export_links = []
        for link in response.css('a[href*="export" i], a:contains("Export")'):
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            if href and text:
                export_links.append({
                    'url': urljoin(response.url, href),
                    'text': text.strip()
                })
        
        yield {
            'type': 'archive_data_extracted',
            'league_name': league_info['league_name'],
            'liga_id': league_info['liga_id'],
            'season': season,
            'req_code': req_code,
            'url': response.url,
            'tables_extracted': len(tables_data),
            'export_links_found': len(export_links),
            'tables_data': tables_data,
            'export_links': export_links
        }
