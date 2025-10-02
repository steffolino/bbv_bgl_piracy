/**
 * 🏀 BASKETBALL API - CLOUDFLARE WORKER
 * Serverless basketball analytics API for deployment
 */

// Basketball data - in production this would be from a database
const BASKETBALL_DATA = {
  totalPlayers: 12367,
  totalTeams: 158,
  totalSeasons: 15,
  topScorer: {
    name: "Christoph Höning",
    pointsPerGame: 33.8
  },
  samplePlayers: [
    {
      id: "1",
      name: "Christoph Höning", 
      currentTeam: "BG Litzendorf",
      league: "German Basketball",
      currentSeason: {
        games: 20,
        pointsPerGame: 33.8,
        reboundsPerGame: 8.2,
        assistsPerGame: 4.1
      },
      careerHighlights: {
        bestSeason: "2017/18",
        totalPoints: 676,
        bestSeasonPPG: 33.8
      },
      recentPerformance: "hot"
    },
    {
      id: "2", 
      name: "Manuel Stumpf",
      currentTeam: "TSV Hirschaid",
      league: "German Basketball",
      currentSeason: {
        games: 20,
        pointsPerGame: 29.8,
        reboundsPerGame: 6.5,
        assistsPerGame: 3.2
      },
      careerHighlights: {
        bestSeason: "2016/17",
        totalPoints: 596,
        bestSeasonPPG: 29.8
      },
      recentPerformance: "hot"
    }
  ]
};

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    // Route handling
    if (url.pathname === '/api/stats/overview') {
      return new Response(JSON.stringify({
        totalPlayers: BASKETBALL_DATA.totalPlayers,
        totalTeams: BASKETBALL_DATA.totalTeams, 
        totalSeasons: BASKETBALL_DATA.totalSeasons,
        topScorer: BASKETBALL_DATA.topScorer
      }), {
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
    
    if (url.pathname === '/api/players') {
      const searchParams = url.searchParams;
      const page = parseInt(searchParams.get('page')) || 1;
      const limit = parseInt(searchParams.get('limit')) || 25;
      
      // In production, filter and paginate real data
      const players = BASKETBALL_DATA.samplePlayers;
      const total = BASKETBALL_DATA.totalPlayers;
      const totalPages = Math.ceil(total / limit);
      
      return new Response(JSON.stringify({
        players: players,
        pagination: {
          page: page,
          limit: limit,
          total: total,
          totalPages: totalPages,
          hasNext: page < totalPages,
          hasPrev: page > 1
        }
      }), {
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
    
    if (url.pathname === '/health') {
      return new Response(JSON.stringify({
        status: 'OK',
        timestamp: new Date().toISOString(),
        message: '🏀 Basketball API is running on Cloudflare Workers!'
      }), {
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
    
    // 404 for unknown routes
    return new Response(JSON.stringify({
      error: 'Not Found',
      availableEndpoints: [
        '/api/stats/overview',
        '/api/players', 
        '/health'
      ]
    }), {
      status: 404,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    });
  }
};
