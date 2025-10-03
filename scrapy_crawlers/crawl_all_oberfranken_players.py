import requests
from bs4 import BeautifulSoup
import json
import time

with open(r"c:\Users\StretzS\projects\bbv_bgl_piracy\oberfranken_leagues_2003_2024.json", "r", encoding="utf-8") as f:
    leagues = json.load(f)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7",
    "Cache-Control": "no-cache",
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

all_players = []
for league in leagues:
    season = league["season"]
    liga_id = league["liga_id"]
    url = f"https://www.basketball-bund.net/statistik.do?reqCode=statTeamArchiv&liga_id={liga_id}&saison_id={season}"
    print(f"Crawling players for league {liga_id} ({league['name']}) in season {season}")
    response = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, "html.parser")
    # Example: parse player rows from the table (adjust selector as needed)
    tables = soup.find_all("table")
    for table in tables:
        if "Mannschaft" in table.get_text():
            rows = table.find_all("tr")[1:]
            for row in rows:
                cells = row.find_all("td")
                if len(cells) < 3:
                    continue
                player_name = cells[0].get_text(strip=True)
                team_name = cells[1].get_text(strip=True)
                stats = cells[2].get_text(strip=True)
                all_players.append({
                    "season": season,
                    "liga_id": liga_id,
                    "league_name": league["name"],
                    "player_name": player_name,
                    "team_name": team_name,
                    "stats": stats
                })
    time.sleep(0.2)

with open("oberfranken_players_2003_2024.json", "w", encoding="utf-8") as f:
    json.dump(all_players, f, ensure_ascii=False, indent=2)
print(f"Saved {len(all_players)} player records to oberfranken_players_2003_2024.json")
