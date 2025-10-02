<template>
  <div class="modal-backdrop">
    <div class="modal modal-open">
      <div class="modal-box w-11/12 max-w-5xl">
        <!-- Header -->
        <div class="flex justify-between items-start mb-6">
          <div class="flex items-center gap-4">
            <div class="avatar placeholder">
              <div class="bg-primary text-primary-content rounded-full w-16">
                <span class="text-xl">{{ playerInitials }}</span>
              </div>
            </div>
            <div>
              <h2 class="text-2xl font-bold">{{ player.first_name }} {{ player.surname }}</h2>
              <div class="flex gap-2 mt-1">
                <div class="badge badge-primary">{{ player.team }}</div>
                <div class="badge badge-secondary">Liga {{ player.liga_id }}</div>
                <div class="badge badge-accent">{{ player.season_id }}/{{ player.season_id + 1 }}</div>
              </div>
            </div>
          </div>
          <button @click="$emit('close')" class="btn btn-sm btn-circle btn-ghost">✕</button>
        </div>

        <!-- Quick Stats Overview -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div class="stat bg-base-200 rounded-lg">
            <div class="stat-title">{{ $t('playerProfile.quickStats.totalPoints') }}</div>
            <div class="stat-value text-primary">{{ playerStats.totalPoints }}</div>
            <div class="stat-desc">{{ $t('common.season') }} {{ player.season_id }}</div>
          </div>
          
          <div class="stat bg-base-200 rounded-lg">
            <div class="stat-title">{{ $t('playerProfile.quickStats.gamesPlayed') }}</div>
            <div class="stat-value">{{ playerStats.totalGames }}</div>
            <div class="stat-desc">{{ $t('playerProfile.quickStats.regularSeason') }}</div>
          </div>
          
          <div class="stat bg-base-200 rounded-lg">
            <div class="stat-title">{{ $t('playerProfile.quickStats.pointsPerGame') }}</div>
            <div class="stat-value text-secondary">{{ playerStats.ppg }}</div>
            <div class="stat-desc">{{ $t('playerProfile.quickStats.average') }}</div>
          </div>
          
          <div class="stat bg-base-200 rounded-lg">
            <div class="stat-title">{{ $t('playerProfile.quickStats.categories') }}</div>
            <div class="stat-value text-accent">{{ playerStats.categoriesCount }}</div>
            <div class="stat-desc">{{ $t('playerProfile.quickStats.statisticalCategories') }}</div>
          </div>
        </div>

        <!-- Category Performance (inspired by Basketball Reference player page) -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <!-- Scoring -->
          <div v-if="playerCategories.scoring" class="card bg-gradient-to-br from-primary to-primary-focus text-primary-content">
            <div class="card-body p-4">
              <h3 class="card-title text-lg">🎯 {{ $t('playerProfile.categoryPerformance.scoring') }}</h3>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span>{{ $t('playerProfile.categoryPerformance.points') }}</span>
                  <span class="font-bold">{{ playerCategories.scoring.points }}</span>
                </div>
                <div class="flex justify-between">
                  <span>{{ $t('playerProfile.categoryPerformance.games') }}</span>
                  <span>{{ playerCategories.scoring.games }}</span>
                </div>
                <div class="flex justify-between">
                  <span>{{ $t('playerProfile.categoryPerformance.ppg') }}</span>
                  <span class="font-bold">{{ playerCategories.scoring.average }}</span>
                </div>
                <div class="flex justify-between">
                  <span>{{ $t('playerProfile.categoryPerformance.leagueRank') }}</span>
                  <span class="badge badge-warning">#{{ playerCategories.scoring.rank }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Free Throws -->
          <div v-if="playerCategories.freeThrows" class="card bg-gradient-to-br from-secondary to-secondary-focus text-secondary-content">
            <div class="card-body p-4">
              <h3 class="card-title text-lg">🎯 {{ $t('playerProfile.categoryPerformance.freeThrows') }}</h3>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span>{{ $t('playerProfile.categoryPerformance.ftMade') }}</span>
                  <span class="font-bold">{{ playerCategories.freeThrows.points }}</span>
                </div>
                <div class="flex justify-between">
                  <span>{{ $t('playerProfile.categoryPerformance.ftAttempts') }}</span>
                  <span>{{ playerCategories.freeThrows.games }}</span>
                </div>
                <div class="flex justify-between">
                  <span>{{ $t('playerProfile.categoryPerformance.ftPercentage') }}</span>
                  <span class="font-bold">{{ playerCategories.freeThrows.average }}%</span>
                </div>
                <div class="flex justify-between">
                  <span>{{ $t('playerProfile.categoryPerformance.leagueRank') }}</span>
                  <span class="badge badge-warning">#{{ playerCategories.freeThrows.rank }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Three Pointers -->
          <div v-if="playerCategories.threePointers" class="card bg-gradient-to-br from-accent to-accent-focus text-accent-content">
            <div class="card-body p-4">
              <h3 class="card-title text-lg">🎯 {{ $t('playerProfile.categoryPerformance.threePointers') }}</h3>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span>{{ $t('playerProfile.categoryPerformance.threePtMade') }}</span>
                  <span class="font-bold">{{ playerCategories.threePointers.points }}</span>
                </div>
                <div class="flex justify-between">
                  <span>{{ $t('playerProfile.categoryPerformance.games') }}</span>
                  <span>{{ playerCategories.threePointers.games }}</span>
                </div>
                <div class="flex justify-between">
                  <span>{{ $t('playerProfile.categoryPerformance.threePtPerGame') }}</span>
                  <span class="font-bold">{{ playerCategories.threePointers.average }}</span>
                </div>
                <div class="flex justify-between">
                  <span>{{ $t('playerProfile.categoryPerformance.leagueRank') }}</span>
                  <span class="badge badge-warning">#{{ playerCategories.threePointers.rank }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Detailed Season Stats Table -->
        <div class="card bg-base-100 shadow-xl mb-6">
          <div class="card-body">
            <h3 class="card-title">📊 {{ $t('playerProfile.seasonStats.title') }}</h3>
            <div class="overflow-x-auto">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>{{ $t('playerProfile.seasonStats.category') }}</th>
                    <th>{{ $t('playerProfile.seasonStats.rank') }}</th>
                    <th>{{ $t('playerProfile.seasonStats.pointsMade') }}</th>
                    <th>{{ $t('playerProfile.seasonStats.gamesAttempts') }}</th>
                    <th>{{ $t('playerProfile.seasonStats.averagePercentage') }}</th>
                    <th>{{ $t('playerProfile.seasonStats.source') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="category in allPlayerData" :key="category.endpoint">
                    <td>
                      <div class="badge" :class="getCategoryBadgeClass(category.endpoint)">
                        {{ getCategoryDisplayName(category.endpoint) }}
                      </div>
                    </td>
                    <td>
                      <div class="badge badge-warning">#{{ category.rank }}</div>
                    </td>
                    <td class="font-bold">{{ category.points }}</td>
                    <td>{{ category.games }}</td>
                    <td class="font-bold">{{ category.average }}</td>
                    <td>
                      <div class="text-xs opacity-50">
                        {{ new Date(category.extracted_at).toLocaleDateString('de-DE') }}
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Player Actions -->
        <div class="flex justify-between items-center">
          <div class="flex gap-2">
            <button @click="sharePlayer" class="btn btn-sm btn-outline">
              📤 {{ $t('playerProfile.actions.sharePlayer') }}
            </button>
            <button @click="exportPlayerCard" class="btn btn-sm btn-primary">
              🏀 {{ $t('playerProfile.actions.playerCard') }}
            </button>
            <button @click="comparePlayer" class="btn btn-sm btn-secondary">
              ⚖️ {{ $t('playerProfile.actions.compare') }}
            </button>
          </div>
          
          <div class="flex gap-2">
            <button @click="viewTeam" class="btn btn-sm btn-accent">
              👥 {{ $t('playerProfile.actions.viewTeam') }}
            </button>
            <button @click="$emit('close')" class="btn btn-sm">
              {{ $t('playerProfile.actions.close') }}
            </button>
          </div>
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
  player: {
    type: Object,
    required: true
  },
  allPlayerData: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'share', 'export', 'compare', 'viewTeam'])

