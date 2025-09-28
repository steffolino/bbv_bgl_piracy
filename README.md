# Basketball Stats Platform (BG Litzendorf Focus)

A modern basketball statistics platform focused on **players** as the primary entity, with BG Litzendorf 1–3 teams as secondary filters.

## Tech Stack

- **Backend/API**: Cloudflare Workers (TypeScript, Hono)
- **Database**: Cloudflare D1 (SQLite) via Prisma
- **Frontend**: Nuxt 3 + Tailwind CSS + DaisyUI + i18n (DE/EN)
- **CI/CD**: GitHub Actions → Cloudflare deployment

## Project Structure

```
├── apps/
│   ├── api-worker/          # Cloudflare Worker API
│   ├── frontend-public/     # Public Nuxt frontend (player-first)
│   └── frontend-admin/      # Admin Nuxt frontend (QA dashboard)
├── packages/
│   ├── db/                  # Prisma schema & client
│   └── shared/              # Shared types & utilities
├── .github/workflows/       # CI/CD pipelines
└── ops/nginx/               # Local development proxy
```

## Quick Start

1. **Install dependencies**
   ```bash
   pnpm install
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Generate database client**
   ```bash
   pnpm run db:generate
   ```

4. **Run development servers**
   ```bash
   pnpm dev
   ```

   This starts:
   - Public frontend: http://localhost:8080
   - Admin frontend: http://localhost:8081  
   - API Worker: http://localhost:8082

## Features

### Public Frontend (Player-First)
- **Dashboard**: Player statistics overview (PTS/G, 3P%, FT%)
- **Player profiles**: Career timelines and season comparisons
- **Explorer**: Build custom charts with player metrics
- **Filters**: BG Litzendorf teams (1-3) as secondary filter
- **Customization**: Dark/light mode, DE/EN language switch

### Admin Frontend (QA Dashboard)
- **Authentication**: Simple cookie-based login (demo: admin/password)
- **QA Issues**: List and manage data quality issues
- **Exports**: Download NDJSON and CSV data exports
- **Alias Management**: (placeholder for team/player name normalization)

### API Worker
- **Health check**: Database connectivity and league count
- **League routes**: Discovery and season data
- **Match data**: Individual match with boxscores
- **QA endpoints**: Issue management and recalculation
- **Exports**: NDJSON boxscores and CSV season stats

## Development

### Local Development
- Uses Docker Compose with Nginx proxy for clean port management
- Hot reloading enabled for all services
- SQLite database for local development

### Database Schema
See `packages/db/prisma/schema.prisma` for the complete data model:
- **Player-centric**: Players as primary entities
- **Provenance**: Source tracking for data quality
- **Flexible matching**: Support for REST API and HTML scraping identifiers

### Deployment
- **CI**: Builds and type-checks on push/PR
- **Worker**: Auto-deploys to Cloudflare Workers on main branch
- **Pages**: Auto-deploys both frontends to Cloudflare Pages

## Data Sources

- **REST API** (current seasons): `/rest/wam/data`, `/rest/liga/id/{ligaId}/season/{seasonId}/matches`
- **Archive HTML** (historical): `statistik.do`, `scouting.do` endpoints
- **QA System**: Automated data quality checks and issue flagging

For more details, see [COPILOT.md](./COPILOT.md)