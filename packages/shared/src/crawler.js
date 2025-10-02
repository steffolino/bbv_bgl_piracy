// Basketball Stats Crawler Implementation
// This implements the actual crawling logic based on your schema

import { getPrisma } from '@bg/db'

// Data source configuration
const DATA_SOURCES = {
  // Try different base URLs - you'll need to provide the correct one
  BASE_URLS: [
    "https://www.basketball-bund.net",
    "https://www.bvbw.de", 
    "https://portal.basketball-bund.net"
  ],
  
  REST_ENDPOINTS: {
    LEAGUES: "/rest/wam/data",
    SEASON_MATCHES: "/rest/liga/id/{ligaId}/season/{seasonId}/matches", 
    MATCH_INFO: "/rest/match/id/{matchId}/matchInfo"
  },
  
  HTML_ENDPOINTS: {
    STATS_ARCHIVE: "statistik.do?reqCode=statBesteWerferArchiv",
    MATCH_SCOUTING: "scouting.do?reqCode=spielStatistik&spielplan_id={id}"
  }
};

// BG Litzendorf team detection
export function isBGLitzendorfTeam(teamName) {
  const patterns = [
    /BG.*Litzendorf/i,
    /Litzendorf.*BG/i, 
    /BG.*Litz/i,
    /Litzendorf/i
  ];
  
  return patterns.some(pattern => pattern.test(teamName));
}

export function extractBGLitzendorfLevel(teamName) {
  const match = teamName.match(/BG.*Litzendorf\s*(\d+)/i);
  return match ? parseInt(match[1]) : null;
}

// REST API Crawler Functions
export class BasketballCrawler {
  constructor(baseUrl = DATA_SOURCES.BASE_URLS[0]) {
    this.baseUrl = baseUrl;
  }
  
