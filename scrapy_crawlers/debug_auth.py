#!/usr/bin/env python3
"""
Quick debug test for 2018 season to understand authentication issue
"""

import requests
from bs4 import BeautifulSoup

# Test with fresh session
session = requests.Session()
session.cookies.update({
    'SESSION': 'YTFhZGEyMGItMzMyZi00NzE1LWJmNGItNGQwNTFiODJhZjhk',
    'cookieconsent_status': 'allow',
    'JSESSIONID': '16BEC2ABAC94A6CA3F62DBE2F57D3B29.TC-BKA-WEB06-80'
})

print("🔍 Testing 2018 season with current authentication...")

# Step 1: Action=100&Verband=2 
setup_url = "https://www.basketball-bund.net/liga_tool/mannschaft/suche/ergebnis_aktuell.do?Action=100&Verband=2&Liga=0&Saison=2018&PageOffset=0"
print(f"Setup URL: {setup_url}")

response = session.get(setup_url)
print(f"Setup response: {response.status_code}")

# Step 2: Action=106
leagues_url = "https://www.basketball-bund.net/liga_tool/mannschaft/suche/ergebnis_aktuell.do?Action=106&Verband=2&Saison=2018&cbBezirkFilter=5&PageOffset=0"
print(f"Leagues URL: {leagues_url}")

response = session.get(leagues_url)
print(f"Leagues response: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check for "Keine Einträge gefunden"
    if "Keine Einträge gefunden" in soup.get_text():
        print("❌ Got 'Keine Einträge gefunden' - authentication/session issue")
    else:
        print("✅ Found content! Let's check for tables...")
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            if len(rows) > 1:
                print(f"Table {i}: {len(rows)} rows")
                # Show first data row
                if len(rows) > 1:
                    cells = rows[1].find_all('td')
                    print(f"  First row: {len(cells)} cells")
                    if len(cells) >= 6:
                        print(f"  Content: {[cell.get_text(strip=True) for cell in cells[:6]]}")
else:
    print(f"❌ Request failed with status {response.status_code}")

print("\\n🔍 Response content sample:")
print(response.text[:500])
print("...")
print(response.text[-500:])
