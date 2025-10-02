#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re

def test_single_league():
    """
    Test parsing of a single Action=107 response that we know has data
    """
    
    print("🔍 TESTING SINGLE LEAGUE PARSING")
    print("Using known working liga_id=1701, season=2010")
    
    # Test the known working URL
    url = 'https://www.basketball-bund.net/index.jsp?Action=107&liga_id=1701&saison_id=2010'
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    })
    
    try:
        print(f"🔍 GET {url}")
        response = session.get(url, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}")
            return
        
        print(f"✅ Response: {len(response.text):,} chars")
        
        # Save for analysis
        with open('test_single_league_1701_2010.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("\n📋 ANALYZING TABLE STRUCTURE:")
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
            
            print(f"\n🔍 Table {table_idx + 1}: {len(rows)} rows")
            
            # Check for sportItem classes (data rows)
            data_rows = table.find_all('tr', class_=re.compile(r'sportItem'))
            if data_rows:
                print(f"  📊 Found {len(data_rows)} data rows with sportItem class")
                
                # Analyze first few data rows
                for i, row in enumerate(data_rows[:3], 1):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    print(f"    Row {i}: {cell_texts}")
            
            # Check for headers
            header_candidates = []
            for row in rows[:5]:  # Check first 5 rows for headers
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                if any(header in ' '.join(cell_texts).lower() for header in ['name', 'spiele', 'punkte', 'team']):
                    header_candidates.append((rows.index(row), cell_texts))
            
            if header_candidates:
                print(f"  📋 Header candidates:")
                for row_idx, texts in header_candidates:
                    print(f"    Row {row_idx}: {texts}")
        
        # Try to extract data with improved logic
        print(f"\n🎯 EXTRACTING DATA:")
        data = extract_data_improved(soup)
        
        if data:
            print(f"✅ Extracted {len(data)} records:")
            for i, record in enumerate(data[:5], 1):
                print(f"  {i}. {record}")
        else:
            print(f"❌ No data extracted")
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")

def extract_data_improved(soup):
    """
    Improved data extraction based on the known structure
    sportItemEven/sportItemOdd classes are on <td> elements, not <tr>
    """
    
    data = []
    
    # Look for tables
    tables = soup.find_all('table')
    
    for table_idx, table in enumerate(tables):
        # Find cells with sportItem class
        sport_item_cells = table.find_all('td', class_=re.compile(r'sportItem'))
        
        if not sport_item_cells:
            continue
        
        print(f"  📊 Table {table_idx + 1}: Found {len(sport_item_cells)} sportItem cells")
        
        # Group cells by rows
        rows = table.find_all('tr')
        for row_idx, row in enumerate(rows):
            row_cells = row.find_all('td', class_=re.compile(r'sportItem'))
            
            if len(row_cells) < 3:  # Need at least a few cells
                continue
            
            cell_texts = [cell.get_text(strip=True) for cell in row_cells]
            
            # Check if this looks like team data
            if len(cell_texts) >= 2 and cell_texts[1]:  # Has team name
                
                record = {
                    'rank': cell_texts[0] if len(cell_texts) > 0 else '',
                    'team': cell_texts[1] if len(cell_texts) > 1 else '',
                    'table_index': table_idx,
                    'row_index': row_idx,
                    'raw_data': cell_texts
                }
                
                # Extract games and points if available
                for i, value in enumerate(cell_texts[2:], 2):
                    if value and value.isdigit():
                        if 'games' not in record and i >= 3:
                            record['games'] = value
                        elif 'points' not in record and i >= 4:
                            record['points'] = value
                
                # Skip empty team names or just numbers
                if (record['team'] and 
                    len(record['team']) > 1 and 
                    not record['team'].isdigit()):
                    
                    data.append(record)
                    print(f"    ✅ Found: {record['team']} (Games: {record.get('games', 'N/A')}, Points: {record.get('points', 'N/A')})")
    
    return data

if __name__ == "__main__":
    test_single_league()
