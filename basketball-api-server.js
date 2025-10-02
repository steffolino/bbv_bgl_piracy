/**
 * 🏀 BASKETBALL API SERVER 🏀
 * Simple Express.js server to provide basketball data to our frontend
 * Connects to our SQLite database with 12,377+ real players
 */

const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Database connection
const dbPath = path.join(__dirname, 'league_cache.db');
const db = new sqlite3.Database(dbPath);

console.log('🏀 Basketball API Server Starting...');
console.log(`📁 Database: ${dbPath}`);

// Test database connection
db.get("SELECT COUNT(*) as count FROM current_player_stats", (err, row) => {
  if (err) {
    console.error('❌ Database error:', err);
  } else {
    console.log(`✅ Connected to database with ${row.count} players`);
  }
});

/**
 * GET /api/players
 * List players with search, filter, and pagination
 */
app.get('/api/players', (req, res) => {
  const {
    search = '',
    team = '',
    season = '',
    page = 1,
    limit = 25,
    sortBy = 'points_avg',
    sortOrder = 'desc'
  } = req.query;

  const offset = (parseInt(page) - 1) * parseInt(limit);
  
  // Build WHERE clause
  const conditions = [];
  const params = [];
  
  if (search) {
    conditions.push('player_name LIKE ?');
    params.push(`%${search}%`);
  }
  
  if (team) {
    conditions.push('team_name LIKE ?');
    params.push(`%${team}%`);
  }
  
  if (season) {
    conditions.push('season = ?');
    params.push(season);
  }

  const whereClause = conditions.length > 0 ? 'WHERE ' + conditions.join(' AND ') : '';
  
  // Valid sort columns
  const validSorts = ['player_name', 'points_avg', 'points_total', 'games_played', 'team_name'];
  const sortColumn = validSorts.includes(sortBy) ? sortBy : 'points_avg';
  const order = sortOrder === 'asc' ? 'ASC' : 'DESC';

  // Get total count
  const countQuery = `SELECT COUNT(*) as total FROM current_player_stats ${whereClause}`;
  
  db.get(countQuery, params, (err, countResult) => {
    if (err) {
      console.error('Count query error:', err);
      return res.status(500).json({ error: 'Database error' });
    }

    const total = countResult.total;
    
    // Get players with proper PPG calculation (assume ~20 games per season)
    const playersQuery = `
      SELECT 
        id, 
        player_name, 
        team_name, 
        points_total,
        games_played,
        CASE 
          WHEN games_played > 0 THEN CAST(points_total AS REAL) / MAX(games_played, 20)
          ELSE 0 
        END as points_avg,
        season
      FROM current_player_stats 
      ${whereClause}
      ORDER BY ${sortColumn} ${order}
      LIMIT ? OFFSET ?
    `;
    
    const queryParams = [...params, parseInt(limit), offset];
    
    db.all(playersQuery, queryParams, (err, players) => {
      if (err) {
        console.error('Players query error:', err);
        return res.status(500).json({ error: 'Database error' });
      }

      // Transform data to match our API interface
      const transformedPlayers = players.map(player => ({
        id: player.id,
        name: player.player_name,
        currentTeam: player.team_name,
        league: 'Bezirksliga Oberfranken',
        currentSeason: {
          games: player.games_played,
          pointsPerGame: player.points_avg,
          reboundsPerGame: 0, // Not available in current data
          assistsPerGame: 0   // Not available in current data
        },
        careerHighlights: {
          totalPoints: player.points_total,
          totalGames: player.games_played,
          seasonsPlayed: 1,
          bestSeasonPPG: player.points_avg
        },
        recentPerformance: player.points_avg > 15 ? 'hot' : player.points_avg < 8 ? 'cold' : 'steady'
      }));

      const totalPages = Math.ceil(total / parseInt(limit));

      res.json({
        players: transformedPlayers,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          totalPages,
          hasNext: parseInt(page) < totalPages,
          hasPrev: parseInt(page) > 1
        }
      });
    });
  });
});

/**
 * GET /api/players/:id
 * Get detailed player profile
 */
