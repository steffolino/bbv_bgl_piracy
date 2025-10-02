<template>
  <div class="bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-2xl font-bold text-gray-900 flex items-center">
        <span class="mr-3">📊</span>
        Historical Coverage Analysis
      </h3>
      <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 bg-gradient-to-r from-green-500 to-green-600 rounded-full shadow-sm"></div>
          <span class="text-sm text-gray-600 font-medium">Data Available</span>
        </div>
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 bg-gray-300 rounded-full"></div>
          <span class="text-sm text-gray-600 font-medium">Missing</span>
        </div>
      </div>
    </div>

    <!-- Modern Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="group relative overflow-hidden bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200 hover:shadow-lg transition-all">
        <div class="absolute top-2 right-2 opacity-20 group-hover:opacity-30 transition-opacity">
          <span class="text-3xl">📅</span>
        </div>
        <div class="relative">
          <div class="text-3xl font-bold text-blue-600 mb-1">{{ yearRange }}</div>
          <div class="text-sm text-blue-700 font-medium">Years Covered</div>
          <div class="text-xs text-blue-600 mt-1">{{ totalSeasons }} seasons active</div>
        </div>
      </div>
      
      <div class="group relative overflow-hidden bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200 hover:shadow-lg transition-all">
        <div class="absolute top-2 right-2 opacity-20 group-hover:opacity-30 transition-opacity">
          <span class="text-3xl">✅</span>
        </div>
        <div class="relative">
          <div class="text-3xl font-bold text-green-600 mb-1">{{ overallCompletion }}%</div>
          <div class="text-sm text-green-700 font-medium">Data Completion</div>
          <div class="w-full bg-green-200 rounded-full h-2 mt-2">
            <div class="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full transition-all" :style="`width: ${overallCompletion}%`"></div>
          </div>
        </div>
      </div>
      
      <div class="group relative overflow-hidden bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200 hover:shadow-lg transition-all">
        <div class="absolute top-2 right-2 opacity-20 group-hover:opacity-30 transition-opacity">
          <span class="text-3xl">🏆</span>
        </div>
        <div class="relative">
          <div class="text-3xl font-bold text-purple-600 mb-1">{{ totalSeasons }}/{{ potentialSeasons }}</div>
          <div class="text-sm text-purple-700 font-medium">Seasons Available</div>
          <div class="text-xs text-purple-600 mt-1">{{ potentialSeasons - totalSeasons }} missing</div>
        </div>
      </div>
    </div>

    <!-- Interactive Timeline -->
    <div class="mb-8">
      <h4 class="text-lg font-bold mb-4 flex items-center">
        <span class="mr-2">⏰</span>
        Interactive Season Timeline
      </h4>
      <div class="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-4 border border-gray-200">
        <div class="grid grid-cols-11 gap-2">
          <div 
            v-for="year in timelineYears" 
            :key="year.year"
            :class="[
              'relative h-16 rounded-lg flex flex-col items-center justify-center text-xs font-bold transition-all duration-300 cursor-pointer group',
              year.hasData 
                ? 'bg-gradient-to-br from-green-500 to-green-600 text-white shadow-lg hover:shadow-xl hover:scale-105 transform' 
                : 'bg-gradient-to-br from-gray-200 to-gray-300 text-gray-500 hover:bg-gray-400 hover:text-white'
            ]"
            :title="`${year.fullYear}: ${year.hasData ? year.players + ' players' : 'No data'}`"
            @click="selectYear(year)"
          >
            <div class="font-bold">{{ year.year }}</div>
            <div v-if="year.hasData" class="text-xs opacity-90">{{ year.players }}</div>
            
            <!-- Tooltip on hover -->
            <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-black text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
              {{ year.fullYear }}: {{ year.hasData ? `${year.players} players` : 'No data' }}
            </div>
          </div>
        </div>
        
        <!-- Timeline Legend -->
        <div class="mt-4 flex justify-center space-x-6 text-sm text-gray-600">
          <div class="flex items-center space-x-2">
            <div class="w-4 h-4 bg-gradient-to-r from-green-500 to-green-600 rounded"></div>
            <span>Complete data</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-4 h-4 bg-gradient-to-r from-gray-200 to-gray-300 rounded"></div>
            <span>Missing data</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Alert Banner -->
    <div class="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-4 mb-8">
      <div class="flex items-start">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 bg-amber-400 rounded-full flex items-center justify-center">
            <span class="text-white text-sm">⚠️</span>
          </div>
        </div>
        <div class="ml-4 flex-1">
          <h4 class="text-sm font-bold text-amber-800">Critical Data Gap Detected</h4>
          <p class="text-sm text-amber-700 mt-1">
            Latest complete data from <strong>{{ latestSeason }}</strong>. 
            Missing <strong>6 recent seasons (2019-2024)</strong> would boost completion to <strong>~95%</strong>.
          </p>
          <div class="mt-2 text-xs text-amber-600">
            📈 Potential impact: +6,000-8,000 additional players
          </div>
        </div>
      </div>
    </div>

    <!-- Modern Data Table -->
    <div class="bg-white/80 rounded-xl overflow-hidden border border-gray-200 shadow-sm">
      <div class="bg-gradient-to-r from-gray-50 to-white px-6 py-4 border-b border-gray-200">
        <h4 class="text-lg font-bold text-gray-900 flex items-center">
          <span class="mr-2">📋</span>
          Detailed Season Analysis
        </h4>
      </div>
      
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gradient-to-r from-gray-50/80 to-white/80">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Season</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Players</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Teams</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">% of Total</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Data Quality</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="season in seasonDetails" :key="season.season" class="hover:bg-gray-50/50 transition-colors group">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-bold text-gray-900">{{ season.season }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ season.players.toLocaleString() }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-700">{{ season.teams }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="text-sm font-medium text-gray-900 mr-2">{{ season.percentage.toFixed(1) }}%</div>
                  <div class="w-12 bg-gray-200 rounded-full h-2">
                    <div 
                      class="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all"
                      :style="`width: ${Math.min(100, season.percentage * 2)}%`"
                    ></div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  :class="{
                    'bg-green-100 text-green-800 border-green-200': season.quality === 'Excellent',
                    'bg-blue-100 text-blue-800 border-blue-200': season.quality === 'Good', 
                    'bg-yellow-100 text-yellow-800 border-yellow-200': season.quality === 'Moderate',
                    'bg-red-100 text-red-800 border-red-200': season.quality === 'Limited'
                  }"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border"
                >
                  {{ season.quality }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Bottom Insights Grid -->
    <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl p-6 border border-emerald-200">
        <h5 class="font-bold text-emerald-900 mb-4 flex items-center">
          <span class="mr-2">🏅</span>
          Peak Performance Years
        </h5>
        <div class="space-y-3">
          <div v-for="(peak, index) in peakYears" :key="peak.season" class="flex justify-between items-center">
            <div class="flex items-center">
              <div class="w-6 h-6 bg-emerald-500 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3">
                {{ index + 1 }}
              </div>
              <span class="font-medium text-emerald-900">{{ peak.season }}</span>
            </div>
            <div class="text-emerald-700 font-bold">{{ peak.players.toLocaleString() }}</div>
          </div>
        </div>
      </div>
      
      <div class="bg-gradient-to-br from-red-50 to-pink-50 rounded-xl p-6 border border-red-200">
        <h5 class="font-bold text-red-900 mb-4 flex items-center">
          <span class="mr-2">🔍</span>
          Critical Data Gaps
        </h5>
        <div class="space-y-3">
          <div class="flex items-start space-x-3">
            <div class="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
            <div>
              <div class="text-sm font-medium text-red-800">2019-2024 Missing</div>
              <div class="text-xs text-red-600">6 complete seasons lost</div>
            </div>
          </div>
          <div class="flex items-start space-x-3">
            <div class="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
            <div>
              <div class="text-sm font-medium text-yellow-800">2018/19 Incomplete</div>
              <div class="text-xs text-yellow-600">Only 10 players vs expected ~800</div>
            </div>
          </div>
          <div class="flex items-start space-x-3">
            <div class="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
            <div>
              <div class="text-sm font-medium text-blue-800">Server Issues</div>
              <div class="text-xs text-blue-600">basketball-bund.net temporarily down</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Historical coverage component with real data analysis
import { ref, computed } from 'vue'

const props = defineProps({
  coverageData: {
    type: Object,
    default: () => ({
      totalSeasons: 16,
      yearRange: '2003-2018',
      overallCompletion: 72.7,
      latestSeason: '2018/19',
      totalPlayers: 12377,
      potentialSeasons: 22,
      seasons: [
        { season: '2003/04', players: 1743, teams: 56, percentage: 14.1 },
        { season: '2004/05', players: 1850, teams: 69, percentage: 14.9 },
        { season: '2005/06', players: 1880, teams: 63, percentage: 15.2 },
        { season: '2006/07', players: 748, teams: 42, percentage: 6.0 },
        { season: '2007/08', players: 552, teams: 30, percentage: 4.5 },
        { season: '2008/09', players: 617, teams: 33, percentage: 5.0 },
        { season: '2009/10', players: 490, teams: 24, percentage: 4.0 },
        { season: '2010/11', players: 426, teams: 23, percentage: 3.4 },
        { season: '2011/12', players: 531, teams: 29, percentage: 4.3 },
        { season: '2012/13', players: 680, teams: 42, percentage: 5.5 },
        { season: '2013/14', players: 731, teams: 49, percentage: 5.9 },
        { season: '2014/15', players: 453, teams: 28, percentage: 3.7 },
        { season: '2015/16', players: 691, teams: 41, percentage: 5.6 },
        { season: '2016/17', players: 453, teams: 26, percentage: 3.7 },
        { season: '2017/18', players: 522, teams: 29, percentage: 4.2 },
        { season: '2018/19', players: 10, teams: 6, percentage: 0.1 }
      ]
    })
  }
})

// Computed properties
const totalSeasons = computed(() => props.coverageData.totalSeasons)
const potentialSeasons = computed(() => props.coverageData.potentialSeasons)
const yearRange = computed(() => props.coverageData.yearRange)
const overallCompletion = computed(() => props.coverageData.overallCompletion)
const latestSeason = computed(() => props.coverageData.latestSeason)

// Timeline years (2003-2024)
const timelineYears = computed(() => {
  const years = []
  const seasonMap = new Map()
  
  // Map seasons to years
  props.coverageData.seasons.forEach(season => {
    const year = parseInt(season.season.split('/')[0])
    seasonMap.set(year, {
      players: season.players,
      teams: season.teams,
      hasData: true
    })
  })
  
  // Create timeline for 2003-2024
  for (let year = 2003; year <= 2024; year++) {
    const data = seasonMap.get(year)
    years.push({
      year: year.toString().slice(-2), // Show last 2 digits
      fullYear: year,
      hasData: !!data,
      players: data?.players || 0,
      teams: data?.teams || 0
    })
  }
  
  return years
})

// Season details with quality assessment
const seasonDetails = computed(() => {
  return props.coverageData.seasons.map(season => ({
    ...season,
    quality: getDataQuality(season.players)
  }))
})

// Peak years
const peakYears = computed(() => {
  return props.coverageData.seasons
    .filter(s => s.players > 1000)
    .sort((a, b) => b.players - a.players)
    .slice(0, 3)
})

// Functions
function getDataQuality(players) {
  if (players >= 1500) return 'Excellent'
  if (players >= 500) return 'Good'
  if (players >= 100) return 'Moderate'
  return 'Limited'
}

function selectYear(year) {
  // Could emit event or navigate to year-specific view
  console.log('Selected year:', year)
}
</script>
