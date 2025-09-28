import { z } from 'zod'

// League Schema
export const LeagueSchema = z.object({
  ligaId: z.string(),
  seasonId: z.string(),
  name: z.string(),
  level: z.string().optional(),
  region: z.string().optional(),
  source: z.string(),
  scraped_at: z.date(),
})

// Season Schema
export const SeasonSchema = z.object({
  seasonId: z.string(),
  year: z.number(),
  ligaId: z.string(),
})

// Match Schema
export const MatchSchema = z.object({
  matchId: z.string().optional(),
  matchNo: z.number().optional(),
  spielplan_id: z.string().optional(),
  seasonId: z.string(),
  ligaId: z.string(),
  date: z.date(),
  homeTeamId: z.string(),
  guestTeamId: z.string(),
  result: z.string().optional(),
  status: z.string(),
})

// BoxscoreRow Schema
export const BoxscoreRowSchema = z.object({
  id: z.string(),
  matchId: z.string().optional(),
  teamId: z.string(),
  playerId: z.string().optional(),
  playerName: z.string(),
  pts: z.number().default(0),
  threePm: z.number().default(0),
  threePa: z.number().default(0),
  ftm: z.number().default(0),
  fta: z.number().default(0),
  source: z.string(),
  scraped_at: z.date(),
})

// Player Schema
export const PlayerSchema = z.object({
  id: z.string(),
  name: z.string(),
  aliases: z.array(z.string()),
})

// Team Schema
export const TeamSchema = z.object({
  id: z.string(),
  name: z.string(),
  aliases: z.array(z.string()),
})

// SeasonStat Schema
export const SeasonStatSchema = z.object({
  id: z.string(),
  playerId: z.string(),
  seasonId: z.string(),
  pts: z.number().default(0),
  g: z.number().default(0),
  pts_g: z.number().default(0),
  threePm: z.number().default(0),
  threePa: z.number().default(0),
  threePPct: z.number().default(0),
  ftm: z.number().default(0),
  fta: z.number().default(0),
  ft_pct: z.number().default(0),
})

// QA Issue Schema
export const QAIssueSchema = z.object({
  id: z.string(),
  type: z.string(),
  matchId: z.string().optional(),
  seasonId: z.string().optional(),
  description: z.string(),
  status: z.enum(['open', 'confirmed', 'ignored']).default('open'),
  created_at: z.date().default(() => new Date()),
})

// Export types
export type League = z.infer<typeof LeagueSchema>
export type Season = z.infer<typeof SeasonSchema>
export type Match = z.infer<typeof MatchSchema>
export type BoxscoreRow = z.infer<typeof BoxscoreRowSchema>
export type Player = z.infer<typeof PlayerSchema>
export type Team = z.infer<typeof TeamSchema>
export type SeasonStat = z.infer<typeof SeasonStatSchema>
export type QAIssue = z.infer<typeof QAIssueSchema>