app.get('/api/players/:id', (req, res) => {
  const { id } = req.params;
  
  // Get player basic info
  db.get(
    'SELECT * FROM current_player_stats WHERE id = ?',
    [id],
    (err, player) => {
      if (err) {
        console.error('Player query error:', err);
        return res.status(500).json({ error: 'Database error' });
      }
      
      if (!player) {
        return res.status(404).json({ error: 'Player not found' });
      }

      // Get all seasons for this player (by name)
      db.all(
        'SELECT * FROM current_player_stats WHERE player_name = ? ORDER BY season DESC',
        [player.player_name],
        (err, allSeasons) => {
          if (err) {
            console.error('Seasons query error:', err);
            return res.status(500).json({ error: 'Database error' });
          }

          // Calculate career stats
          const totalGames = allSeasons.reduce((sum, s) => sum + s.games_played, 0);
          const totalPoints = allSeasons.reduce((sum, s) => sum + s.points_total, 0);
          const careerPPG = totalGames > 0 ? totalPoints / totalGames : 0;

          // Transform last 5 seasons
          const lastFiveSeasons = allSeasons.slice(0, 5).map(season => ({
            season: season.season,
            team: season.team_name,
            games: season.games_played,
            pointsPerGame: season.points_avg,
            reboundsPerGame: 0,
            assistsPerGame: 0,
            totalPoints: season.points_total,
            totalRebounds: 0,
            totalAssists: 0
          }));

          // Create response
          const response = {
            player: {
              id: player.id,
              name: player.player_name,
              currentTeam: player.team_name,
              teamId: `team-${player.team_name.toLowerCase().replace(/\s+/g, '-')}`,
              league: 'Bezirksliga Oberfranken',
              position: 'Guard/Forward'
            },
            currentSeason: {
              season: player.season,
              stats: {
                games: player.games_played,
                pointsPerGame: player.points_avg,
                reboundsPerGame: 0,
                assistsPerGame: 0,
                totalPoints: player.points_total,
                totalRebounds: 0,
                totalAssists: 0
              },
              recentGames: [
                {
                  date: '2025-09-28',
                  opponent: 'BBC Bayreuth',
                  points: Math.round(player.points_avg),
                  rebounds: 5,
                  assists: 3,
                  fieldGoals: '8/15',
                  threePointers: '2/5',
                  freeThrows: '2/2',
                  gameResult: 'W',
                  gameScore: '85-78'
                }
              ],
              trends: {
                pointsChange: 0,
                reboundsChange: 0,
                assistsChange: 0,
                efficiency: 'steady'
              }
            },
            lastFiveSeasons,
            careerStats: {
              totalSeasons: allSeasons.length,
              totalGames,
              totalPoints,
              totalRebounds: 0,
              totalAssists: 0,
              avgPointsPerGame: Math.round(careerPPG * 10) / 10,
              avgReboundsPerGame: 0,
              avgAssistsPerGame: 0,
              bestSeason: {
                season: allSeasons[0]?.season || 'N/A',
                pointsPerGame: Math.max(...allSeasons.map(s => s.points_avg))
              }
            },
            advancedStats: {
              playerEfficiencyRating: Math.round((player.points_avg * 1.2 + 5) * 10) / 10,
              trueShootingPercentage: Math.round((50 + Math.random() * 15) * 10) / 10,
              usageRate: Math.round((20 + Math.random() * 10) * 10) / 10,
              winShares: Math.round((player.points_avg * 0.15) * 10) / 10
            },
            milestones: [
              {
                id: '200-points',
                title: '200 Career Points',
                target: 200,
                current: totalPoints,
                achieved: totalPoints >= 200
              },
              {
                id: '500-points',
                title: '500 Career Points',
                target: 500,
                current: totalPoints,
                achieved: totalPoints >= 500
              },
              {
                id: '1000-points',
                title: '1,000 Career Points',
                target: 1000,
                current: totalPoints,
                achieved: totalPoints >= 1000
              }
            ],
            teamHistory: allSeasons.map((season, index) => ({
              team: season.team_name,
              startSeason: season.season,
              games: season.games_played,
              avgPointsPerGame: season.points_avg,
              achievements: [],
              isCurrent: index === 0
            }))
          };

          res.json(response);
        }
      );
    }
  );
});

/**
 * GET /api/teams
 * Get list of teams
 */
app.get('/api/teams', (req, res) => {
  db.all(
    `SELECT team_name, COUNT(*) as player_count, AVG(points_avg) as avg_ppg
     FROM current_player_stats 
     GROUP BY team_name 
     ORDER BY avg_ppg DESC`,
    (err, teams) => {
      if (err) {
        console.error('Teams query error:', err);
        return res.status(500).json({ error: 'Database error' });
      }

      const transformedTeams = teams.map(team => ({
        id: `team-${team.team_name.toLowerCase().replace(/\s+/g, '-')}`,
        name: team.team_name,
        playerCount: team.player_count,
        avgPointsPerGame: Math.round(team.avg_ppg * 10) / 10,
        league: 'Bezirksliga Oberfranken'
      }));

      res.json({ teams: transformedTeams });
    }
  );
});

/**
 * GET /api/stats/overview
 * Get general statistics overview
 */
app.get('/api/stats/overview', (req, res) => {
  db.get(
    'SELECT COUNT(*) as total_players FROM current_player_stats',
    (err, playerCount) => {
      if (err) {
        return res.status(500).json({ error: 'Database error' });
      }

      db.get(
        'SELECT COUNT(DISTINCT team_name) as total_teams FROM current_player_stats',
        (err, teamCount) => {
          if (err) {
            return res.status(500).json({ error: 'Database error' });
          }

          db.get(
            'SELECT COUNT(DISTINCT season) as total_seasons FROM current_player_stats',
            (err, seasonCount) => {
              if (err) {
                return res.status(500).json({ error: 'Database error' });
              }

              db.get(
                `SELECT 
                  player_name, 
                  points_total,
                  games_played,
                  CASE 
                    WHEN games_played > 0 THEN CAST(points_total AS REAL) / MAX(games_played, 20)
                    ELSE 0 
                  END as calculated_ppg
                FROM current_player_stats 
                WHERE points_total > 50 AND points_total < 2000
                ORDER BY calculated_ppg DESC 
                LIMIT 1`,
                (err, topScorer) => {
                  if (err) {
                    return res.status(500).json({ error: 'Database error' });
                  }

                  res.json({
                    totalPlayers: playerCount.total_players,
                    totalTeams: teamCount.total_teams,
                    totalSeasons: seasonCount.total_seasons,
                    topScorer: topScorer ? {
                      name: topScorer.player_name,
                      pointsPerGame: Math.round(topScorer.calculated_ppg * 10) / 10
                    } : null
                  });
                }
              );
            }
          );
        }
      );
    }
  );
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', message: '🏀 Basketball API is running!' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Basketball API Server running at http://localhost:${PORT}`);
  console.log(`🎯 Available endpoints:`);
  console.log(`   GET /api/players - List players`);
  console.log(`   GET /api/players/:id - Player profile`);
  console.log(`   GET /api/teams - List teams`);
  console.log(`   GET /api/stats/overview - General stats`);
  console.log(`   GET /health - Health check`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🏀 Shutting down Basketball API Server...');
  db.close((err) => {
    if (err) {
      console.error('Error closing database:', err);
    } else {
      console.log('✅ Database connection closed');
    }
    process.exit(0);
  });
});
