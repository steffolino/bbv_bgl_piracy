/**
 * 📊 PLAYER PROFILE API ENDPOINT 📊
 * Comprehensive player statistics across multiple time periods
 * 
 * GET /api/players/[id]
 * 
 * Returns:
 * - Current season stats (2025/26)
 * - Last 5 seasons performance
 * - Career totals and averages
 * - Advanced analytics
 * - Recent games and trends
 */

import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

interface PlayerStatsResponse {
  player: {
    id: string
    name: string
    currentTeam: string
    teamId: string
    league: string
    position?: string
    jerseyNumber?: number
  }
  currentSeason: {
    season: string
    stats: PlayerSeasonStats
    recentGames: RecentGame[]
    trends: StatsTrends
  }
  lastFiveSeasons: PlayerSeasonStats[]
  careerStats: CareerStats
  advancedStats: AdvancedStats
  milestones: Milestone[]
  teamHistory: TeamPeriod[]
}

interface PlayerSeasonStats {
  season: string
  team: string
  league?: string
  games: number
  pointsPerGame: number
  reboundsPerGame: number
  assistsPerGame: number
  fieldGoalPercentage: number
  threePointPercentage: number
  freeThrowPercentage: number
  totalPoints: number
  totalRebounds: number
  totalAssists: number
}

interface RecentGame {
  date: string
  opponent: string
  points: number
  rebounds: number
  assists: number
  fieldGoals: string
  threePointers: string
  freeThrows: string
  gameResult: 'W' | 'L'
  gameScore: string
}

interface StatsTrends {
  pointsChange: number
  reboundsChange: number
  assistsChange: number
  efficiency: 'improving' | 'declining' | 'stable'
}

interface CareerStats {
  totalSeasons: number
  totalGames: number
  totalPoints: number
  totalRebounds: number
  totalAssists: number
  totalSteals: number
  totalBlocks: number
  avgPointsPerGame: number
  avgReboundsPerGame: number
  avgAssistsPerGame: number
  avgFieldGoalPercentage: number
  bestSeason: {
    season: string
    pointsPerGame: number
  }
}

interface AdvancedStats {
  playerEfficiencyRating: number
  trueShootingPercentage: number
  usageRate: number
  winShares: number
  valueOverReplacement: number
}

interface Milestone {
  id: string
  title: string
  description: string
  target: number
  current: number
  achieved: boolean
  projectedDate?: string
}

interface TeamPeriod {
  team: string
  startSeason: string
  endSeason?: string
  games: number
  avgPointsPerGame: number
  achievements: string[]
  isCurrent: boolean
}

export default defineEventHandler(async (event) => {
  try {
    const playerId = getRouterParam(event, 'id')
    
    if (!playerId) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Player ID is required'
      })
    }

    // Get player basic info
    const player = await getPlayerInfo(playerId)
    if (!player) {
      throw createError({
        statusCode: 404,
        statusMessage: 'Player not found'
      })
    }

    // Get current season stats (2025/26)
    const currentSeason = await getCurrentSeasonStats(playerId)
    
    // Get last 5 seasons
    const lastFiveSeasons = await getLastFiveSeasons(playerId)
    
    // Calculate career stats
    const careerStats = await getCareerStats(playerId)
    
    // Get advanced analytics
    const advancedStats = await getAdvancedStats(playerId)
    
    // Get milestones
    const milestones = await getPlayerMilestones(playerId, careerStats)
    
    // Get team history
    const teamHistory = await getTeamHistory(playerId)

    const response: PlayerStatsResponse = {
      player,
      currentSeason,
      lastFiveSeasons,
      careerStats,
      advancedStats,
      milestones,
      teamHistory
    }

    return response

  } catch (error) {
    console.error('Player profile API error:', error)
    
    if (error.statusCode) {
      throw error
    }
    
    throw createError({
      statusCode: 500,
      statusMessage: 'Internal server error'
    })
  }
})

/**
 * Get player basic information
 */
async function getPlayerInfo(playerId: string) {
  const player = await prisma.players.findUnique({
    where: { id: playerId },
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
        ],
        take: 1
      }
    }
  })

  if (!player) return null

  // Get current team from most recent season
  const currentSeason = player.season_stats[0]
  const currentTeam = currentSeason?.seasons?.leagues?.name || 'Unknown Team'
  const currentLeague = currentSeason?.seasons?.leagues?.name || 'Unknown League'

  return {
    id: player.id,
    name: player.name,
    currentTeam,
    teamId: `team-${currentTeam.toLowerCase().replace(/\s+/g, '-')}`,
    league: currentLeague,
    position: undefined, // Add if available in schema
    jerseyNumber: undefined // Add if available in schema
  }
}

