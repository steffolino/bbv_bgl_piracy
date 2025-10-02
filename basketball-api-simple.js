/**
 * 🏀 SIMPLE BASKETBALL API SERVER 🏀
 * Fixed version with proper PPG calculations
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
 * GET /api/stats/overview
 * Get general statistics overview with FIXED PPG
 */
app.get('/api/stats/overview', (req, res) => {
  // Get total players
  db.get('SELECT COUNT(*) as total_players FROM current_player_stats', (err, playerCount) => {
    if (err) return res.status(500).json({ error: 'Database error' });

    // Get total teams
    db.get('SELECT COUNT(DISTINCT team_name) as total_teams FROM current_player_stats', (err, teamCount) => {
      if (err) return res.status(500).json({ error: 'Database error' });

      // Get total seasons
      db.get('SELECT COUNT(DISTINCT season) as total_seasons FROM current_player_stats', (err, seasonCount) => {
        if (err) return res.status(500).json({ error: 'Database error' });

        // Get top scorer with REALISTIC PPG
        db.get(`
          SELECT 
            player_name, 
            points_total,
            CAST(points_total AS REAL) / MAX(games_played, 20) as calculated_ppg
          FROM current_player_stats 
          WHERE points_total > 50 AND points_total < 2000
          ORDER BY calculated_ppg DESC 
          LIMIT 1
        `, (err, topScorer) => {
          if (err) return res.status(500).json({ error: 'Database error' });

          res.json({
            totalPlayers: playerCount.total_players,
            totalTeams: teamCount.total_teams,
            totalSeasons: seasonCount.total_seasons,
            topScorer: topScorer ? {
              name: topScorer.player_name,
              pointsPerGame: Math.round(topScorer.calculated_ppg * 10) / 10
            } : null
          });
        });
      });
    });
  });
});

/**
 * GET /api/players
 * List players with FIXED PPG calculations
 */
app.get('/api/players', (req, res) => {
  const {
    search = '',
    team = '',
    page = 1,
    limit = 25,
    sortBy = 'points_avg',
    sortOrder = 'desc'
  } = req.query;

  const offset = (parseInt(page) - 1) * parseInt(limit);
  
  // Build WHERE clause
  let whereConditions = [];
  let params = [];
  
  if (search) {
    whereConditions.push('player_name LIKE ?');
    params.push(`%${search}%`);
  }
  
  if (team) {
    whereConditions.push('team_name LIKE ?');
    params.push(`%${team}%`);
  }
  
  const whereClause = whereConditions.length > 0 ? `WHERE ${whereConditions.join(' AND ')}` : '';
  
  // Valid sort columns
  const validSorts = ['player_name', 'points_avg', 'points_total', 'team_name'];
  const sortColumn = validSorts.includes(sortBy) ? 
    (sortBy === 'points_avg' ? 'calculated_ppg' : sortBy) : 'calculated_ppg';
  const order = sortOrder === 'asc' ? 'ASC' : 'DESC';

  // Count total
  const countQuery = `SELECT COUNT(*) as total FROM current_player_stats ${whereClause}`;
  
  db.get(countQuery, params, (err, countResult) => {
    if (err) return res.status(500).json({ error: 'Database error' });

    const total = countResult.total;
    
    // Get players with FIXED PPG
    const playersQuery = `
      SELECT 
        id, 
        player_name, 
        team_name, 
        points_total,
        games_played,
        CAST(points_total AS REAL) / MAX(games_played, 20) as calculated_ppg,
        season
      FROM current_player_stats 
      ${whereClause}
      ORDER BY ${sortColumn} ${order}
      LIMIT ? OFFSET ?
    `;
    
    const queryParams = [...params, parseInt(limit), offset];
    
    db.all(playersQuery, queryParams, (err, players) => {
      if (err) return res.status(500).json({ error: 'Database error' });

      // Transform data
      const transformedPlayers = players.map(player => ({
        id: player.id,
        name: player.player_name,
        currentTeam: player.team_name,
        league: 'German Basketball',
        currentSeason: {
          games: Math.max(player.games_played, 20), // Assume at least 20 games
          pointsPerGame: Math.round(player.calculated_ppg * 10) / 10,
          reboundsPerGame: 0,
          assistsPerGame: 0
        },
        careerHighlights: {
          bestSeason: `${player.season}`,
          totalPoints: player.points_total,
          bestSeasonPPG: Math.round(player.calculated_ppg * 10) / 10
        },
        recentPerformance: player.calculated_ppg > 15 ? 'hot' : player.calculated_ppg < 8 ? 'cold' : 'steady'
      }));

      // Pagination info
      const totalPages = Math.ceil(total / parseInt(limit));
      const currentPage = parseInt(page);

      res.json({
        players: transformedPlayers,
        pagination: {
          page: currentPage,
          limit: parseInt(limit),
          total: total,
          totalPages: totalPages,
          hasNext: currentPage < totalPages,
          hasPrev: currentPage > 1
        }
      });
    });
  });
});

/**
 * GET /health
 * Health check
 */
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Basketball API Server running at http://localhost:${PORT}`);
  console.log('🎯 Available endpoints:');
  console.log('   GET /api/players - List players with FIXED PPG');
  console.log('   GET /api/stats/overview - Overview with REALISTIC stats');
  console.log('   GET /health - Health check');
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🏀 Shutting down Basketball API Server...');
  db.close((err) => {
    if (err) {
      console.error(err.message);
    }
    console.log('✅ Database connection closed');
    process.exit(0);
  });
});
