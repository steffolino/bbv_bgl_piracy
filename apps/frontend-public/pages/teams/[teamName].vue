<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Team Header -->
    <div class="hero bg-gradient-to-r from-primary to-secondary text-primary-content mb-8 rounded-lg">
      <div class="hero-content text-center w-full">
        <div class="w-full">
          <!-- Share Button - Top Right -->
          <div class="flex justify-end mb-4">
            <div class="dropdown dropdown-end">
              <ShareButton 
                :title="`${teamDetails?.team_name} - Basketball Team`"
                :description="`Liga ${teamDetails?.league_id} Team mit ${teamDetails?.roster_size} Spielern. Entdecke Statistiken und Spielerprofile.`"
                :hashtags="['Basketball', 'BBL', 'Team', teamDetails?.team_name?.replace(/\s+/g, '') || '']"
                :show-export="true"
                @export="exportTeamData"
                class="btn btn-ghost btn-sm text-primary-content"
              />
            </div>
          </div>
          
          <div class="flex items-center justify-center gap-4 mb-4">
            <div class="avatar placeholder">
              <div class="bg-neutral-focus text-neutral-content rounded-full w-16">
                <span class="text-2xl">{{ teamInitials }}</span>
              </div>
            </div>
            <div>
              <h1 class="text-4xl font-bold">{{ teamDetails?.team_name }}</h1>
              <p class="text-lg opacity-90">Liga {{ teamDetails?.league_id }} • Saison {{ teamDetails?.season_id }}</p>
            </div>
          </div>
          
          <div class="stats stats-horizontal shadow">
            <div class="stat">
              <div class="stat-title text-primary-content opacity-70">Spieler</div>
              <div class="stat-value text-primary-content">{{ teamDetails?.roster_size }}</div>
            </div>
            <div class="stat">
              <div class="stat-title text-primary-content opacity-70">Gesamt Punkte</div>
              <div class="stat-value text-primary-content">{{ teamDetails?.total_points }}</div>
            </div>
            <div class="stat">
              <div class="stat-title text-primary-content opacity-70">Ø PPG</div>
              <div class="stat-value text-primary-content">{{ teamDetails?.avg_ppg }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs tabs-bordered mb-6">
      <a class="tab tab-active" :class="{ 'tab-active': activeTab === 'roster' }" @click="activeTab = 'roster'">
        👥 Kader
      </a>
      <a class="tab" :class="{ 'tab-active': activeTab === 'stats' }" @click="activeTab = 'stats'">
        📊 Statistiken
      </a>
      <a class="tab" :class="{ 'tab-active': activeTab === 'organization' }" @click="activeTab = 'organization'">
        🏢 Verein
      </a>
      <a class="tab" :class="{ 'tab-active': activeTab === 'league' }" @click="activeTab = 'league'">
        🏆 Liga
      </a>
    </div>

    <!-- Roster Tab -->
    <div v-if="activeTab === 'roster'" class="space-y-6">
      <!-- No Players Found Message -->
      <div v-if="teamDetails?.roster_size === 0" class="card bg-warning shadow-xl">
        <div class="card-body text-center">
          <h2 class="card-title justify-center">⚠️ Keine Spielerdaten gefunden</h2>
          <p class="mb-4">Für <strong>{{ teamDetails?.team_name }}</strong> wurden in Liga {{ teamDetails?.league_id }}, Saison {{ teamDetails?.season_id }} keine Spielerdaten gefunden.</p>
          <div class="alert alert-info">
            <div>
              <strong>Mögliche Gründe:</strong>
              <ul class="list-disc list-inside mt-2">
                <li>Team ist in einer anderen Liga/Saison aktiv</li>
                <li>Teamname stimmt nicht exakt überein</li>
                <li>Daten für diese Liga/Saison noch nicht verfügbar</li>
              </ul>
            </div>
          </div>
          <div class="mt-4">
            <a :href="`http://localhost:5001/api/debug/teams?league_id=${teamDetails?.league_id}&season_id=${teamDetails?.season_id}`" 
               target="_blank" class="btn btn-sm btn-outline">
              🔍 Debug: Verfügbare Teams anzeigen
            </a>
          </div>
        </div>
      </div>

      <!-- Top Performers -->
      <div v-else class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">🌟 Top Performer</h2>
          
          <!-- Debug info -->
          <div class="alert alert-info mb-4" v-if="teamDetails">
            <div class="text-xs">
              <strong>Debug Info:</strong><br>
              Roster Size: {{ teamDetails.roster_size }}<br>
              Raw Players Array Length: {{ teamDetails.players?.length || 0 }}<br>
              Consolidated Roster Length: {{ sortedRoster.length }}<br>
              Top Scorers Length: {{ teamDetails.top_scorers?.length || 0 }}<br>
              <br>
              <strong>Name Analysis:</strong><br>
              {{ analyzePlayerNames() }}<br>
              <br>
              <strong>Games Count Analysis:</strong><br>
              {{ analyzeGamesCount() }}<br>
              <br>
              <strong>Raw teamDetails keys:</strong> {{ Object.keys(teamDetails || {}).join(', ') }}<br>
              <br>
              <strong>Sample consolidated player (if exists):</strong><br>
              {{ sortedRoster?.[0] ? JSON.stringify(sortedRoster[0], null, 2) : 'No players found' }}<br>
              <br>
              <strong>Sample original player data:</strong><br>
              {{ teamDetails.players?.[0] ? JSON.stringify(teamDetails.players[0], null, 2) : 'No raw players found' }}
            </div>
          </div>
          
          <!-- Show top scorers if available, otherwise show message -->
          <div v-if="teamDetails?.top_scorers?.length > 0" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <div v-for="(player, index) in teamDetails.top_scorers.slice(0, 5)" :key="player.name" 
                 class="card bg-gradient-to-br from-primary to-secondary text-primary-content">
              <div class="card-body p-4 text-center">
                <div class="badge badge-warning mb-2">#{{ index + 1 }}</div>
                <h3 class="font-bold text-sm">{{ player.name }}</h3>
                <div class="text-2xl font-bold">{{ player.points }}</div>
                <div class="text-xs opacity-70">Punkte</div>
                <div class="text-sm">{{ getPlayerPPG(player) }} PPG</div>
              </div>
            </div>
          </div>
          
          <!-- Fallback: Generate top scorers from players array -->
          <div v-else-if="sortedRoster.length > 0" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <div v-for="(player, index) in sortedRoster.slice(0, 5)" :key="player.name" 
                 class="card bg-gradient-to-br from-primary to-secondary text-primary-content">
              <div class="card-body p-4 text-center">
                <div class="badge badge-warning mb-2">#{{ index + 1 }}</div>
                <h3 class="font-bold text-sm">{{ player.name }}</h3>
                <div class="text-2xl font-bold">{{ player.points }}</div>
                <div class="text-xs opacity-70">Punkte</div>
                <div class="text-sm">{{ getPlayerPPG(player) }} PPG</div>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-8">
            <p class="text-gray-500">Keine Spielerdaten für Top Performer verfügbar</p>
          </div>
        </div>
      </div>

      <!-- Full Roster -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <div class="flex justify-between items-center mb-4">
            <h2 class="card-title">👥 Vollständiger Kader</h2>
            <div class="flex gap-2">
              <button @click="exportRoster" class="btn btn-primary btn-sm">
                📊 Kader exportieren
              </button>
              <button @click="generateTeamCards" class="btn btn-secondary btn-sm">
                🏀 Team Karten
              </button>
            </div>
          </div>
          
          <div class="overflow-x-auto">
            <table class="table table-xs table-zebra w-full">
              <thead>
                <tr>
                  <th @click="sortBy('name')" class="cursor-pointer hover:bg-base-200 sticky left-0 bg-base-100 z-10 min-w-[200px]">
                    {{ t('teams.roster.player') }}
                    <span v-if="sortKey === 'name'" class="text-xs ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th @click="sortBy('points')" class="cursor-pointer hover:bg-base-200">
                    {{ t('teams.roster.points') }}
                    <span v-if="sortKey === 'points'" class="text-xs ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th @click="sortBy('games')" class="cursor-pointer hover:bg-base-200">
                    {{ t('teams.roster.games') }}
                    <span v-if="sortKey === 'games'" class="text-xs ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th @click="sortBy('ppg')" class="cursor-pointer hover:bg-base-200">
                    {{ t('teams.roster.ppg') }}
                    <span v-if="sortKey === 'ppg'" class="text-xs ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th @click="sortBy('3pt')" class="cursor-pointer hover:bg-base-200">
                    {{ t('teams.roster.threePtPerGame') }}
                    <span v-if="sortKey === '3pt'" class="text-xs ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th @click="sortBy('ft%')" class="cursor-pointer hover:bg-base-200">
                    {{ t('teams.roster.freeThrowPercentage') }}
                    <span v-if="sortKey === 'ft%'" class="text-xs ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th @click="sortBy('fta')" class="cursor-pointer hover:bg-base-200">
                    {{ t('teams.roster.freeThrowAttempts') }}
                    <span v-if="sortKey === 'fta'" class="text-xs ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th @click="sortBy('ftm')" class="cursor-pointer hover:bg-base-200">
                    {{ t('teams.roster.freeThrowMade') }}
                    <span v-if="sortKey === 'ftm'" class="text-xs ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th @click="sortBy('ftaPerGame')" class="cursor-pointer hover:bg-base-200">
                    FTA/G
                    <span v-if="sortKey === 'ftaPerGame'" class="text-xs ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th @click="sortBy('ftmPerGame')" class="cursor-pointer hover:bg-base-200">
                    FTM/G
                    <span v-if="sortKey === 'ftmPerGame'" class="text-xs ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th @click="sortBy('impact')" class="cursor-pointer hover:bg-base-200">
                    {{ t('teams.roster.impact') }}
                    <span v-if="sortKey === 'impact'" class="text-xs ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </th>
                  <th>{{ t('teams.roster.actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="player in sortedRoster" :key="player.name">
                  <td class="sticky left-0 bg-base-100 z-10 min-w-[200px]">
                    <div class="flex items-center gap-2">
                      <div class="avatar placeholder">
                        <div class="bg-neutral-focus text-neutral-content rounded-full w-8">
                          <span class="text-xs">{{ getPlayerInitials(player.name) }}</span>
                        </div>
                      </div>
                      <div class="font-medium">
                        <div class="font-bold">{{ player.first_name }} {{ player.last_name }}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="badge badge-primary">{{ player.points }}</div>
                  </td>
                  <td>{{ getValidatedGames(player) }}</td>
                  <td>
                    <div class="font-bold">{{ getPlayerPPG(player) }}</div>
                  </td>
                  <td>
                    <div class="font-bold">{{ get3PunkteProSpiel(player) }}</div>
                  </td>
                  <td>
                    <div class="badge badge-info">{{ getFreiwurfProzent(player) }}%</div>
                  </td>
                  <td>{{ getFreiwurfVersuche(player) }}</td>
                  <td>{{ getFreiwurfGetroffen(player) }}</td>
                  <td>{{ getFreiwurfVersucheProSpiel(player) }}</td>
                  <td>{{ getFreiwurfGetroffenProSpiel(player) }}</td>
                  <td>
                    <div class="badge badge-info">{{ player.advanced_stats?.IMPACT || 'N/A' }}</div>
                  </td>
                  <td>
                    <div class="dropdown dropdown-end">
                      <div tabindex="0" role="button" class="btn btn-xs btn-ghost">⋯</div>
                      <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-40">
                        <li><a @click="viewPlayerProfile(player)">👤 {{ t('players.table.viewProfile') }}</a></li>
                        <li><a @click="generatePlayerCard(player)">🏀 Karte</a></li>
                        <li><a @click="comparePlayer(player)">⚖️ Vergleichen</a></li>
                      </ul>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Team Statistics Tab -->
    <div v-if="activeTab === 'stats'" class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Team Performance Metrics -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <h2 class="card-title">📈 Team Performance</h2>
            <div class="stats stats-vertical shadow">
              <div class="stat">
                <div class="stat-title">Gesamt Punkte</div>
                <div class="stat-value text-primary">{{ teamDetails?.total_points }}</div>
                <div class="stat-desc">über {{ teamDetails?.roster_size }} Spieler</div>
              </div>
              <div class="stat">
                <div class="stat-title">Durchschnitt PPG</div>
                <div class="stat-value text-secondary">{{ teamDetails?.avg_ppg }}</div>
                <div class="stat-desc">pro Spieler</div>
              </div>
              <div class="stat">
                <div class="stat-title">Top Scorer</div>
                <div class="stat-value text-accent">{{ teamDetails?.top_scorers?.[0]?.points }}</div>
                <div class="stat-desc">{{ teamDetails?.top_scorers?.[0]?.name }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Category Distribution -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <h2 class="card-title">🎯 Kategorie Verteilung</h2>
            <div class="space-y-3">
              <div v-for="(count, category) in categoryDistribution" :key="category" 
                   class="flex justify-between items-center">
                <div class="flex items-center gap-2">
                  <div class="badge badge-sm" :class="getCategoryBadgeClass(category)">
                    {{ getCategoryShortName(category) }}
                  </div>
                  <span class="text-sm">{{ getCategoryDisplayName(category) }}</span>
                </div>
                <div class="badge badge-outline">{{ count }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Chart Placeholder -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">📊 Leistungsverteilung</h2>
          <div class="bg-base-200 p-8 rounded-lg text-center">
            <p class="text-lg opacity-50">Interaktive Charts kommen bald...</p>
            <p class="text-sm opacity-30">PPG Verteilung, Impact Scores, etc.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Organization Tab -->
    <div v-if="activeTab === 'organization'" class="space-y-6">
      <div v-if="teamDetails?.organization?.website" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Organization Info -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <h2 class="card-title">🏢 Vereinsinformationen</h2>
            <div class="space-y-4">
              <div>
                <h3 class="font-bold">{{ teamDetails.organization.full_name }}</h3>
                <p class="text-sm opacity-70">Gegründet {{ teamDetails.organization.founded }}</p>
              </div>
              
              <div class="divider"></div>
              
              <div>
                <h4 class="font-medium mb-2">📍 Adresse</h4>
                <p class="text-sm">{{ teamDetails.organization.address.street }}</p>
                <p class="text-sm">{{ teamDetails.organization.address.city }}</p>
              </div>
              
              <div>
                <h4 class="font-medium mb-2">📞 Kontakt</h4>
                <p class="text-sm">📧 {{ teamDetails.organization.contact.email }}</p>
                <p class="text-sm">📱 {{ teamDetails.organization.contact.phone }}</p>
              </div>
              
              <div>
                <h4 class="font-medium mb-2">👥 Verantwortliche</h4>
                <p class="text-sm">Präsident: {{ teamDetails.organization.contact.president }}</p>
                <p class="text-sm">Trainer: {{ teamDetails.organization.contact.coach }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Facilities & Teams -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <h2 class="card-title">🏟️ Einrichtungen & Teams</h2>
            <div class="space-y-4">
              <div>
                <h4 class="font-medium mb-2">🏠 Heimhalle</h4>
                <p class="text-sm font-medium">{{ teamDetails.organization.facilities.home_venue }}</p>
                <p class="text-sm opacity-70">Kapazität: {{ teamDetails.organization.facilities.capacity }} Plätze</p>
                <p class="text-sm opacity-70">{{ teamDetails.organization.facilities.address }}</p>
              </div>
              
              <div class="divider"></div>
              
              <div>
                <h4 class="font-medium mb-2">🏀 Mannschaften</h4>
                <div class="stats stats-horizontal shadow">
                  <div class="stat">
                    <div class="stat-title">Gesamt</div>
                    <div class="stat-value text-sm">{{ teamDetails.organization.teams.total_teams }}</div>
                  </div>
                  <div class="stat">
                    <div class="stat-title">Jugend</div>
                    <div class="stat-value text-sm">{{ teamDetails.organization.teams.youth_teams }}</div>
                  </div>
                  <div class="stat">
                    <div class="stat-title">Senioren</div>
                    <div class="stat-value text-sm">{{ teamDetails.organization.teams.senior_teams }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Website & Social Media -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <h2 class="card-title">🌐 Online Präsenz</h2>
            <div class="space-y-3">
              <a :href="teamDetails.organization.website" target="_blank" 
                 class="btn btn-primary btn-block">
                🌐 Website besuchen
              </a>
              
              <div class="grid grid-cols-1 gap-2">
                <a :href="teamDetails.organization.social_media.facebook" target="_blank" 
                   class="btn btn-outline btn-sm">
                  📘 Facebook
                </a>
                <a :href="`https://instagram.com/${teamDetails.organization.social_media.instagram.replace('@', '')}`" 
                   target="_blank" class="btn btn-outline btn-sm">
                  📷 Instagram
                </a>
                <a :href="`https://twitter.com/${teamDetails.organization.social_media.twitter.replace('@', '')}`" 
                   target="_blank" class="btn btn-outline btn-sm">
                  🐦 Twitter
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Achievements -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <h2 class="card-title">🏆 Erfolge</h2>
            <div class="space-y-2">
              <div v-for="achievement in teamDetails.organization.achievements" :key="achievement"
                   class="badge badge-success badge-lg w-full justify-start">
                🏆 {{ achievement }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Generic team info for teams with no organization data -->
      <div v-else class="card bg-base-100 shadow-xl">
        <div class="card-body text-center">
          <h2 class="card-title justify-center">🏢 Vereinsinformationen</h2>
          
          <!-- Show message based on whether we have player data -->
          <div v-if="teamDetails?.roster_size === 0">
            <p class="text-warning font-bold mb-2">⚠️ Team nicht in aktueller Liga/Saison gefunden</p>
            <p class="opacity-70 mb-4">{{ teamDetails?.team_name }} wurde in Liga {{ teamDetails?.league_id }}, Saison {{ teamDetails?.season_id }} nicht gefunden.</p>
            
            <div class="bg-base-200 p-4 rounded-lg">
              <p class="text-sm mb-2"><strong>Debugging-Hilfe:</strong></p>
              <a :href="`http://localhost:5001/api/debug/teams?league_id=${teamDetails?.league_id}&season_id=${teamDetails?.season_id}`" 
                 target="_blank" class="btn btn-xs btn-primary mb-2">
                🔍 Alle Teams in Liga {{ teamDetails?.league_id }} ({{ teamDetails?.season_id }})
              </a>
              <br>
              <a href="http://localhost:5001/api/debug/teams" target="_blank" class="btn btn-xs btn-secondary">
                🏀 Alle Litzendorf-Varianten anzeigen
              </a>
            </div>
          </div>
          
          <div v-else>
            <p class="opacity-50">Detaillierte Vereinsinformationen sind derzeit nur für BG Litzendorf verfügbar.</p>
            <p class="text-sm opacity-30">Weitere Vereine werden in zukünftigen Updates hinzugefügt.</p>
          </div>
          
          <div class="mt-4">
            <h3 class="font-bold">{{ teamDetails?.team_name }}</h3>
            <p class="text-sm opacity-70">Liga {{ teamDetails?.league_id }} • Saison {{ teamDetails?.season_id }}</p>
            <p class="text-sm opacity-50">{{ teamDetails?.roster_size }} Spieler gefunden</p>
          </div>
        </div>
      </div>
    </div>

    <!-- League Tab -->
    <div v-if="activeTab === 'league'" class="space-y-6">
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">🏆 Liga Tabelle</h2>
          <p class="text-sm opacity-70 mb-4">Liga {{ teamDetails?.league_id }} • Saison {{ teamDetails?.season_id }}</p>
          
          <div v-if="leagueStandings" class="overflow-x-auto">
            <table class="table table-zebra">
              <thead>
                <tr>
                  <th>Platz</th>
                  <th>Mannschaft</th>
                  <th>Spieler</th>
                  <th>Ø PPG</th>
                  <th>Top Scorer</th>
                  <th>Aktionen</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="team in leagueStandings.standings" :key="team.team_name"
                    :class="{ 'bg-primary bg-opacity-20': team.team_name === teamDetails?.team_name }">
                  <td>
                    <div class="badge badge-primary">{{ team.rank }}</div>
                  </td>
                  <td>
                    <div class="font-medium">{{ team.team_name }}</div>
                  </td>
                  <td>{{ team.players.length }}</td>
                  <td>
                    <div class="font-bold">{{ team.avg_ppg.toFixed(1) }}</div>
                  </td>
                  <td>
                    <div class="text-sm">
                      {{ team.top_scorer?.name }}
                      <div class="badge badge-xs badge-outline">{{ team.top_scorer?.points }} pts</div>
                    </div>
                  </td>
                  <td>
                    <button @click="viewTeam(team.team_name)" class="btn btn-xs btn-outline">
                      Team anzeigen
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Enable translations
const { t } = useI18n()

const props = defineProps({
  teamName: String,
  leagueId: Number,
  seasonId: Number
})

const activeTab = ref('roster')
const teamDetails = ref(null)
const leagueStandings = ref(null)
const loading = ref(true)

// Sorting state
const sortKey = ref('')
const sortOrder = ref('asc')

// Get the correct default values based on what's actually in the dataset
const getDefaultLeagueId = () => {
  // Liga 26211 has BG Litzendorf 2, Liga 26212 has other teams
  const teamName = getDefaultTeamName()
  console.log('🏟️ Getting league for team:', teamName)
  
  if (teamName && teamName.includes('Litzendorf')) {
    console.log('🔧 Using Liga 26211 for Litzendorf team')
    return 26211  // Liga where Litzendorf actually exists
  }
  
  const defaultLeague = props.leagueId || 26212
  console.log('🔧 Using default Liga:', defaultLeague)
  return defaultLeague
}

const getDefaultTeamName = () => {
  // Use the actual URL parameter, but fix known issues
  const urlTeamName = props.teamName
  console.log('🏷️ URL team name:', urlTeamName)
  
  if (urlTeamName === 'BG Litzendorf') {
    console.log('🔧 Fixing team name: BG Litzendorf → BG Litzendorf 2')
    return 'BG Litzendorf 2'  // The actual team name in the dataset
  }
  
  return urlTeamName || 'BG Litzendorf 2'
}

const teamInitials = computed(() => {
  if (!teamDetails.value?.team_name) return 'T'
  return teamDetails.value.team_name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .substring(0, 3)
    .toUpperCase()
})

const sortedRoster = computed(() => {
  if (!teamDetails.value?.players) return []
  
  // Group players by name to consolidate multiple statistical entries
  const playerMap = new Map()
  
  teamDetails.value.players.forEach(player => {
    const firstName = (player.first_name || '').trim()
    const lastName = (player.last_name || player.surname || '').trim() // surname is the correct field!
    const fullName = `${firstName} ${lastName}`.trim()
    
    // Debug: check for name issues
    if (firstName === lastName && firstName !== '') {
      console.warn(`Potential name duplication for player: ${firstName} ${lastName}`)
    }
    
    if (playerMap.has(fullName)) {
      // Merge data for existing player
      const existing = playerMap.get(fullName)
      
      // Update names with cleaned versions
      existing.first_name = firstName
      existing.last_name = lastName
      existing.name = fullName
      
      // For different categories, store the specific stats separately
      if (player.endpoint === 'statBesteWerferArchiv') {
        // Best scorers - use this for main points and games (most reliable for actual games played)
        existing.points = Math.max(parseFloat(existing.points) || 0, parseFloat(player.points) || 0)
        // Only update games from the main scoring category, not from FT/3PT categories
        if (!existing.gamesFromMainCategory) {
          existing.games = parseFloat(player.games) || 0
          existing.gamesFromMainCategory = true
        }
      } else if (player.endpoint === 'statBesteFreiWerferArchiv') {
        // Free throw shooters - store free throw specific data
        existing.freeThrow = {
          points: parseFloat(player.points) || 0, // FT made
          games: parseFloat(player.games) || 0,   // FT attempts
          average: parseFloat(player.average) || 0 // FT percentage
        }
      } else if (player.endpoint === 'statBeste3erWerferArchiv') {
        // 3-point shooters - store 3-point specific data
        existing.threePoint = {
          points: parseFloat(player.points) || 0, // 3PT made
          games: parseFloat(player.games) || 0,   // total games
          average: parseFloat(player.average) || 0 // 3PT average per game
        }
      }
      
      // Merge advanced stats if available
      if (player.advanced_stats) {
        existing.advanced_stats = { 
          ...existing.advanced_stats, 
          ...player.advanced_stats 
        }
        
        // For numerical stats, take the maximum value
        Object.keys(player.advanced_stats).forEach(key => {
          const existingVal = parseFloat(existing.advanced_stats[key]) || 0
          const newVal = parseFloat(player.advanced_stats[key]) || 0
          if (newVal > existingVal) {
            existing.advanced_stats[key] = newVal
          }
        })
      }
      
      // Keep track of all endpoints/categories this player appears in
      if (!existing.categories) existing.categories = []
      if (player.endpoint && !existing.categories.includes(player.endpoint)) {
        existing.categories.push(player.endpoint)
      }
    } else {
      // Add new player
      const newPlayer = {
        name: fullName,
        first_name: firstName,
        last_name: lastName,
        points: parseFloat(player.points) || 0,
        games: parseFloat(player.games) || 0,
        average: parseFloat(player.average) || 0,
        advanced_stats: player.advanced_stats || {},
        endpoint: player.endpoint,
        categories: player.endpoint ? [player.endpoint] : [],
        extracted_at: player.extracted_at,
        // Keep original player data for reference
        _original: player
      }
      
      // Set flag if this is from main scoring category (most reliable for games count)
      if (player.endpoint === 'statBesteWerferArchiv') {
        newPlayer.gamesFromMainCategory = true
      }
      
      // Initialize category-specific data based on endpoint
      if (player.endpoint === 'statBesteFreiWerferArchiv') {
        newPlayer.freeThrow = {
          points: parseFloat(player.points) || 0,
          games: parseFloat(player.games) || 0,
          average: parseFloat(player.average) || 0
        }
      } else if (player.endpoint === 'statBeste3erWerferArchiv') {
        newPlayer.threePoint = {
          points: parseFloat(player.points) || 0,
          games: parseFloat(player.games) || 0,
          average: parseFloat(player.average) || 0
        }
      }
      
      playerMap.set(fullName, newPlayer)
    }
  })
  
  // Convert map to array
  let players = Array.from(playerMap.values())
  
  // Apply sorting if specified
  if (sortKey.value) {
    players = players.sort((a, b) => {
      let aVal, bVal
      
      switch (sortKey.value) {
        case 'name':
          aVal = a.name.toLowerCase()
          bVal = b.name.toLowerCase()
          break
        case 'points':
          aVal = a.points
          bVal = b.points
          break
        case 'games':
          aVal = getValidatedGames(a)
          bVal = getValidatedGames(b)
          break
        case 'ppg':
          aVal = parseFloat(getPlayerPPG(a))
          bVal = parseFloat(getPlayerPPG(b))
          break
        case '3pt':
          aVal = parseFloat(get3PunkteProSpiel(a))
          bVal = parseFloat(get3PunkteProSpiel(b))
          break
        case 'ft%':
          aVal = parseFloat(getFreiwurfProzent(a))
          bVal = parseFloat(getFreiwurfProzent(b))
          break
        case 'fta':
          aVal = getFreiwurfVersuche(a)
          bVal = getFreiwurfVersuche(b)
          break
        case 'ftm':
          aVal = getFreiwurfGetroffen(a)
          bVal = getFreiwurfGetroffen(b)
          break
        case 'ftaPerGame':
          aVal = parseFloat(getFreiwurfVersucheProSpiel(a))
          bVal = parseFloat(getFreiwurfVersucheProSpiel(b))
          break
        case 'ftmPerGame':
          aVal = parseFloat(getFreiwurfGetroffenProSpiel(a))
          bVal = parseFloat(getFreiwurfGetroffenProSpiel(b))
          break
        case 'impact':
          aVal = parseFloat(a.advanced_stats?.IMPACT) || 0
          bVal = parseFloat(b.advanced_stats?.IMPACT) || 0
          break
        default:
          return 0
      }
      
      if (sortOrder.value === 'asc') {
        return aVal < bVal ? -1 : aVal > bVal ? 1 : 0
      } else {
        return aVal > bVal ? -1 : aVal < bVal ? 1 : 0
      }
    })
  } else {
    // Default sort by points descending
    players = players.sort((a, b) => b.points - a.points)
  }
  
  return players
})

const categoryDistribution = computed(() => {
  if (!teamDetails.value?.players) return {}
  const distribution = {}
  teamDetails.value.players.forEach(player => {
    const category = player.endpoint || 'unknown'
    distribution[category] = (distribution[category] || 0) + 1
  })
  return distribution
})

// Table columns configuration
const rosterColumns = computed(() => [
  { key: 'player', label: t('teams.roster.player'), sortable: true },
  { key: 'points', label: t('teams.roster.points'), sortable: true, type: 'number' },
  { key: 'games', label: t('teams.roster.games'), sortable: true, type: 'number' },
  { key: 'ppg', label: t('teams.roster.ppg'), sortable: true, type: 'number' },
  { key: 'threePtPerGame', label: t('teams.roster.threePtPerGame'), sortable: true, type: 'number' },
  { key: 'freeThrowPercentage', label: t('teams.roster.freeThrowPercentage'), sortable: true, type: 'number' },
  { key: 'freeThrowAttempts', label: t('teams.roster.freeThrowAttempts'), sortable: true, type: 'number' },
  { key: 'freeThrowMade', label: t('teams.roster.freeThrowMade'), sortable: true, type: 'number' },
  { key: 'ftaPerGame', label: 'FTA/G', sortable: true, type: 'number' },
  { key: 'ftmPerGame', label: 'FTM/G', sortable: true, type: 'number' },
  { key: 'impact', label: t('teams.roster.impact'), sortable: true, type: 'number' },
  { key: 'actions', label: t('teams.roster.actions'), sortable: false }
])

// Sorting function
const sortBy = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'desc' // Default to descending for most stats
  }
}

// Real API data loading functions
const loadTeamDetails = async () => {
  try {
    // Use corrected team name and league ID
    const teamName = getDefaultTeamName()
    const leagueId = getDefaultLeagueId()
    const seasonId = props.seasonId || 2018
    
    console.log(`🔍 Loading team data for: ${teamName}, League: ${leagueId}, Season: ${seasonId}`)
    
    const apiUrl = `http://localhost:5001/api/teams/${encodeURIComponent(teamName)}?league_id=${leagueId}&season_id=${seasonId}`
    console.log('📡 API URL:', apiUrl)
    
    const response = await fetch(apiUrl)
    console.log('📡 Response status:', response.status)
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }
    
    const apiData = await response.json()
    console.log('📦 Raw API response:', apiData)
    console.log('📦 API response keys:', Object.keys(apiData))
    console.log('📦 Players array:', apiData.players?.length, 'players')
    console.log('📦 Sample player:', apiData.players?.[0])
    console.log('📦 Top scorers:', apiData.top_scorers?.length, 'top scorers')
    
    teamDetails.value = apiData
    
    // Log successful API call
    console.log('✅ Real team data loaded from basketball API:', teamDetails.value.team_name)
    console.log('👥 Players found:', teamDetails.value.roster_size)
    console.log('🏢 Organization data:', teamDetails.value.organization !== null)
    
  } catch (error) {
    console.error('❌ Failed to load real team data from API:', error)
    // Fallback to basic structure if API fails
    teamDetails.value = {
      team_name: getDefaultTeamName(),
      league_id: getDefaultLeagueId(),
      season_id: props.seasonId || 2018,
      roster_size: 0,
      total_points: 0,
      avg_ppg: 0,
      players: [],
      top_scorers: [],
      organization: null
    }
    console.log('🔄 Using fallback data structure')
  }
}

const loadLeagueStandings = async () => {
  try {
    const leagueId = getDefaultLeagueId()
    const seasonId = props.seasonId || 2018
    
    console.log(`🏆 Loading league standings for League: ${leagueId}, Season: ${seasonId}`)
    
    const apiUrl = `http://localhost:5001/api/leagues/${leagueId}/standings?season_id=${seasonId}`
    console.log('📡 League API URL:', apiUrl)
    
    const response = await fetch(apiUrl)
    console.log('📡 League response status:', response.status)
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }
    
    const apiData = await response.json()
    console.log('📦 Raw league API response:', apiData)
    
    leagueStandings.value = apiData
    
    console.log('✅ Real league standings loaded from basketball API')
    
  } catch (error) {
    console.error('❌ Failed to load real league standings from API:', error)
    // Fallback to empty structure if API fails
    leagueStandings.value = {
      league_id: getDefaultLeagueId(),
      season_id: props.seasonId || 2018,
      teams_count: 0,
      standings: []
    }
    console.log('🔄 Using fallback league data structure')
  }
}

// Helper functions
const getValidatedGames = (player) => {
  let games = parseFloat(player.games) || 0
  
  // Cap games at reasonable basketball season length
  if (games > 35) {
    games = 35
  }
  
  return games
}

const getPlayerPPG = (player) => {
  const points = parseFloat(player.points) || 0
  let games = parseFloat(player.games) || 0
  
  // Validate games count - basketball seasons typically have 20-35 games max
  if (games > 35) {
    console.warn(`Player ${player.name} has suspicious games count: ${games}. Capping at 35.`)
    games = Math.min(games, 35)
  }
  
  if (games === 0) return '0.0'
  return (points / games).toFixed(1)
}

// 3P/S = 3-Punkte pro Spiel
const get3PunkteProSpiel = (player) => {
  const games = parseFloat(player.games) || 0
  if (games === 0) return '0.0'
  
  // Check if this player has 3-point specific data
  if (player.threePoint) {
    return (player.threePoint.points / Math.max(player.threePoint.games, 1)).toFixed(1)
  }
  
  // Fallback: check if player has 3-point category and use average field
  if (player.categories && player.categories.includes('statBeste3erWerferArchiv')) {
    return (parseFloat(player.average) || 0).toFixed(1)
  }
  
  return '0.0'
}

// FW% = Freiwurf Prozent
const getFreiwurfProzent = (player) => {
  // Check if this player has free throw specific data
  if (player.freeThrow) {
    // The average field already contains the FT percentage!
    return (player.freeThrow.average || 0).toFixed(1)
  }
  
  // Use the average field if available (already is percentage)
  if (player.categories && player.categories.includes('statBesteFreiWerferArchiv')) {
    const avg = parseFloat(player.average) || 0
    return avg.toFixed(1)
  }
  
  return '0.0'
}

// FWV = Freiwurf Versuche (Free Throw Attempts)
const getFreiwurfVersuche = (player) => {
  // Check if this player has free throw specific data
  if (player.freeThrow) {
    return player.freeThrow.games || 0  // In FT stats, "games" = attempts
  }
  
  return 0
}

// FWG = Freiwurf Getroffen (Free Throw Made)
const getFreiwurfGetroffen = (player) => {
  // Check if this player has free throw specific data
  if (player.freeThrow) {
    return player.freeThrow.points || 0  // In FT stats, "points" = made FTs
  }
  
  return 0
}

// FWV/S = Freiwurf Versuche pro Spiel
const getFreiwurfVersucheProSpiel = (player) => {
  const games = getValidatedGames(player)
  if (games === 0) return '0.0'
  
  const attempts = getFreiwurfVersuche(player)
  return (attempts / games).toFixed(1)
}

// FWG/S = Freiwurf Getroffen pro Spiel
const getFreiwurfGetroffenProSpiel = (player) => {
  const games = getValidatedGames(player)
  if (games === 0) return '0.0'
  
  const made = getFreiwurfGetroffen(player)
  return (made / games).toFixed(1)
}

const analyzePlayerNames = () => {
  if (!teamDetails.value?.players) return 'No players data'
  
  const nameIssues = []
  const uniqueNames = new Set()
  
  teamDetails.value.players.slice(0, 5).forEach((player, index) => {
    const firstName = (player.first_name || '').trim()
    const lastName = (player.last_name || player.surname || '').trim()
    const fullName = `${firstName} ${lastName}`.trim()
    
    nameIssues.push({
      index,
      firstName,
      lastName,
      surname: player.surname, // Show the actual field value
      last_name: player.last_name, // Show the actual field value
      fullName,
      endpoint: player.endpoint,
      isDuplicate: firstName === lastName && firstName !== ''
    })
    
    uniqueNames.add(fullName)
  })
  
  return JSON.stringify({
    sampleNames: nameIssues,
    totalRawPlayers: teamDetails.value.players.length,
    uniqueNamesCount: uniqueNames.size
  }, null, 2)
}

const analyzeGamesCount = () => {
  if (!teamDetails.value?.players) return 'No players data'
  
  const gamesAnalysis = {}
  teamDetails.value.players.forEach(player => {
    const endpoint = player.endpoint || 'unknown'
    if (!gamesAnalysis[endpoint]) {
      gamesAnalysis[endpoint] = {
        min: Infinity,
        max: -Infinity,
        avg: 0,
        count: 0,
        samples: []
      }
    }
    
    const games = parseFloat(player.games) || 0
    gamesAnalysis[endpoint].min = Math.min(gamesAnalysis[endpoint].min, games)
    gamesAnalysis[endpoint].max = Math.max(gamesAnalysis[endpoint].max, games)
    gamesAnalysis[endpoint].avg += games
    gamesAnalysis[endpoint].count++
    
    if (gamesAnalysis[endpoint].samples.length < 3) {
      gamesAnalysis[endpoint].samples.push(`${player.first_name} ${player.last_name}: ${games}`)
    }
  })
  
  // Calculate averages
  Object.keys(gamesAnalysis).forEach(key => {
    gamesAnalysis[key].avg = (gamesAnalysis[key].avg / gamesAnalysis[key].count).toFixed(1)
  })
  
  return JSON.stringify(gamesAnalysis, null, 2)
}

const getPlayerInitials = (name) => {
  return name.split(' ').map(n => n.charAt(0)).join('').substring(0, 2).toUpperCase()
}

const getCategoryBadgeClass = (category) => {
  switch (category) {
    case 'statBesteWerferArchiv': return 'badge-primary'
    case 'statBesteFreiWerferArchiv': return 'badge-secondary'
    case 'statBeste3erWerferArchiv': return 'badge-accent'
    default: return 'badge-neutral'
  }
}

const getCategoryShortName = (category) => {
  switch (category) {
    case 'statBesteWerferArchiv': return 'PTS'
    case 'statBesteFreiWerferArchiv': return 'FT'
    case 'statBeste3erWerferArchiv': return '3P'
    default: return '?'
  }
}

const getCategoryDisplayName = (category) => {
  switch (category) {
    case 'statBesteWerferArchiv': return 'Beste Werfer'
    case 'statBesteFreiWerferArchiv': return 'Freiwurf-Schützen'
    case 'statBeste3erWerferArchiv': return '3-Punkte-Schützen'
    default: return 'Unbekannt'
  }
}

// Action functions
const viewPlayerProfile = (player) => {
  alert(`Spielerprofil für ${player.name} wird implementiert...`)
  // TODO: Navigate to player profile page
  // navigateTo(`/players/${encodeURIComponent(player.name)}`)
}

const generatePlayerCard = (player) => {
  alert(`Spielerkarte für ${player.name} wird erstellt...`)
  // TODO: Implement player card generation
}

const comparePlayer = (player) => {
  alert(`Spielervergleich für ${player.name} wird implementiert...`)
  // TODO: Implement player comparison
}

const exportRoster = () => {
  if (!teamDetails.value?.players) {
    alert('Keine Spielerdaten zum Exportieren verfügbar')
    return
  }
  
  const exportData = {
    team: teamDetails.value.team_name,
    league: teamDetails.value.league_id,
    season: teamDetails.value.season_id,
    roster_size: teamDetails.value.roster_size,
    players: sortedRoster.value.map(player => ({
      name: player.name,
      first_name: player.first_name,
      last_name: player.last_name,
      points: player.points,
      games: getValidatedGames(player),
      ppg: getPlayerPPG(player),
      threePtPerGame: get3PunkteProSpiel(player),
      freeThrowPercentage: getFreiwurfProzent(player),
      freeThrowAttempts: getFreiwurfVersuche(player),
      freeThrowMade: getFreiwurfGetroffen(player),
      impact: player.advanced_stats?.IMPACT || 'N/A'
    }))
  }
  
  exportAsJSON(exportData, `${teamDetails.value.team_name}_roster`)
}

const generateTeamCards = () => {
  alert('Team Karten Funktion wird implementiert...')
  // TODO: Implement team cards generation
}

// Export team data in various formats
const exportTeamData = (format) => {
  const teamData = {
    team: teamDetails.value?.team_name,
    league: teamDetails.value?.league_id,
    season: teamDetails.value?.season_id,
    roster_size: teamDetails.value?.roster_size,
    players: teamDetails.value?.roster || [],
    statistics: teamDetails.value?.team_stats || {},
    organization: teamDetails.value?.organization || {}
  }
  
  const timestamp = new Date().toISOString().slice(0, 10)
  const filename = `${teamDetails.value?.team_name?.replace(/\s+/g, '_')}_${timestamp}`
  
  switch (format) {
    case 'csv':
      exportAsCSV(teamData, filename)
      break
    case 'json':
      exportAsJSON(teamData, filename)
      break
    case 'pdf':
      exportAsPDF(teamData, filename)
      break
  }
}

const exportAsCSV = (data, filename) => {
  const headers = ['Name', 'Position', 'Nummer', 'Punkte', 'Spiele', 'PPG']
  const rows = data.players.map(player => [
    player.name || '',
    player.position || '',
    player.number || '',
    player.total_points || 0,
    player.games_played || 0,
    player.avg_ppg || 0
  ])
  
  const csvContent = [headers, ...rows]
    .map(row => row.map(field => `"${field}"`).join(','))
    .join('\n')
  
  downloadFile(csvContent, `${filename}.csv`, 'text/csv')
}

const exportAsJSON = (data, filename) => {
  const jsonContent = JSON.stringify(data, null, 2)
  downloadFile(jsonContent, `${filename}.json`, 'application/json')
}

const exportAsPDF = (data, filename) => {
  // For now, create a simple text version
  const pdfContent = `
Team Report: ${data.team}
Liga: ${data.league}
Saison: ${data.season}
Anzahl Spieler: ${data.roster_size}

Kader:
${data.players.map(player => 
  `${player.name} (#${player.number || 'N/A'}) - ${player.position || 'N/A'} - ${player.avg_ppg || 0} PPG`
).join('\n')}

Erstellt am: ${new Date().toLocaleDateString('de-DE')}
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

const viewTeam = (teamName) => {
  // Navigate to team page
  navigateTo(`/teams/${encodeURIComponent(teamName)}`)
}

onMounted(async () => {
  loading.value = true
  
  // Just load the data directly without redirect logic
  console.log('� Component mounted, loading team data...')
  
  await Promise.all([
    loadTeamDetails(),
    loadLeagueStandings()
  ])
  loading.value = false
})
</script>
