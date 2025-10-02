<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Header -->
    <div class="text-center mb-8 relative">
      <!-- Share Button - Top Right -->
      <div class="absolute top-0 right-0">
        <ShareButton 
          title="Basketball Teams & Vereine - BBV BGL"
          description="Entdecke Basketball-Teams, Mannschaften und Vereinsinformationen. Umfassende Liga-Statistiken und Spielerdaten."
          :hashtags="['Basketball', 'BBL', 'Teams', 'Vereine', 'Liga']"
          :show-export="true"
          @export="exportAllTeams"
        />
      </div>
      
      <h1 class="text-4xl font-bold mb-4">🏀 Teams & Vereine</h1>
      <p class="text-lg opacity-80">Mannschaften, Ligen und Vereinsinformationen</p>
    </div>

    <!-- Search and Filters -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <!-- Team Search -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Team suchen</span>
            </label>
            <input v-model="searchTerm" type="text" placeholder="z.B. BG Litzendorf" 
                   class="input input-bordered">
          </div>

          <!-- League Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Liga</span>
            </label>
            <select v-model="selectedLeague" class="select select-bordered">
              <option value="">Alle Ligen</option>
              <option v-for="league in uniqueLeagues" :key="league" :value="league">
                Liga {{ league }}
              </option>
            </select>
          </div>

          <!-- Season Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Saison</span>
            </label>
            <select v-model="selectedSeason" class="select select-bordered">
              <option value="">Alle Saisons</option>
              <option v-for="season in uniqueSeasons" :key="season" :value="season">
                {{ season }}
              </option>
            </select>
          </div>

          <!-- Sort Options -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Sortierung</span>
            </label>
            <select v-model="sortBy" class="select select-bordered">
              <option value="points">Nach Punkten</option>
              <option value="players">Nach Spieleranzahl</option>
              <option value="name">Nach Name</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Featured Organizations -->
    <div class="card bg-gradient-to-r from-primary to-secondary text-primary-content shadow-xl mb-8">
      <div class="card-body">
        <h2 class="card-title text-white">🌟 Vorgestellte Vereine</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- BG Litzendorf Featured -->
          <div class="card bg-base-100 text-base-content shadow-lg">
            <div class="card-body p-4">
              <div class="flex items-center gap-3 mb-3">
                <div class="avatar placeholder">
                  <div class="bg-primary text-primary-content rounded-full w-12">
                    <span class="text-sm font-bold">BGL</span>
                  </div>
                </div>
                <div>
                  <h3 class="font-bold">BG Litzendorf</h3>
                  <p class="text-xs opacity-70">Basketball Gemeinschaft</p>
                </div>
              </div>
              <div class="stats stats-horizontal shadow">
                <div class="stat p-2">
                  <div class="stat-title text-xs">Teams</div>
                  <div class="stat-value text-sm">3</div>
                </div>
                <div class="stat p-2">
                  <div class="stat-title text-xs">Spieler</div>
                  <div class="stat-value text-sm">118</div>
                </div>
              </div>
              <div class="card-actions justify-end mt-3">
                <a href="https://bg-litzendorf.de/" target="_blank" class="btn btn-xs btn-outline">
                  🌐 Website
                </a>
                <button @click="viewOrganization('BG Litzendorf')" class="btn btn-xs btn-primary">
                  Details
                </button>
              </div>
            </div>
          </div>

          <!-- Placeholder for future featured clubs -->
          <div class="card bg-base-100 text-base-content shadow-lg opacity-50">
            <div class="card-body p-4 text-center">
              <div class="text-4xl mb-2">🏀</div>
              <h3 class="font-bold">Weitere Vereine</h3>
              <p class="text-xs opacity-70">Kommen bald...</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Teams Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <div v-for="team in filteredTeams" :key="`${team.name}-${team.leagues[0]}-${team.seasons[0]}`" 
           class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer"
           @click="viewTeam(team.name, team.leagues[0], team.seasons[0])">
        <div class="card-body p-4">
          <!-- Team Header -->
          <div class="flex items-center gap-3 mb-3">
            <div class="avatar placeholder">
              <div class="bg-neutral-focus text-neutral-content rounded-full w-12">
                <span class="text-sm">{{ getTeamInitials(team.name) }}</span>
              </div>
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-sm leading-tight">{{ team.name }}</h3>
              <p class="text-xs opacity-70">Liga {{ team.leagues[0] }} • {{ team.seasons[0] }}</p>
            </div>
          </div>

          <!-- Team Stats -->
          <div class="stats stats-horizontal shadow mb-3">
            <div class="stat p-2">
              <div class="stat-title text-xs">Spieler</div>
              <div class="stat-value text-sm">{{ team.players_count }}</div>
            </div>
            <div class="stat p-2">
              <div class="stat-title text-xs">Punkte</div>
              <div class="stat-value text-sm">{{ formatNumber(team.total_points) }}</div>
            </div>
          </div>

          <!-- Organization Badge -->
          <div v-if="hasOrganizationInfo(team.name)" class="mb-3">
            <div class="badge badge-success badge-sm">
              🏢 Vereinsinfo verfügbar
            </div>
          </div>

          <!-- Team Actions -->
          <div class="card-actions justify-end">
            <button @click.stop="viewTeamRoster(team)" class="btn btn-xs btn-outline">
              👥 Kader
            </button>
            <button @click.stop="viewTeam(team.name, team.leagues[0], team.seasons[0])" 
                    class="btn btn-xs btn-primary">
              Details
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <span class="loading loading-spinner loading-lg"></span>
      <p class="mt-2">Lade Teams...</p>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && filteredTeams.length === 0" class="text-center py-8 opacity-50">
      <div class="text-6xl mb-4">🔍</div>
      <h3 class="text-xl font-bold mb-2">Keine Teams gefunden</h3>
      <p>Versuche andere Suchkriterien oder Filter.</p>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-center mt-8">
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// State
const teamsData = ref([])
const loading = ref(true)
const searchTerm = ref('')
const selectedLeague = ref('')
const selectedSeason = ref('')
const sortBy = ref('points')
const currentPage = ref(1)
const itemsPerPage = 24

