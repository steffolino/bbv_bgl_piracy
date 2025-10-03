import requests
from bs4 import BeautifulSoup
import time
import json

url = "https://www.basketball-bund.net/index.jsp?Action=106"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7",
    "Cache-Control": "no-cache",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.basketball-bund.net",
    "Referer": "https://www.basketball-bund.net/index.jsp?Action=106",
    "DNT": "1",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Upgrade-Insecure-Requests": "1"
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

seasons = [str(y) for y in range(2003, 2025+1)]
all_leagues = []

for season in seasons:
    print(f"Crawling Oberfranken leagues for season {season}")
    data = {
        "saison_id": season,
        "cbSpielklasseFilter": "0",
        "cbAltersklasseFilter": "-3",
        "cbGeschlechtFilter": "0",
        "cbBezirkFilter": "5",
        "cbKreisFilter": "0"
    }
    startrow = 0
    while True:
        paged_data = data.copy()
        if startrow:
            paged_data["startrow"] = str(startrow)
        response = requests.post(url, headers=headers, cookies=cookies, data=paged_data)
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table", class_="sportView")
        found_leagues = 0
        for table in tables:
            rows = table.find_all("tr")[1:]  # skip header
            for row in rows:
                cells = row.find_all("td")
                if len(cells) < 7:
                    continue
                bezirk = cells[3].get_text(strip=True)
                if bezirk.lower() != "oberfranken":
                    continue
                liga_name = cells[5].get_text(strip=True)
                action_links = cells[6].find_all("a", href=True)
                liga_id = None
                saison_id = season
                for link in action_links:
                    href = link.get("href", "")
                    if "liga_id=" in href:
                        parts = href.split("liga_id=")
                        if len(parts) > 1:
                            liga_id = parts[1].split("&")[0]
                            break
                if liga_id:
                    all_leagues.append({
                        "season": saison_id,
                        "liga_id": liga_id,
                        "name": liga_name,
                        "bezirk": bezirk
                    })
                    found_leagues += 1
        print(f"  Found {found_leagues} Oberfranken leagues on page startrow {startrow}")
        # Check for next page
        nav = soup.find("table", class_="sportViewNavigation")
        next_link = None
        if nav:
            for a in nav.find_all("a", href=True):
                if "startrow=" in a["href"]:
                    next_link = a["href"]
                    break
        if next_link:
            import re
            m = re.search(r"startrow=(\d+)", next_link)
            if m:
                next_startrow = int(m.group(1))
                if next_startrow > startrow:
                    startrow = next_startrow
                    time.sleep(0.5)
                    continue
        break
    time.sleep(1)

with open("oberfranken_leagues_2003_2024.json", "w", encoding="utf-8") as f:
    json.dump(all_leagues, f, ensure_ascii=False, indent=2)
print(f"Saved {len(all_leagues)} Oberfranken leagues from 2003-2024 to oberfranken_leagues_2003_2024.json")
