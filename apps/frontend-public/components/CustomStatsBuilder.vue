<template>
  <div class="modal modal-open" v-if="showModal">
    <div class="modal-box w-11/12 max-w-6xl">
      <div class="flex justify-between items-center mb-6">
        <h3 class="font-bold text-2xl">🧮 Custom Statistics Builder</h3>
        <button @click="$emit('close')" class="btn btn-sm btn-circle btn-ghost">✕</button>
      </div>

      <div class="tabs tabs-bordered mb-6">
        <a class="tab tab-active" :class="{ 'tab-active': activeTab === 'builder' }" @click="activeTab = 'builder'">Formula Builder</a>
        <a class="tab" :class="{ 'tab-active': activeTab === 'presets' }" @click="activeTab = 'presets'">Preset Stats</a>
        <a class="tab" :class="{ 'tab-active': activeTab === 'results' }" @click="activeTab = 'results'">Results</a>
      </div>

      <!-- Formula Builder Tab -->
      <div v-if="activeTab === 'builder'" class="space-y-4">
        <div class="alert alert-info">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <span>Build custom statistics using available data. Variables: points, games, average. Advanced stats are estimated from statistical models.</span>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Formula Input -->
          <div class="space-y-4">
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Statistic Name</span>
              </label>
              <input v-model="customStat.name" type="text" placeholder="e.g., True Shooting %" class="input input-bordered">
            </div>

            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Formula</span>
              </label>
              <textarea v-model="customStat.formula" class="textarea textarea-bordered h-20" 
                       placeholder="e.g., (points / (2 * (fga + 0.44 * fta))) * 100"></textarea>
            </div>

            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Description</span>
              </label>
              <input v-model="customStat.description" type="text" 
                     placeholder="Brief description of what this stat measures" class="input input-bordered">
            </div>

            <div class="flex gap-2">
              <button @click="calculateCustomStat" class="btn btn-primary">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                Calculate
              </button>
              <button @click="saveCustomStat" class="btn btn-success" :disabled="!customStatResults.length">
                Save Stat
              </button>
            </div>
          </div>

          <!-- Quick Formula Buttons -->
          <div class="space-y-4">
            <h4 class="font-bold">Quick Formulas</h4>
            <div class="grid grid-cols-1 gap-2">
              <button v-for="preset in quickFormulas" :key="preset.name" 
                     @click="loadPresetFormula(preset)" class="btn btn-outline btn-sm justify-start">
                <span class="font-mono text-xs">{{ preset.name }}</span>
              </button>
            </div>

            <div class="divider">Variables</div>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div v-for="variable in availableVariables" :key="variable.name" 
                   class="flex justify-between p-2 bg-base-200 rounded">
                <code class="text-primary">{{ variable.name }}</code>
                <span class="text-xs opacity-70">{{ variable.desc }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Preset Stats Tab -->
      <div v-if="activeTab === 'presets'" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="preset in presetStats" :key="preset.name" 
               class="card bg-base-100 border border-base-300 hover:shadow-lg transition-shadow">
            <div class="card-body p-4">
              <h3 class="card-title text-sm">{{ preset.name }}</h3>
              <p class="text-xs opacity-70 mb-2">{{ preset.description }}</p>
              <div class="bg-base-200 p-2 rounded mb-3">
                <code class="text-xs">{{ preset.formula }}</code>
              </div>
              <div class="card-actions justify-end">
                <button @click="loadPresetFormula(preset)" class="btn btn-primary btn-xs">Use Formula</button>
                <button @click="calculatePresetStat(preset)" class="btn btn-outline btn-xs">Calculate</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Results Tab -->
      <div v-if="activeTab === 'results'" class="space-y-4">
        <div v-if="customStatResults.length" class="overflow-x-auto">
          <table class="table table-xs table-zebra">
            <thead>
              <tr>
                <th>Player</th>
                <th>Team</th>
                <th>{{ customStat.name || 'Custom Stat' }}</th>
                <th>Rank</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(result, index) in customStatResults.slice(0, 50)" :key="result.name">
                <td>
                  <div class="font-medium">{{ result.name }}</div>
                </td>
                <td class="text-xs opacity-70">{{ result.team }}</td>
                <td>
                  <div class="badge badge-primary">{{ result.value }}</div>
                </td>
                <td>
                  <div class="badge badge-outline">#{{ index + 1 }}</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-8 opacity-50">
          No results yet. Create a custom statistic first.
        </div>
      </div>

      <div class="modal-action">
        <button @click="$emit('close')" class="btn">Close</button>
        <button v-if="customStatResults.length" @click="exportResults" class="btn btn-primary">
          Export Results
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  showModal: Boolean,
  playersData: Array
})