// Load teams data
const loadTeamsData = async () => {
  loading.value = true
  try {
    // Mock teams data - in real implementation, this would come from the Python API
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    teamsData.value = [
      {
        name: 'BG Litzendorf',
        players_count: 39,
        leagues: [26212],
        seasons: [2018],
        total_points: 1711
      },
      {
        name: 'BG Litzendorf 2',
        players_count: 47,
        leagues: [26212],
        seasons: [2018],
        total_points: 1593
      },
      {
        name: 'BG Litzendorf 3',
        players_count: 32,
        leagues: [26212],
        seasons: [2018],
        total_points: 1181
      },
      {
        name: 'SV Pettstadt',
        players_count: 10,
        leagues: [26212],
        seasons: [2018],
        total_points: 1876
      },
      {
        name: 'TS Kronach',
        players_count: 11,
        leagues: [26212],
        seasons: [2018],
        total_points: 1654
      }
      // More teams would be loaded from API
    ]
  } catch (error) {
    console.error('Error loading teams:', error)
  } finally {
    loading.value = false
  }
}

// Computed properties
const uniqueLeagues = computed(() => {
  const leagues = new Set()
  teamsData.value.forEach(team => {
    team.leagues.forEach(league => leagues.add(league))
  })
  return Array.from(leagues).sort()
})

const uniqueSeasons = computed(() => {
  const seasons = new Set()
  teamsData.value.forEach(team => {
    team.seasons.forEach(season => seasons.add(season))
  })
  return Array.from(seasons).sort()
})

const filteredTeams = computed(() => {
  let filtered = teamsData.value.filter(team => {
    const matchesSearch = !searchTerm.value || 
      team.name.toLowerCase().includes(searchTerm.value.toLowerCase())
    
    const matchesLeague = !selectedLeague.value || 
      team.leagues.includes(parseInt(selectedLeague.value))
    
    const matchesSeason = !selectedSeason.value || 
      team.seasons.includes(parseInt(selectedSeason.value))
    
    return matchesSearch && matchesLeague && matchesSeason
  })

  // Sort teams
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'players':
        return b.players_count - a.players_count
      case 'name':
        return a.name.localeCompare(b.name)
      case 'points':
      default:
        return b.total_points - a.total_points
    }
  })

  // Pagination
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filtered.slice(start, end)
})