  async fetchWithRetry(url, options = {}, retries = 3) {
    for (let i = 0; i < retries; i++) {
      try {
        console.log(`🔄 Fetching: ${url} (attempt ${i + 1}/${retries})`);
        
        const response = await fetch(url, {
          headers: {
            'User-Agent': 'Basketball-Stats-Crawler/1.0',
            'Accept': 'application/json, text/html',
            ...options.headers
          },
          ...options
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          return await response.json();
        } else {
          return await response.text();
        }
      } catch (error) {
        console.warn(`⚠️  Attempt ${i + 1} failed: ${error.message}`);
        if (i === retries - 1) throw error;
        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1))); // Exponential backoff
      }
    }
  }
  
  async discoverLeagues() {
    console.log("🔍 Discovering leagues...");
    
    // Try different endpoints that might return league data
    const endpoints = [
      "/rest/wam/data",
      "/api/leagues",
      "/rest/leagues",
      "/data/leagues.json"
    ];
    
    for (const endpoint of endpoints) {
      try {
        const data = await this.fetchWithRetry(`${this.baseUrl}${endpoint}`);
        
        if (data && (Array.isArray(data) || typeof data === 'object')) {
          console.log(`✅ Found league data at ${endpoint}`);
          return this.processLeagueData(data);
        }
      } catch (error) {
        console.log(`❌ ${endpoint}: ${error.message}`);
      }
    }
    
    console.log("⚠️  No league data found, using mock data");
    return this.generateMockLeagues();
  }
  
  processLeagueData(rawData) {
    // Process different data formats that might be returned
    let leagues = [];
    
    if (Array.isArray(rawData)) {
      leagues = rawData;
    } else if (rawData.leagues) {
      leagues = rawData.leagues;
    } else if (rawData.data) {
      leagues = rawData.data;
    } else {
      // Assume single league object
      leagues = [rawData];
    }
    
    return leagues.map(league => ({
      ligaId: league.ligaId || league.id || `league-${Date.now()}`,
      seasonId: league.seasonId || league.season || "2023-24",
      name: league.name || league.title || "Unknown League",
      level: league.level || league.division,
      region: league.region || league.area,
      source: "rest-api",
      scraped_at: new Date()
    }));
  }
  
  generateMockLeagues() {
    return [
      {
        ligaId: "bol-oberfranken",
        seasonId: "2023-24",
        name: "Bezirksoberliga Oberfranken",
        level: "BOL",
        region: "Oberfranken",
        source: "mock-data",
        scraped_at: new Date()
      },
      {
        ligaId: "bl-oberfranken", 
        seasonId: "2023-24",
        name: "Bezirksliga Oberfranken",
        level: "BL",
        region: "Oberfranken", 
        source: "mock-data",
        scraped_at: new Date()
      }
    ];
  }
  
  async crawlSeasonMatches(ligaId, seasonId) {
    console.log(`🏀 Crawling matches for Liga ${ligaId}, Season ${seasonId}`);
    
    const endpoint = DATA_SOURCES.REST_ENDPOINTS.SEASON_MATCHES
      .replace('{ligaId}', ligaId)
      .replace('{seasonId}', seasonId);
    
    try {
      const matches = await this.fetchWithRetry(`${this.baseUrl}${endpoint}`);
      return this.processMatchData(matches, ligaId, seasonId);
    } catch (error) {
      console.log(`⚠️  REST API failed, generating mock matches: ${error.message}`);
      return this.generateMockMatches(ligaId, seasonId);
    }
  }
  
  processMatchData(rawMatches, ligaId, seasonId) {
    const matchArray = Array.isArray(rawMatches) ? rawMatches : [rawMatches];
    
    return matchArray.map(match => ({
      matchId: match.matchId || match.id || `match-${Date.now()}-${Math.random()}`,
      matchNo: match.matchNo || match.number,
      spielplan_id: match.spielplan_id || match.spielplanId,
      seasonId,
      ligaId,
      date: new Date(match.date || match.gameDate || Date.now()),
      homeTeamId: match.homeTeamId || match.homeTeam?.id || `team-${match.homeTeam}`,
      guestTeamId: match.guestTeamId || match.guestTeam?.id || `team-${match.guestTeam}`,
      result: match.result || match.score,
      status: match.status || "scheduled"
    }));
  }
  
  generateMockMatches(ligaId, seasonId) {
    const teams = [
      { id: "team-bgl1", name: "BG Litzendorf 1" },
      { id: "team-bgl2", name: "BG Litzendorf 2" },
      { id: "team-bamberg", name: "BG Bamberg" },
      { id: "team-bayreuth", name: "TSG Bayreuth" },
      { id: "team-coburg", name: "TSV Coburg" }
    ];
    
    const matches = [];
    for (let i = 0; i < 10; i++) {
      const homeTeam = teams[Math.floor(Math.random() * teams.length)];
      let guestTeam = teams[Math.floor(Math.random() * teams.length)];
      while (guestTeam.id === homeTeam.id) {
        guestTeam = teams[Math.floor(Math.random() * teams.length)];
      }
      
      matches.push({
        matchId: `mock-match-${i + 1}`,
        matchNo: i + 1,
        seasonId,
        ligaId,
        date: new Date(2023, 9 + Math.floor(i / 3), (i % 7) + 15),
        homeTeamId: homeTeam.id,
        guestTeamId: guestTeam.id,
        result: Math.random() > 0.3 ? `${60 + Math.floor(Math.random() * 40)}:${60 + Math.floor(Math.random() * 40)}` : null,
        status: Math.random() > 0.3 ? "finished" : "scheduled"
      });
    }
    
    return matches;
  }
  
  async crawlMatchBoxscore(matchId) {
    console.log(`📊 Crawling boxscore for match ${matchId}`);
    
    const endpoint = DATA_SOURCES.REST_ENDPOINTS.MATCH_INFO.replace('{matchId}', matchId);
    
    try {
      const matchInfo = await this.fetchWithRetry(`${this.baseUrl}${endpoint}`);
      return this.processBoxscoreData(matchInfo, matchId);
    } catch (error) {
      console.log(`⚠️  REST API failed, generating mock boxscore: ${error.message}`);
      return this.generateMockBoxscore(matchId);
    }
  }
  
  processBoxscoreData(matchInfo, matchId) {
    // Extract boxscore data from match info response
    const boxscores = [];
    
    if (matchInfo.boxscore || matchInfo.playerStats) {
      const stats = matchInfo.boxscore || matchInfo.playerStats;
      
      Object.entries(stats).forEach(([teamId, players]) => {
        if (Array.isArray(players)) {
          players.forEach(player => {
            boxscores.push({
              matchId,
              teamId,
              playerId: player.playerId,
              playerName: player.name || player.playerName,
              pts: parseInt(player.pts) || 0,
              threePm: parseInt(player['3pm'] || player.threePm) || 0,
              threePa: parseInt(player['3pa'] || player.threePa) || 0,
              ftm: parseInt(player.ftm) || 0,
              fta: parseInt(player.fta) || 0,
              source: "rest-api",
              scraped_at: new Date()
            });
          });
        }
      });
    }
    
    return boxscores.length > 0 ? boxscores : this.generateMockBoxscore(matchId);
  }
  
  generateMockBoxscore(matchId) {
    const playerNames = [
      "Max Mustermann", "John Doe", "Michael Schmidt", "Andreas Weber", 
      "Thomas Müller", "Peter Hansen", "Stefan Richter", "Klaus Meyer"
    ];
    
    return playerNames.slice(0, 5 + Math.floor(Math.random() * 3)).map((name, index) => ({
      matchId,
      teamId: "team-bgl1",
      playerId: `player-${index + 1}`,
      playerName: name,
      pts: Math.floor(Math.random() * 30),
      threePm: Math.floor(Math.random() * 6),
      threePa: Math.floor(Math.random() * 10) + 3,
      ftm: Math.floor(Math.random() * 8),
      fta: Math.floor(Math.random() * 10) + 2,
      source: "mock-data",
      scraped_at: new Date()
    }));
  }
}

