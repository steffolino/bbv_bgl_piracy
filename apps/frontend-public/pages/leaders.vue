<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Header -->
    <div class="text-center mb-8">
      <h1 class="text-4xl font-bold mb-4">🏆 {{ $t('leaders.title') }}</h1>
      <p class="text-lg opacity-80">{{ $t('leaders.subtitle') }}</p>
    </div>

    <!-- Filters -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Liga Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">{{ $t('leaders.filters.league') }}</span>
            </label>
            <select v-model="selectedLeague" class="select select-bordered">
              <option value="">{{ $t('leaders.filters.allLeagues') }}</option>
              <option v-for="league in availableLeagues" :key="league" :value="league">
                Liga {{ league }}
              </option>
            </select>
          </div>

          <!-- Season Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">{{ $t('leaders.filters.season') }}</span>
            </label>
            <select v-model="selectedSeason" class="select select-bordered">
              <option value="">{{ $t('leaders.filters.allSeasons') }}</option>
              <option v-for="season in availableSeasons" :key="season" :value="season">
                {{ season }}/{{ season + 1 }}
              </option>
            </select>
          </div>

          <!-- Category Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">{{ $t('leaders.filters.category') }}</span>
            </label>
            <select v-model="selectedCategory" class="select select-bordered">
              <option value="">{{ $t('leaders.filters.allCategories') }}</option>
              <option value="statBesteWerferArchiv">{{ $t('players.categories.bestScorers') }}</option>
              <option value="statBesteFreiWerferArchiv">{{ $t('players.categories.freeThrowShooters') }}</option>
              <option value="statBeste3erWerferArchiv">{{ $t('players.categories.threePointShooters') }}</option>
            </select>
          </div>

          <!-- Minimum Games Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">{{ $t('leaders.filters.minGames') }}</span>
            </label>
            <input v-model.number="minGames" type="number" 
                   placeholder="e.g. 5" class="input input-bordered" min="0" max="35">
          </div>
        </div>
      </div>
    </div>

    <!-- Category Leaders Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <!-- Scoring Leaders -->
      <div class="card bg-gradient-to-br from-primary to-primary-focus text-primary-content shadow-xl">
        <div class="card-body">
          <h2 class="card-title text-white">🎯 {{ $t('leaders.categoryLeaders.scoringLeaders') }}</h2>
          <p class="text-primary-content opacity-80 mb-4">{{ $t('leaders.categoryLeaders.topPointScorers') }} (statBesteWerferArchiv)</p>
          
          <div class="space-y-3">
            <div v-for="(player, index) in scoringLeaders.slice(0, 5)" :key="player.name" 
                 class="flex items-center justify-between bg-white bg-opacity-20 rounded-lg p-3">
              <div class="flex items-center gap-3">
                <div class="badge badge-warning">{{ index + 1 }}</div>
                <div>
                  <div class="font-bold">{{ player.first_name }} {{ player.surname }}</div>
                  <div class="text-sm opacity-80">{{ player.team }}</div>
                </div>
              </div>
              <div class="text-right">
                <div class="text-xl font-bold">{{ player.points }}</div>
                <div class="text-sm opacity-80">{{ player.average }} PPG</div>
              </div>
            </div>
          </div>
          
          <div class="mt-4">
            <button @click="viewFullLeaderboard('statBesteWerferArchiv')" 
                    class="btn btn-primary-content btn-outline btn-sm w-full">
              {{ $t('leaders.categoryLeaders.viewFullLeaderboard') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Free Throw Leaders -->
      <div class="card bg-gradient-to-br from-secondary to-secondary-focus text-secondary-content shadow-xl">
        <div class="card-body">
          <h2 class="card-title text-white">🎯 {{ $t('leaders.categoryLeaders.freeThrowLeaders') }}</h2>
          <p class="text-secondary-content opacity-80 mb-4">{{ $t('leaders.categoryLeaders.bestFreeThrowShooters') }} (statBesteFreiWerferArchiv)</p>
          
          <div class="space-y-3">
            <div v-for="(player, index) in freeThrowLeaders.slice(0, 5)" :key="player.name" 
                 class="flex items-center justify-between bg-white bg-opacity-20 rounded-lg p-3">
              <div class="flex items-center gap-3">
                <div class="badge badge-warning">{{ index + 1 }}</div>
                <div>
                  <div class="font-bold">{{ player.first_name }} {{ player.surname }}</div>
                  <div class="text-sm opacity-80">{{ player.team }}</div>
                </div>
              </div>
              <div class="text-right">
                <div class="text-xl font-bold">{{ player.average }}%</div>
                <div class="text-sm opacity-80">{{ player.points }}/{{ player.games }}</div>
              </div>
            </div>
          </div>
          
          <div class="mt-4">
            <button @click="viewFullLeaderboard('statBesteFreiWerferArchiv')" 
                    class="btn btn-secondary-content btn-outline btn-sm w-full">
              {{ $t('leaders.categoryLeaders.viewFullLeaderboard') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Three Point Leaders -->
      <div class="card bg-gradient-to-br from-accent to-accent-focus text-accent-content shadow-xl">
        <div class="card-body">
          <h2 class="card-title text-white">🎯 {{ $t('leaders.categoryLeaders.threePointLeaders') }}</h2>
          <p class="text-accent-content opacity-80 mb-4">{{ $t('leaders.categoryLeaders.top3PointScorers') }} (statBeste3erWerferArchiv)</p>
          
          <div class="space-y-3">
            <div v-for="(player, index) in threePointLeaders.slice(0, 5)" :key="player.name" 
                 class="flex items-center justify-between bg-white bg-opacity-20 rounded-lg p-3">
              <div class="flex items-center gap-3">
                <div class="badge badge-warning">{{ index + 1 }}</div>
                <div>
                  <div class="font-bold">{{ player.first_name }} {{ player.surname }}</div>
                  <div class="text-sm opacity-80">{{ player.team }}</div>
                </div>
              </div>
              <div class="text-right">
                <div class="text-xl font-bold">{{ player.points }}</div>
                <div class="text-sm opacity-80">{{ player.average }}/G</div>
              </div>
            </div>
          </div>
          
          <div class="mt-4">
            <button @click="viewFullLeaderboard('statBeste3erWerferArchiv')" 
                    class="btn btn-accent-content btn-outline btn-sm w-full">
              {{ $t('leaders.categoryLeaders.viewFullLeaderboard') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Complete Leaderboard Table -->
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <div class="flex justify-between items-center mb-4">
          <h2 class="card-title">📊 {{ $t('leaders.leaderboard.title') }}</h2>
          <div class="flex gap-2">
            <button @click="exportLeaderboard" class="btn btn-primary btn-sm">
              📊 {{ $t('leaders.leaderboard.exportData') }}
            </button>
            <div class="dropdown dropdown-end">
              <div tabindex="0" role="button" class="btn btn-sm btn-outline">
                {{ $t('leaders.leaderboard.sortBy') }} {{ getSortLabel() }}
              </div>
              <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
                <li><a @click="setSortBy('points')">{{ $t('leaders.leaderboard.byPoints') }}</a></li>
                <li><a @click="setSortBy('average')">{{ $t('leaders.leaderboard.byAverage') }}</a></li>
                <li><a @click="setSortBy('games')">{{ $t('leaders.leaderboard.byGames') }}</a></li>
                <li><a @click="setSortBy('name')">{{ $t('leaders.leaderboard.byName') }}</a></li>
              </ul>
            </div>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="table table-zebra">
            <thead>
              <tr>
                <th>{{ $t('leaders.leaderboard.rank') }}</th>
                <th>{{ $t('leaders.leaderboard.player') }}</th>
                <th>{{ $t('leaders.leaderboard.team') }}</th>
                <th>{{ $t('leaders.leaderboard.liga') }}</th>
                <th>{{ $t('leaders.leaderboard.season') }}</th>
                <th>{{ $t('leaders.leaderboard.category') }}</th>
                <th>{{ $t('leaders.leaderboard.pointsMade') }}</th>
                <th>{{ $t('leaders.leaderboard.gamesAttempts') }}</th>
                <th>{{ $t('leaders.leaderboard.averagePercentage') }}</th>
                <th>{{ $t('leaders.leaderboard.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(player, index) in paginatedLeaders" :key="`${player.name}-${player.endpoint}`">
                <td>
                  <div class="badge badge-primary">{{ (currentPage - 1) * itemsPerPage + index + 1 }}</div>
                </td>
                <td>
                  <div class="flex items-center gap-3">
                    <div class="avatar placeholder">
                      <div class="bg-neutral-focus text-neutral-content rounded-full w-8">
                        <span class="text-xs">{{ getPlayerInitials(player) }}</span>
                      </div>
                    </div>
                    <div>
                      <div class="font-bold">{{ player.first_name }} {{ player.surname }}</div>
                    </div>
                  </div>
                </td>
                <td>{{ player.team }}</td>
                <td>{{ player.liga_id }}</td>
                <td>{{ player.season_id }}/{{ player.season_id + 1 }}</td>
                <td>
                  <div class="badge" :class="getCategoryBadgeClass(player.endpoint)">
                    {{ getCategoryShortName(player.endpoint) }}
                  </div>
                </td>
                <td class="font-bold">{{ player.points }}</td>
                <td>{{ player.games }}</td>
                <td class="font-bold">{{ player.average }}</td>
                <td>
                  <div class="dropdown dropdown-end">
                    <div tabindex="0" role="button" class="btn btn-xs btn-ghost">⋯</div>
                    <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-40">
                      <li><a @click="viewPlayerProfile(player)">👤 {{ $t('leaders.leaderboard.profile') }}</a></li>
                      <li><a @click="viewPlayerTeam(player)">👥 Team</a></li>
                      <li><a @click="sharePlayer(player)">📤 {{ $t('leaders.leaderboard.share') }}</a></li>
                    </ul>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="flex justify-center mt-6">
          <div class="join">
            <button v-for="page in totalPages" :key="page" 
                    @click="currentPage = page"
                    class="join-item btn btn-sm"
                    :class="{ 'btn-active': page === currentPage }">
              {{ page }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Runtime config
const config = useRuntimeConfig()

// Enable translations
const { t } = useI18n()

// State
const playersData = ref([])
const loading = ref(true)
const selectedLeague = ref('')
const selectedSeason = ref('')
const selectedCategory = ref('')
const minGames = ref(5)
const sortBy = ref('points')
const sortOrder = ref('desc')
const currentPage = ref(1)
const itemsPerPage = 50

// Load players data (try live API first, fallback to local JSON)
const loadPlayersData = async () => {
  try {
    loading.value = true

    // Try live API
    try {
      const params = new URLSearchParams({ limit: '20000' })
      const resp = await fetch(`${config.public.apiBase}/api/players?${params.toString()}`)
      if (resp.ok) {
        const data = await resp.json()
        playersData.value = data.players || []
        console.log('✅ Loaded', playersData.value.length, 'player records from live API')
        return
      }
      console.warn('Live API returned non-OK status, falling back to local data')
    } catch (e) {
      console.warn('Live API unavailable, falling back to local JSON:', e)
    }

    // Fallback
    const response = await fetch('/real_players_extracted.json')
    if (!response.ok) throw new Error('Failed to load data')
    const data = await response.json()
    playersData.value = data.players || []
    console.log('✅ Loaded', playersData.value.length, 'player records from local JSON')

  } catch (error) {
    console.error('❌ Error loading players data:', error)
    playersData.value = []
  } finally {
    loading.value = false
  }
}

// Computed filters
const availableLeagues = computed(() => {
  const leagues = new Set()
  playersData.value.forEach(player => {
    if (player.liga_id) leagues.add(player.liga_id)
  })
  return Array.from(leagues).sort((a, b) => a - b)
})

const availableSeasons = computed(() => {
  const seasons = new Set()
  playersData.value.forEach(player => {
    if (player.season_id) seasons.add(player.season_id)
  })
  return Array.from(seasons).sort((a, b) => a - b)
})

// Filter and sort players
const filteredPlayers = computed(() => {
  let filtered = playersData.value.filter(player => {
    // Apply filters
    if (selectedLeague.value && player.liga_id !== parseInt(selectedLeague.value)) return false
    if (selectedSeason.value && player.season_id !== parseInt(selectedSeason.value)) return false
    if (selectedCategory.value && player.endpoint !== selectedCategory.value) return false
    if (minGames.value && (parseFloat(player.games) || 0) < minGames.value) return false
    
    return true
  })

  // Sort players
  return filtered.sort((a, b) => {
    let aVal, bVal
    
    switch (sortBy.value) {
      case 'points':
        aVal = parseFloat(a.points) || 0
        bVal = parseFloat(b.points) || 0
        break
      case 'average':
        aVal = parseFloat(a.average) || 0
        bVal = parseFloat(b.average) || 0
        break
      case 'games':
        aVal = parseFloat(a.games) || 0
        bVal = parseFloat(b.games) || 0
        break
      case 'name':
        aVal = `${a.first_name} ${a.surname}`.toLowerCase()
        bVal = `${b.first_name} ${b.surname}`.toLowerCase()
        break
      default:
        return 0
    }
    
    if (sortOrder.value === 'desc') {
      return bVal > aVal ? 1 : bVal < aVal ? -1 : 0
    } else {
      return aVal > bVal ? 1 : aVal < bVal ? -1 : 0
    }
  })
})

// Category-specific leaders
const scoringLeaders = computed(() => {
  return playersData.value
    .filter(p => p.endpoint === 'statBesteWerferArchiv' && (parseFloat(p.games) || 0) >= minGames.value)
    .sort((a, b) => (parseFloat(b.points) || 0) - (parseFloat(a.points) || 0))
})

const freeThrowLeaders = computed(() => {
  return playersData.value
    .filter(p => p.endpoint === 'statBesteFreiWerferArchiv' && (parseFloat(p.games) || 0) >= minGames.value)
    .sort((a, b) => (parseFloat(b.average) || 0) - (parseFloat(a.average) || 0))
})

const threePointLeaders = computed(() => {
  return playersData.value
    .filter(p => p.endpoint === 'statBeste3erWerferArchiv' && (parseFloat(p.games) || 0) >= minGames.value)
    .sort((a, b) => (parseFloat(b.points) || 0) - (parseFloat(a.points) || 0))
})

// Pagination
const totalPages = computed(() => Math.ceil(filteredPlayers.value.length / itemsPerPage))

const paginatedLeaders = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredPlayers.value.slice(start, end)
})

// Helper functions
const getPlayerInitials = (player) => {
  const firstName = player.first_name || ''
  const lastName = player.surname || ''
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
}

const getCategoryBadgeClass = (endpoint) => {
  switch (endpoint) {
    case 'statBesteWerferArchiv': return 'badge-primary'
    case 'statBesteFreiWerferArchiv': return 'badge-secondary'
    case 'statBeste3erWerferArchiv': return 'badge-accent'
    default: return 'badge-neutral'
  }
}

const getCategoryShortName = (endpoint) => {
  switch (endpoint) {
    case 'statBesteWerferArchiv': return 'PTS'
    case 'statBesteFreiWerferArchiv': return 'FT'
    case 'statBeste3erWerferArchiv': return '3P'
    default: return '?'
  }
}

const getSortLabel = () => {
  switch (sortBy.value) {
    case 'points': return t('leaders.leaderboard.byPoints')
    case 'average': return t('leaders.leaderboard.byAverage')
    case 'games': return t('leaders.leaderboard.byGames')
    case 'name': return t('leaders.leaderboard.byName')
    default: return t('leaders.leaderboard.byPoints')
  }
}

// Actions
const setSortBy = (field) => {
  if (sortBy.value === field) {
    sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
  } else {
    sortBy.value = field
    sortOrder.value = field === 'name' ? 'asc' : 'desc'
  }
}

const viewFullLeaderboard = (category) => {
  selectedCategory.value = category
  currentPage.value = 1
  
  // Scroll to table
  document.querySelector('.card.bg-base-100.shadow-xl').scrollIntoView({ 
    behavior: 'smooth' 
  })
}

const viewPlayerProfile = (player) => {
  // TODO: Implement player profile modal or navigation
  alert(`Player profile for ${player.first_name} ${player.surname} coming soon...`)
}

const viewPlayerTeam = (player) => {
  const encodedTeamName = encodeURIComponent(player.team)
  navigateTo(`/teams/${encodedTeamName}?league=${player.liga_id}&season=${player.season_id}`)
}

const sharePlayer = (player) => {
  const playerText = `🏀 ${player.first_name} ${player.surname} - ${player.team}

📊 ${getCategoryShortName(player.endpoint)} Leader:
• ${player.points} ${player.endpoint === 'statBesteFreiWerferArchiv' ? 'FT Made' : 'Points'}
• ${player.games} ${player.endpoint === 'statBesteFreiWerferArchiv' ? 'Attempts' : 'Games'}
• ${player.average} ${player.endpoint === 'statBesteFreiWerferArchiv' ? '% FT' : 'Average'}
• Liga ${player.liga_id} • Season ${player.season_id}/${player.season_id + 1}

🏆 Basketball-Bund.net Data`

  const currentUrl = window.location.href
  const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(playerText + '\n\n' + currentUrl)}`
  
  window.open(whatsappUrl, '_blank')
}

const exportLeaderboard = () => {
  const exportData = {
    filters: {
      league: selectedLeague.value,
      season: selectedSeason.value,
      category: selectedCategory.value,
      minGames: minGames.value
    },
    leaders: filteredPlayers.value.map(player => ({
      name: `${player.first_name} ${player.surname}`,
      team: player.team,
      league: player.liga_id,
      season: player.season_id,
      category: getCategoryShortName(player.endpoint),
      points: player.points,
      games: player.games,
      average: player.average,
      rank: player.rank
    })),
    exportDate: new Date().toISOString()
  }
  
  const json = JSON.stringify(exportData, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `basketball_leaders_${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

onMounted(() => {
  loadPlayersData()
})
</script>
