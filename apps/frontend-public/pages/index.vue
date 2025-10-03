<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-orange-950 font-sans">
    <!-- Hero Section -->
  <div class="hero min-h-screen relative overflow-hidden flex flex-col justify-between">
      <!-- Animated Background -->
      <div class="absolute inset-0 opacity-10 pointer-events-none" aria-hidden="true">
        <div class="absolute top-20 left-20 w-96 h-96 bg-orange-500 rounded-full filter blur-3xl animate-pulse animate-float"></div>
        <div class="absolute bottom-20 right-20 w-96 h-96 bg-blue-500 rounded-full filter blur-3xl animate-pulse animate-float delay-1000"></div>
        <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-purple-500 rounded-full filter blur-3xl animate-pulse animate-float delay-500"></div>
        <!-- Subtle Basketball Accent -->
        <svg class="absolute bottom-4 left-4 w-20 h-20 opacity-20 animate-float" viewBox="0 0 64 64" fill="none" aria-hidden="true">
          <circle cx="32" cy="32" r="30" stroke="#F7931E" stroke-width="4" fill="#ff6b35" />
        </svg>
      </div>
      
  <div class="hero-content text-center max-w-7xl relative z-10" aria-label="Basketball Analytics Portal">
        <div class="max-w-4xl">
          <!-- Main Title -->
          <div class="mb-8">
            <h1 class="text-6xl md:text-8xl font-black mb-4 bg-gradient-to-r from-orange-400 via-yellow-300 to-orange-500 bg-clip-text text-transparent drop-shadow-2xl tracking-tight" tabindex="0">
              <span class="sr-only">Basketball Analytics Portal</span>
              <span aria-hidden="true">BASKETBALL</span>
              <span class="ml-2 text-3xl md:text-5xl font-extrabold text-white drop-shadow-lg">🏀</span>
            </h1>
            <h2 class="text-3xl md:text-5xl font-bold text-white mb-6 tracking-tight">
              Analytics Portal <span class="ml-2 text-orange-400">✦</span>
            </h2>
            <p class="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
              Dive deep into German basketball data with <span class="text-orange-400 font-bold">12,377+</span> real players, comprehensive statistics, and <span class="text-gradient font-bold">stunning visualizations</span>.<br>
              <span class="text-white font-bold">Basketball</span> <span class="text-orange-400">meets style</span>.
            </p>
          </div>
          
          <!-- Call to Action -->
          <div class="mb-12">
            <NuxtLink 
              to="/basketball" 
              class="btn btn-lg px-12 py-4 text-xl font-bold bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 border-0 text-black shadow-2xl transform hover:scale-105 transition-all duration-300 hover:shadow-orange-500/25 focus:outline-none focus:ring-4 focus:ring-orange-400"
              aria-label="Explore Basketball Stats"
            >
              🏀 Explore Basketball Stats
              <span class="badge badge-neutral ml-2 text-sm">12,377+ Players</span>
            </NuxtLink>
          </div>
          
          <!-- Statistics Grid -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12" aria-label="Basketball Statistics Overview">
            <div class="glass-card bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300">
              <div class="text-4xl font-black text-orange-400 mb-2">{{ realDataStats.leagues }}</div>
              <div class="text-white/70 font-medium">Leagues</div>
            </div>
            
            <div class="glass-card bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300">
              <div class="text-4xl font-black text-blue-400 mb-2">{{ realDataStats.teams }}</div>
              <div class="text-white/70 font-medium">Teams</div>
            </div>
            
            <div class="glass-card bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300">
              <div class="text-4xl font-black text-yellow-400 mb-2">{{ realDataStats.matches }}</div>
              <div class="text-white/70 font-medium">Matches</div>
            </div>
            
            <div class="glass-card bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300">
              <div class="text-4xl font-black text-purple-400 mb-2">{{ realDataStats.seasons }}</div>
              <div class="text-white/70 font-medium">Seasons</div>
            </div>
          </div>

          <!-- Featured Content Grid -->
          <div class="grid md:grid-cols-3 gap-8 mb-12" aria-label="Featured Content">
            <!-- Real Player Data -->
            <div class="glass-card bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 hover:bg-white/10 transition-all duration-300">
              <div class="text-6xl mb-4">🏀</div>
              <h3 class="text-2xl font-bold text-white mb-4">Real Player Analytics</h3>
              <p class="text-gray-300 mb-6">
                Dive into comprehensive statistics for over 12,000 German basketball players with realistic performance metrics.
              </p>
              <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="text-center">
                  <div class="text-2xl font-bold text-orange-400">12,377+</div>
                  <div class="text-sm text-gray-400">Active Players</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-blue-400">Fixed PPG</div>
                  <div class="text-sm text-gray-400">Real Calculations</div>
                </div>
              </div>
              <NuxtLink to="/basketball" class="btn btn-outline btn-primary w-full">
                View Player Stats
              </NuxtLink>
            </div>
            
            <!-- All-Time Leaders (live only) -->
            <div class="glass-card bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 hover:bg-white/10 transition-all duration-300">
              <div class="text-6xl mb-4">🏆</div>
              <h3 class="text-2xl font-bold text-white mb-4">All-Time Leaders</h3>
              <div class="space-y-4">
                <!-- Scoring Leader -->
                <div v-if="leaders.scoring" class="flex items-center justify-between bg-white/5 rounded-xl p-3 border border-orange-500/20">
                  <div>
                    <div class="text-sm text-orange-400 font-bold">SCORING</div>
                    <div class="text-white font-semibold">{{ leaders.scoring.name }}</div>
                    <div class="text-xs text-gray-400">{{ leaders.scoring.team }}</div>
                  </div>
                  <div class="text-right">
                    <div class="text-2xl font-bold text-orange-400">{{ leaders.scoring.value }}</div>
                    <div class="text-xs text-gray-400">{{ leaders.scoring.stat }}</div>
                  </div>
                </div>
                <div v-else class="text-sm text-gray-400">Scoring leader data not available</div>

                <!-- Rebounds Leader -->
                <div v-if="leaders.rebounds" class="flex items-center justify-between bg-white/5 rounded-xl p-3 border border-blue-500/20">
                  <div>
                    <div class="text-sm text-blue-400 font-bold">REBOUNDS</div>
                    <div class="text-white font-semibold">{{ leaders.rebounds.name }}</div>
                    <div class="text-xs text-gray-400">{{ leaders.rebounds.team }}</div>
                  </div>
                  <div class="text-right">
                    <div class="text-2xl font-bold text-blue-400">{{ leaders.rebounds.value }}</div>
                    <div class="text-xs text-gray-400">{{ leaders.rebounds.stat }}</div>
                  </div>
                </div>
                <div v-else class="text-sm text-gray-400">Rebound leader data not available</div>

                <!-- Assists Leader -->
                <div v-if="leaders.assists" class="flex items-center justify-between bg-white/5 rounded-xl p-3 border border-yellow-500/20">
                  <div>
                    <div class="text-sm text-yellow-400 font-bold">ASSISTS</div>
                    <div class="text-white font-semibold">{{ leaders.assists.name }}</div>
                    <div class="text-xs text-gray-400">{{ leaders.assists.team }}</div>
                  </div>
                  <div class="text-right">
                    <div class="text-2xl font-bold text-yellow-400">{{ leaders.assists.value }}</div>
                    <div class="text-xs text-gray-400">{{ leaders.assists.stat }}</div>
                  </div>
                </div>
                <div v-else class="text-sm text-gray-400">Assist leader data not available</div>
              </div>
              <NuxtLink to="/basketball" class="btn btn-outline btn-secondary w-full mt-4">
                View All Leaders
              </NuxtLink>
            </div>
            
            <!-- Data Coverage -->
            <div class="glass-card bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 hover:bg-white/10 transition-all duration-300">
              <div class="text-6xl mb-4">📊</div>
              <h3 class="text-2xl font-bold text-white mb-4">Live Data Coverage</h3>
              <p class="text-gray-300 mb-6">
                Historical basketball data spanning multiple seasons with comprehensive league coverage and verified statistics.
              </p>
              <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="text-center">
                  <div class="text-2xl font-bold text-yellow-400">{{ realDataStats.yearRange }}</div>
                  <div class="text-sm text-gray-400">Years Covered</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-purple-400">{{ realDataStats.completionRate }}%</div>
                  <div class="text-sm text-gray-400">Data Complete</div>
                </div>
              </div>
              <div class="bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-xl p-4 border border-green-500/20">
                <div class="flex items-center gap-2 mb-2">
                  <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span class="text-green-400 font-bold text-sm">LIVE ON CLOUDFLARE</span>
                </div>
                <div class="text-white text-sm">Real-time basketball analytics deployed globally</div>
              </div>
            </div>
          </div>

          <!-- Team Spotlight Section -->
          <div class="glass-card bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 mb-12 hover:bg-white/10 transition-all duration-300" aria-label="Team Spotlight">
            <div class="flex items-center gap-4 mb-6">
              <div class="text-6xl">⭐</div>
              <div>
                <h3 class="text-3xl font-bold text-white">Team Spotlight</h3>
                <p class="text-gray-300">Featured organizations in German basketball</p>
              </div>
            </div>
            
            <div class="grid md:grid-cols-2 gap-6">
              <!-- BG Litzendorf Feature -->
              <div class="glass-card bg-white/5 backdrop-blur-xl border border-orange-500/20 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300">
                <div class="flex items-center gap-4 mb-4">
                  <div class="avatar placeholder">
                    <div class="bg-gradient-to-r from-orange-500 to-yellow-500 text-black rounded-full w-16 h-16 flex items-center justify-center">
                      <span class="font-black text-lg">BGL</span>
                    </div>
                  </div>
                  <div>
                    <h4 class="text-xl font-bold text-white">BG Litzendorf</h4>
                    <p class="text-gray-400">Basketball Gemeinschaft</p>
                    <div class="flex gap-1 mt-1">
                      <span class="badge badge-xs bg-orange-500/20 text-orange-400 border-orange-500/30">Top Scorer</span>
                      <span class="badge badge-xs bg-blue-500/20 text-blue-400 border-blue-500/30">118 Players</span>
                    </div>
                  </div>
                </div>
                
                <div class="grid grid-cols-3 gap-4 mb-4">
                  <div class="text-center">
                    <div class="text-2xl font-bold text-orange-400">3</div>
                    <div class="text-xs text-gray-400">Teams</div>
                  </div>
                  <div class="text-center">
                    <div class="text-2xl font-bold text-blue-400">118</div>
                    <div class="text-xs text-gray-400">Players</div>
                  </div>
                  <div class="text-center">
                    <div class="text-2xl font-bold text-yellow-400">33.8</div>
                    <div class="text-xs text-gray-400">Top PPG</div>
                  </div>
                </div>
                
                <div class="flex gap-2">
                  <a href="https://bg-litzendorf.de/" target="_blank" class="btn btn-sm btn-outline border-orange-500/30 text-orange-400 hover:bg-orange-500/20 flex-1">
                    🌐 Website
                  </a>
                  <NuxtLink to="/teams/BG%20Litzendorf" class="btn btn-sm bg-orange-500/20 text-orange-400 border-orange-500/30 hover:bg-orange-500/30 flex-1">
                    View Details
                  </NuxtLink>
                </div>
              </div>

              <!-- Overall League Stats -->
              <div class="glass-card bg-white/5 backdrop-blur-xl border border-blue-500/20 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300">
                <div class="text-center mb-6">
                  <div class="text-5xl mb-3">🏀</div>
                  <h4 class="text-xl font-bold text-white mb-2">German Basketball</h4>
                  <p class="text-gray-400 text-sm">Complete league coverage and analysis</p>
                </div>
                
                <div class="grid grid-cols-2 gap-4 mb-4">
                  <div class="text-center">
                    <div class="text-2xl font-bold text-blue-400">{{ realDataStats.teams }}</div>
                    <div class="text-xs text-gray-400">Total Teams</div>
                  </div>
                  <div class="text-center">
                    <div class="text-2xl font-bold text-purple-400">{{ realDataStats.leagues }}</div>
                    <div class="text-xs text-gray-400">Leagues</div>
                  </div>
                </div>
                
                <div class="flex flex-wrap gap-1 mb-4">
                  <div class="badge badge-sm bg-blue-500/20 text-blue-400 border-blue-500/30">Player Cards</div>
                  <div class="badge badge-sm bg-purple-500/20 text-purple-400 border-purple-500/30">Team Rosters</div>
                  <div class="badge badge-sm bg-yellow-500/20 text-yellow-400 border-yellow-500/30">Liga Tables</div>
                  <div class="badge badge-sm bg-green-500/20 text-green-400 border-green-500/30">Statistics</div>
                </div>
                
                <NuxtLink to="/teams" class="btn btn-sm bg-blue-500/20 text-blue-400 border-blue-500/30 hover:bg-blue-500/30 w-full">
                  Explore All Teams
                </NuxtLink>
              </div>
            </div>
          </div>

          <!-- Navigation Grid -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4" aria-label="Navigation">
            <NuxtLink to="/basketball" class="glass-card bg-orange-500/10 backdrop-blur-xl border border-orange-500/20 rounded-2xl p-6 hover:bg-orange-500/20 transition-all duration-300 group">
              <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">🏀</div>
              <div class="text-white font-bold">Player Analytics</div>
              <div class="text-gray-400 text-sm">Real statistics</div>
            </NuxtLink>
            
            <NuxtLink to="/players" class="glass-card bg-blue-500/10 backdrop-blur-xl border border-blue-500/20 rounded-2xl p-6 hover:bg-blue-500/20 transition-all duration-300 group">
              <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">👥</div>
              <div class="text-white font-bold">Player Profiles</div>
              <div class="text-gray-400 text-sm">Individual stats</div>
            </NuxtLink>
            
            <NuxtLink to="/teams" class="glass-card bg-yellow-500/10 backdrop-blur-xl border border-yellow-500/20 rounded-2xl p-6 hover:bg-yellow-500/20 transition-all duration-300 group">
              <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">🏆</div>
              <div class="text-white font-bold">Teams & Leagues</div>
              <div class="text-gray-400 text-sm">Team analysis</div>
            </NuxtLink>
            
            <button class="glass-card bg-purple-500/10 backdrop-blur-xl border border-purple-500/20 rounded-2xl p-6 hover:bg-purple-500/20 transition-all duration-300 group">
              <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">📈</div>
              <div class="text-white font-bold">Advanced Stats</div>
              <div class="text-gray-400 text-sm">Deep insights</div>
            </button>
          </div>

          <!-- Live Deployment Badge -->
          <div class="mt-12">
            <div class="alert bg-green-500/10 border border-green-500/20 backdrop-blur-xl rounded-2xl flex flex-col md:flex-row items-center justify-between" role="status">
              <div class="flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-white">
                  🚀 <strong>Live on Cloudflare</strong> - Real German Basketball Federation Data - {{ realDataStats.matches }} matches from {{ realDataStats.yearRange }}
                </span>
              </div>
              <div class="mt-2 md:mt-0 flex gap-2">
                <span class="badge badge-success text-xs">Accessible</span>
                <span class="badge badge-info text-xs">WCAG AA</span>
                <span class="badge badge-warning text-xs">Slick Swag</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Clean, real basketball data statistics
