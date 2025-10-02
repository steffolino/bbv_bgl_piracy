# Basketball-Bund.net API Documentation

## 1. System Architecture

The site is a legacy Struts/JSP application with AngularJS components, gradually wrapped by newer REST endpoints.

**Two parallel worlds:**
- **REST API (JSON)** → Used by the newer "static" UI (`/static/#/...`) for current seasons
- **HTML endpoints** (`.do` and `.jsp`) → Used for archives and statistics, often returning full tables

## 2. REST Endpoints (JSON)

### Entry Points

**Discover leagues:**
```
POST https://www.basketball-bund.net/rest/wam/data
```
- Accepts POST with `{ "verbandIds": [...], "gebietIds": [...], ... }`
- Returns associations, regions, league lists (`ligaId`, `seasonId`)
- Example: Verband = Bayern (`verbandId=2`), Bezirk = Oberfranken (`gebietId="5_"`)

### League & Season

**League details:**
```
GET https://www.basketball-bund.net/rest/liga/id/{ligaId}/season/{seasonId}/matches
```
- Lists matches for a season in a given league
- Returns `matchId`, date, teams, results

**Match details:**
```
GET https://www.basketball-bund.net/rest/match/id/{matchId}/matchInfo
```
- Returns match metadata: date, teams, referees, hall, etc.
- Includes `matchBoxscore` and `playByPlay` (only for current/active games)
- If no boxscore: returns `matchBoxscore: null`

### IDs
- `matchId` → REST primary key for matches (current)
- `seasonTeamId`, `teamPermanentId` → Team IDs
- `ligaId` → League ID
- `seasonId` → Season (year)

## 3. HTML Endpoints (Legacy / Archive)

Used when REST is missing (especially archives before ~2021).

**League tables:**
```
GET index.jsp?Action=107&liga_id={ligaId}&saison_id={seasonId}
```

**Fixtures:**
```
GET index.jsp?Action=108&liga_id={ligaId}&saison_id={seasonId}&defaultview=1
```

**Team statistics (archive):**
```
GET statistik.do?reqCode=statTeamArchiv&liga_id={ligaId}&saison_id={seasonId}
```

**Top scorers, FT, 3P (archive):**
```
GET statistik.do?reqCode=statBesteWerferArchiv&liga_id={ligaId}&saison_id={seasonId}&_top=-1
GET statistik.do?reqCode=statBesteFreiWerferArchiv&liga_id={ligaId}&saison_id={seasonId}&_top=-1
GET statistik.do?reqCode=statBeste3erWerferArchiv&liga_id={ligaId}&saison_id={seasonId}&_top=-1
```

**Boxscores per game:**
```
GET scouting.do?reqCode=spielStatistik&spielplan_id={id}
```
- Only works for some games, often fails in deep archives
- `spielplan_id` does not equal `matchId`; it's a separate legacy key
- Sometimes visible in Excel exports as "Spielnummer"

## 4. Exported Data

The site offers Excel exports (`.xls`) for leagues and seasons.

**Columns:**
- Spieltag, Spielnummer, Datum, Heimmannschaft, Gastmannschaft, Endstand
- `Spielnummer` = `matchNo` (not equal to REST `matchId`, but mappable)
- Lines with `*` = forfeited / cancelled
- Exports are often the only way to recover `spielplan_id` for archive seasons

## 5. Mapping Across IDs

- `matchId` → REST key (JSON, current)
- `matchNo` (Excel "Spielnummer") → reference number, sometimes needed to align with HTML
- `spielplan_id` (HTML Boxscore) → legacy key, not always accessible

**To normalize:** Store all three and map them by date + teams + season.

## 6. Archive vs Current

### Current seasons (ongoing):
- REST API works (`matchInfo`, `boxscore`, `playByPlay`)
- Good for per-game stats and advanced metrics

### Archive (old seasons):
- No `matchInfo`/`boxscore` via REST
- Only season-wide stats via `statistik.do` tables
- Per-game boxscores often missing or broken
- **Therefore:** archive analysis limited to season aggregates (points, 3P, FT)

## 7. Scraping Strategy

### Archive:
- Scrape `statistik.do` for team and player aggregates
- Scrape Excel exports for results (`matchNo`)
- Boxscores via `scouting.do` only when accessible

### Current Season:
- REST (`matchInfo`) for per-game boxscores and play-by-play
- Weekly re-scrape; archive never rescraped

## 8. Limitations / Pitfalls

- Boxscore links (`scouting.do`) often dead for archives → only aggregates left
- Inconsistent IDs (`matchId`, `spielplan_id`, `matchNo`)
- HTML tables need parsing (no JSON)
- Forfeits/Verzicht marked with `*` or empty scores
- Quotas (3P%, FT%) can't be computed if attempts missing

## 9. Implementation Summary

✅ **In short:**
- Use **REST** for current seasons → rich per-game stats
- Use **HTML + Excel** for archives → only season aggregates reliable
- Keep all ID variants (`matchId`, `matchNo`, `spielplan_id`) in DB for mapping
- Provenance/caching is key: mark source (REST vs Archive)

## 10. Example URLs

### REST Examples:
```
POST https://www.basketball-bund.net/rest/wam/data
GET https://www.basketball-bund.net/rest/liga/id/12345/season/2024/matches
GET https://www.basketball-bund.net/rest/match/id/67890/matchInfo
```

### HTML Examples:
```
GET https://www.basketball-bund.net/statistik.do?reqCode=statTeamArchiv&liga_id=12345&saison_id=2023
GET https://www.basketball-bund.net/scouting.do?reqCode=spielStatistik&spielplan_id=54321
GET https://www.basketball-bund.net/index.jsp?Action=107&liga_id=12345&saison_id=2023
```

## 11. Data Flow

```
Discovery (REST) → League IDs → Season IDs → Match IDs
                ↓
Current Season: REST API → Full boxscores + play-by-play
Archive Season: HTML scraping → Aggregate stats only
                ↓
Database: Store with provenance metadata
```
