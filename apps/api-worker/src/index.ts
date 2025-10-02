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
      .map((row: any) => JSON.stringify({
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
      ...seasonStats.map((stat: any) => [
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

// Crawl Logs routes - Proxy to Python API bridge
const PYTHON_API_BASE = 'http://localhost:5000'

app.get('/crawl/sessions', async (c) => {
  const limit = c.req.query('limit') || '20'
  
  try {
    const response = await fetch(`${PYTHON_API_BASE}/api/crawl/sessions?limit=${limit}`)
    const data = await response.json() as any
    
    if (!response.ok) {
      return c.json({ error: data.error || 'Failed to fetch sessions' }, response.status)
    }
    
    return c.json(data)
  } catch (error) {
    console.error('Failed to connect to Python API bridge:', error)
    
    // Fallback to mock data if Python API is unavailable
    return c.json({
      sessions: [
        {
          id: 'log_test_20250929_135949',
          session_name: 'Log Test Spider - 2025-09-29 13:59:49',
          spider_name: 'log_test',
          start_time: '2025-09-29T13:59:49',
          status: 'completed',
          total_requests: 4,
          successful_requests: 4,
          failed_requests: 0,
          items_scraped: 0,
          leagues_discovered: 0,
          duration_minutes: 1
        }
      ],
      total: 1,
      note: 'Fallback data - Python API bridge unavailable'
    })
  }
})

app.get('/crawl/sessions/:sessionId', async (c) => {
  const { sessionId } = c.req.param()
  
  try {
    const response = await fetch(`${PYTHON_API_BASE}/api/crawl/sessions/${sessionId}`)
    const data = await response.json() as any
    
    if (!response.ok) {
      return c.json({ error: data.error || 'Session not found' }, response.status)
    }
    
    return c.json(data)
  } catch (error) {
    console.error('Failed to connect to Python API bridge:', error)
    
    // Fallback mock data
    return c.json({
      session: {
        id: sessionId,
        session_name: 'Log Test Spider - 2025-09-29 13:59:49',
        spider_name: 'log_test',
        start_time: '2025-09-29T13:59:49',
        status: 'completed',
        configuration: {
          test_scenarios: 4,
          enhanced_logging: true,
          database_path: 'crawl_logs.db'
        }
      },
      log_levels: {
        'INFO': 18,
        'WARNING': 1,
        'ERROR': 0,
        'DEBUG': 5
      },
      discoveries_count: 0,
      errors_count: 0,
      top_discoveries: [],
      note: 'Fallback data - Python API bridge unavailable'
    })
  }
})

app.get('/crawl/logs/search', async (c) => {
  const params = new URLSearchParams()
  
  // Forward all query parameters
  const queryParams = ['session_id', 'level', 'search', 'league_id', 'start_date', 'end_date', 'limit', 'offset']
  queryParams.forEach(param => {
    const value = c.req.query(param)
    if (value) params.append(param, value)
  })
  
  try {
    const response = await fetch(`${PYTHON_API_BASE}/api/crawl/logs/search?${params.toString()}`)
    const data = await response.json() as any
    
    if (!response.ok) {
      return c.json({ error: data.error || 'Failed to search logs' }, response.status)
    }
    
    return c.json(data)
  } catch (error) {
    console.error('Failed to connect to Python API bridge:', error)
    
    // Fallback mock data
    return c.json({
      logs: [
        {
          id: 'log_001',
          timestamp: '2025-09-29T13:59:49',
          level: 'INFO',
          logger_name: 'log_test',
          message: '🚀 Crawl logging session started: log_test_20250929_135949',
          url: null,
          response_status: null,
          league_id: null,
          season_year: null
        },
        {
          id: 'log_002',
          timestamp: '2025-09-29T13:59:50',
          level: 'INFO',
          logger_name: 'log_test',
          message: '📝 Enhanced logging enabled for session: log_test_20250929_135949',
          url: null,
          response_status: null,
          league_id: null,
          season_year: null
        }
      ],
      total: 2,
      filters: Object.fromEntries(params),
      note: 'Fallback data - Python API bridge unavailable'
    })
  }
})

app.get('/crawl/discoveries', async (c) => {
  const params = new URLSearchParams()
  
  // Forward discovery search parameters
  const queryParams = ['session_id', 'league_name', 'district_name', 'min_matches', 'season_year', 'data_quality', 'limit']
  queryParams.forEach(param => {
    const value = c.req.query(param)
    if (value) params.append(param, value)
  })
  
  try {
    const response = await fetch(`${PYTHON_API_BASE}/api/crawl/discoveries?${params.toString()}`)
    const data = await response.json() as any
    
    if (!response.ok) {
      return c.json({ error: data.error || 'Failed to fetch discoveries' }, response.status)
    }
    
    return c.json(data)
  } catch (error) {
    console.error('Failed to connect to Python API bridge:', error)
    
    return c.json({
      discoveries: [],
      total: 0,
      note: 'Fallback data - Python API bridge unavailable'
    })
  }
})

app.get('/crawl/statistics', async (c) => {
  const days = c.req.query('days') || '30'
  
  try {
    const response = await fetch(`${PYTHON_API_BASE}/api/crawl/statistics?days=${days}`)
    const data = await response.json() as any
    
    if (!response.ok) {
      return c.json({ error: data.error || 'Failed to fetch statistics' }, response.status)
    }
    
    return c.json(data)
  } catch (error) {
    console.error('Failed to connect to Python API bridge:', error)
    
    return c.json({
      period_days: parseInt(days),
      session_stats: {
        total_sessions: 2,
        completed_sessions: 2,
        failed_sessions: 0,
        running_sessions: 0,
        total_requests: 4,
        successful_requests: 4,
        failed_requests: 0,
        total_items: 0,
        total_discoveries: 0
      },
      log_levels: {
        'INFO': 18,
        'WARNING': 1,
        'ERROR': 0,
        'DEBUG': 5
      },
      success_rate: 100.0,
      error_types: {},
      note: 'Fallback data - Python API bridge unavailable'
    })
  }
})

app.get('/crawl/league/:leagueId/history', async (c) => {
  const { leagueId } = c.req.param()
  
  try {
    const response = await fetch(`${PYTHON_API_BASE}/api/crawl/league/${leagueId}/history`)
    const data = await response.json() as any
    
    if (!response.ok) {
      return c.json({ error: data.error || 'Failed to fetch league history' }, response.status)
    }
    
    return c.json(data)
  } catch (error) {
    console.error('Failed to connect to Python API bridge:', error)
    
    return c.json({
      league_id: leagueId,
      history: [],
      note: 'Fallback data - Python API bridge unavailable'
    })
  }
})

// Admin Authentication Middleware
app.use('/admin/*', async (c, next) => {
  const authHeader = c.req.header('Authorization')
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return c.json({ error: 'Authentication required' }, 401)
  }
  
  const token = authHeader.substring(7)
  // TODO: Implement JWT verification
  // For now, accept any token for development
  
  await next()
})

// Admin Vereine Management Routes
app.get('/admin/vereine', async (c) => {
  const prisma = getPrisma(c.env.DB)
  
  try {
    const vereine = await prisma.verein.findMany({
      include: {
        teams: {
          select: {
            id: true,
            name: true,
            category: true,
            team_number: true,
            is_active: true
          }
        },
        _count: {
          select: {
            teams: true,
            admin_users: true
          }
        }
      },
      orderBy: {
        name: 'asc'
      }
    })
    
    return c.json({
      vereine: vereine.map((v: any) => ({
        ...v,
        team_count: v._count.teams,
        admin_count: v._count.admin_users
      }))
    })
  } catch (error) {
    return c.json({ error: 'Failed to fetch vereine' }, 500)
  }
})

app.post('/admin/vereine', async (c) => {
  const prisma = getPrisma(c.env.DB)
  
  try {
    const data = await c.req.json()
    
    // Validate required fields
    if (!data.name) {
      return c.json({ error: 'Verein name is required' }, 400)
    }
    
    const verein = await prisma.verein.create({
      data: {
        name: data.name,
        short_name: data.short_name,
        website: data.website,
        email: data.email,
        phone: data.phone,
        instagram: data.instagram,
        facebook: data.facebook,
        twitter: data.twitter,
        address_street: data.address_street,
        address_city: data.address_city,
        address_postal_code: data.address_postal_code,
        address_state: data.address_state,
        region: data.region,
        country: data.country || 'Deutschland',
        founded_year: data.founded_year,
        description: data.description,
        logo_url: data.logo_url,
        primary_color: data.primary_color,
        secondary_color: data.secondary_color,
        home_gym_name: data.home_gym_name,
        home_gym_address: data.home_gym_address,
        home_gym_capacity: data.home_gym_capacity,
        home_gym_facilities: data.home_gym_facilities,
        admin_user_id: data.admin_user_id
      }
    })
    
    // TODO: Create audit log entry
    
    return c.json(verein, 201)
  } catch (error) {
    return c.json({ error: 'Failed to create verein' }, 500)
  }
})

app.get('/admin/vereine/:id', async (c) => {
  const { id } = c.req.param()
  const prisma = getPrisma(c.env.DB)
  
  try {
    const verein = await prisma.verein.findUnique({
      where: { id },
      include: {
        teams: {
          orderBy: [
            { category: 'asc' },
            { team_number: 'asc' }
          ]
        },
        admin_users: {
          select: {
            id: true,
            email: true,
            first_name: true,
            last_name: true,
            role: true,
            is_active: true
          }
        }
      }
    })
    
    if (!verein) {
      return c.json({ error: 'Verein not found' }, 404)
    }
    
    return c.json(verein)
  } catch (error) {
    return c.json({ error: 'Failed to fetch verein' }, 500)
  }
})

app.put('/admin/vereine/:id', async (c) => {
  const { id } = c.req.param()
  const prisma = getPrisma(c.env.DB)
  
  try {
    const data = await c.req.json()
    
    const verein = await prisma.verein.update({
      where: { id },
      data: {
        name: data.name,
        short_name: data.short_name,
        website: data.website,
        email: data.email,
        phone: data.phone,
        instagram: data.instagram,
        facebook: data.facebook,
        twitter: data.twitter,
        address_street: data.address_street,
        address_city: data.address_city,
        address_postal_code: data.address_postal_code,
        address_state: data.address_state,
        region: data.region,
        country: data.country,
        founded_year: data.founded_year,
        description: data.description,
        logo_url: data.logo_url,
        primary_color: data.primary_color,
        secondary_color: data.secondary_color,
        home_gym_name: data.home_gym_name,
        home_gym_address: data.home_gym_address,
        home_gym_capacity: data.home_gym_capacity,
        home_gym_facilities: data.home_gym_facilities,
        updated_at: new Date()
      }
    })
    
    return c.json(verein)
  } catch (error) {
    return c.json({ error: 'Failed to update verein' }, 500)
  }
})

app.delete('/admin/vereine/:id', async (c) => {
  const { id } = c.req.param()
  const prisma = getPrisma(c.env.DB)
  
  try {
    // Check if verein has teams
    const teamCount = await prisma.team.count({
      where: { verein_id: id }
    })
    
    if (teamCount > 0) {
      return c.json({ 
        error: 'Cannot delete verein with associated teams. Please reassign or delete teams first.' 
      }, 400)
    }
    
    await prisma.verein.delete({
      where: { id }
    })
    
    return c.json({ message: 'Verein deleted successfully' })
  } catch (error) {
    return c.json({ error: 'Failed to delete verein' }, 500)
  }
})

// Team Management Routes
app.post('/admin/vereine/:vereinId/teams', async (c) => {
  const { vereinId } = c.req.param()
  const prisma = getPrisma(c.env.DB)
  
  try {
    const data = await c.req.json()
    
    const team = await prisma.team.create({
      data: {
        name: data.name,
        verein_id: vereinId,
        team_number: data.team_number || 1,
        category: data.category,
        gender: data.gender,
        league_level: data.league_level,
        jersey_home_color: data.jersey_home_color,
        jersey_away_color: data.jersey_away_color,
        home_court: data.home_court,
        sponsors: data.sponsors,
        season_start: data.season_start
      }
    })
    
    return c.json(team, 201)
  } catch (error) {
    return c.json({ error: 'Failed to create team' }, 500)
  }
})

app.put('/admin/teams/:id', async (c) => {
  const { id } = c.req.param()
  const prisma = getPrisma(c.env.DB)
  
  try {
    const data = await c.req.json()
    
    const team = await prisma.team.update({
      where: { id },
      data: {
        name: data.name,
        verein_id: data.verein_id,
        team_number: data.team_number,
        category: data.category,
        gender: data.gender,
        league_level: data.league_level,
        jersey_home_color: data.jersey_home_color,
        jersey_away_color: data.jersey_away_color,
        home_court: data.home_court,
        sponsors: data.sponsors,
        is_active: data.is_active,
        season_start: data.season_start,
        season_end: data.season_end
      }
    })
    
    return c.json(team)
  } catch (error) {
    return c.json({ error: 'Failed to update team' }, 500)
  }
})

app.delete('/admin/teams/:id', async (c) => {
  const { id } = c.req.param()
  const prisma = getPrisma(c.env.DB)
  
  try {
    // Check if team has associated matches or players
    const matchCount = await prisma.match.count({
      where: {
        OR: [
          { homeTeamId: id },
          { guestTeamId: id }
        ]
      }
    })
    
    if (matchCount > 0) {
      // Don't delete, just deactivate
      const team = await prisma.team.update({
        where: { id },
        data: { 
          is_active: false,
          season_end: new Date().getFullYear()
        }
      })
      
      return c.json({ 
        message: 'Team deactivated (has match history)',
        team 
      })
    } else {
      await prisma.team.delete({
        where: { id }
      })
      
      return c.json({ message: 'Team deleted successfully' })
    }
  } catch (error) {
    return c.json({ error: 'Failed to delete team' }, 500)
  }
})

// Team Suggestions (AI-powered matching)
app.get('/admin/vereine/:id/team-suggestions', async (c) => {
  const { id } = c.req.param()
  const prisma = getPrisma(c.env.DB)
  
  try {
    const verein = await prisma.verein.findUnique({
      where: { id },
      select: { name: true, short_name: true }
    })
    
    if (!verein) {
      return c.json({ error: 'Verein not found' }, 404)
    }
    
    // Find unassigned teams that might belong to this verein
    const searchTerms = [
      verein.short_name,
      verein.name.replace(' e.V.', ''),
      verein.name.split(' ')[0] // First part like "BG", "BBC", etc.
    ].filter(Boolean)
    
    const suggestions = await prisma.team.findMany({
      where: {
        verein_id: null, // Unassigned teams only
        OR: searchTerms.map(term => ({
          name: {
            contains: term,
            mode: 'insensitive'
          }
        }))
      },
      take: 20
    })
    
    // Calculate match confidence
    const suggestionsWithConfidence = suggestions.map((team: any) => {
      let confidence = 0
      const teamLower = team.name.toLowerCase()
      
      for (const term of searchTerms) {
        if (teamLower.includes(term.toLowerCase())) {
          confidence += 30
        }
      }
      
      // Exact match bonus
      if (teamLower.startsWith(verein.short_name?.toLowerCase() || '')) {
        confidence += 40
      }
      
      return {
        ...team,
        confidence: Math.min(confidence, 99),
        suggested_category: extractCategory(team.name),
        suggested_team_number: extractTeamNumber(team.name)
      }
    })
    
    return c.json({
      verein,
      suggestions: suggestionsWithConfidence.sort((a: any, b: any) => b.confidence - a.confidence)
    })
  } catch (error) {
    return c.json({ error: 'Failed to generate suggestions' }, 500)
  }
})

// Bulk Import Teams
app.post('/admin/vereine/:id/import-teams', async (c) => {
  const { id } = c.req.param()
  const prisma = getPrisma(c.env.DB)
  
  try {
    const { team_ids } = await c.req.json()
    
    if (!Array.isArray(team_ids)) {
      return c.json({ error: 'team_ids must be an array' }, 400)
    }
    
    const results = await Promise.all(
      team_ids.map(async (teamId) => {
        try {
          const team = await prisma.team.update({
            where: { id: teamId },
            data: { verein_id: id }
          })
          return { success: true, team }
        } catch (error) {
          return { success: false, teamId, error: error instanceof Error ? error.message : 'Unknown error' }
        }
      })
    )
    
    const successful = results.filter(r => r.success)
    const failed = results.filter(r => !r.success)
    
    return c.json({
      imported: successful.length,
      failed: failed.length,
      results
    })
  } catch (error) {
    return c.json({ error: 'Failed to import teams' }, 500)
  }
})

// File Upload for Logos
app.post('/admin/vereine/:id/logo', async (c) => {
  // TODO: Implement file upload handling
  // This would typically integrate with Cloudflare Images or similar
  return c.json({
    message: 'Logo upload endpoint - to be implemented with file storage'
  })
})

// Helper functions
function extractCategory(teamName: string): string {
  const name = teamName.toLowerCase()
  
  if (name.includes('u8')) return 'U8'
  if (name.includes('u10')) return 'U10'
  if (name.includes('u12')) return 'U12'
  if (name.includes('u14')) return 'U14'
  if (name.includes('u16')) return 'U16'
  if (name.includes('u18')) return 'U18'
  if (name.includes('u20')) return 'U20'
  if (name.includes('ü40') || name.includes('senior')) return 'Ü40'
  if (name.includes('ü50')) return 'Ü50'
  if (name.includes('herren') || name.includes('männlich')) return 'Herren'
  if (name.includes('damen') || name.includes('weiblich')) return 'Damen'
  
  return 'Unbekannt'
}

function extractTeamNumber(teamName: string): number {
  const match = teamName.match(/\s+(\d+)$/)
  return match ? parseInt(match[1]) : 1
}

export default app