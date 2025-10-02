import scrapy
import re
from urllib.parse import urljoin, parse_qs, urlparse


class StatistikSpider(scrapy.Spider):
    name = 'statistik_comprehensive'
    allowed_domains = ['basketball-bund.net']
    
    # Define all the statistical views we want to crawl
    STATISTIK_VIEWS = [
        {
            'reqCode': 'statTeam',
            'name': 'Team Statistics/Standings',
            'description': 'League standings and team statistics'
        },
        {
            'reqCode': 'statBesteWerfer', 
            'name': 'Top Scorers (Points per Game)',
            'description': 'Best scorers by points per game',
            'params': {'_top': '-1'}  # Get all players, not just top 10
        },
        {
            'reqCode': 'statBesteFreiWerfer',
            'name': 'Free Throw Statistics', 
            'description': 'Best free throw shooters',
            'params': {'_top': '-1'}
        },
        {
            'reqCode': 'statBeste3erWerfer',
            'name': '3-Point Statistics',
            'description': 'Best 3-point shooters', 
            'params': {'_top': '-1'}
        },
        # We can add more statistical views as we discover them
        {
            'reqCode': 'statBesteRebounds',
            'name': 'Rebounding Statistics',
            'description': 'Best rebounders',
            'params': {'_top': '-1'}
        },
        {
            'reqCode': 'statBesteAssists', 
            'name': 'Assist Statistics',
            'description': 'Best assist leaders',
            'params': {'_top': '-1'}
        },
        {
            'reqCode': 'statBesteBlocks',
            'name': 'Block Statistics', 
            'description': 'Best shot blockers',
            'params': {'_top': '-1'}
        },
        {
            'reqCode': 'statBesteSteals',
            'name': 'Steal Statistics',
            'description': 'Best steal leaders', 
            'params': {'_top': '-1'}
        }
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
    }
    
    def start_requests(self):
        """Start by finding all league IDs, then crawl all statistical views"""
        # First, get league IDs from the main listing pages
        base_url = 'https://www.basketball-bund.net/index.jsp?Action=100&Verband=2&viewid=&startrow={}'
        start_rows = [0, 10, 50, 100, 150, 200, 300]  # Key pages for Oberfranken
        
        for start_row in start_rows:
            url = base_url.format(start_row)
            yield scrapy.Request(
                url=url,
                callback=self.extract_league_ids,
                meta={'start_row': start_row}
            )
        
        # Also start with the known example
        yield self.create_statistik_requests('47960', 'Example League')
        
        # Also check boxscore pages for each league we discover
        yield self.create_boxscore_requests('47960', 'Example League')
    
    def extract_league_ids(self, response):
        """Extract liga_id values from league listing pages"""
        start_row = response.meta['start_row']
        self.logger.info(f'🔍 Extracting league IDs from startrow={start_row}')
        
        # Look for Action=102 links that contain liga_id
        league_links = response.css('a[href*="Action=102"][href*="liga_id="]')
        
        league_ids = []
        for link in league_links:
            href = link.css('::attr(href)').get()
            text = link.css('::text').get() or ''
            
            if href:
                # Extract liga_id
                liga_id_match = re.search(r'liga_id=(\d+)', href)
                if liga_id_match:
                    liga_id = liga_id_match.group(1)
                    league_ids.append({
                        'liga_id': liga_id,
                        'league_name': text.strip(),
                        'source_url': response.url
                    })
        
        self.logger.info(f'📊 Found {len(league_ids)} leagues on startrow={start_row}')
        
        # Now create statistical requests for each league
        for league_info in league_ids:
            yield from self.create_statistik_requests(
                league_info['liga_id'], 
                league_info['league_name']
            )
            # Also create boxscore requests
            yield from self.create_boxscore_requests(
                league_info['liga_id'],
                league_info['league_name']
            )
        
        # Yield summary
        yield {
            'type': 'league_discovery',
            'source_url': response.url,
            'start_row': start_row,
            'leagues_found': len(league_ids),
            'league_ids': league_ids
        }
    
    def create_statistik_requests(self, liga_id, league_name):
        """Create requests for all statistical views of a league"""
        base_url = 'https://www.basketball-bund.net/statistik.do'
        
        for view in self.STATISTIK_VIEWS:
            # Build URL parameters
            params = {
                'reqCode': view['reqCode'],
                'liga_id': liga_id
            }
            
            # Add any additional parameters for this view
            if 'params' in view:
                params.update(view['params'])
            
            # Build query string
            query_parts = [f"{key}={value}" for key, value in params.items()]
            url = f"{base_url}?{'&'.join(query_parts)}"
            
            yield scrapy.Request(
                url=url,
                callback=self.parse_statistik_view,
                meta={
                    'liga_id': liga_id,
                    'league_name': league_name,
                    'view_info': view,
                    'statistik_url': url
                }
            )
    
    def create_boxscore_requests(self, liga_id, league_name):
        """Create requests for boxscore pages (Action=103)"""
        boxscore_url = f'https://www.basketball-bund.net/index.jsp?Action=103&liga_id={liga_id}'
        
        yield scrapy.Request(
            url=boxscore_url,
            callback=self.parse_boxscore_page,
            meta={
                'liga_id': liga_id,
                'league_name': league_name,
                'page_type': 'boxscore'
            }
        )
    
    def parse_statistik_view(self, response):
        """Parse individual statistical view pages"""
        liga_id = response.meta['liga_id']
        league_name = response.meta['league_name']
        view_info = response.meta['view_info']
        
        self.logger.info(f'📈 Processing {view_info["name"]} for league {league_name} (ID: {liga_id})')
        
        # Look for export buttons
        export_buttons = self.find_export_buttons(response)
        
        if export_buttons:
            self.logger.info(f'   Found {len(export_buttons)} export options')
            for export_info in export_buttons:
                yield response.follow(
                    export_info['url'],
                    callback=self.parse_statistik_export,
                    meta={
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'view_info': view_info,
                        'export_info': export_info,
                        'source_url': response.url
                    }
                )
        
        # Extract data directly from the page as well
        page_data = self.extract_statistik_data(response, view_info)
        
        yield {
            'type': 'statistik_view',
            'url': response.url,
            'liga_id': liga_id,
            'league_name': league_name,
            'view_name': view_info['name'],
            'view_reqCode': view_info['reqCode'],
            'export_buttons_found': len(export_buttons),
            'export_buttons': export_buttons,
            'page_data': page_data
        }
    
    def parse_boxscore_page(self, response):
        """Parse boxscore pages (Action=103) for individual game data"""
        liga_id = response.meta['liga_id']
        league_name = response.meta['league_name']
        
        self.logger.info(f'🏀 Processing boxscore page for league {league_name} (ID: {liga_id})')
        
        # Look for export buttons on boxscore pages
        export_buttons = self.find_export_buttons(response)
        
        if export_buttons:
            self.logger.info(f'   Found {len(export_buttons)} export options on boxscore page')
            for export_info in export_buttons:
                yield response.follow(
                    export_info['url'],
                    callback=self.parse_boxscore_export,
                    meta={
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'export_info': export_info,
                        'source_url': response.url
                    }
                )
        
        # Look for individual game/boxscore links
        game_links = self.extract_game_links(response)
        
        if game_links:
            self.logger.info(f'   Found {len(game_links)} game links')
            # Follow a few sample game links (don't overwhelm the server)
            for game_link in game_links[:5]:  # First 5 games as samples
                yield response.follow(
                    game_link['url'],
                    callback=self.parse_individual_game,
                    meta={
                        'liga_id': liga_id,
                        'league_name': league_name,
                        'game_info': game_link,
                        'source_url': response.url
                    }
                )
        
        # Extract data directly from the boxscore page
        boxscore_data = self.extract_boxscore_data(response)
        
        yield {
            'type': 'boxscore_page',
            'url': response.url,
            'liga_id': liga_id,
            'league_name': league_name,
            'export_buttons_found': len(export_buttons),
            'game_links_found': len(game_links),
            'boxscore_data': boxscore_data
        }
    
    def extract_game_links(self, response):
        """Extract links to individual games from boxscore page"""
        game_links = []
        
        # Look for links that might lead to individual game details
        # Common patterns: Action=104 (game details), spiel_id, game_id, etc.
        game_link_patterns = [
            'a[href*="Action=104"]',  # Individual game details
            'a[href*="spiel_id="]',   # Game ID links
            'a[href*="game_id="]',    # Game ID links
            'a[href*="spielbericht"]' # Game report links
        ]
        
        for pattern in game_link_patterns:
            links = response.css(pattern)
            for link in links:
                href = link.css('::attr(href)').get()
                text = link.css('::text').get() or ''
                
                if href:
                    # Extract game/spiel ID if present
                    game_id_match = re.search(r'(?:spiel_id|game_id)=(\d+)', href)
                    game_id = game_id_match.group(1) if game_id_match else None
                    
                    game_links.append({
                        'url': response.urljoin(href),
                        'text': text.strip(),
                        'href': href,
                        'game_id': game_id
                    })
        
        return game_links
    
    def extract_boxscore_data(self, response):
        """Extract data from boxscore listing page"""
        data = {
            'title': response.css('title::text').get(),
            'tables_count': len(response.css('table')),
        }
        
        # Look for game schedule/results tables
        tables = response.css('table')
        table_data = []
        
        for i, table in enumerate(tables[:2]):  # First 2 tables
            rows = table.css('tr')
            
            if len(rows) < 2:
                continue
                
            # Extract headers
            headers = []
            if rows:
                header_row = rows[0]
                for cell in header_row.css('th, td'):
                    cell_text = cell.css('::text').get()
                    if cell_text:
                        headers.append(cell_text.strip())
            
            # Extract sample game data
            sample_games = []
            for row in rows[1:6]:  # First 5 games
                game_cells = []
                game_links = []
                
                for cell in row.css('td'):
                    cell_text = ' '.join(cell.css('::text').getall()).strip()
                    if cell_text:
                        game_cells.append(cell_text)
                    
                    # Look for links in each cell
                    cell_link = cell.css('a')
                    if cell_link:
                        link_href = cell_link.css('::attr(href)').get()
                        link_text = cell_link.css('::text').get()
                        if link_href:
                            game_links.append({
                                'href': link_href,
                                'text': link_text.strip() if link_text else '',
                                'full_url': response.urljoin(link_href)
                            })
                
                if game_cells:
                    sample_games.append({
                        'cells': game_cells,
                        'links': game_links
                    })
            
            if headers or sample_games:
                table_data.append({
                    'table_index': i,
                    'row_count': len(rows),
                    'headers': headers,
                    'sample_games': sample_games
                })
        
        data['tables'] = table_data
        
        # Check if the page indicates no games yet
        page_text = response.text.lower()
        no_games_indicators = ['keine spiele', 'no games', 'noch keine', 'season has not started']
        data['has_games'] = not any(indicator in page_text for indicator in no_games_indicators)
        
        return data
    
    def parse_individual_game(self, response):
        """Parse individual game/boxscore pages"""
        liga_id = response.meta['liga_id']
        league_name = response.meta['league_name'] 
        game_info = response.meta['game_info']
        source_url = response.meta['source_url']
        
        self.logger.info(f'🏀 Processing individual game: {game_info["text"]} for {league_name}')
        
        # Look for export buttons on individual game pages
        export_buttons = self.find_export_buttons(response)
        
        for export_info in export_buttons:
            yield response.follow(
                export_info['url'],
                callback=self.parse_boxscore_export,
                meta={
                    'liga_id': liga_id,
                    'league_name': league_name,
                    'game_info': game_info,
                    'export_info': export_info,
                    'source_url': response.url,
                    'export_context': 'individual_game'
                }
            )
        
        # Extract game data
        game_data = self.extract_individual_game_data(response)
        
        yield {
            'type': 'individual_game',
            'url': response.url,
            'source_url': source_url,
            'liga_id': liga_id,
            'league_name': league_name,
            'game_info': game_info,
            'export_buttons_found': len(export_buttons),
            'game_data': game_data
        }
    
    def extract_individual_game_data(self, response):
        """Extract data from individual game pages"""
        data = {
            'title': response.css('title::text').get(),
            'tables_count': len(response.css('table')),
        }
        
        # Look for boxscore tables, team stats, player stats
        tables = response.css('table')
        
        for i, table in enumerate(tables[:3]):  # First 3 tables
            rows = table.css('tr')
            
            if len(rows) > 1:
                # Try to identify what kind of data this table contains
                table_text = ' '.join(table.css('::text').getall()).lower()
                
                table_type = 'unknown'
                if any(keyword in table_text for keyword in ['punkte', 'points', 'score']):
                    table_type = 'scoring'
                elif any(keyword in table_text for keyword in ['rebounds', 'assists', 'steals']):
                    table_type = 'player_stats' 
                elif any(keyword in table_text for keyword in ['team', 'mannschaft']):
                    table_type = 'team_stats'
                
                data[f'table_{i}_type'] = table_type
                data[f'table_{i}_rows'] = len(rows)
        
        return data
    
    def parse_boxscore_export(self, response):
        """Parse exported boxscore/game data"""
        liga_id = response.meta['liga_id']
        league_name = response.meta['league_name']
        export_info = response.meta['export_info']
        source_url = response.meta['source_url']
        game_info = response.meta.get('game_info')
        export_context = response.meta.get('export_context', 'boxscore_page')
        
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        
        self.logger.info(f'🏀 Processing boxscore export: {export_info["text"]}')
        self.logger.info(f'   Context: {export_context}')
        self.logger.info(f'   Liga: {league_name} (ID: {liga_id})')
        self.logger.info(f'   Content-Type: {content_type}')
        self.logger.info(f'   Size: {len(response.body)} bytes')
        
        # Detect format and parse
        file_format = self.detect_export_format(response, content_type)
        parsed_data = self.parse_export_content(response, file_format)
        
        # Get preview
        preview = (response.text[:400] if response.text else 
                  response.body[:400].decode('utf-8', errors='ignore'))
        
        yield {
            'type': 'boxscore_export_data',
            'liga_id': liga_id,
            'league_name': league_name,
            'export_context': export_context,
            'game_info': game_info,
            'export_type': export_info['type'],
            'export_text': export_info['text'],
            'source_url': source_url,
            'export_url': response.url,
            'content_type': content_type,
            'file_format': file_format,
            'size': len(response.body),
            'preview': preview,
            'parsed_data': parsed_data
        }
    
    def find_export_buttons(self, response):
        """Find all export buttons on a statistik page"""
        export_buttons = []
        
        # 1. Look for "Liste ausdrucken (HTML)" and similar buttons
        html_print_buttons = response.css('a[href*="print"], input[value*="ausdrucken"], input[value*="print"]')
        html_print_buttons.extend(response.css('a:contains("ausdrucken"), a:contains("print"), a:contains("HTML")'))
        
        for button in html_print_buttons:
            href = button.css('::attr(href)').get()
            value = button.css('::attr(value)').get()
            text = button.css('::text').get() or ''
            
            if href:
                export_buttons.append({
                    'type': 'html_print',
                    'text': text.strip(),
                    'url': href,
                    'full_url': response.urljoin(href)
                })
            elif value and 'ausdrucken' in value.lower():
                # This might be a form button, need to handle form submission
                form = button.xpath('./ancestor::form[1]')
                if form:
                    action = form.css('::attr(action)').get() or response.url
                    export_buttons.append({
                        'type': 'form_submit',
                        'text': value,
                        'url': action,
                        'full_url': response.urljoin(action),
                        'method': form.css('::attr(method)').get() or 'GET'
                    })
        
        # 2. Look for Excel/CSV export buttons
        excel_buttons = response.css('a[href*="excel"], a[href*="csv"], a[href*="export"]')
        excel_buttons.extend(response.css('a:contains("Excel"), a:contains("CSV"), a:contains("Export")'))
        
        for button in excel_buttons:
            href = button.css('::attr(href)').get()
            text = button.css('::text').get() or ''
            
            if href and href not in [eb['url'] for eb in export_buttons]:  # Avoid duplicates
                export_buttons.append({
                    'type': 'excel_export',
                    'text': text.strip(),
                    'url': href,
                    'full_url': response.urljoin(href)
                })
        
        # 3. Look for JavaScript export functions
        js_exports = response.css('a[href*="javascript:"], a[onclick]')
        for js_link in js_exports:
            href = js_link.css('::attr(href)').get() or ''
            onclick = js_link.css('::attr(onclick)').get() or ''
            text = js_link.css('::text').get() or ''
            
            js_code = href + onclick
            if any(keyword in js_code.lower() for keyword in ['export', 'print', 'ausdrucken', 'excel']):
                # Try to extract or construct the actual URL
                actual_url = self.extract_js_url(js_code, response.url)
                if actual_url:
                    export_buttons.append({
                        'type': 'javascript_export',
                        'text': text.strip(),
                        'url': actual_url,
                        'full_url': response.urljoin(actual_url),
                        'js_function': js_code
                    })
        
        # 4. Look for hidden export URLs in page source
        hidden_exports = self.find_hidden_export_urls(response)
        export_buttons.extend(hidden_exports)
        
        return export_buttons
    
    def extract_js_url(self, js_code, current_url):
        """Extract actual URLs from JavaScript export functions"""
        # Common patterns
        patterns = [
            r'window\.open\([\'"]([^\'\"]+)[\'"]',
            r'location\.href\s*=\s*[\'"]([^\'\"]+)[\'"]',
            r'[\'"]([^\'\"]*statistik\.do[^\'\"]*)[\'"]'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_code)
            for match in matches:
                if 'statistik.do' in match or 'print' in match.lower():
                    return match
        
        return None
    
    def find_hidden_export_urls(self, response):
        """Find export URLs hidden in page source"""
        hidden_exports = []
        page_source = response.text
        
        # Look for statistik.do URLs with print/export parameters
        patterns = [
            r'(statistik\.do\?[^"\'>\s]*print[^"\'>\s]*)',
            r'(statistik\.do\?[^"\'>\s]*export[^"\'>\s]*)',
            r'(statistik\.do\?[^"\'>\s]*ausgabe[^"\'>\s]*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            for match in matches:
                hidden_exports.append({
                    'type': 'hidden_url',
                    'text': f'Hidden: {match[:50]}...',
                    'url': match,
                    'full_url': response.urljoin(match)
                })
        
        return hidden_exports
    
    def extract_statistik_data(self, response, view_info):
        """Extract data directly from the statistik page"""
        data = {
            'title': response.css('title::text').get(),
            'tables_count': len(response.css('table')),
        }
        
        # Extract table data
        tables = response.css('table')
        table_data = []
        
        for i, table in enumerate(tables[:3]):  # First 3 tables
            rows = table.css('tr')
            
            if len(rows) < 2:  # Skip tables without data
                continue
            
            # Extract headers
            headers = []
            header_row = rows[0]
            for cell in header_row.css('th, td'):
                cell_text = cell.css('::text').get()
                if cell_text:
                    headers.append(cell_text.strip())
            
            # Extract sample data rows
            sample_rows = []
            for row in rows[1:11]:  # First 10 data rows
                row_cells = []
                for cell in row.css('td'):
                    cell_text = ' '.join(cell.css('::text').getall()).strip()
                    if cell_text:
                        row_cells.append(cell_text)
                
                if row_cells:
                    sample_rows.append(row_cells)
            
            if headers or sample_rows:
                table_data.append({
                    'table_index': i,
                    'row_count': len(rows),
                    'headers': headers,
                    'sample_rows': sample_rows[:5]  # First 5 rows
                })
        
        data['tables'] = table_data
        return data
    
    def parse_statistik_export(self, response):
        """Parse exported statistik data"""
        liga_id = response.meta['liga_id']
        league_name = response.meta['league_name']
        view_info = response.meta['view_info']
        export_info = response.meta['export_info']
        source_url = response.meta['source_url']
        
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        
        self.logger.info(f'📊 Processing export: {export_info["text"]} for {view_info["name"]}')
        self.logger.info(f'   Liga: {league_name} (ID: {liga_id})')
        self.logger.info(f'   Content-Type: {content_type}')
        self.logger.info(f'   Size: {len(response.body)} bytes')
        
        # Detect format and parse
        file_format = self.detect_export_format(response, content_type)
        parsed_data = self.parse_export_content(response, file_format)
        
        # Get preview
        preview = (response.text[:400] if response.text else 
                  response.body[:400].decode('utf-8', errors='ignore'))
        
        yield {
            'type': 'statistik_export_data',
            'liga_id': liga_id,
            'league_name': league_name,
            'view_name': view_info['name'],
            'view_reqCode': view_info['reqCode'],
            'export_type': export_info['type'],
            'export_text': export_info['text'],
            'source_url': source_url,
            'export_url': response.url,
            'content_type': content_type,
            'file_format': file_format,
            'size': len(response.body),
            'preview': preview,
            'parsed_data': parsed_data
        }
    
    def detect_export_format(self, response, content_type):
        """Detect the format of exported data"""
        if 'html' in content_type.lower():
            return 'html'
        elif 'csv' in content_type.lower():
            return 'csv'
        elif 'excel' in content_type.lower() or 'spreadsheet' in content_type.lower():
            return 'excel'
        elif 'json' in content_type.lower():
            return 'json'
        else:
            # Auto-detect from content
            content_start = response.body[:300].lower()
            if b'<html' in content_start or b'<table' in content_start:
                return 'html'
            elif b',' in content_start and (b'"' in content_start or b';' in content_start):
                return 'csv'
            else:
                return 'text'
    
    def parse_export_content(self, response, file_format):
        """Parse export content based on format"""
        if file_format == 'html':
            return self.parse_html_export(response)
        elif file_format == 'csv':
            return self.parse_csv_export(response.text)
        elif file_format == 'json':
            return self.parse_json_export(response.text)
        else:
            return {
                'format': file_format,
                'raw_preview': response.text[:500] if response.text else None
            }
    
    def parse_html_export(self, response):
        """Parse HTML export data"""
        tables = response.css('table')
        
        parsed_tables = []
        for i, table in enumerate(tables[:2]):  # First 2 tables
            rows = table.css('tr')
            
            # Extract all rows
            table_rows = []
            for row in rows:
                cells = row.css('td::text, th::text').getall()
                cells = [cell.strip() for cell in cells if cell.strip()]
                if cells:
                    table_rows.append(cells)
            
            parsed_tables.append({
                'table_index': i,
                'total_rows': len(rows),
                'data_rows': table_rows,
                'headers': table_rows[0] if table_rows else []
            })
        
        return {
            'format': 'html',
            'table_count': len(tables),
            'tables': parsed_tables
        }
    
    def parse_csv_export(self, content):
        """Parse CSV export data"""
        if not content:
            return {'error': 'Empty CSV content'}
        
        lines = content.strip().split('\n')
        rows = []
        
        for line in lines:
            if line.strip():
                # Handle different CSV separators
                if ';' in line:
                    row = [field.strip().strip('"\'') for field in line.split(';')]
                else:
                    row = [field.strip().strip('"\'') for field in line.split(',')]
                rows.append(row)
        
        return {
            'format': 'csv',
            'total_lines': len(lines),
            'headers': rows[0] if rows else [],
            'data_rows': rows[1:] if len(rows) > 1 else [],
            'sample_preview': rows[:10]  # First 10 rows
        }
    
    def parse_json_export(self, content):
        """Parse JSON export data"""
        try:
            import json
            data = json.loads(content)
            return {
                'format': 'json',
                'data': data
            }
        except:
            return {
                'format': 'json',
                'error': 'Invalid JSON',
                'preview': content[:300]
            }
