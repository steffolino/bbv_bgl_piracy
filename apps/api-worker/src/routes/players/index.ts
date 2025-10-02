/**
 * 🏀 PLAYERS LIST API ENDPOINT 🏀
 * Browse and search through all basketball players
 * 
 * GET /api/players
 * 
 * Query Parameters:
 * - search: Search by player name
 * - team: Filter by team/club
 * - league: Filter by league
 * - season: Filter by season (default: current)
 * - page: Page number (default: 1)
 * - limit: Results per page (default: 25)
 * - sortBy: Sort field (name, points, rebounds, assists)
 * - sortOrder: asc or desc
 */

import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

interface PlayersListResponse {
  players: PlayerListItem[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
    hasNext: boolean
    hasPrev: boolean
  }
  filters: {
    availableTeams: string[]
    availableLeagues: string[]
    availableSeasons: string[]
  }
}

interface PlayerListItem {
  id: string
  name: string
  currentTeam: string
  league: string
  currentSeason: {
    games: number
    pointsPerGame: number
    reboundsPerGame: number
    assistsPerGame: number
  }
  careerHighlights: {
    totalPoints: number
    totalGames: number
    seasonsPlayed: number
    bestSeasonPPG: number
  }
  recentPerformance: 'hot' | 'cold' | 'steady'
  jerseyNumber?: number
  position?: string
}

export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event)
    
    // Parse query parameters
    const search = (query.search as string) || ''
    const team = (query.team as string) || ''
    const league = (query.league as string) || ''
    const season = parseInt((query.season as string) || '2025') // Current season
    const page = Math.max(1, parseInt((query.page as string) || '1'))
    const limit = Math.min(100, Math.max(1, parseInt((query.limit as string) || '25')))
    const sortBy = (query.sortBy as string) || 'name'
    const sortOrder = (query.sortOrder as string) === 'desc' ? 'desc' : 'asc'
    
    const offset = (page - 1) * limit

    // Build where clause for filtering
    const whereClause = await buildWhereClause({
      search,
      team,
      league,
      season
    })

    // Get total count for pagination
    const total = await prisma.players.count({
      where: whereClause
    })

    // Get players with stats
    const playersData = await prisma.players.findMany({
      where: whereClause,
      include: {
        season_stats: {
          include: {
            seasons: {
              include: {
                leagues: true
              }
            }
          },
          orderBy: [
            { seasons: { year: 'desc' } }
          ]
        }
      },
      skip: offset,
      take: limit,
      orderBy: getOrderByClause(sortBy, sortOrder)
    })

    // Transform data to response format
    const players: PlayerListItem[] = playersData.map(player => {
      const currentSeasonStats = player.season_stats.filter(
        stat => stat.seasons.year === season
      )
      
      const allSeasonStats = player.season_stats
      
      // Calculate current season averages
      const currentStats = calculateSeasonAverages(currentSeasonStats)
      
      // Calculate career highlights
      const careerHighlights = calculateCareerHighlights(allSeasonStats)
      
      // Determine recent performance trend
      const recentPerformance = calculatePerformanceTrend(player.season_stats, season)
      
      // Get current team and league
      const currentTeamInfo = getCurrentTeamInfo(player.season_stats, season)

      return {
        id: player.id,
        name: player.name,
        currentTeam: currentTeamInfo.team,
        league: currentTeamInfo.league,
        currentSeason: currentStats,
        careerHighlights,
        recentPerformance,
        jerseyNumber: undefined, // Add if available in schema
        position: undefined // Add if available in schema
      }
    })

    // Get filter options
    const filters = await getFilterOptions()

    const totalPages = Math.ceil(total / limit)

    const response: PlayersListResponse = {
      players,
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1
      },
      filters
    }

    return response

  } catch (error) {
    console.error('Players list API error:', error)
    
    throw createError({
      statusCode: 500,
      statusMessage: 'Internal server error'
    })
  }
})

/**
 * Build where clause for filtering players
 */
async function buildWhereClause(filters: {
  search: string
  team: string
  league: string
  season: number
}) {
  const whereClause: any = {}

  // Search by player name
  if (filters.search) {
    whereClause.name = {
      contains: filters.search,
      mode: 'insensitive'
    }
  }

  // Filter by team or league
  if (filters.team || filters.league || filters.season) {
    whereClause.season_stats = {
      some: {
        ...(filters.season && {
          seasons: {
            year: filters.season
          }
        }),
        ...(filters.team || filters.league) && {
          seasons: {
            ...(filters.season && { year: filters.season }),
            leagues: {
              ...(filters.team && {
                name: {
                  contains: filters.team,
                  mode: 'insensitive'
                }
              }),
              ...(filters.league && {
                name: {
                  contains: filters.league,
                  mode: 'insensitive'
                }
              })
            }
          }
        }
      }
    }
  }

  return whereClause
}

/**
 * Get order by clause for sorting
 */
