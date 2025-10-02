<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">📊 {{ $t('teams.seasonStats.title') }}</h2>
      
      <!-- Team Overview Stats (inspired by Basketball Reference team page) -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="stat bg-base-200 rounded-lg">
          <div class="stat-title">{{ $t('teams.seasonStats.rosterSize') }}</div>
          <div class="stat-value text-primary">{{ teamStats.rosterSize }}</div>
          <div class="stat-desc">{{ $t('teams.seasonStats.activePlayersDesc') }}</div>
        </div>
        
        <div class="stat bg-base-200 rounded-lg">
          <div class="stat-title">{{ $t('teams.seasonStats.totalPoints') }}</div>
          <div class="stat-value text-secondary">{{ teamStats.totalPoints }}</div>
          <div class="stat-desc">{{ $t('teams.seasonStats.seasonTotalDesc') }}</div>
        </div>
        
        <div class="stat bg-base-200 rounded-lg">
          <div class="stat-title">{{ $t('teams.seasonStats.teamPPG') }}</div>
          <div class="stat-value text-accent">{{ teamStats.teamPPG }}</div>
          <div class="stat-desc">{{ $t('teams.seasonStats.pointsPerGameDesc') }}</div>
        </div>
        
        <div class="stat bg-base-200 rounded-lg">
          <div class="stat-title">{{ $t('teams.seasonStats.gamesPlayed') }}</div>
          <div class="stat-value">{{ teamStats.totalGames }}</div>
          <div class="stat-desc">{{ $t('teams.seasonStats.combinedDesc') }}</div>
        </div>
      </div>

      <!-- Category Leaders (using real endpoints) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Best Scorer (statBesteWerferArchiv) -->
        <div class="card bg-gradient-to-br from-primary to-primary-focus text-primary-content">
          <div class="card-body p-4">
            <h3 class="font-bold mb-2">🎯 {{ $t('teams.seasonStats.bestScorer') }}</h3>
            <div v-if="categoryLeaders.bestScorer" class="space-y-2">
              <div class="text-lg font-bold">{{ categoryLeaders.bestScorer.name }}</div>
              <div class="text-2xl font-extrabold">{{ categoryLeaders.bestScorer.points }}</div>
              <div class="text-sm opacity-80">{{ categoryLeaders.bestScorer.average }} PPG</div>
            </div>
            <div v-else class="text-center opacity-50">
              {{ $t('teams.seasonStats.noDataAvailable') }}
            </div>
          </div>
        </div>

        <!-- Best Free Throw Shooter (statBesteFreiWerferArchiv) -->
        <div class="card bg-gradient-to-br from-secondary to-secondary-focus text-secondary-content">
          <div class="card-body p-4">
            <h3 class="font-bold mb-2">🎯 {{ $t('teams.seasonStats.freeThrowShooter') }}</h3>
            <div v-if="categoryLeaders.freeThrowShooter" class="space-y-2">
              <div class="text-lg font-bold">{{ categoryLeaders.freeThrowShooter.name }}</div>
              <div class="text-2xl font-extrabold">{{ categoryLeaders.freeThrowShooter.average }}%</div>
              <div class="text-sm opacity-80">{{ categoryLeaders.freeThrowShooter.points }}/{{ categoryLeaders.freeThrowShooter.games }}</div>
            </div>
            <div v-else class="text-center opacity-50">
              {{ $t('teams.seasonStats.noDataAvailable') }}
            </div>
          </div>
        </div>

        <!-- Best 3-Point Shooter (statBeste3erWerferArchiv) -->
        <div class="card bg-gradient-to-br from-accent to-accent-focus text-accent-content">
          <div class="card-body p-4">
            <h3 class="font-bold mb-2">🎯 {{ $t('teams.seasonStats.threePointShooter') }}</h3>
            <div v-if="categoryLeaders.threePointShooter" class="space-y-2">
              <div class="text-lg font-bold">{{ categoryLeaders.threePointShooter.name }}</div>
              <div class="text-2xl font-extrabold">{{ categoryLeaders.threePointShooter.points }}</div>
              <div class="text-sm opacity-80">{{ categoryLeaders.threePointShooter.average }} per game</div>
            </div>
            <div v-else class="text-center opacity-50">
              {{ $t('teams.seasonStats.noDataAvailable') }}
            </div>
          </div>
        </div>
      </div>

      <!-- Category Breakdown Table (real categories) -->
      <div class="mt-6">
        <h3 class="text-lg font-semibold mb-3">{{ $t('teams.seasonStats.categoryBreakdown') }}</h3>
        <div class="overflow-x-auto">
          <table class="table table-sm">
            <thead>
              <tr>
                <th>{{ $t('teams.seasonStats.category') }}</th>
                <th>{{ $t('teams.seasonStats.players') }}</th>
                <th>{{ $t('teams.seasonStats.totalPoints') }}</th>
                <th>{{ $t('teams.seasonStats.avgPoints') }}</th>
                <th>{{ $t('teams.seasonStats.topPerformer') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="category in categoryBreakdown" :key="category.endpoint">
                <td>
                  <div class="badge" :class="getCategoryBadgeClass(category.endpoint)">
                    {{ getCategoryDisplayName(category.endpoint) }}
                  </div>
                </td>
                <td>{{ category.playerCount }}</td>
                <td>{{ category.totalPoints }}</td>
                <td>{{ category.avgPoints.toFixed(1) }}</td>
                <td>{{ category.topPerformer?.name || 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Enable translations
const { t } = useI18n()

const props = defineProps({
  players: {
    type: Array,
    default: () => []
  }
})

// Calculate team statistics from real player data
const teamStats = computed(() => {
  if (!props.players || props.players.length === 0) {
    return {
      rosterSize: 0,
      totalPoints: 0,
      teamPPG: 0,
      totalGames: 0
    }
  }

  // Consolidate players to avoid counting duplicates across categories
  const uniquePlayers = new Map()
  
  props.players.forEach(player => {
    const key = `${player.first_name}_${player.surname}_${player.team}`
    if (!uniquePlayers.has(key)) {
      uniquePlayers.set(key, {
        name: `${player.first_name} ${player.surname}`,
        points: parseFloat(player.points) || 0,
        games: parseFloat(player.games) || 0,
        average: parseFloat(player.average) || 0
      })
    } else {
      // Take the maximum values when player appears in multiple categories
      const existing = uniquePlayers.get(key)
      existing.points = Math.max(existing.points, parseFloat(player.points) || 0)
      existing.games = Math.max(existing.games, parseFloat(player.games) || 0)
    }
  })

  const consolidatedPlayers = Array.from(uniquePlayers.values())
  const totalPoints = consolidatedPlayers.reduce((sum, p) => sum + p.points, 0)
  const totalGames = consolidatedPlayers.reduce((sum, p) => sum + p.games, 0)
  
  return {
    rosterSize: consolidatedPlayers.length,
    totalPoints,
    teamPPG: consolidatedPlayers.length > 0 ? (totalPoints / consolidatedPlayers.length).toFixed(1) : 0,
    totalGames
  }
})

// Find category leaders using real data
const categoryLeaders = computed(() => {
  const leaders = {
    bestScorer: null,
    freeThrowShooter: null,
    threePointShooter: null
  }

  // Best Scorer (statBesteWerferArchiv)
  const scorers = props.players.filter(p => p.endpoint === 'statBesteWerferArchiv')
  if (scorers.length > 0) {
    leaders.bestScorer = scorers.reduce((prev, curr) => 
      (parseFloat(curr.points) || 0) > (parseFloat(prev.points) || 0) ? curr : prev
    )
  }

  // Best Free Throw Shooter (statBesteFreiWerferArchiv)
  const ftShooters = props.players.filter(p => p.endpoint === 'statBesteFreiWerferArchiv')
  if (ftShooters.length > 0) {
    leaders.freeThrowShooter = ftShooters.reduce((prev, curr) => 
      (parseFloat(curr.average) || 0) > (parseFloat(prev.average) || 0) ? curr : prev
    )
  }

  // Best 3-Point Shooter (statBeste3erWerferArchiv)
  const threeShooters = props.players.filter(p => p.endpoint === 'statBeste3erWerferArchiv')
  if (threeShooters.length > 0) {
    leaders.threePointShooter = threeShooters.reduce((prev, curr) => 
      (parseFloat(curr.points) || 0) > (parseFloat(prev.points) || 0) ? curr : prev
    )
  }

  return leaders
})

// Category breakdown using real endpoints
const categoryBreakdown = computed(() => {
  const categories = {}
  
  props.players.forEach(player => {
    const endpoint = player.endpoint || 'unknown'
    
    if (!categories[endpoint]) {
      categories[endpoint] = {
        endpoint,
        players: [],
        totalPoints: 0,
        playerCount: 0
      }
    }
    
    categories[endpoint].players.push(player)
    categories[endpoint].totalPoints += parseFloat(player.points) || 0
    categories[endpoint].playerCount++
  })

  return Object.values(categories).map(cat => ({
    ...cat,
    avgPoints: cat.playerCount > 0 ? cat.totalPoints / cat.playerCount : 0,
    topPerformer: cat.players.reduce((prev, curr) => 
      (parseFloat(curr.points) || 0) > (parseFloat(prev.points) || 0) ? curr : prev
    )
  }))
})

// Helper functions for real categories
const getCategoryDisplayName = (endpoint) => {
  switch (endpoint) {
    case 'statBesteWerferArchiv': return t('players.categories.bestScorers')
    case 'statBesteFreiWerferArchiv': return t('players.categories.freeThrowShooters')
    case 'statBeste3erWerferArchiv': return t('players.categories.threePointShooters')
    default: return t('players.unknownCategory')
  }
}

const getCategoryBadgeClass = (endpoint) => {
  switch (endpoint) {
    case 'statBesteWerferArchiv': return 'badge-primary'
    case 'statBesteFreiWerferArchiv': return 'badge-secondary'
    case 'statBeste3erWerferArchiv': return 'badge-accent'
    default: return 'badge-neutral'
  }
}
</script>
