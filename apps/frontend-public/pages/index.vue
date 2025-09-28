<template>
  <div>
    <!-- Hero Section -->
    <div class="hero bg-gradient-to-r from-primary to-secondary text-primary-content py-16">
      <div class="hero-content text-center">
        <div class="max-w-md">
          <h1 class="mb-5 text-5xl font-bold">{{ $t('dashboard.title') }}</h1>
          <p class="mb-5">{{ $t('dashboard.subtitle') }}</p>
        </div>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
      <!-- Top Players Card -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">{{ $t('dashboard.topPlayers') }}</h2>
          
          <div v-if="loading" class="flex justify-center">
            <span class="loading loading-spinner loading-lg"></span>
          </div>
          
          <div v-else-if="topPlayers.length > 0" class="overflow-x-auto">
            <table class="table table-sm">
              <thead>
                <tr>
                  <th>{{ $t('player.profile') }}</th>
                  <th>{{ $t('dashboard.pointsPerGame') }}</th>
                  <th>{{ $t('dashboard.threePointPct') }}</th>
                  <th>{{ $t('dashboard.freeThrowPct') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="player in topPlayers" :key="player.id" class="hover">
                  <td>
                    <NuxtLink :to="`/players/${player.id}`" class="link link-hover font-medium">
                      {{ player.name }}
                    </NuxtLink>
                  </td>
                  <td>{{ player.pts_g?.toFixed(1) || '0.0' }}</td>
                  <td>{{ player.threePPct ? (player.threePPct * 100).toFixed(1) + '%' : 'N/A' }}</td>
                  <td>{{ player.ft_pct ? (player.ft_pct * 100).toFixed(1) + '%' : 'N/A' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div v-else class="text-center py-8">
            <p class="text-base-content/70">{{ $t('common.noData') }}</p>
          </div>
        </div>
      </div>

      <!-- Seasons Card -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">{{ $t('dashboard.seasons') }}</h2>
          
          <!-- Filters -->
          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text">{{ $t('filters.team') }}</span>
            </label>
            <select 
              v-model="teamFilter" 
              class="select select-bordered select-sm"
              @change="fetchData"
            >
              <option value="">{{ $t('filters.allTeams') }}</option>
              <option value="bgl">{{ $t('filters.bgLitzendorf') }}</option>
            </select>
          </div>
          
          <div v-if="loading" class="flex justify-center">
            <span class="loading loading-spinner loading-lg"></span>
          </div>
          
          <div v-else-if="seasons.length > 0" class="space-y-3">
            <div v-for="season in seasons" :key="season.seasonId" class="border rounded-lg p-4">
              <div class="flex justify-between items-center">
                <div>
                  <h3 class="font-semibold">{{ season.year }}</h3>
                  <p class="text-sm text-base-content/70">{{ season.league?.name || 'Unknown League' }}</p>
                </div>
                <div class="badge badge-outline">{{ season._count?.matches || 0 }} games</div>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-8">
            <p class="text-base-content/70">{{ $t('common.noData') }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Player {
  id: string
  name: string
  pts_g?: number
  threePPct?: number
  ft_pct?: number
}

interface Season {
  seasonId: string
  year: number
  league?: {
    name: string
  }
  _count?: {
    matches: number
  }
}

const config = useRuntimeConfig()
const loading = ref(true)
const topPlayers = ref<Player[]>([])
const seasons = ref<Season[]>([])
const teamFilter = ref('')

async function fetchData() {
  try {
    loading.value = true
    
    // Mock data for development since API might not be fully set up
    const mockPlayers: Player[] = [
      { id: '1', name: 'Max Mustermann', pts_g: 18.5, threePPct: 0.385, ft_pct: 0.850 },
      { id: '2', name: 'John Doe', pts_g: 16.2, threePPct: 0.425, ft_pct: 0.790 },
      { id: '3', name: 'Michael Schmidt', pts_g: 15.8, threePPct: 0.365, ft_pct: 0.820 },
      { id: '4', name: 'Andreas Weber', pts_g: 14.3, threePPct: 0.395, ft_pct: 0.775 },
      { id: '5', name: 'Thomas Müller', pts_g: 13.9, threePPct: 0.355, ft_pct: 0.810 }
    ]
    
    const mockSeasons: Season[] = [
      { 
        seasonId: '2023-24', 
        year: 2024, 
        league: { name: 'Bezirksoberliga' }, 
        _count: { matches: 26 } 
      },
      { 
        seasonId: '2022-23', 
        year: 2023, 
        league: { name: 'Bezirksoberliga' }, 
        _count: { matches: 24 } 
      },
      { 
        seasonId: '2021-22', 
        year: 2022, 
        league: { name: 'Bezirksliga' }, 
        _count: { matches: 22 } 
      }
    ]

    // Filter mock data based on team filter
    if (teamFilter.value === 'bgl') {
      topPlayers.value = mockPlayers.filter((_, index) => index % 2 === 0) // Show every other player as BGL
    } else {
      topPlayers.value = mockPlayers
    }
    
    seasons.value = mockSeasons
    
  } catch (error) {
    console.error('Error fetching data:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>