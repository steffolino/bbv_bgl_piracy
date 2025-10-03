<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
    <!-- Modern Header with Glass Effect -->
    <div class="sticky top-0 z-40 backdrop-blur-xl bg-white/80 border-b border-white/20 shadow-lg">
      <div class="container mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl flex items-center justify-center shadow-lg">
              <span class="text-2xl">🏀</span>
            </div>
            <div>
              <h1 class="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                Basketball Analytics
              </h1>
              <p class="text-sm text-gray-500">
                {{ overview?.totalPlayers?.toLocaleString() || 0 }} Players • {{ overview?.totalTeams || 0 }} Teams
              </p>
            </div>
          </div>
          <div class="hidden md:flex items-center space-x-2">
            <div class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
              ✅ Live Data
            </div>
            <div class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              {{ overview?.totalSeasons || 0 }} Seasons
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container mx-auto px-6 py-8">
      <!-- Hero Stats Cards -->
      <div v-if="overview" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="group relative overflow-hidden bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-white/20">
          <div class="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-blue-600/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="relative">
            <div class="flex items-center justify-between mb-2">
              <span class="text-2xl">👥</span>
              <div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            </div>
            <div class="text-3xl font-bold text-gray-900 mb-1">{{ overview.totalPlayers.toLocaleString() }}</div>
            <div class="text-sm text-gray-600 font-medium">Total Players</div>
          </div>
        </div>

        <div class="group relative overflow-hidden bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-white/20">
          <div class="absolute inset-0 bg-gradient-to-br from-green-500/10 to-green-600/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="relative">
            <div class="flex items-center justify-between mb-2">
              <span class="text-2xl">🏆</span>
              <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            </div>
            <div class="text-3xl font-bold text-gray-900 mb-1">{{ overview.totalTeams }}</div>
            <div class="text-sm text-gray-600 font-medium">Active Teams</div>
          </div>
        </div>

        <div class="group relative overflow-hidden bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-white/20">
          <div class="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-purple-600/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="relative">
            <div class="flex items-center justify-between mb-2">
              <span class="text-2xl">📅</span>
              <div class="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
            </div>
            <div class="text-3xl font-bold text-gray-900 mb-1">{{ overview.totalSeasons }}</div>
            <div class="text-sm text-gray-600 font-medium">Seasons</div>
          </div>
        </div>

        <div class="group relative overflow-hidden bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-white/20">
          <div class="absolute inset-0 bg-gradient-to-br from-orange-500/10 to-red-500/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="relative">
            <div class="flex items-center justify-between mb-2">
              <span class="text-2xl">🔥</span>
              <div class="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
            </div>
            <div class="text-3xl font-bold text-gray-900 mb-1">{{ overview.topScorer?.pointsPerGame.toFixed(1) }}</div>
            <div class="text-sm text-gray-600 font-medium">Top PPG</div>
            <div class="text-xs text-gray-500 truncate">{{ overview.topScorer?.name }}</div>
          </div>
        </div>
      </div>

      <!-- Historical Coverage Component -->
      <div class="mb-8">
        <HistoricalCoverage />
      </div>

      <!-- Modern Search Interface -->
      <div class="bg-white/70 backdrop-blur-sm rounded-2xl p-6 mb-8 shadow-lg border border-white/20">
        <div class="flex items-center mb-4">
          <span class="text-2xl mr-3">🔍</span>
          <h2 class="text-xl font-bold text-gray-900">Player Search & Filters</h2>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="relative">
            <input
              v-model="searchFilters.search"
              type="text"
              placeholder="Search players..."
              class="w-full pl-10 pr-4 py-3 bg-white/80 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all placeholder-gray-400"
              @input="searchPlayers"
            />
            <span class="absolute left-3 top-3.5 text-gray-400">🔍</span>
          </div>
          
          <div class="relative">
            <input
              v-model="searchFilters.team"
              type="text"
              placeholder="Filter by team..."
              class="w-full pl-10 pr-4 py-3 bg-white/80 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all placeholder-gray-400"
              @input="searchPlayers"
            />
            <span class="absolute left-3 top-3.5 text-gray-400">🏢</span>
          </div>
          
          <select
            v-model="searchFilters.sortBy"
            class="w-full px-4 py-3 bg-white/80 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            @change="searchPlayers"
          >
            <option value="points_avg">Points Per Game</option>
            <option value="points_total">Total Points</option>
            <option value="player_name">Player Name</option>
            <option value="team_name">Team Name</option>
          </select>
          
          <select
            v-model="searchFilters.sortOrder"
            class="w-full px-4 py-3 bg-white/80 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            @change="searchPlayers"
          >
            <option value="desc">Highest First</option>
            <option value="asc">Lowest First</option>
          </select>
        </div>
      </div>

      <!-- Modern Players Table -->
      <div class="bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100/50 bg-gradient-to-r from-gray-50/50 to-white/50">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-bold text-gray-900 flex items-center">
                <span class="mr-2">🏆</span>
                Player Statistics
              </h2>
              <p class="text-sm text-gray-600">Basketball-Reference.com style analytics</p>
            </div>
            <div v-if="pagination" class="text-sm text-gray-500">
              {{ pagination.total.toLocaleString() }} total players
            </div>
          </div>
        </div>
        
        <div v-if="loading" class="p-12 text-center">
          <div class="inline-flex items-center space-x-2">
            <div class="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <span class="text-lg text-gray-600">Loading players...</span>
          </div>
        </div>

        <div v-else-if="players.length === 0" class="p-12 text-center">
          <div class="text-6xl mb-4">🔍</div>
          <div class="text-xl text-gray-600 mb-2">No players found</div>
          <div class="text-sm text-gray-500">Try adjusting your search criteria</div>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full">
            <thead class="bg-gradient-to-r from-gray-50/80 to-white/80">
              <tr>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Player</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Team</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Games</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">PPG</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Total Points</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Performance</th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100/50">
              <tr v-for="player in players" :key="player.id" class="hover:bg-white/50 transition-colors group">
                <td class="px-6 py-4">
                  <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      {{ player.name.split(' ').map(n => n[0]).join('').slice(0, 2) }}
                    </div>
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ player.name }}</div>
                      <div class="text-xs text-gray-500">{{ player.league }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    {{ player.currentTeam }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm font-medium text-gray-900">
                  {{ player.currentSeason.games }}
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm font-bold text-gray-900">{{ player.currentSeason.pointsPerGame.toFixed(1) }}</div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm font-medium text-gray-900">{{ player.careerHighlights.totalPoints.toLocaleString() }}</div>
                </td>
                <td class="px-6 py-4">
                  <span
                    :class="{
                      'bg-red-100 text-red-800 border-red-200': player.recentPerformance === 'hot',
                      'bg-blue-100 text-blue-800 border-blue-200': player.recentPerformance === 'cold',
                      'bg-gray-100 text-gray-800 border-gray-200': player.recentPerformance === 'steady'
                    }"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border"
                  >
                    {{ player.recentPerformance === 'hot' ? '🔥 Hot' : player.recentPerformance === 'cold' ? '❄️ Cold' : '📈 Steady' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <button
                    @click="viewPlayer(player)"
                    class="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-sm hover:shadow-md group-hover:scale-105"
                  >
                    <span class="mr-1">👤</span>
                    View Profile
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Modern Pagination -->
        <div v-if="pagination && pagination.totalPages > 1" class="px-6 py-4 border-t border-gray-100/50 bg-gray-50/30">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-600">
              Showing <span class="font-medium">{{ ((pagination.page - 1) * pagination.limit) + 1 }}</span> to 
              <span class="font-medium">{{ Math.min(pagination.page * pagination.limit, pagination.total) }}</span> of 
              <span class="font-medium">{{ pagination.total.toLocaleString() }}</span> players
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click="changePage(pagination.page - 1)"
                :disabled="!pagination.hasPrev"
                class="inline-flex items-center px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span class="mr-1">←</span>
                Previous
              </button>
              <div class="hidden md:flex items-center space-x-1">
                <span v-for="page in getPageNumbers()" :key="page" class="px-3 py-2">
                  <button
                    v-if="page !== '...'"
                    @click="changePage(page)"
                    :class="page === pagination.page ? 'bg-blue-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
                    class="w-8 h-8 rounded-lg text-sm font-medium border border-gray-200 transition-colors"
                  >
                    {{ page }}
                  </button>
                  <span v-else class="text-gray-400">...</span>
                </span>
              </div>
              <span class="md:hidden px-3 py-2 text-sm text-gray-700">
                Page {{ pagination.page }} of {{ pagination.totalPages }}
              </span>
              <button
                @click="changePage(pagination.page + 1)"
                :disabled="!pagination.hasNext"
                class="inline-flex items-center px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Next
                <span class="ml-1">→</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Ultra-Modern Player Profile Modal -->
      <div v-if="selectedPlayer" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div class="bg-white/95 backdrop-blur-xl rounded-3xl max-w-5xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-white/20">
          <!-- Modal Header -->
          <div class="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 p-6 rounded-t-3xl">
            <div class="flex justify-between items-start">
              <div class="flex items-center space-x-4">
                <div class="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center text-white font-bold text-xl">
                  {{ selectedPlayer.player.name.split(' ').map(n => n[0]).join('').slice(0, 2) }}
                </div>
                <div>
                  <h2 class="text-3xl font-bold text-white">{{ selectedPlayer.player.name }}</h2>
                  <p class="text-xl text-blue-100">{{ selectedPlayer.player.currentTeam }}</p>
                  <p class="text-blue-200">{{ selectedPlayer.player.league }}</p>
                </div>
              </div>
              <button
                @click="selectedPlayer = null"
                class="w-10 h-10 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center text-white text-xl transition-colors"
              >
                ×
              </button>
            </div>
          </div>

          <div class="p-6">
            <!-- Stats Grid -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <!-- Current Season -->
              <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6 border border-blue-200">
                <div class="flex items-center mb-4">
                  <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center mr-3">
                    <span class="text-white text-sm">📊</span>
                  </div>
                  <h3 class="text-lg font-bold text-blue-900">Current Season</h3>
                </div>
                <div class="text-sm text-blue-700 mb-3">{{ selectedPlayer.currentSeason.season }}</div>
                <div class="space-y-3">
                  <div class="flex justify-between items-center">
                    <span class="text-blue-700">Games:</span>
                    <span class="font-bold text-blue-900">{{ selectedPlayer.currentSeason.stats.games }}</span>
                  </div>
                  <div class="flex justify-between items-center">
                    <span class="text-blue-700">PPG:</span>
                    <span class="font-bold text-blue-900">{{ selectedPlayer.currentSeason.stats.pointsPerGame.toFixed(1) }}</span>
                  </div>
                  <div class="flex justify-between items-center">
                    <span class="text-blue-700">Total Points:</span>
                    <span class="font-bold text-blue-900">{{ selectedPlayer.currentSeason.stats.totalPoints }}</span>
                  </div>
                </div>
              </div>

              <!-- Career Totals -->
              <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6 border border-green-200">
                <div class="flex items-center mb-4">
                  <div class="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center mr-3">
                    <span class="text-white text-sm">🏆</span>
                  </div>
                  <h3 class="text-lg font-bold text-green-900">Career Totals</h3>
                </div>
                <div class="space-y-3">
                  <div class="flex justify-between items-center">
                    <span class="text-green-700">Seasons:</span>
                    <span class="font-bold text-green-900">{{ selectedPlayer.careerStats.totalSeasons }}</span>
                  </div>
                  <div class="flex justify-between items-center">
                    <span class="text-green-700">Total Games:</span>
                    <span class="font-bold text-green-900">{{ selectedPlayer.careerStats.totalGames }}</span>
                  </div>
                  <div class="flex justify-between items-center">
                    <span class="text-green-700">Career PPG:</span>
                    <span class="font-bold text-green-900">{{ selectedPlayer.careerStats.avgPointsPerGame.toFixed(1) }}</span>
                  </div>
                  <div class="flex justify-between items-center">
                    <span class="text-green-700">Total Points:</span>
                    <span class="font-bold text-green-900">{{ selectedPlayer.careerStats.totalPoints.toLocaleString() }}</span>
                  </div>
                </div>
              </div>

              <!-- Advanced Stats -->
              <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6 border border-purple-200">
                <div class="flex items-center mb-4">
                  <div class="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center mr-3">
                    <span class="text-white text-sm">⚡</span>
                  </div>
                  <h3 class="text-lg font-bold text-purple-900">Advanced Stats</h3>
                </div>
                <div class="space-y-3">
                  <div class="flex justify-between items-center">
                    <span class="text-purple-700">PER:</span>
                    <span class="font-bold text-purple-900">{{ selectedPlayer.advancedStats.playerEfficiencyRating }}</span>
                  </div>
                  <div class="flex justify-between items-center">
                    <span class="text-purple-700">TS%:</span>
                    <span class="font-bold text-purple-900">{{ selectedPlayer.advancedStats.trueShootingPercentage }}%</span>
                  </div>
                  <div class="flex justify-between items-center">
                    <span class="text-purple-700">Usage%:</span>
                    <span class="font-bold text-purple-900">{{ selectedPlayer.advancedStats.usageRate }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Season History -->
            <div v-if="selectedPlayer.lastFiveSeasons.length > 0" class="mb-8">
              <h3 class="text-2xl font-bold mb-6 flex items-center">
                <span class="mr-3">�</span>
                Recent Seasons Performance
              </h3>
              <div class="bg-white/50 rounded-2xl overflow-hidden border border-gray-200">
                <table class="min-w-full">
                  <thead class="bg-gradient-to-r from-gray-100 to-gray-50">
                    <tr>
                      <th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Season</th>
                      <th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Team</th>
                      <th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Games</th>
                      <th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">PPG</th>
                      <th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">Total Points</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100">
                    <tr v-for="season in selectedPlayer.lastFiveSeasons" :key="season.season" class="hover:bg-gray-50/50">
                      <td class="px-6 py-4 font-medium text-gray-900">{{ season.season }}</td>
                      <td class="px-6 py-4 text-gray-700">{{ season.team }}</td>
                      <td class="px-6 py-4 text-gray-700">{{ season.games }}</td>
                      <td class="px-6 py-4 font-medium text-gray-900">{{ season.pointsPerGame.toFixed(1) }}</td>
                      <td class="px-6 py-4 text-gray-700">{{ season.totalPoints }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Milestones -->
            <div class="mb-6">
              <h3 class="text-2xl font-bold mb-6 flex items-center">
                <span class="mr-3">�</span>
                Career Milestones
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div v-for="milestone in selectedPlayer.milestones" :key="milestone.id" class="bg-gradient-to-br from-gray-50 to-white rounded-2xl p-6 border border-gray-200 hover:shadow-lg transition-shadow">
                  <div class="flex items-center justify-between mb-4">
                    <h4 class="font-bold text-gray-900">{{ milestone.title }}</h4>
                    <span v-if="milestone.achieved" class="text-2xl">🏆</span>
                    <span v-else class="text-2xl opacity-30">🏆</span>
                  </div>
                  <div class="text-sm text-gray-600 mb-3">
                    {{ milestone.current.toLocaleString() }} / {{ milestone.target.toLocaleString() }}
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      :class="milestone.achieved ? 'bg-gradient-to-r from-green-500 to-green-600' : 'bg-gradient-to-r from-blue-500 to-blue-600'"
                      class="h-3 rounded-full transition-all duration-500"
                      :style="{ width: Math.min(100, (milestone.current / milestone.target) * 100) + '%' }"
                    ></div>
                  </div>
                  <div class="mt-2 text-xs text-gray-500">
                    {{ Math.round((milestone.current / milestone.target) * 100) }}% complete
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Basketball-Reference.com style frontend with ultra-modern design
import { ref, computed, onMounted } from 'vue'
const config = useRuntimeConfig()
const API_BASE = config.public.apiBase || 'https://basketball-api.inequality.workers.dev'

// Reactive data
const overview = ref(null)
const players = ref([])
const pagination = ref(null)
const loading = ref(false)
const selectedPlayer = ref(null)

// Search filters
const searchFilters = ref({
  search: '',
  team: '',
  sortBy: 'points_avg',
  sortOrder: 'desc',
  page: 1
})

// Debounce function
let debounceTimer = null
function debounce(func, delay) {
  return function (...args) {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => func.apply(this, args), delay)
  }
}

// Generate pagination numbers with ellipsis
function getPageNumbers() {
  if (!pagination.value) return []
  
  const current = pagination.value.page
  const total = pagination.value.totalPages
  const delta = 2 // Number of pages to show on each side
  
  const range = []
  const rangeWithDots = []
  
  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    range.push(i)
  }
  
  if (current - delta > 2) {
    rangeWithDots.push(1, '...')
  } else {
    rangeWithDots.push(1)
  }
  
  rangeWithDots.push(...range)
  
  if (current + delta < total - 1) {
    rangeWithDots.push('...', total)
  } else if (total > 1) {
    rangeWithDots.push(total)
  }
  
  return rangeWithDots.filter((v, i, a) => a.indexOf(v) === i)
}

// Fetch overview stats
async function fetchOverview() {
  try {
    const response = await fetch(`${API_BASE}/api/stats/overview`)
    overview.value = await response.json()
  } catch (error) {
    console.error('Error fetching overview:', error)
  }
}

// Search players with debounce
const searchPlayers = debounce(async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      search: searchFilters.value.search,
      team: searchFilters.value.team,
      sortBy: searchFilters.value.sortBy,
      sortOrder: searchFilters.value.sortOrder,
      page: searchFilters.value.page,
      limit: 25
    })
    
    const response = await fetch(`${API_BASE}/api/players?${params}`)
    const data = await response.json()
    
    players.value = data.players
    pagination.value = data.pagination
  } catch (error) {
    console.error('Error searching players:', error)
  } finally {
    loading.value = false
  }
}, 300)

// Change page
function changePage(newPage) {
  if (newPage < 1 || newPage > pagination.value.totalPages) return
  searchFilters.value.page = newPage
  searchPlayers()
}

// View player profile
async function viewPlayer(player) {
  try {
    const response = await fetch(`${API_BASE}/api/players/${player.id}`)
    selectedPlayer.value = await response.json()
  } catch (error) {
    console.error('Error fetching player details:', error)
  }
}

// Initialize
onMounted(() => {
  fetchOverview()
  searchPlayers()
})

// Set page title
useHead({
  title: 'Basketball Analytics - Modern German Basketball Database'
})

// Prevent SSR for this component to avoid hydration issues
definePageMeta({
  ssr: false
})
</script>
