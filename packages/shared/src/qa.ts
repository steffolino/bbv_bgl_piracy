// QA Helper functions

export function zScore(value: number, mean: number, stdDev: number): number {
  if (stdDev === 0) return 0
  return (value - mean) / stdDev
}

export function isOutlier(value: number, mean: number, stdDev: number, threshold: number = 4): boolean {
  return Math.abs(zScore(value, mean, stdDev)) > threshold
}

export function isQuotaVisible(attempts: number, made: number): boolean {
  return attempts > 0
}

export function calculatePercentage(made: number, attempts: number): number {
  if (attempts === 0) return 0
  return Math.round((made / attempts) * 100 * 100) / 100 // Round to 2 decimal places
}

export function calculatePointsPerGame(points: number, games: number): number {
  if (games === 0) return 0
  return Math.round((points / games) * 100) / 100 // Round to 2 decimal places
}

// QA validation functions
export function validateSeasonTotals(
  seasonTotal: number,
  boxscoreSum: number,
  gamesPlayed: number,
  tolerance: number = 2
): boolean {
  const toleranceTotal = tolerance * gamesPlayed
  return Math.abs(seasonTotal - boxscoreSum) <= toleranceTotal
}

export function isDuplicateMatch(
  match1: { homeTeamId: string; guestTeamId: string; date: Date; result?: string },
  match2: { homeTeamId: string; guestTeamId: string; date: Date; result?: string }
): boolean {
  return (
    match1.homeTeamId === match2.homeTeamId &&
    match1.guestTeamId === match2.guestTeamId &&
    match1.date.getTime() === match2.date.getTime() &&
    match1.result === match2.result
  )
}

// Team name normalization for BG Litzendorf filtering
export function isBGLitzendorfTeam(teamName: string): boolean {
  const normalized = teamName.toLowerCase().trim()
  return normalized.includes('bg litzendorf') || 
         normalized.includes('bgl') ||
         normalized.match(/bg\s*litzendorf\s*[1-3]?/i) !== null
}

export function extractBGLitzendorfLevel(teamName: string): number | null {
  const match = teamName.match(/bg\s*litzendorf\s*(\d)/i)
  if (match) {
    const level = parseInt(match[1])
    return level >= 1 && level <= 3 ? level : 1
  }
  return isBGLitzendorfTeam(teamName) ? 1 : null
}