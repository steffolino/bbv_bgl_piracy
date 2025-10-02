#!/usr/bin/env python3
"""
Quick diagnostic to understand the crawler behavior
"""

import requests
import json
from bs4 import BeautifulSoup

def test_single_league_stats():
    """Test what we're actually getting from liga_id 263"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Test liga_id 263 for SPG (points)
    url = "https://www.basketball-bund.net/statistik.do?spielzeit=2010&liga_id=263&modus=SPG"
    
    try:
        response = session.get(url)
        print(f"Response status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the statistics table
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            print(f"Total table rows: {len(rows)}")
            
            # Check header
            if rows:
                header = rows[0]
                header_cells = header.find_all(['th', 'td'])
                print(f"Header columns: {[cell.get_text(strip=True) for cell in header_cells]}")
            
            # Check data rows
            data_rows = rows[1:] if len(rows) > 1 else []
            print(f"Data rows: {len(data_rows)}")
            
            for i, row in enumerate(data_rows[:10]):  # Show first 10
                cells = row.find_all('td')
                if cells:
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    print(f"Row {i+1}: {row_data}")
        else:
            print("No table found in response")
            
        # Check for "Keine Einträge" or similar messages
        if "Keine Einträge" in response.text:
            print("Found 'Keine Einträge' message")
        if "Nicht gefunden" in response.text:
            print("Found 'Nicht gefunden' message")
            
        # Save response for inspection
        with open("debug_liga_263_response.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Response saved to debug_liga_263_response.html")
        
    except Exception as e:
        print(f"Error: {e}")

def check_other_liga_ids():
    """Check if other known liga_ids work better"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Test known working liga_ids
    test_ids = ['1701', '250', '3340', '263']
    
    for liga_id in test_ids:
        url = f"https://www.basketball-bund.net/statistik.do?spielzeit=2010&liga_id={liga_id}&modus=SPG"
        
        try:
            response = session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')
                data_rows = len(rows) - 1 if len(rows) > 1 else 0
                print(f"Liga {liga_id}: {data_rows} players")
            else:
                print(f"Liga {liga_id}: No table found")
                
        except Exception as e:
            print(f"Liga {liga_id}: Error - {e}")

if __name__ == "__main__":
    print("=== Testing Single League (263) ===")
    test_single_league_stats()
    
    print("\n=== Testing Multiple Liga IDs ===")
    check_other_liga_ids()