const totalPages = computed(() => {
  const totalFiltered = teamsData.value.filter(team => {
    const matchesSearch = !searchTerm.value || 
      team.name.toLowerCase().includes(searchTerm.value.toLowerCase())
    const matchesLeague = !selectedLeague.value || 
      team.leagues.includes(parseInt(selectedLeague.value))
    const matchesSeason = !selectedSeason.value || 
      team.seasons.includes(parseInt(selectedSeason.value))
    return matchesSearch && matchesLeague && matchesSeason
  }).length
  
  return Math.ceil(totalFiltered / itemsPerPage)
})

// Helper functions
const getTeamInitials = (teamName) => {
  return teamName
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .substring(0, 3)
    .toUpperCase()
}

const formatNumber = (num) => {
  return new Intl.NumberFormat('de-DE').format(num)
}

const hasOrganizationInfo = (teamName) => {
  return teamName.toLowerCase().includes('litzendorf')
}

// Navigation functions
const viewTeam = (teamName, leagueId, seasonId) => {
  const encodedName = encodeURIComponent(teamName)
  navigateTo(`/teams/${encodedName}?league=${leagueId}&season=${seasonId}`)
}

const viewTeamRoster = (team) => {
  const encodedName = encodeURIComponent(team.name)
  navigateTo(`/teams/${encodedName}?league=${team.leagues[0]}&season=${team.seasons[0]}#roster`)
}

const viewOrganization = (orgName) => {
  const encodedName = encodeURIComponent(orgName)
  navigateTo(`/teams/${encodedName}?tab=organization`)
}

// Export functions
const exportAllTeams = (format) => {
  const teamsData = {
    summary: {
      total_teams: filteredTeams.value.length,
      total_organizations: uniqueOrganizations.value.length,
      leagues: uniqueLeagues.value,
      export_date: new Date().toISOString()
    },
    teams: filteredTeams.value.map(team => ({
      name: team.name,
      leagues: team.leagues,
      seasons: team.seasons,
      player_count: team.playerCount,
      total_points: team.totalPoints,
      avg_ppg: team.avgPPG,
      organization: team.organization
    })),
    organizations: uniqueOrganizations.value.map(org => ({
      name: org,
      teams: filteredTeams.value.filter(team => team.organization === org).length
    }))
  }
  
  const timestamp = new Date().toISOString().slice(0, 10)
  const filename = `basketball_teams_${timestamp}`
  
  switch (format) {
    case 'csv':
      exportTeamsAsCSV(teamsData, filename)
      break
    case 'json':
      exportTeamsAsJSON(teamsData, filename)
      break
    case 'pdf':
      exportTeamsAsPDF(teamsData, filename)
      break
  }
}

const exportTeamsAsCSV = (data, filename) => {
  const headers = ['Team', 'Liga', 'Saison', 'Spieler', 'Punkte', 'PPG', 'Organisation']
  const rows = data.teams.map(team => [
    team.name,
    team.leagues.join('; '),
    team.seasons.join('; '),
    team.player_count,
    team.total_points,
    team.avg_ppg,
    team.organization
  ])
  
  const csvContent = [headers, ...rows]
    .map(row => row.map(field => `"${field}"`).join(','))
    .join('\n')
  
  downloadFile(csvContent, `${filename}.csv`, 'text/csv')
}

const exportTeamsAsJSON = (data, filename) => {
  const jsonContent = JSON.stringify(data, null, 2)
  downloadFile(jsonContent, `${filename}.json`, 'application/json')
}

const exportTeamsAsPDF = (data, filename) => {
  const pdfContent = `
Basketball Teams Export
Erstellt am: ${new Date().toLocaleDateString('de-DE')}

Zusammenfassung:
- Anzahl Teams: ${data.summary.total_teams}
- Anzahl Organisationen: ${data.summary.total_organizations}
- Ligen: ${data.summary.leagues.join(', ')}

Teams:
${data.teams.map(team => 
  `${team.name} (${team.organization}) - Liga ${team.leagues.join(', ')} - ${team.player_count} Spieler - ${team.avg_ppg} PPG`
).join('\n')}

Organisationen:
${data.organizations.map(org => 
  `${org.name}: ${org.teams} Teams`
).join('\n')}
  `
  downloadFile(pdfContent, `${filename}.txt`, 'text/plain')
}

const downloadFile = (content, filename, mimeType) => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// Lifecycle
onMounted(() => {
  loadTeamsData()
})
</script>
