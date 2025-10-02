#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def test_user_provided_urls():
    """Test the exact URLs provided by the user"""
    
    print("🧪 TESTING USER-PROVIDED URLs")
    
    # URLs exactly as provided by user
    test_urls = [
        "https://www.basketball-bund.net/statistik.do?reqCode=statTeamArchiv&liga_id=26212&saison_id=2018",
        "https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id=26212&saison_id=2018&_top=-1",
        "https://www.basketball-bund.net/statistik.do?reqCode=statBesteFreiWerferArchiv&liga_id=26212&saison_id=2018&_top=-1",
        "https://www.basketball-bund.net/statistik.do?reqCode=statBeste3erWerferArchiv&liga_id=26212&saison_id=2018&_top=-1",
        "https://www.basketball-bund.net/index.jsp?Action=108&liga_id=26212&saison_id=2018"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Referer': 'https://www.basketball-bund.net/',
    }
    
    results = []
    
    for i, url in enumerate(test_urls):
        print(f"\n{i+1}. Testing: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"   Status: {response.status_code}")
            print(f"   Content length: {len(response.text)}")
            
            if response.status_code == 200:
                # Parse and extract data
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for data tables
                tables = soup.find_all('table')
                data_tables = []
                
                for table in tables:
                    rows = table.find_all('tr')
                    if len(rows) > 1:  # Has header + data
                        table_text = table.get_text().lower()
                        
                        # Check if this looks like a data table
                        if any(term in table_text for term in ['spieler', 'name', 'punkte', 'team', 'mannschaft']):
                            data_tables.append(table)
                
                print(f"   Found {len(data_tables)} data tables")
                
                # Extract data from the first/main data table
                extracted_data = []
                if data_tables:
                    main_table = data_tables[0]
                    extracted_data = extract_table_data(main_table, url)
                
                print(f"   Extracted {len(extracted_data)} data rows")
                
                if extracted_data:
                    print(f"   Sample data: {extracted_data[0]}")
                
                results.append({
                    'url': url,
                    'status': response.status_code,
                    'data_count': len(extracted_data),
                    'data': extracted_data[:5],  # First 5 rows
                    'tables_found': len(data_tables),
                    'content_preview': soup.get_text()[:500]
                })
                
                # Save full HTML for first URL
                if i == 0:
                    with open('debug_user_url_example.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"   ✅ Saved full HTML to debug_user_url_example.html")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                results.append({
                    'url': url,
                    'status': response.status_code,
                    'error': f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'url': url,
                'error': str(e)
            })
    
    # Save test results
    output = {
        'test_timestamp': datetime.now().isoformat(),
        'user_provided_urls': test_urls,
        'results': results
    }
    
    with open('user_url_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Test results saved to user_url_test_results.json")

def extract_table_data(table, source_url):
    """Extract data from HTML table"""
    
    try:
        data = []
        rows = table.find_all('tr')
        
        if len(rows) < 2:
            return []
        
        # Get headers
        header_row = rows[0]
        headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
        
        # Process data rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            
            if len(cells) >= 2:
                row_data = {
                    'source_url': source_url,
                    'extracted_at': datetime.now().isoformat()
                }
                
                # Map cell data to headers
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        header = headers[i]
                        cell_text = cell.get_text(strip=True)
                        
                        # Store both raw and processed data
                        row_data[f'col_{i}_{header}'] = cell_text
                        
                        # Try to identify common fields
                        if any(term in header for term in ['name', 'spieler']):
                            if cell_text and len(cell_text) > 1:
                                row_data['player_name'] = cell_text
                        
                        elif any(term in header for term in ['team', 'mannschaft']):
                            if cell_text and len(cell_text) > 1:
                                row_data['team_name'] = cell_text
                        
                        elif any(term in header for term in ['punkte', 'points']):
                            try:
                                row_data['points'] = float(cell_text.replace(',', '.'))
                            except:
                                pass
                        
                        elif any(term in header for term in ['spiele', 'games']):
                            try:
                                row_data['games'] = int(cell_text)
                            except:
                                pass
                
                # Only add if we have meaningful data
                if len([k for k in row_data.keys() if not k.startswith('col_')]) > 2:
                    data.append(row_data)
        
        return data
        
    except Exception as e:
        print(f"Error extracting table data: {e}")
        return []

if __name__ == "__main__":
    test_user_provided_urls()
