<template>
  <div class="basketball-card" :style="{ width: cardWidth + 'px', height: cardHeight + 'px' }">
    <!-- Card Border & Background -->
    <div class="card-border">
      <!-- Top Header with Number -->
      <div class="card-number">{{ player.number || '23' }}</div>
      
      <!-- Main Photo Area -->
      <div class="photo-area">
        <div class="photo-frame">
          <!-- Placeholder Basketball Player Image -->
          <div class="player-image">
            <div class="player-silhouette">
              🏀
            </div>
          </div>
        </div>
        
        <!-- Team Logo Area -->
        <div class="team-logo">
          <div class="team-logo-circle">
            <span class="team-initials">{{ getTeamInitials(player.team) }}</span>
          </div>
        </div>
      </div>
      
      <!-- Player Name Banner -->
      <div class="name-banner">
        <div class="player-name">{{ player.name || 'BASKETBALL PLAYER' }}</div>
      </div>
      
      <!-- Player Info Section -->
      <div class="player-info">
        <div class="info-line">
          <span class="label">Team:</span>
          <span class="value">{{ player.team || 'Basketball Team' }}</span>
        </div>
        <div class="info-line">
          <span class="label">Liga:</span>
          <span class="value">{{ player.liga_id || 'N/A' }}</span>
        </div>
        <div class="info-line">
          <span class="label">Saison:</span>
          <span class="value">{{ player.season_id || '2018' }}/{{ (player.season_id || 2018) + 1 }}</span>
        </div>
      </div>
      
      <!-- Statistics Table -->
      <div class="stats-table">
        <div class="stats-header">
          <span class="year">SAISON</span>
          <span class="team">TEAM</span>
          <span class="gp">GP</span>
          <span class="pts">PTS</span>
          <span class="avg">AVG</span>
          <span class="pct">PCT</span>
        </div>
        <div class="stats-row">
          <span class="year">{{ player.season_id || '2018' }}-{{ ((player.season_id || 2018) + 1).toString().slice(-2) }}</span>
          <span class="team">{{ getTeamInitials(player.team) }}</span>
          <span class="gp">{{ player.games || 'N/A' }}</span>
          <span class="pts">{{ player.points || '0' }}</span>
          <span class="avg">{{ player.average ? player.average.toFixed(1) : 'N/A' }}</span>
          <span class="pct">{{ formatPercentage(player) }}</span>
        </div>
      </div>
      
      <!-- League Logo & Description -->
      <div class="league-info">
        <div class="league-logo">
          <div class="bbl-logo">BBL</div>
        </div>
        <div class="description">
          {{ getPlayerDescription(player) }}
        </div>
      </div>
      
      <!-- Guard Element (Red stripe) -->
      <div class="guard-stripe">GUARD</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  player: {
    type: Object,
    required: true
  },
  cardWidth: {
    type: Number,
    default: 300
  },
  cardHeight: {
    type: Number,
    default: 420
  }
})

const getTeamInitials = (teamName) => {
  if (!teamName) return 'BBT'
  
  return teamName
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .substring(0, 3)
    .toUpperCase()
}

const formatPercentage = (player) => {
  if (!player.average) return 'N/A'
  
  // If it's a shooting percentage category, format as percentage
  if (player.endpoint === 'statBesteFreiWerferArchiv' || player.endpoint === 'statBeste3erWerferArchiv') {
    return player.average.toFixed(1) + '%'
  }
  
  // Otherwise, calculate a mock shooting percentage based on performance
  const mockPercentage = Math.min(95, Math.max(25, (player.average || 10) * 4))
  return mockPercentage.toFixed(1) + '%'
}

const getPlayerDescription = (player) => {
  const category = player.endpoint || 'statBesteWerferArchiv'
  const teamName = player.team || 'Basketball Team'
  const performance = player.average || 0
  
  let description = `Spieler aus ${teamName.split(' ')[0]}. `
  
  switch (category) {
    case 'statBesteFreiWerferArchiv':
      description += `Starker Freiwurfschütze mit ${performance.toFixed(1)}% Trefferquote.`
      break
    case 'statBeste3erWerferArchiv':
      description += `Zuverlässiger 3-Punkte-Schütze mit ${performance.toFixed(1)}% Quote.`
      break
    default:
      description += `Scorer mit ${performance.toFixed(1)} Punkten pro Spiel.`
  }
  
  return description
}
</script>

<style scoped>
.basketball-card {
  position: relative;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  font-family: 'Arial', sans-serif;
  margin: 10px;
}

.card-border {
  width: 100%;
  height: 100%;
  padding: 8px;
  background: linear-gradient(145deg, #ffffff, #f1f3f4);
  border: 2px solid #c41e3a;
  position: relative;
}

.card-number {
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 24px;
  font-weight: bold;
  color: #000;
  z-index: 10;
}

.photo-area {
  position: relative;
  height: 45%;
  margin: 25px 8px 8px 8px;
  background: linear-gradient(45deg, #2c3e50, #34495e);
  border-radius: 8px;
  overflow: hidden;
}

.photo-frame {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.player-image {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.player-silhouette {
  font-size: 48px;
  opacity: 0.7;
  filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
}

.team-logo {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 40px;
  height: 40px;
}

.team-logo-circle {
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #c41e3a, #8b1a1a);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.team-initials {
  color: white;
  font-size: 10px;
  font-weight: bold;
}

.name-banner {
  background: linear-gradient(90deg, #c41e3a, #8b1a1a);
  color: white;
  text-align: center;
  padding: 6px;
  margin: 4px 8px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.player-name {
  font-size: 14px;
  font-weight: bold;
  letter-spacing: 1px;
  text-transform: uppercase;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}

.player-info {
  padding: 8px 12px;
  background: rgba(255,255,255,0.9);
  margin: 4px 8px;
  border-radius: 4px;
  border-left: 4px solid #c41e3a;
}

.info-line {
  display: flex;
  justify-content: space-between;
  margin: 2px 0;
  font-size: 11px;
}

.label {
  font-weight: bold;
  color: #2c3e50;
}

.value {
  color: #34495e;
}

.stats-table {
  margin: 4px 8px;
  background: white;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #ddd;
}

.stats-header, .stats-row {
  display: grid;
  grid-template-columns: 1.2fr 1fr 0.7fr 0.7fr 0.7fr 0.8fr;
  gap: 2px;
  font-size: 9px;
  text-align: center;
}

.stats-header {
  background: linear-gradient(90deg, #2c3e50, #34495e);
  color: white;
  font-weight: bold;
  padding: 3px 2px;
}

.stats-row {
  padding: 3px 2px;
  border-top: 1px solid #eee;
  background: #f8f9fa;
}

.league-info {
  position: absolute;
  bottom: 8px;
  left: 8px;
  right: 8px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.league-logo {
  flex-shrink: 0;
}

.bbl-logo {
  background: linear-gradient(45deg, #2c3e50, #34495e);
  color: white;
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.description {
  flex: 1;
  font-size: 8px;
  line-height: 1.3;
  color: #2c3e50;
  background: rgba(255,255,255,0.9);
  padding: 4px 6px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.guard-stripe {
  position: absolute;
  top: 50px;
  right: 0;
  background: linear-gradient(90deg, #c41e3a, #8b1a1a);
  color: white;
  padding: 2px 8px;
  font-size: 10px;
  font-weight: bold;
  letter-spacing: 1px;
  transform: rotate(90deg);
  transform-origin: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .basketball-card {
    transform: scale(0.9);
  }
}
</style>