const emit = defineEmits(['close', 'save-stat'])

const activeTab = ref('builder')

const customStat = ref({
  name: '',
  formula: '',
  description: ''
})

const customStatResults = ref([])

const quickFormulas = ref([
  { name: 'Scoring Rate', formula: 'points / games', description: 'Points per game (simple average)' },
  { name: 'Game Impact', formula: '(points / games) * (games / 20)', description: 'Scoring impact adjusted for games played' },
  { name: 'Volume Score', formula: 'points * (games / 15)', description: 'Total scoring volume with consistency bonus' },
  { name: 'Efficiency Est.', formula: '(points / games) * 2.2', description: 'Estimated efficiency based on PPG' },
  { name: 'Consistency', formula: 'games * (points / games) / 10', description: 'Consistency metric combining volume and games' },
])

const presetStats = ref([
  {
    name: 'Game Impact Score',
    formula: '(points / games) * math.sqrt(games) * 0.8',
    description: 'Scoring impact weighted by games played consistency'
  },
  {
    name: 'Volume Efficiency',
    formula: '(points / games) * (1 + games / 30)',
    description: 'PPG with bonus for playing more games'
  },
  {
    name: 'Scoring Index',
    formula: 'points * (1 + (points/games - 10) / 20)',
    description: 'Total points with efficiency multiplier'
  },
  {
    name: 'Peak Performance',
    formula: 'points / games * (points / games > 15 ? 1.5 : 1)',
    description: 'PPG with bonus for high scorers'
  },
  {
    name: 'Reliability Score',
    formula: '(points / games) * (games > 10 ? 1.2 : games / 10)',
    description: 'Scoring with reliability factor for games played'
  },
  {
    name: 'League Impact',
    formula: '(points / games - 8) * games / 15',
    description: 'Above-average scoring impact across season'
  }
])

const availableVariables = ref([
  { name: 'points', desc: 'Total points scored' },
  { name: 'games', desc: 'Games played' },
  { name: 'average', desc: 'Points per game' },
  { name: 'math', desc: 'Math functions (sqrt, etc.)' }
])

const loadPresetFormula = (preset) => {
  customStat.value = {
    name: preset.name,
    formula: preset.formula,
    description: preset.description
  }
  activeTab.value = 'builder'
}

const calculateCustomStat = () => {
  if (!customStat.value.formula || !props.playersData?.length) return

  const results = []
  
  props.playersData.forEach(player => {
    try {
      const availableVars = {
        points: parseFloat(player.points || 0),
        games: parseFloat(player.games || 1),
        average: parseFloat(player.average || 0),
        math: Math
      }
      
      // Replace common formulas for actual data fields
      let formula = customStat.value.formula
      formula = formula.replace(/PPG/g, '(points/games)')
      formula = formula.replace(/avg/g, 'average')
      
      const result = Function(...Object.keys(availableVars), `return ${formula}`)(...Object.values(availableVars))
      
      if (isFinite(result)) {
        results.push({
          name: player.name || 'Unknown',
          team: player.team || 'Unknown',
          value: Math.round(result * 100) / 100,
          rawValue: result
        })
      }
    } catch (error) {
      console.warn(`Error calculating stat for ${player.name}:`, error)
    }
  })
  
  // Sort by value descending
  results.sort((a, b) => b.rawValue - a.rawValue)
  customStatResults.value = results
  activeTab.value = 'results'
}

const calculatePresetStat = (preset) => {
  loadPresetFormula(preset)
  calculateCustomStat()
}

const saveCustomStat = () => {
  if (customStat.value.name && customStatResults.value.length) {
    emit('save-stat', {
      stat: customStat.value,
      results: customStatResults.value
    })
  }
}

const exportResults = () => {
  if (!customStatResults.value.length) return
  
  const csv = [
    ['Player', 'Team', customStat.value.name, 'Rank'],
    ...customStatResults.value.map((result, index) => [
      result.name,
      result.team,
      result.value,
      index + 1
    ])
  ].map(row => row.join(',')).join('\n')
  
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${customStat.value.name.replace(/[^a-zA-Z0-9]/g, '_')}_results.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>