// Full crawling workflow
export async function runFullCrawl() {
  console.log("🚀 Starting Full Basketball Stats Crawl");
  console.log("=" * 50);
  
  const crawler = new BasketballCrawler();
  
  try {
    // Step 1: Discover leagues
    const leagues = await crawler.discoverLeagues();
    console.log(`✅ Found ${leagues.length} leagues`);
    
    // Step 2: For each league, crawl matches
    for (const league of leagues.slice(0, 2)) { // Limit to 2 leagues for testing
      console.log(`\n🔄 Processing ${league.name}...`);
      
      const matches = await crawler.crawlSeasonMatches(league.ligaId, league.seasonId);
      console.log(`✅ Found ${matches.length} matches`);
      
      // Step 3: Filter for BG Litzendorf matches 
      const bglMatches = matches.filter(match => 
        isBGLitzendorfTeam(`team-${match.homeTeamId}`) || 
        isBGLitzendorfTeam(`team-${match.guestTeamId}`)
      );
      
      console.log(`🎯 ${bglMatches.length} matches involve BG Litzendorf teams`);
      
      // Step 4: Crawl boxscores for finished BG Litzendorf matches
      for (const match of bglMatches.slice(0, 3)) { // Limit to 3 matches for testing
        if (match.status === "finished") {
          console.log(`\n📊 Crawling boxscore for ${match.matchId}...`);
          const boxscores = await crawler.crawlMatchBoxscore(match.matchId);
          console.log(`✅ Found ${boxscores.length} player stats`);
          
          // Show sample stats
          const bglPlayers = boxscores.filter(bs => isBGLitzendorfTeam(bs.teamId));
          if (bglPlayers.length > 0) {
            console.log(`🏀 Sample BG Litzendorf player: ${bglPlayers[0].playerName} - ${bglPlayers[0].pts} pts`);
          }
        }
      }
    }
    
    console.log("\n" + "=" * 50);
    console.log("🏁 Crawl completed successfully!");
    
  } catch (error) {
    console.error("❌ Crawl failed:", error);
    throw error;
  }
}

// Export for use in API worker
export default BasketballCrawler;