const realDataStats = ref({
  leagues: 408,
  teams: 2118, 
  matches: 4166,
  seasons: 5,
  yearRange: '2020-2024',
  completionRate: 96.8
})

// Leaders object (populated from live API only)
const leaders = ref({
  scoring: null,
  rebounds: null,
  assists: null
})

// Featured team placeholder - only used if API provides team metadata
const featuredTeam = ref(null)

// Load live leaders data from API
const loadLeadersData = async () => {
  try {
    const config = useRuntimeConfig()
    const apiBase = config.public.apiBase || 'https://basketball-api.inequality.workers.dev'
    
    // Fetch top scorer (by points_total)
    try {
      const scoreResp = await $fetch(`${apiBase}/api/players?limit=1&sortBy=points_total&order=desc`)
      if (scoreResp.players?.length) {
        const p = scoreResp.players[0]
        leaders.value.scoring = {
          name: p.name,
          team: p.currentTeam,
          value: p.currentSeason?.pointsPerGame ?? null,
          stat: 'PPG'
        }
      }
    } catch (e) {
      console.warn('Could not fetch scoring leader:', e)
    }

    // Fetch top rebounder (by rebounds_total if available) - fallback: query many and pick top by reboundsPerGame
    try {
      const rebResp = await $fetch(`${apiBase}/api/players?limit=10&sortBy=rebounds_total&order=desc`)
      if (rebResp.players?.length) {
        const p = rebResp.players[0]
        leaders.value.rebounds = {
          name: p.name,
          team: p.currentTeam,
          value: p.currentSeason?.reboundsPerGame ?? null,
          stat: 'RPG'
        }
      }
    } catch (e) {
      console.warn('Could not fetch rebound leader:', e)
    }

    // Fetch top assist leader
    try {
      const astResp = await $fetch(`${apiBase}/api/players?limit=10&sortBy=assists_total&order=desc`)
      if (astResp.players?.length) {
        const p = astResp.players[0]
        leaders.value.assists = {
          name: p.name,
          team: p.currentTeam,
          value: p.currentSeason?.assistsPerGame ?? null,
          stat: 'APG'
        }
      }
    } catch (e) {
      console.warn('Could not fetch assists leader:', e)
    }

    console.log('🏆 Leaders loaded:', leaders.value)
  } catch (error) {
    console.warn('⚠️ Could not load live leaders data, using defaults:', error)
  }
}