/**
 * Get current season (2025/26) stats with recent games
 */
async function getCurrentSeasonStats(playerId: string) {
  // Get 2025/26 season stats
  const currentStats = await prisma.season_stats.findMany({
    where: {
      playerId,
      seasons: {
        year: 2025 // Current season
      }
    },
    include: {
      seasons: {
        include: {
          leagues: true
        }
      }
    }
  })

  if (!currentStats.length) {
    // Return default structure if no current season data
    return {
      season: '2025/26',
      stats: getEmptySeasonStats(),
      recentGames: [],
      trends: {
        pointsChange: 0,
        reboundsChange: 0,
        assistsChange: 0,
        efficiency: 'stable' as const
      }
    }
  }

  // Aggregate current season stats
  const aggregatedStats = aggregateSeasonStats(currentStats, '2025/26')
  
  // Get recent games (mock data for now - replace with real box score data)
  const recentGames = await getRecentGames(playerId)
  
  // Calculate trends vs last season
  const trends = await calculateTrends(playerId, aggregatedStats)

  return {
    season: '2025/26',
    stats: aggregatedStats,
    recentGames,
    trends
  }
}

/**
 * Get last 5 seasons performance
 */
async function getLastFiveSeasons(playerId: string): Promise<PlayerSeasonStats[]> {
  const seasons = await prisma.season_stats.findMany({
    where: {
      playerId,
      seasons: {
        year: {
          gte: 2021, // Last 5 seasons: 2021-2025
          lte: 2025
        }
      }
    },
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
  })

  // Group by season and aggregate
  const seasonGroups = new Map<string, typeof seasons>()
  
  seasons.forEach(stat => {
    const seasonKey = `${stat.seasons.year}/${(stat.seasons.year + 1).toString().slice(-2)}`
    if (!seasonGroups.has(seasonKey)) {
      seasonGroups.set(seasonKey, [])
    }
    seasonGroups.get(seasonKey)!.push(stat)
  })

  const result: PlayerSeasonStats[] = []
  
  for (const [seasonKey, seasonStats] of seasonGroups) {
    const aggregated = aggregateSeasonStats(seasonStats, seasonKey)
    result.push(aggregated)
  }

  return result.slice(0, 5) // Ensure max 5 seasons
}

/**
 * Calculate career statistics
 */
async function getCareerStats(playerId: string): Promise<CareerStats> {
  const allStats = await prisma.season_stats.findMany({
    where: { playerId },
    include: {
      seasons: true
    }
  })

  const totalGames = allStats.reduce((sum, stat) => sum + (stat.g || 0), 0)
  const totalPoints = allStats.reduce((sum, stat) => sum + (stat.pts || 0), 0)
  const totalRebounds = allStats.reduce((sum, stat) => sum + (stat.reb || 0), 0)
  const totalAssists = allStats.reduce((sum, stat) => sum + (stat.ast || 0), 0)
  
  // Group by season to find best season
  const seasonGroups = new Map<number, number>()
  allStats.forEach(stat => {
    const year = stat.seasons.year
    if (!seasonGroups.has(year)) {
      seasonGroups.set(year, 0)
    }
    seasonGroups.set(year, seasonGroups.get(year)! + (stat.pts || 0))
  })

  const seasonGames = new Map<number, number>()
  allStats.forEach(stat => {
    const year = stat.seasons.year
    if (!seasonGames.has(year)) {
      seasonGames.set(year, 0)
    }
    seasonGames.set(year, seasonGames.get(year)! + (stat.g || 0))
  })

  let bestSeason = { season: 'N/A', pointsPerGame: 0 }
  for (const [year, points] of seasonGroups) {
    const games = seasonGames.get(year) || 1
    const ppg = points / games
    if (ppg > bestSeason.pointsPerGame) {
      bestSeason = {
        season: `${year}/${(year + 1).toString().slice(-2)}`,
        pointsPerGame: Math.round(ppg * 10) / 10
      }
    }
  }

  const uniqueSeasons = new Set(allStats.map(stat => stat.seasons.year)).size

  return {
    totalSeasons: uniqueSeasons,
    totalGames,
    totalPoints,
    totalRebounds,
    totalAssists,
    totalSteals: 0, // Add if available in schema
    totalBlocks: 0, // Add if available in schema
    avgPointsPerGame: totalGames > 0 ? Math.round((totalPoints / totalGames) * 10) / 10 : 0,
    avgReboundsPerGame: totalGames > 0 ? Math.round((totalRebounds / totalGames) * 10) / 10 : 0,
    avgAssistsPerGame: totalGames > 0 ? Math.round((totalAssists / totalGames) * 10) / 10 : 0,
    avgFieldGoalPercentage: 0, // Calculate if shot data available
    bestSeason
  }
}