// Player initials for avatar
const playerInitials = computed(() => {
  const firstName = props.player.first_name || ''
  const lastName = props.player.surname || ''
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
})

// Calculate overall player stats from all categories
const playerStats = computed(() => {
  const categories = props.allPlayerData || [props.player]
  
  // Consolidate stats across categories
  let totalPoints = 0
  let totalGames = 0
  const categoriesCount = categories.length
  
  categories.forEach(cat => {
    // For total points, sum from scoring category only to avoid double counting
    if (cat.endpoint === 'statBesteWerferArchiv') {
      totalPoints = Math.max(totalPoints, parseFloat(cat.points) || 0)
      totalGames = Math.max(totalGames, parseFloat(cat.games) || 0)
    }
  })
  
  // If no scoring category, use the max from available categories
  if (totalPoints === 0) {
    totalPoints = Math.max(...categories.map(cat => parseFloat(cat.points) || 0))
    totalGames = Math.max(...categories.map(cat => parseFloat(cat.games) || 0))
  }
  
  const ppg = totalGames > 0 ? (totalPoints / totalGames).toFixed(1) : '0.0'
  
  return {
    totalPoints,
    totalGames,
    ppg,
    categoriesCount
  }
})

// Organize player data by categories
const playerCategories = computed(() => {
  const categories = {
    scoring: null,
    freeThrows: null,
    threePointers: null
  }
  
  props.allPlayerData.forEach(data => {
    switch (data.endpoint) {
      case 'statBesteWerferArchiv':
        categories.scoring = data
        break
      case 'statBesteFreiWerferArchiv':
        categories.freeThrows = data
        break
      case 'statBeste3erWerferArchiv':
        categories.threePointers = data
        break
    }
  })
  
  return categories
})

// Helper functions
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

// Action handlers
const sharePlayer = () => {
  const playerText = `🏀 ${props.player.first_name} ${props.player.surname} - ${props.player.team}

📊 Season ${props.player.season_id}/${props.player.season_id + 1} Stats:
• ${playerStats.value.totalPoints} Points in ${playerStats.value.totalGames} Games
• ${playerStats.value.ppg} PPG
• Liga ${props.player.liga_id}
• ${playerStats.value.categoriesCount} Statistical Categories

🏆 Basketball-Bund.net Data`

  const currentUrl = window.location.href
  const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(playerText + '\n\n' + currentUrl)}`
  
  window.open(whatsappUrl, '_blank')
}

const exportPlayerCard = () => {
  emit('export', props.player)
}

const comparePlayer = () => {
  emit('compare', props.player)
}

const viewTeam = () => {
  emit('viewTeam', props.player.team)
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
