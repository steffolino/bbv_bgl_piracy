#!/usr/bin/env python3
"""
Test Action=106 league discovery for a season (paginated tables)
"""
import requests
import time
import random
from bs4 import BeautifulSoup

def discover_leagues_for_season(season_id, startrow=0):
    url = f"https://www.basketball-bund.net/index.jsp?Action=106"
    if startrow and int(startrow) > 0:
        url += f"&startrow={int(startrow)}&viewid="
    post_data = {
        "saison_id": str(season_id),
        "cbSpielklasseFilter": "0",
        "cbAltersklasseFilter": "-3",
        "cbGeschlechtFilter": "0",
        "cbBezirkFilter": "5",
        "cbKreisFilter": "0"
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.basketball-bund.net',
        'Referer': 'https://www.basketball-bund.net/index.jsp?Action=106',
        'DNT': '1',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Upgrade-Insecure-Requests': '1'
    }
    cookies = {
        "SESSION": "YjE0NGNiOWQtZDYwYi00NDVjLWEwOWYtYWY5YmY1OWQ2ZmIw",
        "__cmpcc": "1",
        "__cmpconsentx47082": "CQYtZrAQYtZrAAfQ6BENB_FgAP_AAEPAAAigJSkR5C5cDWFBeTJ3QMskeYQX0cgBZgABAgaAASABCDAAcIQAkkESIAyAAAACAQAAIDSBAAAADAhAAEAAAIgBAADoAAAEgBAIIAAEABERQ0IAAAgKCIgAEAAIAAAxIkAAkAKAAILiQFAAgIAiAAABAAAAAIABAAMAAAAIAAACAAIAAAAAAAAAgAAAAAACABAIAAAAAAAAII3wPQAFgAVAAuABwADwAIAAVAAyABoADwAJgAXAAxABoADeAH4AQgAhgBNACcAGAAMMAc4A7oB-AH6AQgAiwBHACRAEmAJSAWIAxQBrwDaAHEAO2Af0A_4CLwErAJiATIAmkBQ4CjwFIgKbAU-At0BcgC8wGQgMkAZYAy4BpoDiwHjgQrAjeAAA.f_gACHgAAAA",
        "__cmpcccx47082": "aCQYui6hgAAh_RqxozGI0rCyOeIZk1NDIGQ0GYsSxBghqZWKmC9CerFiRiamGSNSwsZNTVkhoZDLDKajJoYsDRMGDLJGGRC0ExaksVYRgSYAAA",
        "_cc_id": "870093237fb05496cfd48ed954561d73",
        "panoramaId_expiry": "1760077199952",
        "panoramaId": "962a795531b7c466f3736667a8c3185ca02c3382d7333b1eca5acb185015aa03",
        "panoramaIdType": "panoDevice",
        "connectId": '{"ttl":86400000,"lastUsed":1759472400813,"lastSynced":1759472400813}',
        "__gads": "ID=37a4d38a6355e67a:T=1759472400:RT=1759472925:S=ALNI_Ma8PYixZyZDnk9LiDRfo8ZKp1bEbA",
        "__gpi": "UID=0000129399e70ef0:T=1759472400:RT=1759472925:S=ALNI_MbmfZvq29zMNdz2yfqjWDK2jGQJWw",
        "__eoi": "ID=d2a31613eb138f89:T=1759472400:RT=1759472925:S=AA-AfjZtB12hn8hOxQQNPte-4bkZ",
        "cto_bundle": "YQEXU181Y09pNmhWRFlhVWtRUXVqQ1Z5WXZ6cjgwNGVkekkxOERLMTRQc1FBY0hwaE5aY3d5UnpZbzloZkcwZGhZWGc5UlVuNiUyRm5kRktsQWFzZFFQYmx3dFZ1QmtSTUcwd25DMkR1SXhiQnlINm8xT3hGQ2cxdDU4aFIzNFl5YUlvNDglMkJqc2RuU2pjcXY3UnB0OUtZVG5mQWZMT2dicmQlMkZzeDBNR3FOM0lEWEclMkZWcyUzRA",
        "emqsegs": "e0,e3m,ey,ed,e38,e3i,e3s,ec,e3o,e3b,e1,e8"
    }
    resp = requests.post(url, headers=headers, cookies=cookies, data=post_data)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    leagues = []
    for table in soup.find_all("table", class_="sportView"):
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 7:
                continue
            action_cell = cells[-1]
            link = action_cell.find("a", href=True)
            if link and "liga_id=" in link["href"]:
                import re
                m = re.search(r"liga_id=(\d+)", link["href"])
                if m:
                    league_id = m.group(1)
                    league_name = cells[5].get_text(strip=True)
                    leagues.append({"id": league_id, "name": league_name})
    return leagues, soup

def test_paginated_league_discovery(season_id):
    all_leagues = []
    visited_startrows = set()
    startrow = 0
    page = 1
    while True:
        leagues, soup = discover_leagues_for_season(season_id, startrow)
        if not leagues:
            break
        all_leagues.extend(leagues)
        visited_startrows.add(startrow)
        # Find all possible startrow links on the page
        next_startrows = set()
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            import re
            match = re.search(r'startrow=(\d+)', href)
            if match:
                sr = int(match.group(1))
                if sr not in visited_startrows:
                    next_startrows.add(sr)
        if next_startrows:
            startrow = min(next_startrows)
            page += 1
            time.sleep(random.uniform(1, 2))
            continue
        break
    print(f"Season {season_id}: Found {len(all_leagues)} leagues")
    for league in all_leagues:
        print(f"  {league['id']}: {league['name']}")

if __name__ == "__main__":
    # Test for 2024
    test_paginated_league_discovery(2024)