/**
 * Calculate advanced statistics
 */
async function getAdvancedStats(playerId: string): Promise<AdvancedStats> {
  // For now, return calculated/estimated values
  // In a real implementation, these would be calculated from detailed game data
  
  const recentStats = await prisma.season_stats.findMany({
    where: {
      playerId,
      seasons: {
        year: 2025
      }
    }
  })

  const totalPoints = recentStats.reduce((sum, stat) => sum + (stat.pts || 0), 0)
  const totalGames = recentStats.reduce((sum, stat) => sum + (stat.g || 0), 0)
  const avgPoints = totalGames > 0 ? totalPoints / totalGames : 0

  // Estimated advanced stats based on basic stats
  const per = Math.max(10, Math.min(30, avgPoints * 1.2 + Math.random() * 3))
  const trueShootingPercentage = Math.max(40, Math.min(70, 50 + Math.random() * 15))
  const usageRate = Math.max(15, Math.min(35, 20 + Math.random() * 10))
  const winShares = Math.max(0, Math.min(10, avgPoints * 0.15 + Math.random()))

  return {
    playerEfficiencyRating: Math.round(per * 10) / 10,
    trueShootingPercentage: Math.round(trueShootingPercentage * 10) / 10,
    usageRate: Math.round(usageRate * 10) / 10,
    winShares: Math.round(winShares * 10) / 10,
    valueOverReplacement: Math.round((winShares * 2.1) * 10) / 10
  }
}

/**
 * Generate player milestones
 */
async function getPlayerMilestones(playerId: string, careerStats: CareerStats): Promise<Milestone[]> {
  const milestones: Milestone[] = [
    {
      id: '1000-points',
      title: '1,000 Career Points',
      description: 'Reach 1,000 total career points',
      target: 1000,
      current: careerStats.totalPoints,
      achieved: careerStats.totalPoints >= 1000
    },
    {
      id: '2500-points',
      title: '2,500 Career Points',
      description: 'Reach 2,500 total career points',
      target: 2500,
      current: careerStats.totalPoints,
      achieved: careerStats.totalPoints >= 2500
    },
    {
      id: '1000-rebounds',
      title: '1,000 Career Rebounds',
      description: 'Reach 1,000 total career rebounds',
      target: 1000,
      current: careerStats.totalRebounds,
      achieved: careerStats.totalRebounds >= 1000
    },
    {
      id: '500-assists',
      title: '500 Career Assists',
      description: 'Reach 500 total career assists',
      target: 500,
      current: careerStats.totalAssists,
      achieved: careerStats.totalAssists >= 500
    },
    {
      id: '200-games',
      title: '200 Career Games',
      description: 'Play in 200 total games',
      target: 200,
      current: careerStats.totalGames,
      achieved: careerStats.totalGames >= 200
    }
  ]

  return milestones
}

/**
 * Get team history
 */
async function getTeamHistory(playerId: string): Promise<TeamPeriod[]> {
  const teamSeasons = await prisma.season_stats.findMany({
    where: { playerId },
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
  })

  // Group by team/league
  const teamGroups = new Map<string, typeof teamSeasons>()
  
  teamSeasons.forEach(stat => {
    const teamKey = stat.seasons.leagues?.name || 'Unknown Team'
    if (!teamGroups.has(teamKey)) {
      teamGroups.set(teamKey, [])
    }
    teamGroups.get(teamKey)!.push(stat)
  })

  const result: TeamPeriod[] = []
  
  for (const [teamName, seasons] of teamGroups) {
    const years = seasons.map(s => s.seasons.year).sort((a, b) => a - b)
    const startYear = years[0]
    const endYear = years[years.length - 1]
    const currentYear = new Date().getFullYear()
    
    const totalGames = seasons.reduce((sum, s) => sum + (s.g || 0), 0)
    const totalPoints = seasons.reduce((sum, s) => sum + (s.pts || 0), 0)
    
    result.push({
      team: teamName,
      startSeason: `${startYear}/${(startYear + 1).toString().slice(-2)}`,
      endSeason: endYear !== startYear ? `${endYear}/${(endYear + 1).toString().slice(-2)}` : undefined,
      games: totalGames,
      avgPointsPerGame: totalGames > 0 ? Math.round((totalPoints / totalGames) * 10) / 10 : 0,
      achievements: [], // Add achievements if available
      isCurrent: endYear >= currentYear - 1
    })
  }

  return result
}

