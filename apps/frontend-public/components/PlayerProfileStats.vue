<template>
  <div class="player-profile-stats">
    <!-- Player Header -->
    <div class="player-header">
      <div class="player-info">
        <h1 class="player-name">{{ playerName }}</h1>
        <div class="player-meta">
          <span class="current-team">{{ currentTeam }}</span>
          <span class="position" v-if="position">{{ position }}</span>
          <span class="jersey-number" v-if="jerseyNumber">#{{ jerseyNumber }}</span>
        </div>
        <div class="flex gap-2 mt-2 items-center">
          <label class="text-sm font-bold">#</label>
          <input type="number" v-model="editableNumber" min="0" max="99" class="input input-bordered input-xs w-16" />
          <label class="text-sm font-bold">Position:</label>
          <select v-model="editablePosition" class="select select-xs w-32">
            <option value="GUARD">GUARD</option>
            <option value="FORWARD">FORWARD</option>
            <option value="CENTER">CENTER</option>
          </select>
        </div>
      </div>
      <div class="player-photo" v-if="playerPhoto">
        <img :src="playerPhoto" :alt="playerName" />
      </div>
    </div>

    <!-- Statistics Tabs -->
    <div class="stats-tabs">
      <button 
        v-for="tab in statsTabs" 
        :key="tab.key"
        class="tab-button"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Current Season Stats -->
    <div v-if="activeTab === 'current'" class="stats-section">
      <div class="section-header">
        <h2>Current Season (2025/26)</h2>
        <div class="season-meta">
          <span class="games-played">{{ currentStats.games }} Games</span>
          <span class="last-updated">Updated: {{ lastUpdated }}</span>
        </div>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card primary">
          <div class="stat-value">{{ currentStats.pointsPerGame }}</div>
          <div class="stat-label">PPG</div>
          <div class="stat-trend" :class="currentStats.pointsTrend">
            <Icon :name="getTrendIcon(currentStats.pointsTrend)" />
            {{ currentStats.pointsChange }}
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-value">{{ currentStats.reboundsPerGame }}</div>
          <div class="stat-label">RPG</div>
        </div>
        
        <div class="stat-card">
          <div class="stat-value">{{ currentStats.assistsPerGame }}</div>
          <div class="stat-label">APG</div>
        </div>
        
        <div class="stat-card">
          <div class="stat-value">{{ currentStats.fieldGoalPercentage }}%</div>
          <div class="stat-label">FG%</div>
        </div>
        
        <div class="stat-card">
          <div class="stat-value">{{ currentStats.threePointPercentage }}%</div>
          <div class="stat-label">3P%</div>
        </div>
        
        <div class="stat-card">
          <div class="stat-value">{{ currentStats.freeThrowPercentage }}%</div>
          <div class="stat-label">FT%</div>
        </div>
      </div>

      <!-- Recent Games Performance -->
      <div class="recent-games">
        <h3>Last 5 Games</h3>
        <div class="games-chart">
          <div 
            v-for="(game, index) in recentGames" 
            :key="index"
            class="game-bar"
            :style="{ height: `${(game.points / maxRecentPoints) * 100}%` }"
            :title="`${game.opponent}: ${game.points} pts, ${game.rebounds} reb, ${game.assists} ast`"
          >
            <div class="game-points">{{ game.points }}</div>
            <div class="game-opponent">{{ game.opponent }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Last 5 Seasons Stats -->
    <div v-if="activeTab === 'recent'" class="stats-section">
      <div class="section-header">
        <h2>Last 5 Seasons (2021-2025)</h2>
        <p class="section-description">Season-by-season performance trends</p>
      </div>
      
      <div class="seasons-table">
        <table>
          <thead>
            <tr>
              <th>Season</th>
              <th>Team</th>
              <th>GP</th>
              <th>PPG</th>
              <th>RPG</th>
              <th>APG</th>
              <th>FG%</th>
              <th>3P%</th>
              <th>FT%</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="season in lastFiveSeasons" 
              :key="season.season"
              :class="{ 'current-season': season.isCurrent }"
            >
              <td class="season-name">{{ season.season }}</td>
              <td class="team-name">{{ season.team }}</td>
              <td>{{ season.games }}</td>
              <td class="stat-highlight">{{ season.pointsPerGame }}</td>
              <td>{{ season.reboundsPerGame }}</td>
              <td>{{ season.assistsPerGame }}</td>
              <td>{{ season.fieldGoalPercentage }}%</td>
              <td>{{ season.threePointPercentage }}%</td>
              <td>{{ season.freeThrowPercentage }}%</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Performance Trends Chart -->
      <div class="trends-chart">
        <h3>Performance Trends</h3>
        <div class="chart-container">
          <svg class="trend-svg" viewBox="0 0 400 200">
            <!-- PPG Line -->
            <polyline
              :points="getChartPoints(lastFiveSeasons, 'pointsPerGame')"
              class="trend-line points"
              fill="none"
            />
            <!-- RPG Line -->
            <polyline
              :points="getChartPoints(lastFiveSeasons, 'reboundsPerGame')"
              class="trend-line rebounds"
              fill="none"
            />
            <!-- APG Line -->
            <polyline
              :points="getChartPoints(lastFiveSeasons, 'assistsPerGame')"
              class="trend-line assists"
              fill="none"
            />
          </svg>
          <div class="chart-legend">
            <div class="legend-item">
              <div class="legend-color points"></div>
              <span>Points</span>
            </div>
            <div class="legend-item">
              <div class="legend-color rebounds"></div>
              <span>Rebounds</span>
            </div>
            <div class="legend-item">
              <div class="legend-color assists"></div>
              <span>Assists</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Career Stats -->
    <div v-if="activeTab === 'career'" class="stats-section">
      <div class="section-header">
        <h2>Career Statistics</h2>
        <div class="career-meta">
          <span class="career-span">{{ careerYears }} seasons</span>
          <span class="total-games">{{ careerStats.totalGames }} total games</span>
        </div>
      </div>
      
      <div class="career-overview">
        <div class="career-totals">
          <h3>Career Totals</h3>
          <div class="totals-grid">
            <div class="total-stat">
              <div class="total-value">{{ careerStats.totalPoints }}</div>
              <div class="total-label">Points</div>
            </div>
            <div class="total-stat">
              <div class="total-value">{{ careerStats.totalRebounds }}</div>
              <div class="total-label">Rebounds</div>
            </div>
            <div class="total-stat">
              <div class="total-value">{{ careerStats.totalAssists }}</div>
              <div class="total-label">Assists</div>
            </div>
            <div class="total-stat">
              <div class="total-value">{{ careerStats.totalSteals }}</div>
              <div class="total-label">Steals</div>
            </div>
          </div>
        </div>

        <div class="career-averages">
          <h3>Career Averages</h3>
          <div class="averages-grid">
            <div class="avg-stat">
              <div class="avg-value">{{ careerStats.avgPointsPerGame }}</div>
              <div class="avg-label">PPG</div>
            </div>
            <div class="avg-stat">
              <div class="avg-value">{{ careerStats.avgReboundsPerGame }}</div>
              <div class="avg-label">RPG</div>
            </div>
            <div class="avg-stat">
              <div class="avg-value">{{ careerStats.avgAssistsPerGame }}</div>
              <div class="avg-label">APG</div>
            </div>
            <div class="avg-stat">
              <div class="avg-value">{{ careerStats.avgFieldGoalPercentage }}%</div>
              <div class="avg-label">FG%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Career Milestones -->
      <div class="career-milestones">
        <h3>Career Milestones</h3>
        <div class="milestones-list">
          <div 
            v-for="milestone in careerMilestones" 
            :key="milestone.id"
            class="milestone-item"
            :class="{ achieved: milestone.achieved }"
          >
            <div class="milestone-icon">
              <Icon :name="milestone.achieved ? 'check-circle' : 'circle'" />
            </div>
            <div class="milestone-content">
              <div class="milestone-title">{{ milestone.title }}</div>
              <div class="milestone-progress">
                {{ milestone.current }} / {{ milestone.target }}
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: `${(milestone.current / milestone.target) * 100}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Team History -->
      <div class="team-history">
        <h3>Team History</h3>
        <div class="teams-timeline">
          <div 
            v-for="teamPeriod in teamHistory" 
            :key="teamPeriod.id"
            class="team-period"
            :class="{ active: teamPeriod.isCurrent }"
          >
            <div class="team-logo" v-if="teamPeriod.logo">
              <img :src="teamPeriod.logo" :alt="teamPeriod.team" />
            </div>
            <div class="team-info">
              <div class="team-name">{{ teamPeriod.team }}</div>
              <div class="team-period-years">{{ teamPeriod.years }}</div>
              <div class="team-stats">
                {{ teamPeriod.games }} games, {{ teamPeriod.avgPoints }} PPG
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Advanced Stats -->
    <div v-if="activeTab === 'advanced'" class="stats-section">
      <div class="section-header">
        <h2>Advanced Analytics</h2>
        <p class="section-description">Deep dive into performance metrics</p>
      </div>
      
      <!-- Efficiency Metrics -->
      <div class="advanced-stats-grid">
        <div class="advanced-stat-card">
          <div class="stat-title">Player Efficiency Rating</div>
          <div class="stat-value large">{{ advancedStats.per }}</div>
          <div class="stat-context">League Avg: 15.0</div>
        </div>
        
        <div class="advanced-stat-card">
          <div class="stat-title">True Shooting %</div>
          <div class="stat-value large">{{ advancedStats.trueShootingPercentage }}%</div>
          <div class="stat-context">Accounts for 3PT and FT</div>
        </div>
        
        <div class="advanced-stat-card">
          <div class="stat-title">Usage Rate</div>
          <div class="stat-value large">{{ advancedStats.usageRate }}%</div>
          <div class="stat-context">Team possessions used</div>
        </div>
        
        <div class="advanced-stat-card">
          <div class="stat-title">Win Shares</div>
          <div class="stat-value large">{{ advancedStats.winShares }}</div>
          <div class="stat-context">Contribution to team wins</div>
        </div>
      </div>

      <!-- Shot Chart -->
      <div class="shot-chart-section">
        <h3>Shot Chart (Current Season)</h3>
        <div class="shot-chart">
          <!-- Basketball court SVG with shot data -->
          <svg class="court-svg" viewBox="0 0 400 300">
            <!-- Court outline -->
            <rect x="50" y="50" width="300" height="200" class="court-outline" fill="none" stroke="#ccc" stroke-width="2"/>
            <!-- Three-point line -->
            <path d="M 50 100 Q 200 60 350 100 L 350 200 Q 200 240 50 200 Z" class="three-point-line" fill="none" stroke="#ccc" stroke-width="2"/>
            <!-- Free throw line -->
            <rect x="150" y="50" width="100" height="80" class="free-throw-area" fill="none" stroke="#ccc" stroke-width="1"/>
            
            <!-- Shot markers -->
            <circle 
              v-for="shot in shotChartData" 
              :key="shot.id"
              :cx="shot.x" 
              :cy="shot.y" 
              :r="4"
              :class="['shot-marker', shot.made ? 'made' : 'missed']"
              :title="`${shot.distance}ft ${shot.made ? 'Made' : 'Missed'}`"
            />
          </svg>
          
          <div class="shot-chart-legend">
            <div class="legend-item">
              <div class="shot-marker made"></div>
              <span>Made Shot</span>
            </div>
            <div class="legend-item">
              <div class="shot-marker missed"></div>
              <span>Missed Shot</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'

interface PlayerStats {
  games: number
  pointsPerGame: number
  reboundsPerGame: number
  assistsPerGame: number
  fieldGoalPercentage: number
  threePointPercentage: number
  freeThrowPercentage: number
  pointsTrend?: 'up' | 'down' | 'stable'
  pointsChange?: string
}

interface SeasonStats extends PlayerStats {
  season: string
  team: string
  isCurrent?: boolean
}

interface RecentGame {
  opponent: string
  points: number
  rebounds: number
  assists: number
  date: string
}

interface CareerStats {
  totalGames: number
  totalPoints: number
  totalRebounds: number
  totalAssists: number
  totalSteals: number
  avgPointsPerGame: number
  avgReboundsPerGame: number
  avgAssistsPerGame: number
  avgFieldGoalPercentage: number
}

interface Milestone {
  id: string
  title: string
  current: number
  target: number
  achieved: boolean
}

interface TeamPeriod {
  id: string
  team: string
  years: string
  games: number
  avgPoints: number
  logo?: string
  isCurrent: boolean
}

interface AdvancedStats {
  per: number
  trueShootingPercentage: number
  usageRate: number
  winShares: number
}

interface ShotData {
  id: string
  x: number
  y: number
  distance: number
  made: boolean
}

// Props
const props = defineProps<{
  playerId: string
  playerName: string
  currentTeam: string
  position?: string
  jerseyNumber?: number
  playerPhoto?: string
}>()

// ...existing code...
const editableNumber = ref(props.jerseyNumber || 0)
const editablePosition = ref(props.position || 'GUARD')
watch(() => props.jerseyNumber, (val) => { editableNumber.value = val || 0 })
watch(() => props.position, (val) => { editablePosition.value = val || 'GUARD' })

// Reactive state
const activeTab = ref('current')
const lastUpdated = ref(new Date().toLocaleDateString())

// Tabs configuration
const statsTabs = [
  { key: 'current', label: 'Current Season' },
  { key: 'recent', label: 'Last 5 Seasons' },
  { key: 'career', label: 'Career' },
  { key: 'advanced', label: 'Advanced' }
]

// Mock data - replace with real API calls
const currentStats = ref<PlayerStats>({
  games: 8,
  pointsPerGame: 18.5,
  reboundsPerGame: 7.2,
  assistsPerGame: 4.1,
  fieldGoalPercentage: 47.8,
  threePointPercentage: 38.5,
  freeThrowPercentage: 82.1,
  pointsTrend: 'up',
  pointsChange: '+2.3'
})

const recentGames = ref<RecentGame[]>([
  { opponent: 'BBC Bayreuth', points: 22, rebounds: 8, assists: 5, date: '2025-09-28' },
  { opponent: 'BBC Coburg', points: 15, rebounds: 6, assists: 3, date: '2025-09-25' },
  { opponent: 'RSC Oberhaid', points: 20, rebounds: 9, assists: 4, date: '2025-09-22' },
  { opponent: 'SV Pettstadt', points: 18, rebounds: 5, assists: 6, date: '2025-09-19' },
  { opponent: 'TSG Bamberg', points: 17, rebounds: 7, assists: 2, date: '2025-09-16' }
])

const lastFiveSeasons = ref<SeasonStats[]>([
  {
    season: '2025/26',
    team: 'BG Litzendorf',
    games: 8,
    pointsPerGame: 18.5,
    reboundsPerGame: 7.2,
    assistsPerGame: 4.1,
    fieldGoalPercentage: 47.8,
    threePointPercentage: 38.5,
    freeThrowPercentage: 82.1,
    isCurrent: true
  },
  {
    season: '2024/25',
    team: 'BG Litzendorf',
    games: 26,
    pointsPerGame: 16.2,
    reboundsPerGame: 6.8,
    assistsPerGame: 3.9,
    fieldGoalPercentage: 45.2,
    threePointPercentage: 35.1,
    freeThrowPercentage: 78.9
  },
  {
    season: '2023/24',
    team: 'BG Litzendorf',
    games: 24,
    pointsPerGame: 15.8,
    reboundsPerGame: 6.5,
    assistsPerGame: 3.2,
    fieldGoalPercentage: 44.1,
    threePointPercentage: 33.8,
    freeThrowPercentage: 76.4
  },
  {
    season: '2022/23',
    team: 'RSC Oberhaid',
    games: 22,
    pointsPerGame: 14.1,
    reboundsPerGame: 5.9,
    assistsPerGame: 2.8,
    fieldGoalPercentage: 42.8,
    threePointPercentage: 31.2,
    freeThrowPercentage: 74.1
  },
  {
    season: '2021/22',
    team: 'RSC Oberhaid',
    games: 20,
    pointsPerGame: 12.3,
    reboundsPerGame: 5.1,
    assistsPerGame: 2.1,
    fieldGoalPercentage: 41.2,
    threePointPercentage: 28.9,
    freeThrowPercentage: 71.8
  }
])

const careerStats = ref<CareerStats>({
  totalGames: 150,
  totalPoints: 2247,
  totalRebounds: 945,
  totalAssists: 483,
  totalSteals: 187,
  avgPointsPerGame: 15.0,
  avgReboundsPerGame: 6.3,
  avgAssistsPerGame: 3.2,
  avgFieldGoalPercentage: 44.1
})

const careerMilestones = ref<Milestone[]>([
  { id: '1', title: '1,000 Career Points', current: 2247, target: 1000, achieved: true },
  { id: '2', title: '2,500 Career Points', current: 2247, target: 2500, achieved: false },
  { id: '3', title: '1,000 Career Rebounds', current: 945, target: 1000, achieved: false },
  { id: '4', title: '500 Career Assists', current: 483, target: 500, achieved: false },
  { id: '5', title: '200 Career Games', current: 150, target: 200, achieved: false }
])

const teamHistory = ref<TeamPeriod[]>([
  {
    id: '1',
    team: 'BG Litzendorf',
    years: '2023-Present',
    games: 58,
    avgPoints: 17.1,
    isCurrent: true
  },
  {
    id: '2',
    team: 'RSC Oberhaid',
    years: '2021-2023',
    games: 92,
    avgPoints: 13.2,
    isCurrent: false
  }
])

const advancedStats = ref<AdvancedStats>({
  per: 18.7,
  trueShootingPercentage: 58.2,
  usageRate: 24.1,
  winShares: 2.3
})

const shotChartData = ref<ShotData[]>([
  { id: '1', x: 100, y: 80, distance: 15, made: true },
  { id: '2', x: 120, y: 90, distance: 18, made: false },
  { id: '3', x: 200, y: 70, distance: 22, made: true },
  { id: '4', x: 280, y: 85, distance: 20, made: true },
  { id: '5', x: 300, y: 95, distance: 24, made: false },
  // Add more shot data...
])

// Computed properties
const maxRecentPoints = computed(() => {
  return Math.max(...recentGames.value.map(game => game.points))
})

const careerYears = computed(() => {
  const startYear = 2021
  const currentYear = new Date().getFullYear()
  return currentYear - startYear + 1
})

// Methods
const getTrendIcon = (trend: string) => {
  switch (trend) {
    case 'up': return 'arrow-up'
    case 'down': return 'arrow-down'
    default: return 'minus'
  }
}

const getChartPoints = (seasons: SeasonStats[], statKey: keyof PlayerStats) => {
  const points = seasons.map((season, index) => {
    const x = (index / (seasons.length - 1)) * 350 + 25
    const maxStat = Math.max(...seasons.map(s => s[statKey] as number))
    const y = 180 - ((season[statKey] as number / maxStat) * 160)
    return `${x},${y}`
  })
  return points.join(' ')
}

// Lifecycle
onMounted(() => {
  // Load player data
  // TODO: Replace with real API calls
})
</script>

<style scoped>
.player-profile-stats {
  @apply max-w-6xl mx-auto p-6 space-y-8;
}

.player-header {
  @apply flex items-center justify-between bg-white rounded-lg shadow-md p-6;
}

.player-info {
  @apply flex-1;
}

.player-name {
  @apply text-3xl font-bold text-gray-900 mb-2;
}

.player-meta {
  @apply flex items-center space-x-4 text-gray-600;
}

.current-team {
  @apply text-lg font-medium text-blue-600;
}

.position, .jersey-number {
  @apply px-2 py-1 bg-gray-100 rounded text-sm;
}

.player-photo img {
  @apply w-24 h-24 rounded-full object-cover border-4 border-gray-200;
}

.stats-tabs {
  @apply flex space-x-1 bg-gray-100 rounded-lg p-1;
}

.tab-button {
  @apply flex-1 py-2 px-4 rounded-md text-sm font-medium text-gray-600 transition-colors;
}

.tab-button.active {
  @apply bg-white text-blue-600 shadow-sm;
}

.stats-section {
  @apply bg-white rounded-lg shadow-md p-6;
}

.section-header {
  @apply mb-6;
}

.section-header h2 {
  @apply text-2xl font-bold text-gray-900 mb-2;
}

.season-meta, .career-meta {
  @apply flex items-center space-x-4 text-gray-600;
}

.stats-grid {
  @apply grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8;
}

.stat-card {
  @apply bg-gray-50 rounded-lg p-4 text-center;
}

.stat-card.primary {
  @apply bg-blue-50 border border-blue-200;
}

.stat-value {
  @apply text-2xl font-bold text-gray-900;
}

.stat-label {
  @apply text-sm text-gray-600 mt-1;
}

.stat-trend {
  @apply flex items-center justify-center space-x-1 text-xs mt-2;
}

.stat-trend.up {
  @apply text-green-600;
}

.stat-trend.down {
  @apply text-red-600;
}

.recent-games {
  @apply mt-8;
}

.recent-games h3 {
  @apply text-lg font-semibold text-gray-900 mb-4;
}

.games-chart {
  @apply flex items-end space-x-2 h-32 bg-gray-50 rounded-lg p-4;
}

.game-bar {
  @apply flex-1 bg-blue-500 rounded-t-sm relative cursor-pointer transition-colors hover:bg-blue-600;
  min-height: 20px;
}

.game-points {
  @apply absolute -top-6 left-1/2 transform -translate-x-1/2 text-xs font-semibold;
}

.game-opponent {
  @apply absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 whitespace-nowrap;
}

.seasons-table {
  @apply overflow-x-auto mb-8;
}

.seasons-table table {
  @apply w-full;
}

.seasons-table th {
  @apply px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b;
}

.seasons-table td {
  @apply px-4 py-4 whitespace-nowrap text-sm text-gray-900 border-b;
}

.seasons-table tr.current-season {
  @apply bg-blue-50;
}

.stat-highlight {
  @apply font-semibold text-blue-600;
}

.trends-chart {
  @apply mt-8;
}

.trends-chart h3 {
  @apply text-lg font-semibold text-gray-900 mb-4;
}

.chart-container {
  @apply bg-gray-50 rounded-lg p-4;
}

.trend-svg {
  @apply w-full h-48;
}

.trend-line {
  @apply stroke-2;
}

.trend-line.points {
  @apply stroke-blue-500;
}

.trend-line.rebounds {
  @apply stroke-green-500;
}

.trend-line.assists {
  @apply stroke-purple-500;
}

.chart-legend {
  @apply flex justify-center space-x-6 mt-4;
}

.legend-item {
  @apply flex items-center space-x-2;
}

.legend-color {
  @apply w-4 h-0.5;
}

.legend-color.points {
  @apply bg-blue-500;
}

.legend-color.rebounds {
  @apply bg-green-500;
}

.legend-color.assists {
  @apply bg-purple-500;
}

.career-overview {
  @apply grid md:grid-cols-2 gap-8 mb-8;
}

.totals-grid, .averages-grid {
  @apply grid grid-cols-2 gap-4;
}

.total-stat, .avg-stat {
  @apply text-center bg-gray-50 rounded-lg p-4;
}

.total-value, .avg-value {
  @apply text-2xl font-bold text-gray-900;
}

.total-label, .avg-label {
  @apply text-sm text-gray-600 mt-1;
}

.career-milestones h3 {
  @apply text-lg font-semibold text-gray-900 mb-4;
}

.milestones-list {
  @apply space-y-4;
}

.milestone-item {
  @apply flex items-center space-x-4 p-4 bg-gray-50 rounded-lg;
}

.milestone-item.achieved {
  @apply bg-green-50;
}

.milestone-icon {
  @apply text-gray-400;
}

.milestone-item.achieved .milestone-icon {
  @apply text-green-500;
}

.milestone-content {
  @apply flex-1;
}

.milestone-title {
  @apply font-medium text-gray-900;
}

.milestone-progress {
  @apply text-sm text-gray-600 mt-1;
}

.progress-bar {
  @apply w-full bg-gray-200 rounded-full h-2 mt-2;
}

.progress-fill {
  @apply bg-blue-500 h-2 rounded-full transition-all duration-300;
}

.team-history h3 {
  @apply text-lg font-semibold text-gray-900 mb-4;
}

.teams-timeline {
  @apply space-y-4;
}

.team-period {
  @apply flex items-center space-x-4 p-4 bg-gray-50 rounded-lg;
}

.team-period.active {
  @apply bg-blue-50 border border-blue-200;
}

.team-logo img {
  @apply w-12 h-12 rounded-full object-cover;
}

.team-name {
  @apply font-medium text-gray-900;
}

.team-period-years {
  @apply text-sm text-gray-600;
}

.team-stats {
  @apply text-sm text-gray-500;
}

.advanced-stats-grid {
  @apply grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8;
}

.advanced-stat-card {
  @apply bg-gray-50 rounded-lg p-6 text-center;
}

.stat-title {
  @apply text-sm font-medium text-gray-600 mb-2;
}

.stat-value.large {
  @apply text-3xl font-bold text-gray-900;
}

.stat-context {
  @apply text-xs text-gray-500 mt-1;
}

.shot-chart-section h3 {
  @apply text-lg font-semibold text-gray-900 mb-4;
}

.shot-chart {
  @apply bg-gray-50 rounded-lg p-4;
}

.court-svg {
  @apply w-full h-64;
}

.shot-marker {
  @apply cursor-pointer;
}

.shot-marker.made {
  @apply fill-green-500 stroke-green-600;
}

.shot-marker.missed {
  @apply fill-red-500 stroke-red-600;
}

.shot-chart-legend {
  @apply flex justify-center space-x-6 mt-4;
}

.shot-chart-legend .legend-item {
  @apply flex items-center space-x-2;
}

.shot-chart-legend .shot-marker {
  @apply w-3 h-3 rounded-full;
}
</style>