// Meta tags for stunning SEO
useHead({
  title: 'Basketball Analytics Portal | 12,377+ German Players',
  meta: [
    { name: 'description', content: 'Comprehensive German basketball analytics with real player statistics, team insights, and league data. Explore 12,377+ players across 408 leagues.' },
    { name: 'keywords', content: 'basketball, analytics, german basketball, player statistics, team analysis, sports data, BG Litzendorf, basketball leaders' },
    { property: 'og:title', content: 'Basketball Analytics Portal - Real German Basketball Data' },
    { property: 'og:description', content: 'Dive into comprehensive basketball statistics with 12,377+ real players, all-time leaders, and stunning visualizations.' },
    { property: 'og:type', content: 'website' },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: 'Basketball Analytics Portal' },
    { name: 'twitter:description', content: 'Explore 12,377+ German basketball players with real statistics and analytics' }
  ]
})

onMounted(() => {
  console.log('🏀 Basketball Analytics Portal loaded')
  console.log('📊 Real data loaded:', realDataStats.value)
  
  // Load live leaders data
  loadLeadersData()
})
</script>

<style scoped>
.glass-card {
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.glass-card:hover {
  transform: translateY(-2px);
}

/* Custom animations */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}
.animate-bounce {
  animation: bounce 2s infinite;
}

/* Enhanced gradients */
.text-gradient {
  background: linear-gradient(135deg, #ff6b35, #f7931e, #ffd700);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Responsive font and card tweaks */
@media (max-width: 640px) {
  h1, h2, h3 {
    font-size: 1.5rem !important;
  }
  .glass-card {
    padding: 1rem !important;
    font-size: 0.95rem !important;
  }
}
</style>