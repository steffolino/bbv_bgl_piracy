
import { PrismaClient } from '@prisma/client';
import fs from 'fs';
import path from 'path';

const prisma = new PrismaClient();

// Directory containing crawled JSON files
const DATA_DIR = path.resolve(__dirname, '../../paginated_data');

async function ingestSeasonFile(filePath: string) {
  const raw = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(raw);
  const { season, players, liga_ids } = data;

  // Insert leagues if not exists
  for (const liga of liga_ids) {
    const existingLeague = await prisma.league.findUnique({
      where: { ligaId_seasonId: { ligaId: liga.liga_id, seasonId: String(season) } }
    });
    if (!existingLeague) {
      await prisma.league.create({
        data: {
          ligaId: liga.liga_id,
          seasonId: String(season),
          name: liga.name,
          source: 'crawl',
          scraped_at: new Date(),
        }
      });
    }
  }

  // Insert players and stats if not exists
  for (const entry of players) {
    if (!entry.name) continue;
    let player = await prisma.player.findFirst({ where: { name: entry.name } });
    if (!player) {
      player = await prisma.player.create({ data: { name: entry.name } });
    }
    const existingStat = await prisma.seasonStat.findUnique({
      where: { playerId_seasonId: { playerId: player.id, seasonId: String(season) } }
    });
    if (!existingStat) {
      await prisma.seasonStat.create({
        data: {
          playerId: player.id,
          seasonId: String(season),
          pts: parseInt(entry.col_2 || '0'),
          g: parseInt(entry.col_3 || '0'),
          pts_g: parseFloat(entry.col_4 || '0'),
          threePm: parseInt(entry.col_5 || '0'),
          threePa: parseInt(entry.col_6 || '0'),
          threePPct: parseFloat(entry.col_7 || '0'),
          ftm: parseInt(entry.col_8 || '0'),
          fta: parseInt(entry.col_9 || '0'),
          ft_pct: parseFloat(entry.col_10 || '0'),
        }
      });
    }
  }
}

async function main() {
  const files = fs.readdirSync(DATA_DIR).filter((f: string) => f.endsWith('.json'));
  for (const file of files) {
    console.log(`Ingesting ${file}...`);
    await ingestSeasonFile(path.join(DATA_DIR, file));
  }
  await prisma.$disconnect();
  console.log('✅ Ingestion complete.');
}

main().catch(e => {
  console.error(e);
  prisma.$disconnect();
});
