import scrapy
from urllib.parse import urljoin


class TestSpecificArchiveSpider(scrapy.Spider):
    name = 'test_specific_archive'
    allowed_domains = ['basketball-bund.net']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.3,
    }
    
    def start_requests(self):
        """Test specific combinations to find what works"""
        
        # Test league IDs (including the one from your examples + some variants)
        test_liga_ids = [
            '17248',  # From your original example
            '51819',  # From current season examples
            '17249', '17250', '17247',  # Variants around 17248
            '17000', '17100', '17200', '17300'  # Other ranges
        ]
        
        # Test seasons
        test_seasons = ['2024', '2023', '2022', '2021', '2020', '2019', '2018']
        
        # Test reqCodes 
        test_req_codes = [
            'statTeamArchiv',
            'statBesteWerferArchiv',
            'statBesteFreiWerferArchiv', 
            'statBeste3erWerferArchiv'
        ]
        
        # Also test current season patterns (Action=102/103) for comparison
        for liga_id in test_liga_ids[:3]:  # Test first 3 league IDs
            current_url = f'https://www.basketball-bund.net/index.jsp?Action=102&liga_id={liga_id}'
            yield scrapy.Request(
                url=current_url,
                callback=self.test_url,
                meta={
                    'test_type': 'current_season',
                    'liga_id': liga_id,
                    'season': 'current',
                    'req_code': 'current'
                }
            )
        
        # Test archive patterns
        for liga_id in test_liga_ids[:3]:  # Test first 3 league IDs
            for season in test_seasons[:4]:  # Test first 4 seasons
                for req_code in test_req_codes[:2]:  # Test first 2 reqCodes
                    archive_url = (
                        f'https://www.basketball-bund.net/index.jsp?'
                        f'Action=107&liga_id={liga_id}&'
                        f'saison_id={season}&reqCode={req_code}'
                    )
                    
                    yield scrapy.Request(
                        url=archive_url,
                        callback=self.test_url,
                        meta={
                            'test_type': 'archive',
                            'liga_id': liga_id,
                            'season': season,
                            'req_code': req_code
                        }
                    )

    def test_url(self, response):
        """Analyze what each URL returns"""
        test_type = response.meta['test_type']
        liga_id = response.meta['liga_id']
        season = response.meta['season']
        req_code = response.meta['req_code']
        
        content_length = len(response.text)
        status = response.status
        
        # Analyze content
        tables = response.css('table')
        table_count = len(tables)
        
        # Check for meaningful data
        meaningful_tables = 0
        meaningful_indicators = []
        
        for table in tables:
            table_text = table.get_text(strip=True)
            if len(table_text) > 100:  # Substantial content
                # Look for basketball-specific indicators
                basketball_keywords = [
                    'platz', 'team', 'mannschaft', 'punkte', 'spiele', 
                    'siege', 'niederlagen', 'tore', 'körbe', 'spieler',
                    'minuten', 'freiwürfe', 'dreier'
                ]
                
                table_lower = table_text.lower()
                found_keywords = [kw for kw in basketball_keywords if kw in table_lower]
                
                if found_keywords:
                    meaningful_tables += 1
                    meaningful_indicators.extend(found_keywords)
        
        # Check for error/empty indicators
        error_indicators = []
        text_lower = response.text.lower()
        
        if any(phrase in text_lower for phrase in ['keine daten', 'nicht gefunden', 'fehler']):
            error_indicators.append('no_data_text')
        if content_length < 2000:
            error_indicators.append('short_content')
        if status != 200:
            error_indicators.append(f'http_{status}')
        
        # Determine if this is a working URL
        has_data = meaningful_tables > 0 and len(error_indicators) == 0
        
        result = {
            'type': 'url_test_result',
            'test_type': test_type,
            'url': response.url,
            'liga_id': liga_id,
            'season': season,
            'req_code': req_code,
            'status_code': status,
            'content_length': content_length,
            'table_count': table_count,
            'meaningful_tables': meaningful_tables,
            'has_data': has_data,
            'basketball_indicators': list(set(meaningful_indicators)),
            'error_indicators': error_indicators
        }
        
        # Log interesting findings
        if has_data:
            self.logger.info(
                f'✅ WORKING: {test_type} - Liga: {liga_id} - Season: {season} - '
                f'{req_code} - Tables: {meaningful_tables} - Indicators: {meaningful_indicators[:3]}'
            )
        else:
            self.logger.info(
                f'❌ EMPTY: {test_type} - Liga: {liga_id} - Season: {season} - '
                f'{req_code} - Errors: {error_indicators}'
            )
        
        yield result
        
        # If we found working data, also check for export links
        if has_data:
            export_links = []
            for link in response.css('a[href*="export" i], a:contains("Export"), a[href*="presseExport"]'):
                href = link.css('::attr(href)').get()
                text = link.css('::text').get()
                if href and text:
                    export_links.append({
                        'url': urljoin(response.url, href),
                        'text': text.strip()
                    })
            
            if export_links:
                yield {
                    'type': 'working_url_with_exports',
                    'url': response.url,
                    'liga_id': liga_id,
                    'season': season,
                    'req_code': req_code,
                    'export_links': export_links
                }
