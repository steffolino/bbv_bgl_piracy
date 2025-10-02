#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

def debug_discovery_page():
    """Debug the discovery page to see actual HTML structure"""
    
    url = "https://www.basketball-bund.net/index.jsp"
    params = {
        'Action': '106',
        'viewid': '',
        'saison_id': '2018',
        'cbSpielklasseFilter': '0',
        'cbAltersklasseFilter': '-3',
        'cbGeschlechtFilter': '0',
        'cbBezirkFilter': '5',
        'cbKreisFilter': '0'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        'Referer': 'https://www.basketball-bund.net/',
    }
    
    print("🔍 DEBUGGING DISCOVERY PAGE")
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Final URL: {response.url}")
        print(f"Content length: {len(response.text)}")
        
        if response.status_code == 200:
            # Save raw HTML for inspection
            with open('debug_discovery_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("✅ Saved raw HTML to debug_discovery_page.html")
            
            # Parse and analyze structure
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print("\n📋 LINKS WITH liga_id:")
            links = soup.find_all('a', href=True)
            liga_links = [link for link in links if 'liga_id=' in link['href']]
            print(f"Found {len(liga_links)} links with liga_id")
            
            for i, link in enumerate(liga_links[:10]):  # Show first 10
                print(f"  {i+1}: {link['href']} -> {link.get_text(strip=True)}")
            
            print("\n📋 ALL LINKS:")
            all_links = [link['href'] for link in links if link['href'] and not link['href'].startswith('#')]
            print(f"Found {len(all_links)} total links")
            
            for i, href in enumerate(all_links[:20]):  # Show first 20
                print(f"  {i+1}: {href}")
            
            print("\n📋 FORMS:")
            forms = soup.find_all('form')
            print(f"Found {len(forms)} forms")
            
            for i, form in enumerate(forms):
                print(f"  Form {i+1}: action='{form.get('action')}' method='{form.get('method')}'")
                inputs = form.find_all('input')
                selects = form.find_all('select')
                print(f"    Inputs: {len(inputs)}, Selects: {len(selects)}")
            
            print("\n📋 TABLES:")
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables")
            
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                print(f"  Table {i+1}: {len(rows)} rows")
                if rows:
                    first_row_text = rows[0].get_text(strip=True)[:100]
                    print(f"    First row: {first_row_text}...")
            
            print("\n📋 CONTENT PREVIEW:")
            text_content = soup.get_text()
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            for i, line in enumerate(lines[:30]):
                print(f"  {i+1}: {line}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_discovery_page()
