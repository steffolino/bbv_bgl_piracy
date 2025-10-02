#!/usr/bin/env python3
"""
Parse the Oberfranken 2018 leagues response to extract ALL league names and IDs
"""

import re
from bs4 import BeautifulSoup
import json

def parse_oberfranken_leagues():
    """Parse the saved oberfranken response to extract league names and IDs"""
    
    with open('oberfranken_2018_leagues.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all unique liga_ids
    liga_ids = set()
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link.get('href', '')
        match = re.search(r'liga_id=(\d+)', href)
        if match:
            liga_ids.add(match.group(1))
    
    print(f"Total unique liga_ids found: {len(liga_ids)}")
    print(f"Liga IDs: {sorted(liga_ids)}")
    
    # Now extract league names by finding the table structure
    leagues = []
    
    # Look for table rows that contain league information
    rows = soup.find_all('tr')
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 4:  # Should have multiple columns
            
            # Look for Action links in this row
            action_links = []
            for cell in cells:
                links_in_cell = cell.find_all('a', href=True)
                for link in links_in_cell:
                    href = link.get('href', '')
                    if 'liga_id=' in href:
                        match = re.search(r'liga_id=(\d+)', href)
                        if match:
                            action_links.append(match.group(1))
            
            if action_links:
                # Extract league name from the row
                league_name = "Unknown"
                bezirk = "Unknown"
                
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    # Skip empty cells and cells with just &nbsp;
                    if cell_text and cell_text not in ['', '&nbsp;', ' ']:
                        # Look for text that looks like a league name
                        if any(word in cell_text.lower() for word in ['liga', 'oberliga', 'bezirk', 'kreis', 'herren', 'damen']):
                            if len(cell_text) > len(league_name):
                                league_name = cell_text
                        elif any(word in cell_text.lower() for word in ['ober', 'mittel', 'unter', 'franken']):
                            bezirk = cell_text
                
                # Add unique leagues
                liga_id = action_links[0]  # Take first liga_id from this row
                if not any(l['id'] == liga_id for l in leagues):
                    leagues.append({
                        'id': liga_id,
                        'name': league_name,
                        'bezirk': bezirk
                    })
    
    print(f"\n=== OBERFRANKEN 2018 LEAGUES ===")
    for i, league in enumerate(leagues, 1):
        print(f"{i:2d}. ID: {league['id']:>6} | NAME: {league['name']}")
        if league['bezirk'] != "Unknown":
            print(f"     BEZIRK: {league['bezirk']}")
    
    # Save to JSON
    with open('oberfranken_2018_leagues_FINAL.json', 'w', encoding='utf-8') as f:
        json.dump(leagues, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ SAVED TO: oberfranken_2018_leagues_FINAL.json")
    
    # Test one liga_id with statistik.do
    if leagues:
        test_league = leagues[0]
        print(f"\n=== TESTING LIGA_ID {test_league['id']} ===")
        print(f"League: {test_league['name']}")
        print(f"URL: https://www.basketball-bund.net/statistik.do?reqCode=statBesteWerferArchiv&liga_id={test_league['id']}&saison_id=2018&_top=-1")
    
    return leagues

if __name__ == "__main__":
    parse_oberfranken_leagues()