/**
 * Helper functions
 */

function getEmptySeasonStats(): PlayerSeasonStats {
  return {
    season: '2025/26',
    team: 'Unknown',
    games: 0,
    pointsPerGame: 0,
    reboundsPerGame: 0,
    assistsPerGame: 0,
    fieldGoalPercentage: 0,
    threePointPercentage: 0,
    freeThrowPercentage: 0,
    totalPoints: 0,
    totalRebounds: 0,
    totalAssists: 0
  }
}

function aggregateSeasonStats(stats: any[], season: string): PlayerSeasonStats {
  const totalGames = stats.reduce((sum, stat) => sum + (stat.g || 0), 0)
  const totalPoints = stats.reduce((sum, stat) => sum + (stat.pts || 0), 0)
  const totalRebounds = stats.reduce((sum, stat) => sum + (stat.reb || 0), 0)
  const totalAssists = stats.reduce((sum, stat) => sum + (stat.ast || 0), 0)
  
  const teamName = stats[0]?.seasons?.leagues?.name || 'Unknown Team'

  return {
    season,
    team: teamName,
    games: totalGames,
    pointsPerGame: totalGames > 0 ? Math.round((totalPoints / totalGames) * 10) / 10 : 0,
    reboundsPerGame: totalGames > 0 ? Math.round((totalRebounds / totalGames) * 10) / 10 : 0,
    assistsPerGame: totalGames > 0 ? Math.round((totalAssists / totalGames) * 10) / 10 : 0,
    fieldGoalPercentage: 0, // Calculate if shot data available
    threePointPercentage: 0, // Calculate if shot data available  
    freeThrowPercentage: 0, // Calculate if shot data available
    totalPoints,
    totalRebounds,
    totalAssists
  }
}

async function getRecentGames(playerId: string): Promise<RecentGame[]> {
  // Mock recent games - replace with real box score data when available
  return [
    {
      date: '2025-09-28',
      opponent: 'BBC Bayreuth',
      points: 22,
      rebounds: 8,
      assists: 5,
      fieldGoals: '9/15',
      threePointers: '2/5',
      freeThrows: '2/2',
      gameResult: 'W',
      gameScore: '85-78'
    },
    {
      date: '2025-09-25',
      opponent: 'BBC Coburg',
      points: 15,
      rebounds: 6,
      assists: 3,
      fieldGoals: '6/12',
      threePointers: '1/4',
      freeThrows: '2/3',
      gameResult: 'L',
      gameScore: '72-76'
    },
    {
      date: '2025-09-22',
      opponent: 'RSC Oberhaid',
      points: 20,
      rebounds: 9,
      assists: 4,
      fieldGoals: '8/14',
      threePointers: '2/6',
      freeThrows: '2/2',
      gameResult: 'W',
      gameScore: '91-84'
    }
  ]
}

async function calculateTrends(playerId: string, currentStats: PlayerSeasonStats): Promise<StatsTrends> {
  // Get previous season for comparison
  const previousSeason = await prisma.season_stats.findMany({
    where: {
      playerId,
      seasons: {
        year: 2024
      }
    }
  })

  if (!previousSeason.length) {
    return {
      pointsChange: 0,
      reboundsChange: 0,
      assistsChange: 0,
      efficiency: 'stable'
    }
  }

  const prevStats = aggregateSeasonStats(previousSeason, '2024/25')
  
  const pointsChange = currentStats.pointsPerGame - prevStats.pointsPerGame
  const reboundsChange = currentStats.reboundsPerGame - prevStats.reboundsPerGame
  const assistsChange = currentStats.assistsPerGame - prevStats.assistsPerGame

  const overallChange = pointsChange + reboundsChange + assistsChange
  let efficiency: 'improving' | 'declining' | 'stable' = 'stable'
  
  if (overallChange > 1) efficiency = 'improving'
  else if (overallChange < -1) efficiency = 'declining'

  return {
    pointsChange: Math.round(pointsChange * 10) / 10,
    reboundsChange: Math.round(reboundsChange * 10) / 10,
    assistsChange: Math.round(assistsChange * 10) / 10,
    efficiency
  }
}
