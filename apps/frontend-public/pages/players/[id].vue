<template>
  <div class="player-profile-page">
    <!-- Breadcrumb Navigation -->
    <nav class="breadcrumb">
      <NuxtLink to="/" class="breadcrumb-link">Home</NuxtLink>
      <span class="breadcrumb-separator">/</span>
      <NuxtLink to="/players" class="breadcrumb-link">Players</NuxtLink>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-current">{{ playerData?.name }}</span>
    </nav>

    <!-- Loading State -->
    <div v-if="pending" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading player data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <h2>Player Not Found</h2>
      <p>Sorry, we couldn't find data for this player.</p>
      <NuxtLink to="/players" class="back-link">← Back to Players</NuxtLink>
    </div>

    <!-- Player Profile -->
    <div v-else-if="playerData" class="player-content">
      <!-- Player Profile Stats Component -->
      <PlayerProfileStats
        :player-id="playerData.id"
        :player-name="playerData.name"
        :current-team="playerData.currentTeam"
        :position="playerData.position"
        :jersey-number="playerData.jerseyNumber"
        :player-photo="playerData.photo"
      />

      <!-- Additional Context -->
      <div class="additional-info">
        <!-- Recent News/Updates -->
        <div class="news-section">
          <h3>Recent Updates</h3>
          <div class="news-list">
            <div v-for="update in recentUpdates" :key="update.id" class="news-item">
              <div class="news-date">{{ formatDate(update.date) }}</div>
              <div class="news-content">{{ update.content }}</div>
            </div>
          </div>
        </div>

        <!-- Similar Players -->
        <div class="similar-players-section">
          <h3>Similar Players</h3>
          <div class="similar-players">
            <NuxtLink
              v-for="similar in similarPlayers"
              :key="similar.id"
              :to="`/players/${similar.id}`"
              class="similar-player-card"
            >
              <div class="similar-player-name">{{ similar.name }}</div>
              <div class="similar-player-team">{{ similar.team }}</div>
              <div class="similar-player-stats">
                {{ similar.ppg }} PPG, {{ similar.rpg }} RPG
              </div>
            </NuxtLink>
          </div>
        </div>

        <!-- Team Context -->
        <div class="team-context">
          <h3>Current Team</h3>
          <NuxtLink :to="`/teams/${playerData.teamId}`" class="team-card">
            <div class="team-logo" v-if="playerData.teamLogo">
              <img :src="playerData.teamLogo" :alt="playerData.currentTeam" />
            </div>
            <div class="team-info">
              <div class="team-name">{{ playerData.currentTeam }}</div>
              <div class="team-league">{{ playerData.league }}</div>
              <div class="team-record">{{ playerData.teamRecord }}</div>
            </div>
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Define the page metadata
definePageMeta({
  title: 'Player Profile',
  description: 'Detailed player statistics and performance analysis'
})

// Get the player ID from the route
const route = useRoute()
const playerId = route.params.id as string

// Player data interface
interface PlayerData {
  id: string
  name: string
  currentTeam: string
  teamId: string
  teamLogo?: string
  league: string
  teamRecord: string
  position?: string
  jerseyNumber?: number
  photo?: string
}

interface RecentUpdate {
  id: string
  date: string
  content: string
}

interface SimilarPlayer {
  id: string
  name: string
  team: string
  ppg: number
  rpg: number
}

// Reactive data
const pending = ref(false)
const error = ref(false)

// Mock player data - replace with real API call
const playerData = ref<PlayerData>({
  id: playerId,
  name: 'Max Mustermann',
  currentTeam: 'BG Litzendorf',
  teamId: 'bg-litzendorf',
  teamLogo: '/images/teams/bg-litzendorf-logo.png',
  league: 'Bezirksoberliga Herren',
  teamRecord: '12-4 (1st Place)',
  position: 'Small Forward',
  jerseyNumber: 23,
  photo: '/images/players/max-mustermann.jpg'
})

const recentUpdates = ref<RecentUpdate[]>([
  {
    id: '1',
    date: '2025-09-28',
    content: 'Scored career-high 28 points in win against BBC Bayreuth'
  },
  {
    id: '2',
    date: '2025-09-25',
    content: 'Named Player of the Week for outstanding performance'
  },
  {
    id: '3',
    date: '2025-09-20',
    content: 'Reached 2,000 career points milestone'
  }
])

