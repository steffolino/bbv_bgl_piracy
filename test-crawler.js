// Simple crawler test script for basketball stats
// This will help us test the data sources and crawling logic

const BASE_URL = "https://www.basketball-bund.net"; // Adjust this to the actual base URL

async function testLeagueDiscovery() {
  console.log("🔍 Testing League Discovery...");
  
  try {
    const response = await fetch(`${BASE_URL}/rest/wam/data`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log("✅ League discovery successful!");
    console.log("Sample data:", JSON.stringify(data, null, 2));
    
    return data;
  } catch (error) {
    console.error("❌ League discovery failed:", error.message);
    return null;
  }
}

async function testSeasonMatches(ligaId, seasonId) {
  console.log(`🏀 Testing Season Matches for Liga ${ligaId}, Season ${seasonId}...`);
  
  try {
    const response = await fetch(`${BASE_URL}/rest/liga/id/${ligaId}/season/${seasonId}/matches`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const matches = await response.json();
    console.log(`✅ Found ${matches.length || Object.keys(matches).length} matches!`);
    console.log("Sample match:", JSON.stringify(matches[0] || matches, null, 2));
    
    return matches;
  } catch (error) {
    console.error(`❌ Season matches failed:`, error.message);
    return null;
  }
}

async function testMatchDetails(matchId) {
  console.log(`📊 Testing Match Details for Match ${matchId}...`);
  
  try {
    const response = await fetch(`${BASE_URL}/rest/match/id/${matchId}/matchInfo`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const matchInfo = await response.json();
    console.log("✅ Match details retrieved!");
    console.log("Match info:", JSON.stringify(matchInfo, null, 2));
    
    return matchInfo;
  } catch (error) {
    console.error(`❌ Match details failed:`, error.message);
    return null;
  }
}

async function testBGLitzendorfFilter(data) {
  console.log("🔍 Testing BG Litzendorf filtering...");
  
  // Sample team name patterns for BG Litzendorf
  const bgLitzendorfPatterns = [
    /BG.*Litzendorf/i,
    /Litzendorf.*BG/i,
    /BG.*Litz/i,
    /Litzendorf/i
  ];
  
  function isBGLitzendorfTeam(teamName) {
    return bgLitzendorfPatterns.some(pattern => pattern.test(teamName));
  }
  
  // Test with sample team names
  const testTeams = [
    "BG Litzendorf 1",
    "BG Litzendorf 2", 
    "BG Litzendorf 3",
    "TSV Litzendorf",
    "Bayern München",
    "BG Bamberg"
  ];
  
  testTeams.forEach(team => {
    const isBGL = isBGLitzendorfTeam(team);
    console.log(`${isBGL ? '✅' : '❌'} ${team} -> ${isBGL ? 'BG Litzendorf' : 'Other team'}`);
  });
}

// Mock data generator for testing database insertion
function generateMockData() {
  console.log("🎲 Generating mock basketball data...");
  
  const mockLeague = {
    ligaId: "test-liga-123",
    seasonId: "2023-24",
    name: "Bezirksoberliga Oberfranken",
    level: "BOL",
    region: "Oberfranken",
    source: "rest-api",
    scraped_at: new Date()
  };
  
  const mockMatches = [
    {
      matchId: "match-001",
      matchNo: 1,
      seasonId: "2023-24",
      ligaId: "test-liga-123",
      date: new Date("2023-10-15"),
      homeTeamId: "team-bgl1",
      guestTeamId: "team-opponent1",
      result: "85:72",
      status: "finished"
    },
    {
      matchId: "match-002", 
      matchNo: 2,
      seasonId: "2023-24",
      ligaId: "test-liga-123",
      date: new Date("2023-10-22"),
      homeTeamId: "team-opponent2",
      guestTeamId: "team-bgl1",
      result: "78:91",
      status: "finished"
    }
  ];
  
  const mockBoxscores = [
    {
      matchId: "match-001",
      teamId: "team-bgl1",
      playerName: "Max Mustermann",
      pts: 23,
      threePm: 4,
      threePa: 7,
      ftm: 3,
      fta: 4,
      source: "rest-api",
      scraped_at: new Date()
    },
    {
      matchId: "match-001",
      teamId: "team-bgl1", 
      playerName: "John Doe",
      pts: 18,
      threePm: 2,
      threePa: 5,
      ftm: 6,
      fta: 8,
      source: "rest-api",
      scraped_at: new Date()
    }
  ];
  
  console.log("✅ Mock data generated!");
  return { mockLeague, mockMatches, mockBoxscores };
}

// Main test function
async function runCrawlerTests() {
  console.log("🚀 Starting Basketball Stats Crawler Tests");
  console.log("=" * 50);
  
  // Test 1: League Discovery
  const leagues = await testLeagueDiscovery();
  
  // Test 2: BG Litzendorf filtering
  await testBGLitzendorfFilter();
  
  // Test 3: Generate mock data
  const mockData = generateMockData();
  
  // Test 4: If we got real league data, test season matches
  if (leagues && leagues.length > 0) {
    const sampleLeague = leagues[0];
    await testSeasonMatches(sampleLeague.ligaId, sampleLeague.seasonId);
  } else {
    console.log("⚠️  No real league data available, skipping live API tests");
    console.log("💡 Consider testing with mock Liga ID and Season ID");
    
    // Test with mock IDs
    await testSeasonMatches("test-liga", "2023-24");
  }
  
  console.log("=" * 50);
  console.log("🏁 Crawler tests completed!");
}

// Run the tests
runCrawlerTests().catch(console.error);
