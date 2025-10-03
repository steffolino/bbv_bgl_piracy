#!/usr/bin/env python3
"""
Test Action=106 league discovery for a season (paginated tables)
"""
import requests
from bs4 import BeautifulSoup

def discover_leagues_for_season(season_id, page_offset=0):
    url = "https://www.basketball-bund.net/index.jsp?Action=106"
    data = {
        "saison_id": str(season_id),
        "cbSpielklasseFilter": "0",
        "cbAltersklasseFilter": "-3",
        "cbGeschlechtFilter": "0",
        "cbBezirkFilter": "5",
        "cbKreisFilter": "0",
        "PageOffset": str(page_offset)
    }
    resp = requests.post(url, data=data)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # Find all league rows (example: table with class 'dataTable')
    leagues = []
    for table in soup.find_all("table", class_="dataTable"):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                # Try to extract league id from link
                link = cells[0].find("a")
                if link and "liga_id=" in link.get("href", ""):
                    import re
                    m = re.search(r"liga_id=(\d+)", link["href"])
                    if m:
                        league_id = m.group(1)
                        league_name = cells[0].get_text(strip=True)
                        leagues.append({"id": league_id, "name": league_name})
    return leagues, soup

def test_paginated_league_discovery(season_id):
    all_leagues = []
    page_offset = 0
    while True:
        leagues, soup = discover_leagues_for_season(season_id, page_offset)
        if not leagues:
            break
        all_leagues.extend(leagues)
        # Check for next page button
        next_btn = soup.find("a", string="Nächste Seite")
        if next_btn:
            page_offset += 1
        else:
            break
    print(f"Season {season_id}: Found {len(all_leagues)} leagues")
    for league in all_leagues:
        print(f"  {league['id']}: {league['name']}")

if __name__ == "__main__":
    # Test for 2024
    test_paginated_league_discovery(2024)
