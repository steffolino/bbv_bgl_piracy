#!/usr/bin/env python3
"""
Test the exact 2018 working URL to see what's wrong
"""

import requests
from bs4 import BeautifulSoup

def test_exact_2018_url():
    """Test the exact URL that worked in 2018"""
    
    # From sample_export.csv - this exact URL worked in 2018
    working_2018_url = "https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id=26212&saison_id=2018&_top=-1"
    
    print(f"Testing exact 2018 working URL:")
    print(f"URL: {working_2018_url}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(working_2018_url)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        
        # Check what kind of error we get
        if "reqCode" in response.text:
            print("❌ reqCode parameter error detected")
            
        if "Seite nicht gefunden" in response.text:
            print("❌ Page not found error")
            
        if "does not contain handler parameter" in response.text:
            print("❌ Handler parameter error")
            
        # Look for any redirects or new patterns
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')
        if title:
            print(f"Page title: {title.get_text()}")
            
        # Check if there are any form elements suggesting new API
        forms = soup.find_all('form')
        print(f"Forms found: {len(forms)}")
        
        for i, form in enumerate(forms[:3]):  # Show first 3 forms
            action = form.get('action', '')
            method = form.get('method', 'GET')
            inputs = form.find_all('input')
            print(f"  Form {i+1}: {method} {action} ({len(inputs)} inputs)")
            
        # Look for any links that might show new API pattern
        links = soup.find_all('a', href=True)
        statistik_links = [link for link in links if 'statistik' in link.get('href', '').lower()]
        print(f"Statistik links found: {len(statistik_links)}")
        
        for link in statistik_links[:3]:  # Show first 3 statistik links
            href = link.get('href')
            text = link.get_text(strip=True)
            print(f"  Link: {href} ({text})")
        
        # Save response for manual inspection
        with open('test_exact_2018_url_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Response saved to test_exact_2018_url_response.html")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_exact_2018_url()
