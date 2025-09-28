import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { getPrisma } from '@bg/db'

type Bindings = {
  DB: D1Database
  ENVIRONMENT?: string
}

const app = new Hono<{ Bindings: Bindings }>()

// Middleware
app.use('*', cors({
  origin: ['http://localhost:8080', 'http://localhost:8081'],
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowHeaders: ['Content-Type', 'Authorization'],
}))

// Health check
app.get('/health', async (c) => {
  try {
    const prisma = getPrisma(c.env.DB)
    const leagueCount = await prisma.league.count()
    
    return c.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      database: 'connected',
      leagues: leagueCount
    })
  } catch (error) {
    return c.json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Unknown error'
    }, 500)
  }
})

// League routes
app.get('/league/:ligaId/:seasonId', async (c) => {
  const { ligaId, seasonId } = c.req.param()
  const prisma = getPrisma(c.env.DB)
  
  try {
    const league = await prisma.league.findUnique({
      where: {
        ligaId_seasonId: {
          ligaId,
          seasonId
        }
      },
      include: {
        matches: {
          include: {
            homeTeam: true,
            guestTeam: true
          }
        }
      }
    })
    
    if (!league) {
      return c.json({ error: 'League not found' }, 404)
    }
    
    return c.json(league)
  } catch (error) {
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.get('/league/discover/rest', async (c) => {
  // Stub for league discovery
  return c.json({
    message: 'League discovery endpoint - to be implemented',
    endpoint: '/rest/wam/data'
  })
})

// Match routes
app.get('/match/:matchId', async (c) => {
  const { matchId } = c.req.param()
  const prisma = getPrisma(c.env.DB)
  
  try {
    const match = await prisma.match.findUnique({
      where: { matchId },
      include: {
        homeTeam: true,
        guestTeam: true,
        boxscoreRows: {
          include: {
            player: true,
            team: true
          }
        }
      }
    })
    
    if (!match) {
      return c.json({ error: 'Match not found' }, 404)
    }
    
    return c.json(match)
  } catch (error) {
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.get('/match/archiv/scouting/:spielplan_id', async (c) => {
  const { spielplan_id } = c.req.param()
  
  return c.json({
    message: 'Archive scouting endpoint - to be implemented',
    spielplan_id,
    endpoint: `scouting.do?reqCode=spielStatistik&spielplan_id=${spielplan_id}`
  })
})

// Export routes
app.get('/exports/boxscores.ndjson', async (c) => {
  const prisma = getPrisma(c.env.DB)
  
  try {
    const boxscores = await prisma.boxscoreRow.findMany({
      include: {
        match: true,
        player: true,
        team: true
      }
    })
    
    // Convert to NDJSON format
    const ndjson = boxscores
      .map(row => JSON.stringify({
        ...row,
        provenance: {
          source: row.source,
          scraped_at: row.scraped_at
        }
      }))
      .join('\n')
    
    c.header('Content-Type', 'application/x-ndjson')
    return c.text(ndjson)
  } catch (error) {
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.get('/exports/season.csv', async (c) => {
  const prisma = getPrisma(c.env.DB)
  
  try {
    const seasonStats = await prisma.seasonStat.findMany({
      include: {
        player: true,
        season: true
      }
    })
    
    // Convert to CSV format
    const headers = ['playerId', 'playerName', 'seasonId', 'year', 'pts', 'g', 'pts_g', '3pm', '3pa', '3p_pct', 'ftm', 'fta', 'ft_pct']
    const csv = [
      headers.join(','),
      ...seasonStats.map(stat => [
        stat.playerId,
        `"${stat.player.name}"`,
        stat.seasonId,
        stat.season.year,
        stat.pts,
        stat.g,
        stat.pts_g,
        stat.threePm,
        stat.threePa,
        stat.threePPct,
        stat.ftm,
        stat.fta,
        stat.ft_pct
      ].join(','))
    ].join('\n')
    
    c.header('Content-Type', 'text/csv')
    return c.text(csv)
  } catch (error) {
    return c.json({ error: 'Internal server error' }, 500)
  }
})

// QA routes
app.get('/qa/issues', async (c) => {
  const prisma = getPrisma(c.env.DB)
  
  try {
    const issues = await prisma.qA_Issue.findMany({
      include: {
        match: true,
        season: true
      },
      orderBy: {
        created_at: 'desc'
      }
    })
    
    return c.json(issues)
  } catch (error) {
    return c.json({ error: 'Internal server error' }, 500)
  }
})

app.post('/qa/recalculate/:seasonId', async (c) => {
  const { seasonId } = c.req.param()
  
  return c.json({
    message: 'QA recalculation endpoint - to be implemented',
    seasonId
  })
})

// Admin routes
app.post('/admin/aliases', async (c) => {
  return c.json({
    message: 'Alias management endpoint - to be implemented'
  })
})

app.post('/admin/qa/:id/:action', async (c) => {
  const { id, action } = c.req.param()
  
  if (!['confirm', 'ignore'].includes(action)) {
    return c.json({ error: 'Invalid action' }, 400)
  }
  
  const prisma = getPrisma(c.env.DB)
  
  try {
    const updatedIssue = await prisma.qA_Issue.update({
      where: { id },
      data: { status: action === 'confirm' ? 'confirmed' : 'ignored' }
    })
    
    return c.json(updatedIssue)
  } catch (error) {
    return c.json({ error: 'Issue not found or update failed' }, 404)
  }
})

export default app