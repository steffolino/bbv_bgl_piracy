<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Header Section -->
    <div class="text-center mb-8 relative">
      <!-- Share Button - Top Right -->
      <div class="absolute top-0 right-0">
        <ShareButton 
          title="Basketball Spieler Statistiken - BBV BGL"
          description="Entdecke echte Spielerdaten vom Deutschen Basketball Bund. Umfassende Statistiken, Spielerprofile und Analytics."
          :hashtags="['Basketball', 'BBL', 'Spieler', 'Statistiken', 'DBB']"
          :show-export="true"
          @export="exportPlayersData"
        />
      </div>
      
      <h1 class="text-4xl font-bold mb-4">🏀 Spieler Statistiken</h1>
      <p class="text-lg opacity-80">Echte Spielerdaten vom Deutschen Basketball Bund</p>
    </div>

    <!-- Advanced Filters Section -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <div class="flex justify-between items-center mb-4">
          <h2 class="card-title">🔍 Spieler filtern</h2>
          
          <!-- Action Buttons -->
          <div class="flex gap-2">
            <button @click="showCustomStats = true" class="btn btn-secondary btn-sm">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              Custom Stats
            </button>
            
            <button @click="showExportModal = true" class="btn btn-accent btn-sm">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export Cards
            </button>
            
            <div class="dropdown dropdown-end">
              <div tabindex="0" role="button" class="btn btn-primary btn-sm">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Quick Export
              </div>
              <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
                <li><a @click="quickExport('csv')">📊 Export CSV</a></li>
                <li><a @click="quickExport('json')">📄 Export JSON</a></li>
                <li><a @click="quickExport('pdf')">📑 Export PDF</a></li>
                <li class="menu-title">Player Cards</li>
                <li><a @click="exportTopPlayersCards">🏆 Top 10 Cards</a></li>
                <li><a @click="exportAllCategoryCards">🎯 Category Leaders</a></li>
              </ul>
            </div>
            
            <button 
              v-if="selectedPlayersForComparison.length > 0" 
              @click="openComparison" 
              class="btn btn-info btn-sm"
            >
              Compare ({{ selectedPlayersForComparison.length }})
            </button>
            <button 
              v-if="selectedPlayersForComparison.length > 0" 
              @click="clearComparison" 
              class="btn btn-outline btn-sm"
            >
              Clear
            </button>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <!-- Category Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">{{ $t('players.filters.category') }}</span>
            </label>
            <select v-model="filters.category" @change="updateFilters" class="select select-bordered select-sm">
              <option value="">{{ $t('players.filters.allCategories') }}</option>
              <option value="statBesteWerferArchiv">{{ $t('players.categories.bestScorers') }}</option>
              <option value="statBesteFreiWerferArchiv">{{ $t('players.categories.freeThrowShooters') }}</option>
              <option value="statBeste3erWerferArchiv">{{ $t('players.categories.threePointShooters') }}</option>
            </select>
          </div>

          <!-- League Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">{{ $t('players.filters.league') }}</span>
            </label>
            <select v-model="filters.league" @change="updateFilters" class="select select-bordered select-sm">
              <option value="">{{ $t('players.filters.allLeagues') }}</option>
              <option v-for="league in uniqueLeagues" :key="league" :value="league">{{ $t('players.filters.leagueLabel', { id: league }) }}</option>
            </select>
          </div>

          <!-- Team Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">{{ $t('players.filters.team') }}</span>
            </label>
            <select v-model="filters.team" @change="updateFilters" class="select select-bordered select-sm">
              <option value="">{{ $t('players.filters.allTeams') }}</option>
              <option v-for="team in uniqueTeams" :key="team" :value="team">{{ team }}</option>
            </select>
          </div>

          <!-- Season Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">{{ $t('players.filters.season') }}</span>
            </label>
            <select v-model="filters.season" @change="updateFilters" class="select select-bordered select-sm">
              <option value="">{{ $t('players.filters.allSeasons') }}</option>
              <option v-for="season in uniqueSeasons" :key="season" :value="season">{{ season }}/{{ season + 1 }}</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Player Name Search -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">{{ $t('players.filters.searchPlayer') }}</span>
            </label>
            <input v-model="filters.playerName" @input="updateFilters" type="text" :placeholder="$t('players.filters.enterPlayerName')" class="input input-bordered input-sm">
          </div>

          <!-- Min Points Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">{{ $t('players.filters.minPoints') }}</span>
            </label>
            <input v-model="filters.minPoints" @input="updateFilters" type="number" placeholder="0" class="input input-bordered input-sm">
          </div>

          <!-- View Mode -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">{{ $t('players.viewMode.title') }}</span>
            </label>
            <select v-model="viewMode" @change="updateFilters" class="select select-bordered select-sm">
              <option value="combined">{{ $t('players.viewMode.combined') }}</option>
              <option value="separate">{{ $t('players.viewMode.separate') }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics Table -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <div class="flex justify-between items-center mb-4">
          <h2 class="card-title">
            📈 {{ $t('players.table.title') }} ({{ $t('players.dataSource') }})
            <div class="badge badge-primary">{{ filteredPlayers.length }} {{ $t('players.stats.players') }}</div>
          </h2>
          <div class="text-sm opacity-70">
            {{ $t('players.realDataFrom') }} - {{ $t('players.stats.showing') }} {{ filteredPlayers.length }} {{ $t('players.stats.of') }} {{ totalPlayers }} {{ $t('players.stats.players') }}
          </div>
        </div>

        <!-- Compact Table -->
        <div class="overflow-x-auto">
          <table class="table table-zebra table-xs">
            <thead>
              <tr class="bg-base-200">
                <th class="w-8">
                  <input type="checkbox" class="checkbox checkbox-xs" @change="toggleSelectAll" :checked="selectAllChecked">
                </th>
                <th class="sticky left-0 bg-base-200 z-10 cursor-pointer min-w-[180px]" @click="sortByColumn('name')">
                  <div class="flex items-center gap-1">
                    <span class="font-semibold">Player</span>
                    <span v-if="sortBy === 'name'" class="text-xs">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </div>
                </th>
                <th class="cursor-pointer min-w-[120px]" @click="sortByColumn('team')">
                  <div class="flex items-center gap-1">
                    <span class="font-semibold">Team</span>
                    <span v-if="sortBy === 'team'" class="text-xs">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </div>
                </th>
                <th class="cursor-pointer w-16" @click="sortByColumn('liga_id')">
                  <div class="flex items-center gap-1">
                    <span class="font-semibold">Liga</span>
                    <span v-if="sortBy === 'liga_id'" class="text-xs">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </div>
                </th>
                <th class="cursor-pointer w-16 text-right" @click="sortByColumn('totalPoints')">
                  <div class="flex items-center justify-end gap-1">
                    <span class="font-semibold">{{ getColumnTitle1() }}</span>
                    <span v-if="sortBy === 'totalPoints'" class="text-xs">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </div>
                </th>
                <th class="cursor-pointer w-12 text-center" @click="sortByColumn('totalGames')">
                  <div class="flex items-center justify-center gap-1">
                    <span class="font-semibold">{{ getColumnTitle2() }}</span>
                    <span v-if="sortBy === 'totalGames'" class="text-xs">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </div>
                </th>
                <th class="cursor-pointer w-16 text-right" @click="sortByColumn('avgPoints')">
                  <div class="flex items-center justify-end gap-1">
                    <span class="font-semibold">{{ getColumnTitle3() }}</span>
                    <span v-if="sortBy === 'avgPoints'" class="text-xs">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </div>
                </th>
                <th class="cursor-pointer w-16 text-right" @click="sortByColumn('per')">
                  <div class="flex items-center justify-end gap-1">
                    <span class="font-semibold">PER</span>
                    <span v-if="sortBy === 'per'" class="text-xs">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                  </div>
                </th>
                <th class="w-24">Stats</th>
                <th class="w-20">Rank</th>
                <th class="w-16">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(player, index) in paginatedPlayers" :key="`${player.name}-${player.team}-${player.liga_id}`" class="hover">
                <td>
                  <input 
                    type="checkbox" 
                    class="checkbox checkbox-xs" 
                    :checked="isPlayerSelected(player)"
                    @change="togglePlayerSelection(player)"
                  >
                </td>
                <td class="sticky left-0 bg-base-100 z-10">
                  <div class="flex items-center gap-2">
                    <div class="avatar placeholder">
                      <div class="bg-neutral text-neutral-content rounded-full w-6 h-6">
                        <span class="text-xs font-bold">{{ player.name ? player.name.slice(0, 2).toUpperCase() : '??' }}</span>
                      </div>
                    </div>
                    <div class="min-w-0">
                      <div class="font-semibold text-sm truncate">{{ player.name || 'Unknown Player' }}</div>
                      <div class="text-xs opacity-60 truncate">{{ player.first_name }} {{ player.surname }}</div>
                    </div>
                  </div>
                </td>
                <td class="text-sm">
                  <div class="truncate max-w-[120px]" :title="player.team">{{ player.team || '-' }}</div>
                </td>
                <td class="text-xs text-center font-mono opacity-70">{{ player.liga_id || '-' }}</td>
                <td class="text-right">
                  <span class="font-bold text-primary">{{ player.totalPoints || 0 }}</span>
                </td>
                <td class="text-center text-sm">{{ player.totalGames || '-' }}</td>
                <td class="text-right">
                  <span class="font-mono text-sm">{{ formatTableValue3(player) }}</span>
                </td>
                <td class="text-right">
                  <span class="font-mono text-sm" :class="getPERClass(player.per)">{{ player.per ? player.per.toFixed(1) : '-' }}</span>
                </td>
                <td>
                  <div class="flex flex-wrap gap-1">
                    <div v-for="category in player.categories" :key="category" class="badge badge-xs" :class="getCategoryBadgeClass(category)">
                      {{ getCategoryShortName(category) }}
                    </div>
                  </div>
                </td>
                <td>
                  <div class="text-xs space-y-1">
                    <div v-for="ranking in player.rankings" :key="ranking.category" class="flex items-center">
                      <span class="font-bold text-primary">#{{ ranking.rank }}</span>
                      <span class="ml-1 opacity-60">{{ getCategoryShortName(ranking.category) }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="dropdown dropdown-end">
                    <div tabindex="0" role="button" class="btn btn-ghost btn-xs">⋯</div>
                    <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-36">
                      <li><a @click="viewPlayerProfile(player)" class="text-xs">View Profile</a></li>
                      <li><a @click="generatePlayerCard(player)" class="text-xs">Generate Card</a></li>
                      <li><a @click="togglePlayerSelection(player)" class="text-xs">
                        {{ isPlayerSelected(player) ? 'Remove' : 'Compare' }}
                      </a></li>
                      <li><a @click="sharePlayer(player)" class="text-xs">Share Player</a></li>
                    </ul>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="flex justify-between items-center mt-6">
          <div class="text-sm opacity-70">
            {{ $t('players.pagination.page') }} {{ currentPage }} {{ $t('players.pagination.of') }} {{ totalPages }}
          </div>
          <div class="join">
            <button class="join-item btn btn-sm" :disabled="currentPage === 1" @click="currentPage = 1">
              {{ $t('players.pagination.first') }}
            </button>
            <button class="join-item btn btn-sm" :disabled="currentPage === 1" @click="currentPage--">
              {{ $t('players.pagination.previous') }}
            </button>
            <button class="join-item btn btn-sm btn-active">
              {{ currentPage }}
            </button>
            <button class="join-item btn btn-sm" :disabled="currentPage === totalPages" @click="currentPage++">
              {{ $t('players.pagination.next') }}
            </button>
            <button class="join-item btn btn-sm" :disabled="currentPage === totalPages" @click="currentPage = totalPages">
              {{ $t('players.pagination.last') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Player Profile Modal -->
    <dialog ref="playerProfileModal" class="modal">
      <div class="modal-box max-w-4xl">
        <div v-if="selectedPlayer" class="space-y-6">
          <!-- Player Header -->
          <div class="flex items-center gap-4 pb-4 border-b">
            <div class="avatar placeholder">
              <div class="bg-primary text-primary-content rounded-full w-16">
                <span class="text-xl">{{ selectedPlayer.name ? selectedPlayer.name.slice(0, 2).toUpperCase() : 'N/A' }}</span>
              </div>
            </div>
            <div>
              <h3 class="text-2xl font-bold">{{ selectedPlayer.name }}</h3>
              <p class="text-lg opacity-70">{{ selectedPlayer.team }}</p>
              <div class="flex gap-2 mt-2">
                <div class="badge badge-primary">{{ getCategoryDisplayName(selectedPlayer.endpoint) }}</div>
                <div class="badge badge-secondary">{{ selectedPlayer.season_id }}/{{ selectedPlayer.season_id + 1 }}</div>
              </div>
            </div>
          </div>

          <!-- Player Stats -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="stat bg-base-200 rounded-lg">
              <div class="stat-title">{{ getStatTitle1(selectedPlayer.endpoint) }}</div>
              <div class="stat-value text-primary">{{ selectedPlayer.points }}</div>
              <div class="stat-desc">{{ getStatDesc1(selectedPlayer.endpoint) }}</div>
            </div>
            <div class="stat bg-base-200 rounded-lg">
              <div class="stat-title">{{ getStatTitle2(selectedPlayer.endpoint) }}</div>
              <div class="stat-value">{{ selectedPlayer.games }}</div>
              <div class="stat-desc">{{ getStatDesc2(selectedPlayer.endpoint) }}</div>
            </div>
            <div class="stat bg-base-200 rounded-lg">
              <div class="stat-title">{{ getStatTitle3(selectedPlayer.endpoint) }}</div>
              <div class="stat-value text-secondary">{{ formatStatValue3(selectedPlayer) }}</div>
              <div class="stat-desc">{{ getStatDesc3(selectedPlayer.endpoint) }}</div>
            </div>
          </div>

          <!-- Player Career Stats (All Categories) -->
          <div v-if="playerCareerStats.length > 0">
            <h4 class="text-xl font-semibold mb-4">Career Statistics</h4>
            <div class="overflow-x-auto">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Category</th>
                    <th>Season</th>
                    <th>Team</th>
                    <th>Points</th>
                    <th>Games</th>
                    <th>Avg</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="stat in playerCareerStats" :key="`${stat.endpoint}-${stat.season_id}`">
                    <td>{{ getCategoryDisplayName(stat.endpoint) }}</td>
                    <td>{{ stat.season_id }}/{{ stat.season_id + 1 }}</td>
                    <td>{{ stat.team }}</td>
                    <td class="font-bold">{{ stat.points }}</td>
                    <td>{{ stat.games }}</td>
                    <td>{{ stat.average?.toFixed(1) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="modal-action">
          <button @click="generateSelectedPlayerCard" class="btn btn-primary">
            🏀 Generate Basketball Card
          </button>
          <button @click="closePlayerProfile" class="btn">{{ $t('common.close') }}</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button @click="closePlayerProfile">close</button>
      </form>
    </dialog>

    <!-- Player Comparison Modal -->
    <dialog ref="comparisonModal" class="modal">
      <div class="modal-box max-w-6xl">
        <h3 class="font-bold text-lg mb-4">{{ $t('players.compare.title') }}</h3>
        
        <div v-if="selectedPlayersForComparison.length > 1" class="space-y-6">
          <!-- Comparison Table -->
          <div class="overflow-x-auto">
            <table class="table table-sm">
              <thead>
                <tr>
                  <th>{{ $t('players.table.player') }}</th>
                  <th>{{ $t('players.table.team') }}</th>
                  <th>{{ $t('players.table.totalPoints') }}</th>
                  <th>{{ $t('players.table.games') }}</th>
                  <th>{{ $t('players.table.avgPoints') }}</th>
                  <th>{{ $t('players.table.per') }}</th>
                  <th>{{ $t('players.table.categories') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="player in selectedPlayersForComparison" :key="player.name" class="hover">
                  <td class="font-semibold">{{ player.name }}</td>
                  <td>{{ player.team }}</td>
                  <td class="font-bold text-primary">{{ player.totalPoints }}</td>
                  <td>{{ player.totalGames }}</td>
                  <td class="font-mono">{{ player.avgPoints?.toFixed(1) }}</td>
                  <td class="font-mono text-secondary">{{ player.per?.toFixed(1) }}</td>
                  <td>
                    <div class="flex flex-wrap gap-1">
                      <span v-for="category in player.categories" :key="category" class="badge badge-secondary badge-xs">
                        {{ getCategoryDisplayName(category) }}
                      </span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Comparison Charts -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="card bg-base-200">
              <div class="card-body">
                <h4 class="card-title text-sm">{{ $t('players.compare.pointsComparison') }}</h4>
                <div class="space-y-2">
                  <div v-for="player in selectedPlayersForComparison" :key="player.name" class="flex justify-between items-center">
                    <span class="text-sm">{{ player.name }}</span>
                    <div class="flex items-center gap-2">
                      <progress class="progress progress-primary w-20" :value="player.totalPoints" :max="Math.max(...selectedPlayersForComparison.map(p => p.totalPoints))"></progress>
                      <span class="text-sm font-mono">{{ player.totalPoints }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="card bg-base-200">
              <div class="card-body">
                <h4 class="card-title text-sm">{{ $t('players.compare.efficiencyComparison') }}</h4>
                <div class="space-y-2">
                  <div v-for="player in selectedPlayersForComparison" :key="player.name" class="flex justify-between items-center">
                    <span class="text-sm">{{ player.name }}</span>
                    <div class="flex items-center gap-2">
                      <progress class="progress progress-secondary w-20" :value="player.per || 0" max="30"></progress>
                      <span class="text-sm font-mono">{{ player.per?.toFixed(1) || 'N/A' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-action">
          <button @click="closeComparison" class="btn">{{ $t('common.close') }}</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button @click="closeComparison">close</button>
      </form>
    </dialog>

    <!-- Custom Stats Builder Modal -->
    <CustomStatsBuilder 
      :show-modal="showCustomStats"
      :players-data="playersData.players"
      @close="showCustomStats = false"
      @save-stat="saveCustomStat"
    />

    <!-- Export Modal -->
    <ExportModal 
      :show-modal="showExportModal"
      :players-data="playersData.players"
      :filtered-players="filteredPlayers"
      @close="showExportModal = false"
    />
    
    <!-- Card Modal -->
    <CardModal v-if="selectedPlayer" ref="cardModalRef" :player="selectedPlayer" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
const config = useRuntimeConfig()

// Use Nuxt's i18n composable
// const { t } = useI18n()

// Temporary static German translations
const t = (key) => {
  const translations = {
    'players.title': 'Spieler Statistiken',
    'players.subtitle': 'Echte Spielerdaten vom Deutschen Basketball Bund',
    'players.filters.title': 'Spieler filtern',
    'players.compare.button': 'Spieler vergleichen',
    'players.compare.clear': 'Auswahl löschen',
    'players.compare.title': 'Spielervergleich',
    'players.filters.category': 'Kategorie',
    'players.filters.allCategories': 'Alle Kategorien',
    'players.categories.bestScorers': 'Beste Werfer',
    'players.categories.freeThrowShooters': 'Freiwurf-Schützen',
    'players.categories.threePointShooters': '3-Punkte-Schützen',
    'players.filters.league': 'Liga',
    'players.filters.allLeagues': 'Alle Ligen',
    'players.filters.leagueLabel': 'Liga {id}',
    'players.filters.team': 'Mannschaft',
    'players.filters.allTeams': 'Alle Mannschaften',
    'players.filters.season': 'Saison',
    'players.filters.allSeasons': 'Alle Saisons',
    'players.filters.searchPlayer': 'Spieler suchen',
    'players.filters.enterPlayerName': 'Spielername eingeben...',
    'players.filters.minPoints': 'Min. Punkte',
    'players.viewMode.title': 'Ansichtsmodus',
    'players.viewMode.combined': 'Kombiniert',
    'players.viewMode.separate': 'Getrennt',
    'players.table.title': 'Spieler Tabelle',
    'players.table.player': 'Spieler',
    'players.table.category': 'Kat.',
    'players.table.team': 'Team',
    'players.table.league': 'Liga',
    'players.table.season': 'Saison',
    'players.table.points': 'Pts',
    'players.table.games': 'G',
    'players.table.pointsPerGame': 'PPG',
    'players.table.per': 'PER',
    'players.table.actions': 'Aktionen',
    'players.loading': 'Lade Spielerdaten...',
    'players.error': 'Fehler beim Laden der Daten',
    'players.noData': 'Keine Spielerdaten gefunden',
    'players.dataSource': 'Echte Basketball-Bund Export Daten',
    'players.realDataFrom': 'Echte Daten von basketball-bund.net',
    'players.stats.showing': 'Zeige',
    'players.stats.of': 'von', 
    'players.stats.players': 'Spielern',
    'players.pagination.page': 'Seite',
    'players.pagination.of': 'von',
    'players.pagination.first': 'Erste',
    'players.pagination.previous': 'Zurück',
    'players.pagination.next': 'Weiter',
    'players.pagination.last': 'Letzte',
    'common.unknown': 'Unbekannt',
    'common.close': 'Schließen'
  }
  
  if (key.includes('{id}')) {
    return translations[key.replace('{id}', arguments[1]?.id || '')]
  }
  
  return translations[key] || key
}

// Data
const playersData = ref({ players: [] })
const totalPlayers = ref(0)
const loading = ref(true)
const error = ref(null)
const selectedPlayer = ref(null)
const playerProfileModal = ref(null)
const comparisonModal = ref(null)
const selectedPlayersForComparison = ref([])

// Modal refs
const cardModalRef = ref(null)

// Export and Custom Stats Modals
const showExportModal = ref(false)
const showCustomStats = ref(false)
const customStats = ref([])

// Export functions for share button
const exportPlayersData = (format) => {
  quickExport(format)
}

// Quick export function (existing)s
const quickExport = (format) => {
  const dataToExport = filteredPlayers.value.slice(0, 1000) // Limit for performance
  const timestamp = new Date().toISOString().split('T')[0]
  const filename = `basketball_stats_${timestamp}`
  
  if (format === 'csv') {
    exportCSV(dataToExport, filename)
  } else if (format === 'json') {
    exportJSON(dataToExport, filename)
  } else if (format === 'pdf') {
    // For PDF, we'll use the ExportModal component
    showExportModal.value = true
  }
}

const exportCSV = (data, filename) => {
  const headers = ['Name', 'Team', 'Liga', 'Punkte', 'Spiele', 'PPG', 'Kategorie', 'Saison']
  const rows = data.map(player => [
    player.name || '',
    player.mannschaft || '',
    player.liga || '',
    player.punkte || '',
    player.spiele || '',
    player.spiele > 0 ? (parseFloat(player.punkte) / parseFloat(player.spiele)).toFixed(1) : '0',
    getCategoryDisplayName(player.kategorie),
    player.saison || ''
  ].map(cell => `"${cell}"`).join(','))
  
  const csv = [headers.join(','), ...rows].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${filename}.csv`
  link.click()
  URL.revokeObjectURL(link.href)
}

const exportJSON = (data, filename) => {
  const exportData = data.map(player => ({
    name: player.name,
    team: player.mannschaft,
    league: player.liga,
    points: parseFloat(player.punkte) || 0,
    games: parseFloat(player.spiele) || 0,
    ppg: player.spiele > 0 ? parseFloat((parseFloat(player.punkte) / parseFloat(player.spiele)).toFixed(1)) : 0,
    category: getCategoryDisplayName(player.kategorie),
    season: player.saison
  }))
  
  const json = JSON.stringify(exportData, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${filename}.json`
  link.click()
  URL.revokeObjectURL(link.href)
}

const exportTopPlayersCards = () => {
  // This would trigger bulk export of top 10 players
  showExportModal.value = true
  // Could pre-configure the export modal for top players
}

const exportAllCategoryCards = () => {
  // This would trigger bulk export of category leaders
  showExportModal.value = true
}

const saveCustomStat = (data) => {
  customStats.value.push(data)
  showCustomStats.value = false
  // Could persist to localStorage or send to backend
}

// Filters
const filters = ref({
  category: '',
  league: '',
  team: '',
  season: '',
  playerName: '',
  minPoints: ''
})

// Sorting and Pagination
const sortBy = ref('totalPoints')
const sortOrder = ref('desc')
const currentPage = ref(1)
const playersPerPage = 50
const viewMode = ref('combined') // 'combined' or 'separate'

// Load player data (try live API, fallback to local JSON)
const loadPlayerData = async () => {
  try {
    loading.value = true
    error.value = null

    // Try live API
    try {
      const params = new URLSearchParams({ limit: '20000' })
      const resp = await fetch(`${config.public.apiBase}/api/players?${params.toString()}`)
      if (resp.ok) {
        const data = await resp.json()
        playersData.value = data
        totalPlayers.value = data.players?.length || 0
        return
      }
      console.warn('Live API returned non-OK status, falling back to local data')
    } catch (e) {
      console.warn('Live API unavailable, falling back to local JSON:', e)
    }

    // Fallback to local JSON
    const response = await fetch('/real_players_extracted.json')
    if (!response.ok) throw new Error('Failed to load fallback player data')
    const data = await response.json()
    playersData.value = data
    totalPlayers.value = data.players?.length || 0

  } catch (err) {
    console.error('Error loading player data:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Calculate Player Efficiency Rating (PER)
const calculatePER = (player) => {
  // Simplified PER calculation based on available data
  // PER = (Points + Rebounds + Assists + Steals + Blocks - Missed FG - Missed FT - Turnovers) / Minutes * Scale Factor
  // Since we only have points and games, we'll use a simplified version
  if (!player.points || !player.games) return 0
  
  const pointsPerGame = player.points / player.games
  const baseEfficiency = pointsPerGame * 1.5 // Simple multiplier
  
  // Normalize to typical PER scale (15 is average)
  return Math.min(baseEfficiency, 40) // Cap at 40 (elite level)
}

// Combine player data across categories
const combinePlayerData = (players) => {
  const playerMap = new Map()
  
  players.forEach(player => {
    const key = `${player.name}-${player.team}-${player.liga_id}-${player.season_id}`
    
    if (!playerMap.has(key)) {
      playerMap.set(key, {
        name: player.name,
        first_name: player.first_name,
        surname: player.surname,
        team: player.team,
        liga_id: player.liga_id,
        season_id: player.season_id,
        totalPoints: 0,
        totalGames: 0,
        categories: [],
        rankings: [],
        per: 0
      })
    }
    
    const combined = playerMap.get(key)
    combined.totalPoints += player.points || 0
    combined.totalGames += player.games || 0
    combined.categories.push(player.endpoint)
    combined.rankings.push({
      category: player.endpoint,
      rank: player.rank
    })
  })
  
  // Calculate averages and PER for combined data
  playerMap.forEach(player => {
    player.avgPoints = player.totalGames > 0 ? player.totalPoints / player.totalGames : 0
    player.per = calculatePER(player)
  })
  
  return Array.from(playerMap.values())
}

// Computed properties
const uniqueCategories = computed(() => {
  const categories = new Set()
  playersData.value.players?.forEach(player => {
    if (player.endpoint) categories.add(player.endpoint)
  })
  return Array.from(categories).sort()
})

const uniqueLeagues = computed(() => {
  const leagues = new Set()
  playersData.value.players?.forEach(player => {
    if (player.liga_id) leagues.add(player.liga_id)
  })
  return Array.from(leagues).sort((a, b) => a - b)
})

const uniqueTeams = computed(() => {
  const teams = new Set()
  playersData.value.players?.forEach(player => {
    if (player.team) teams.add(player.team)
  })
  return Array.from(teams).sort()
})

const uniqueSeasons = computed(() => {
  const seasons = new Set()
  playersData.value.players?.forEach(player => {
    if (player.season_id) seasons.add(player.season_id)
  })
  return Array.from(seasons).sort((a, b) => a - b)
})

const processedPlayers = computed(() => {
  let players = playersData.value.players || []
  
  if (viewMode.value === 'combined') {
    return combinePlayerData(players)
  }
  
  // For separate mode, add individual PER calculation
  return players.map(player => ({
    ...player,
    per: calculatePER(player),
    totalPoints: player.points,
    totalGames: player.games,
    avgPoints: player.average,
    categories: [player.endpoint],
    rankings: [{ category: player.endpoint, rank: player.rank }]
  }))
})

const filteredPlayers = computed(() => {
  let filtered = processedPlayers.value
  
  // Apply filters
  if (filters.value.category) {
    filtered = filtered.filter(player => 
      player.categories.includes(filters.value.category)
    )
  }
  
  if (filters.value.league) {
    filtered = filtered.filter(player => player.liga_id === parseInt(filters.value.league))
  }
  
  if (filters.value.team) {
    filtered = filtered.filter(player => player.team === filters.value.team)
  }
  
  if (filters.value.season) {
    filtered = filtered.filter(player => player.season_id === parseInt(filters.value.season))
  }
  
  if (filters.value.playerName) {
    const searchTerm = filters.value.playerName.toLowerCase()
    filtered = filtered.filter(player => 
      (player.name && player.name.toLowerCase().includes(searchTerm)) ||
      (player.first_name && player.first_name.toLowerCase().includes(searchTerm)) ||
      (player.surname && player.surname.toLowerCase().includes(searchTerm))
    )
  }
  
  if (filters.value.minPoints) {
    const minPoints = parseInt(filters.value.minPoints)
    filtered = filtered.filter(player => (player.totalPoints || 0) >= minPoints)
  }
  
  return filtered
})

const sortedPlayers = computed(() => {
  const sorted = [...filteredPlayers.value]
  
  sorted.sort((a, b) => {
    let aVal, bVal
    
    switch (sortBy.value) {
      case 'totalPoints':
        aVal = a.totalPoints || 0
        bVal = b.totalPoints || 0
        break
      case 'totalGames':
        aVal = a.totalGames || 0
        bVal = b.totalGames || 0
        break
      case 'avgPoints':
        aVal = a.avgPoints || 0
        bVal = b.avgPoints || 0
        break
      case 'per':
        aVal = a.per || 0
        bVal = b.per || 0
        break
      case 'name':
        aVal = a.name || ''
        bVal = b.name || ''
        return sortOrder.value === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
      case 'team':
        aVal = a.team || ''
        bVal = b.team || ''
        return sortOrder.value === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
      case 'liga_id':
        aVal = a.liga_id || 0
        bVal = b.liga_id || 0
        break
      default:
        aVal = a.totalPoints || 0
        bVal = b.totalPoints || 0
    }
    
    return sortOrder.value === 'desc' ? bVal - aVal : aVal - bVal
  })
  
  return sorted
})

const totalPages = computed(() => {
  return Math.ceil(sortedPlayers.value.length / playersPerPage)
})

const paginatedPlayers = computed(() => {
  const start = (currentPage.value - 1) * playersPerPage
  const end = start + playersPerPage
  return sortedPlayers.value.slice(start, end)
})

const playerCareerStats = computed(() => {
  if (!selectedPlayer.value) return []
  
  const playerName = selectedPlayer.value.name
  return playersData.value.players?.filter(player => 
    player.name === playerName
  ) || []
})

const selectAllChecked = computed(() => {
  return paginatedPlayers.value.length > 0 && paginatedPlayers.value.every(player => isPlayerSelected(player))
})

// Methods
const getCategoryDisplayName = (endpoint) => {
  switch (endpoint) {
    case 'statBesteWerferArchiv':
      return t('players.categories.bestScorers')
    case 'statBesteFreiWerferArchiv':
      return t('players.categories.freeThrowShooters')
    case 'statBeste3erWerferArchiv':
      return t('players.categories.threePointShooters')
    default:
      return endpoint || t('common.unknown')
  }
}

const getCategoryShortName = (endpoint) => {
  switch (endpoint) {
    case 'statBesteWerferArchiv':
      return 'PTS'
    case 'statBesteFreiWerferArchiv':
      return 'FT'
    case 'statBeste3erWerferArchiv':
      return '3P'
    default:
      return '?'
  }
}

const getCategoryBadgeClass = (endpoint) => {
  switch (endpoint) {
    case 'statBesteWerferArchiv':
      return 'badge-primary'
    case 'statBesteFreiWerferArchiv':
      return 'badge-secondary'
    case 'statBeste3erWerferArchiv':
      return 'badge-accent'
    default:
      return 'badge-neutral'
  }
}

const getPERClass = (impact) => {
  if (!impact) return 'text-gray-400'
  if (impact >= 20) return 'text-success font-bold'  // Elite impact
  if (impact >= 15) return 'text-info font-bold'     // High impact
  if (impact >= 10) return 'text-warning'            // Good impact
  return 'text-error'                                 // Low impact
}

// Helper functions for player profile stats display
const getStatTitle1 = (endpoint) => {
  switch (endpoint) {
    case 'statBesteWerferArchiv': return 'Total Points'
    case 'statBesteFreiWerferArchiv': return 'Free Throws Made'
    case 'statBeste3erWerferArchiv': return '3-Pointers Made'
    default: return 'Stat 1'
  }
}

const getStatDesc1 = (endpoint) => {
  switch (endpoint) {
    case 'statBesteWerferArchiv': return 'Season total'
    case 'statBesteFreiWerferArchiv': return 'Successful attempts'
    case 'statBeste3erWerferArchiv': return 'Successful attempts'
    default: return 'Description'
  }
}

const getStatTitle2 = (endpoint) => {
  switch (endpoint) {
    case 'statBesteWerferArchiv': return 'Games Played'
    case 'statBesteFreiWerferArchiv': return 'Free Throws Attempted'
    case 'statBeste3erWerferArchiv': return '3-Pointers Attempted'
    default: return 'Stat 2'
  }
}

const getStatDesc2 = (endpoint) => {
  switch (endpoint) {
    case 'statBesteWerferArchiv': return 'Regular season'
    case 'statBesteFreiWerferArchiv': return 'Total attempts'
    case 'statBeste3erWerferArchiv': return 'Total attempts'
    default: return 'Description'
  }
}

const getStatTitle3 = (endpoint) => {
  switch (endpoint) {
    case 'statBesteWerferArchiv': return 'Points per Game'
    case 'statBesteFreiWerferArchiv': return 'Free Throw %'
    case 'statBeste3erWerferArchiv': return '3-Point %'
    default: return 'Stat 3'
  }
}

const getStatDesc3 = (endpoint) => {
  switch (endpoint) {
    case 'statBesteWerferArchiv': return 'Average performance'
    case 'statBesteFreiWerferArchiv': return 'Success rate'
    case 'statBeste3erWerferArchiv': return 'Success rate'
    default: return 'Description'
  }
}

const formatStatValue3 = (player) => {
  if (!player.average) return '-'
  
  switch (player.endpoint) {
    case 'statBesteWerferArchiv': 
      return player.average.toFixed(1)
    case 'statBesteFreiWerferArchiv':
    case 'statBeste3erWerferArchiv':
      return player.average.toFixed(1) + '%'
    default: 
      return player.average.toFixed(1)
  }
}

// Dynamic column titles based on current filters
const getColumnTitle1 = () => {
  const category = filters.value.category
  if (!category || category === '') return 'Pts' // Default
  
  switch (category) {
    case 'statBesteWerferArchiv': return 'Pts'
    case 'statBesteFreiWerferArchiv': return 'Made'
    case 'statBeste3erWerferArchiv': return '3PM'
    default: return 'Pts'
  }
}

const getColumnTitle2 = () => {
  const category = filters.value.category
  if (!category || category === '') return 'G' // Default
  
  switch (category) {
    case 'statBesteWerferArchiv': return 'G'
    case 'statBesteFreiWerferArchiv': return 'Att'
    case 'statBeste3erWerferArchiv': return '3PA'
    default: return 'G'
  }
}

const getColumnTitle3 = () => {
  const category = filters.value.category
  if (!category || category === '') return 'PPG' // Default
  
  switch (category) {
    case 'statBesteWerferArchiv': return 'PPG'
    case 'statBesteFreiWerferArchiv': return 'FT%'
    case 'statBeste3erWerferArchiv': return '3P%'
    default: return 'PPG'
  }
}

// Format table values correctly for each category
const formatTableValue3 = (player) => {
  if (!player.avgPoints) return '-'
  
  // Check if player has multiple categories, use the average differently
  const hasFreethrow = player.categories?.includes('statBesteFreiWerferArchiv')
  const hasThreePoint = player.categories?.includes('statBeste3erWerferArchiv')
  const currentFilter = filters.value.category
  
  // If filtering by specific category, format accordingly
  if (currentFilter === 'statBesteFreiWerferArchiv' || (hasFreethrow && !currentFilter)) {
    return player.avgPoints.toFixed(1) + '%'
  }
  if (currentFilter === 'statBeste3erWerferArchiv' || (hasThreePoint && !currentFilter)) {
    return player.avgPoints.toFixed(1) + '%'
  }
  
  // Default to PPG format
  return player.avgPoints.toFixed(1)
}

const sortByColumn = (column) => {
  if (sortBy.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column
    sortOrder.value = 'desc'
  }
}

const updateFilters = () => {
  currentPage.value = 1
}

const viewPlayerProfile = (player) => {
  selectedPlayer.value = player
  playerProfileModal.value?.showModal()
}

const sharePlayer = (player) => {
  // Format text based on player's primary category
  const primaryCategory = player.categories?.[0] || 'statBesteWerferArchiv'
  let statsText = ''
  
  switch (primaryCategory) {
    case 'statBesteWerferArchiv':
      statsText = `• ${player.totalPoints || 0} Punkte in ${player.totalGames || 0} Spielen\n• ${player.avgPoints ? player.avgPoints.toFixed(1) : 'N/A'} PPG`
      break
    case 'statBesteFreiWerferArchiv':
      statsText = `• ${player.totalPoints || 0} FTM / ${player.totalGames || 0} FTA\n• ${player.avgPoints ? player.avgPoints.toFixed(1) : 'N/A'}% Freiwurf`
      break
    case 'statBeste3erWerferArchiv':
      statsText = `• ${player.totalPoints || 0} 3PM / ${player.totalGames || 0} 3PA\n• ${player.avgPoints ? player.avgPoints.toFixed(1) : 'N/A'}% 3-Punkte`
      break
    default:
      statsText = `• ${player.totalPoints || 0} Punkte in ${player.totalGames || 0} Spielen\n• ${player.avgPoints ? player.avgPoints.toFixed(1) : 'N/A'} PPG`
  }
  
  const playerText = `🏀 ${player.name || 'Basketball Player'} - ${player.team || 'Team'}\n\n📊 Stats:\n${statsText}\n• Liga ${player.liga_id || 'N/A'}\n• PER: ${player.per ? player.per.toFixed(1) : 'N/A'}`
  
  // Create share URLs
  const currentUrl = window.location.href
  const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(playerText + '\n\n' + currentUrl)}`
  const telegramUrl = `https://t.me/share/url?url=${encodeURIComponent(currentUrl)}&text=${encodeURIComponent(playerText)}`
  const emailUrl = `mailto:?subject=${encodeURIComponent(`Basketball Player: ${player.name}`)}&body=${encodeURIComponent(playerText + '\n\nMehr Details: ' + currentUrl)}`
  
  // Create temporary share menu
  const shareMenu = document.createElement('div')
  shareMenu.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'
  shareMenu.innerHTML = `
    <div class="bg-base-100 rounded-lg p-6 max-w-sm w-full mx-4">
      <h3 class="font-bold text-lg mb-4">Share ${player.name}</h3>
      <div class="space-y-2">
        <a href="${whatsappUrl}" target="_blank" class="btn btn-block btn-sm">
          📱 WhatsApp
        </a>
        <a href="${telegramUrl}" target="_blank" class="btn btn-block btn-sm">
          ✈️ Telegram
        </a>
        <a href="${emailUrl}" class="btn btn-block btn-sm">
          📧 Email
        </a>
        <button onclick="navigator.clipboard.writeText('${playerText.replace(/'/g, "\\'")}\\n\\n${currentUrl}'); this.textContent = 'Copied!'" class="btn btn-block btn-sm">
          📋 Copy to Clipboard
        </button>
      </div>
      <button onclick="this.closest('.fixed').remove()" class="btn btn-sm btn-ghost mt-4 w-full">Close</button>
    </div>
  `
  
  document.body.appendChild(shareMenu)
  
  // Remove on click outside
  shareMenu.addEventListener('click', (e) => {
    if (e.target === shareMenu) {
      shareMenu.remove()
    }
  })
}

// Card generation functions
const generatePlayerCard = (player) => {
  selectedPlayer.value = player
  nextTick(() => {
    cardModalRef.value?.showModal()
  })
}

const generateSelectedPlayerCard = () => {
  if (selectedPlayer.value) {
    nextTick(() => {
      cardModalRef.value?.showModal()
    })
  }
}

const closePlayerProfile = () => {
  selectedPlayer.value = null
  playerProfileModal.value?.close()
}

const isPlayerSelected = (player) => {
  return selectedPlayersForComparison.value.some(p => 
    p.name === player.name && p.team === player.team
  )
}

const togglePlayerSelection = (player) => {
  const index = selectedPlayersForComparison.value.findIndex(p => 
    p.name === player.name && p.team === player.team
  )
  
  if (index > -1) {
    selectedPlayersForComparison.value.splice(index, 1)
  } else {
    if (selectedPlayersForComparison.value.length < 5) { // Limit to 5 players
      selectedPlayersForComparison.value.push(player)
    }
  }
}

const toggleSelectAll = () => {
  if (selectAllChecked.value) {
    // Deselect all visible players
    paginatedPlayers.value.forEach(player => {
      const index = selectedPlayersForComparison.value.findIndex(p => 
        p.name === player.name && p.team === player.team
      )
      if (index > -1) {
        selectedPlayersForComparison.value.splice(index, 1)
      }
    })
  } else {
    // Select all visible players (up to limit)
    paginatedPlayers.value.forEach(player => {
      if (selectedPlayersForComparison.value.length < 5 && !isPlayerSelected(player)) {
        selectedPlayersForComparison.value.push(player)
      }
    })
  }
}

const openComparison = () => {
  comparisonModal.value?.showModal()
}

const closeComparison = () => {
  comparisonModal.value?.close()
}

const clearComparison = () => {
  selectedPlayersForComparison.value = []
}

// Watchers
watch(filteredPlayers, () => {
  if (currentPage.value > totalPages.value) {
    currentPage.value = 1
  }
})

// Lifecycle
onMounted(() => {
  loadPlayerData()
})
</script>

