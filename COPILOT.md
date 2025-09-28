# Epic: Basketball Stats Platform (Player-Centric, BG Litzendorf Focus)

## Vision
Build a modern basketball statistics platform focused on **players** as the primary entity.  
BG Litzendorf 1–3 is a **secondary filter**: users can view all players or restrict to BG Litzendorf across all seasons.  

- **DB-first approach** with well-defined schemas  
- **Cloudflare deployment** (Workers + D1/Pages)  
- **Local development environment** with `.env` files and Docker proxy  
- **Two frontends**:  
  - Admin/QA Dashboard (login protected)  
  - Public User Analytics (player-first, customizable)

---

## Tech Stack
- **Backend/API**: Cloudflare Workers (TypeScript, Hono)  
- **DB**: Cloudflare D1 (SQLite) via Prisma (DB-first migrations)  
- **Frontend**: Nuxt 4 + Tailwind + DaisyUI + i18n (DE/EN)  
- **CI/CD**: GitHub → Cloudflare deployment (dev & prod environments)

---

## Data Model (DB-First)
Tables (with primary keys & provenance):
- `League(ligaId, seasonId, name, level, region, source, scraped_at)`  
- `Season(seasonId, year, ligaId)`  
- `Match(matchId?, matchNo?, spielplan_id?, seasonId, ligaId, date, homeTeamId, guestTeamId, result, status)`  
- `BoxscoreRow(id, matchId, teamId, playerId?, playerName, pts, 3pm, 3pa, ftm, fta, source, scraped_at)`  
- `Player(id?, name, aliases[])`  
- `Team(id?, name, aliases[])`  
- `SeasonStat(playerId, seasonId, pts, g, pts_g, 3pm, 3pa, 3p_pct, ftm, fta, ft_pct)`  
- `Alias(entityType, value, targetId)`  
- `QA_Issue(id, type, matchId?, seasonId?, description, status, created_at)`

---

## Sources
- **REST (preferred for current seasons)**  
  - `/rest/wam/data` (league discovery)  
  - `/rest/liga/id/{ligaId}/season/{seasonId}/matches`  
  - `/rest/match/id/{matchId}/matchInfo` (+ boxscore if available)

- **Archiv (HTML fallback)**  
  - `statistik.do?reqCode=statBesteWerferArchiv|statBeste3erWerferArchiv|statBesteFreiWerferArchiv|statTeamArchiv`  
  - `scouting.do?reqCode=spielStatistik&spielplan_id={id}`  

- **Mapping**  
  - Excel `Spielnummer` = `matchNo`  
  - REST key = `matchId`  
  - HTML key = `spielplan_id`

---

## QA Rules
- Sum check: season totals ≈ Σ boxscores (±2 pts/game)  
- Quota check: show % only if attempts > 0  
- Duplicates: same teams/date/result → flag  
- Outliers: z-score > 4 on pts/game → flag  
- Verzicht/abgesagt: mark from exports/flags  

---

## Frontend (UX)
- **Admin Dashboard (login)**  
  - QA board with issue list + actions (reparse, confirm, ignore)  
  - Crawler controls (manual re-scrape, schedule view)  
  - Stammdaten editor (aliases)  
  - Exports (NDJSON + CSV)

- **Public Frontend (player-first)**  
  - **Dashboard**: default view shows **player statistics** (PTS/G, 3P%, FT%, career timelines)  
  - **Player profile**: career timeline, season view, comparisons  
  - **Explorer (build-your-own)**:  
    - Main dimension: **Players**  
    - Secondary filters: Team (BG Litzendorf 1–3 or all), Season, League  
    - Choose metrics (PTS, 3P, FT, PTS/G)  
    - Combine stats into advanced metrics (e.g. PER)  
    - Chart types: line, bar, scatter, animation (trend lines, bar race, scrubber)  
  - **Customization**: dark/light mode, language switch (DE/EN), archive+current combined or split, all-time stats  
  - **Inspiration**: basketball-reference.com, but modern/cleaner with DaisyUI cards + animations

---

## Tasks

### Repo Setup
- [ ] Init monorepo (Nuxt frontend + Workers backend)  
- [ ] Configure Prisma (DB-first schema)  
- [ ] Add Cloudflare config for Workers + D1  
- [ ] Setup `.env` handling (DATABASE_URL, API_KEYS, SCRAPE_INTERVAL, etc.)  
- [ ] Docker config for local dev (proxy + dev DB)  

### Backend/API
- [ ] Implement league/season/match discovery (REST)  
- [ ] Implement archiv parsers (`statistik.do`, `scouting.do`)  
- [ ] Normalization layer (Match, Boxscore, SeasonStat)  
- [ ] QA service (issue detection & storage)  
- [ ] Exports: NDJSON + CSV  

### Frontend Public
- [ ] Nuxt 4 project with DaisyUI, Tailwind, i18n  
- [ ] Layout with dark/light mode, language switch  
- [ ] Dashboard with player-focused cards and charts  
- [ ] Player profile view (career + comparison)  
- [ ] Explorer (metrics, filters, animations, build-your-own)

### Frontend Admin
- [ ] Auth (login protected)  
- [ ] QA dashboard (issue list + actions)  
- [ ] Crawler control panel  
- [ ] Alias management  
- [ ] Export download page  

### Deployment
- [ ] GitHub Actions → Cloudflare (dev + prod)  
- [ ] Local dev with `docker-compose.dev.yml`  

---

## Acceptance Criteria
- Repo builds locally with `npm run dev` and `.env` setup  
- Cloudflare deploys run automatically on push to main  
- Admin login works; QA board lists issues with links  
- User sees **player-first statistics** by default  
- BG Litzendorf 1–3 available as **filter**, not as primary navigation  
- User can build custom charts (metrics, trends, animations)  
- Scraper jobs run weekly for current season; archive never rescraped  
- Exports available in NDJSON + CSV with provenance fields  