function getOrderByClause(sortBy: string, sortOrder: 'asc' | 'desc') {
  switch (sortBy) {
    case 'name':
      return { name: sortOrder }
    case 'points':
      // For now, sort by name - would need aggregated stats for proper sorting
      return { name: sortOrder }
    case 'rebounds':
      return { name: sortOrder }
    case 'assists':
      return { name: sortOrder }
    default:
      return { name: 'asc' }
  }
}

/**
 * Calculate season averages for a player
 */
function calculateSeasonAverages(seasonStats: any[]) {
  if (!seasonStats.length) {
    return {
      games: 0,
      pointsPerGame: 0,
      reboundsPerGame: 0,
      assistsPerGame: 0
    }
  }

  const totalGames = seasonStats.reduce((sum, stat) => sum + (stat.g || 0), 0)
  const totalPoints = seasonStats.reduce((sum, stat) => sum + (stat.pts || 0), 0)
  const totalRebounds = seasonStats.reduce((sum, stat) => sum + (stat.reb || 0), 0)
  const totalAssists = seasonStats.reduce((sum, stat) => sum + (stat.ast || 0), 0)

  return {
    games: totalGames,
    pointsPerGame: totalGames > 0 ? Math.round((totalPoints / totalGames) * 10) / 10 : 0,
    reboundsPerGame: totalGames > 0 ? Math.round((totalRebounds / totalGames) * 10) / 10 : 0,
    assistsPerGame: totalGames > 0 ? Math.round((totalAssists / totalGames) * 10) / 10 : 0
  }
}

/**
 * Calculate career highlights for a player
 */
function calculateCareerHighlights(allStats: any[]) {
  const totalGames = allStats.reduce((sum, stat) => sum + (stat.g || 0), 0)
  const totalPoints = allStats.reduce((sum, stat) => sum + (stat.pts || 0), 0)
  
  // Group by season to find best season
  const seasonGroups = new Map<number, { points: number, games: number }>()
  
  allStats.forEach(stat => {
    const year = stat.seasons.year
    if (!seasonGroups.has(year)) {
      seasonGroups.set(year, { points: 0, games: 0 })
    }
    const season = seasonGroups.get(year)!
    season.points += stat.pts || 0
    season.games += stat.g || 0
  })

  let bestSeasonPPG = 0
  for (const [year, season] of seasonGroups) {
    if (season.games > 0) {
      const ppg = season.points / season.games
      if (ppg > bestSeasonPPG) {
        bestSeasonPPG = ppg
      }
    }
  }

  const seasonsPlayed = seasonGroups.size

  return {
    totalPoints,
    totalGames,
    seasonsPlayed,
    bestSeasonPPG: Math.round(bestSeasonPPG * 10) / 10
  }
}

/**
 * Calculate performance trend
 */
function calculatePerformanceTrend(allStats: any[], currentSeason: number): 'hot' | 'cold' | 'steady' {
  const currentStats = allStats.filter(stat => stat.seasons.year === currentSeason)
  const previousStats = allStats.filter(stat => stat.seasons.year === currentSeason - 1)
  
  if (!currentStats.length || !previousStats.length) {
    return 'steady'
  }

  const currentAvg = calculateSeasonAverages(currentStats)
  const previousAvg = calculateSeasonAverages(previousStats)
  
  const improvement = currentAvg.pointsPerGame - previousAvg.pointsPerGame
  
  if (improvement > 2) return 'hot'
  if (improvement < -2) return 'cold'
  return 'steady'
}

/**
 * Get current team and league info
 */
function getCurrentTeamInfo(allStats: any[], season: number) {
  const currentSeasonStats = allStats.filter(stat => stat.seasons.year === season)
  
  if (currentSeasonStats.length > 0) {
    const teamName = currentSeasonStats[0].seasons.leagues?.name || 'Unknown Team'
    return {
      team: teamName,
      league: teamName // For now, team and league are the same
    }
  }

  // Fallback to most recent season
  if (allStats.length > 0) {
    const latestStat = allStats[0] // Already ordered by year desc
    const teamName = latestStat.seasons.leagues?.name || 'Unknown Team'
    return {
      team: teamName,
      league: teamName
    }
  }

  return {
    team: 'Unknown Team',
    league: 'Unknown League'
  }
}

/**
 * Get available filter options
 */
async function getFilterOptions() {
  // Get all unique teams/leagues
  const teams = await prisma.leagues.findMany({
    select: {
      name: true
    },
    distinct: ['name']
  })

  // Get available seasons
  const seasons = await prisma.seasons.findMany({
    select: {
      year: true
    },
    distinct: ['year'],
    orderBy: {
      year: 'desc'
    }
  })

  return {
    availableTeams: teams.map(t => t.name).sort(),
    availableLeagues: teams.map(t => t.name).sort(), // Same as teams for now
    availableSeasons: seasons.map(s => s.year.toString())
  }
}