const similarPlayers = ref<SimilarPlayer[]>([
  { id: 'p2', name: 'Stefan Schmidt', team: 'BBC Bayreuth', ppg: 17.8, rpg: 6.9 },
  { id: 'p3', name: 'Michael Weber', team: 'RSC Oberhaid', ppg: 18.2, rpg: 7.1 },
  { id: 'p4', name: 'Andreas Müller', team: 'BBC Coburg', ppg: 16.5, rpg: 6.8 }
])

// Methods
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('de-DE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// SEO and meta
useHead({
  title: `${playerData.value?.name} - Player Profile`,
  meta: [
    {
      name: 'description',
      content: `Detailed statistics and performance analysis for ${playerData.value?.name} of ${playerData.value?.currentTeam}`
    },
    {
      property: 'og:title',
      content: `${playerData.value?.name} - Basketball Stats`
    },
    {
      property: 'og:description',
      content: `View comprehensive statistics including current season, last 5 seasons, and career totals for ${playerData.value?.name}`
    }
  ]
})

// Data fetching (replace with real API)
// Try fetching real player data from API, otherwise use mock above
try {
  const config = useRuntimeConfig()
  const { data, pending: p, error: e } = await useFetch(`${config.public.apiBase}/api/players/${playerId}`, {
    key: `player-${playerId}`
  })

  if (data && data.value) {
    // Map API shape to local interface (best effort)
    const d: any = data.value
    playerData.value = {
      id: d.id || playerData.value.id,
      name: d.name || d.full_name || playerData.value.name,
      currentTeam: d.current_team || d.team || playerData.value.currentTeam,
      teamId: d.team_id || playerData.value.teamId,
      teamLogo: d.team_logo || playerData.value.teamLogo,
      league: d.league || playerData.value.league,
      teamRecord: d.team_record || playerData.value.teamRecord,
      position: d.position || playerData.value.position,
      jerseyNumber: d.jersey_number || playerData.value.jerseyNumber,
      photo: d.photo || playerData.value.photo
    }
  }
} catch (e) {
  console.warn('Live API player fetch failed, using mock data:', e)
}
</script>

<style scoped>
.player-profile-page {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 1rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
  padding: 0 1rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.breadcrumb-link {
  color: #3b82f6;
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: #1d4ed8;
}

.breadcrumb-separator {
  margin: 0 0.5rem;
}

.breadcrumb-current {
  color: #374151;
  font-weight: 500;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 50vh;
  color: #6b7280;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-container {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.error-container h2 {
  color: #374151;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.back-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  margin-top: 1rem;
  display: inline-block;
}

.back-link:hover {
  color: #1d4ed8;
}

.player-content {
  max-width: 80rem;
  margin: 0 auto;
}

.additional-info {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 2rem;
  margin-top: 2rem;
}

@media (max-width: 1024px) {
  .additional-info {
    grid-template-columns: 1fr;
  }
}

.news-section,
.similar-players-section,
.team-context {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.news-section h3,
.similar-players-section h3,
.team-context h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
}

.news-list {
  space-y: 1rem;
}

.news-item {
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.news-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.news-date {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.news-content {
  font-size: 0.875rem;
  color: #374151;
  line-height: 1.5;
}

.similar-players {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.similar-player-card {
  display: block;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 0.375rem;
  text-decoration: none;
  transition: background-color 0.2s;
}

.similar-player-card:hover {
  background: #f3f4f6;
}

.similar-player-name {
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.25rem;
}

.similar-player-team {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.similar-player-stats {
  font-size: 0.75rem;
  color: #9ca3af;
}

.team-card {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  text-decoration: none;
  transition: background-color 0.2s;
}

.team-card:hover {
  background: #f3f4f6;
}

.team-logo {
  margin-right: 1rem;
}

.team-logo img {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  object-fit: cover;
}

.team-name {
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.25rem;
}

.team-league {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.team-record {
  font-size: 0.75rem;
  color: #9ca3af;
}
</style>
