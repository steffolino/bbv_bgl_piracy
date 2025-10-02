<template>
  <div class="modal modal-open" v-if="showModal">
    <div class="modal-box w-11/12 max-w-4xl">
      <div class="flex justify-between items-center mb-6">
        <h3 class="font-bold text-2xl">🏀 Export Player Cards</h3>
        <button @click="$emit('close')" class="btn btn-sm btn-circle btn-ghost">✕</button>
      </div>

      <div class="tabs tabs-bordered mb-6">
        <a class="tab" :class="{ 'tab-active': activeTab === 'single' }" @click="activeTab = 'single'">Single Card</a>
        <a class="tab" :class="{ 'tab-active': activeTab === 'bulk' }" @click="activeTab = 'bulk'">Bulk Export</a>
        <a class="tab" :class="{ 'tab-active': activeTab === 'table' }" @click="activeTab = 'table'">Table Export</a>
      </div>

      <!-- Single Card Tab -->
      <div v-if="activeTab === 'single'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Card Configuration -->
        <div class="space-y-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Select Player</span>
            </label>
            <select v-model="selectedPlayer" class="select select-bordered">
              <option value="">Choose a player...</option>
              <option v-for="player in topPlayers" :key="player.name" :value="player">
                {{ player.name }} - {{ player.mannschaft }}
              </option>
            </select>
          </div>

          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Card Style</span>
            </label>
            <div class="grid grid-cols-2 gap-2">
              <label class="cursor-pointer">
                <input type="radio" v-model="cardStyle" value="vintage" name="style" class="radio radio-primary" checked>
                <span class="label-text ml-2">Vintage Upper Deck</span>
              </label>
              <label class="cursor-pointer">
                <input type="radio" v-model="cardStyle" value="modern" name="style" class="radio radio-primary">
                <span class="label-text ml-2">Modern Clean</span>
              </label>
            </div>
          </div>

          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Card Size</span>
            </label>
            <select v-model="cardSize" class="select select-bordered select-sm">
              <option value="standard">Standard (600x850)</option>
              <option value="large">Large (800x1100)</option>
              <option value="mini">Mini (400x600)</option>
            </select>
          </div>

          <div class="space-y-2">
            <button @click="generateCard" :disabled="!selectedPlayer || generating" 
                   class="btn btn-primary w-full">
              <span v-if="generating" class="loading loading-spinner loading-sm"></span>
              {{ generating ? 'Generating...' : 'Generate Card' }}
            </button>
            
            <button v-if="generatedCard" @click="downloadCard" class="btn btn-success w-full">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download Card
            </button>
          </div>
        </div>

        <!-- Card Preview -->
        <div class="space-y-4">
          <h4 class="font-bold">Card Preview</h4>
          <div v-if="generatedCard" class="bg-base-200 p-4 rounded-lg">
            <img :src="`data:image/png;base64,${generatedCard.image_base64}`" 
                 alt="Player Card" class="w-full max-w-sm mx-auto rounded-lg shadow-lg">
          </div>
          <div v-else class="bg-base-200 p-8 rounded-lg text-center opacity-50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <p>Card preview will appear here</p>
          </div>
        </div>
      </div>

      <!-- Bulk Export Tab -->
      <div v-if="activeTab === 'bulk'" class="space-y-4">
        <div class="alert alert-info">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <span>Generate cards for multiple players. This may take some time for large selections.</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Selection Method</span>
              </label>
              <div class="space-y-2">
                <label class="cursor-pointer flex items-center">
                  <input type="radio" v-model="bulkMethod" value="top" name="bulk" class="radio radio-primary">
                  <span class="label-text ml-2">Top Players</span>
                </label>
                <label class="cursor-pointer flex items-center">
                  <input type="radio" v-model="bulkMethod" value="category" name="bulk" class="radio radio-primary">
                  <span class="label-text ml-2">By Category</span>
                </label>
                <label class="cursor-pointer flex items-center">
                  <input type="radio" v-model="bulkMethod" value="team" name="bulk" class="radio radio-primary">
                  <span class="label-text ml-2">By Team</span>
                </label>
              </div>
            </div>

            <div v-if="bulkMethod === 'top'" class="form-control">
              <label class="label">
                <span class="label-text font-medium">Number of Players</span>
              </label>
              <input type="number" v-model="bulkCount" min="1" max="50" class="input input-bordered">
            </div>

            <div v-if="bulkMethod === 'category'" class="form-control">
              <label class="label">
                <span class="label-text font-medium">Category</span>
              </label>
              <select v-model="bulkCategory" class="select select-bordered">
                <option value="statBesteWerferArchiv">Beste Werfer</option>
                <option value="statBesteFreiWerferArchiv">Freiwurf-Schützen</option>
                <option value="statBeste3erWerferArchiv">3-Punkte-Schützen</option>
              </select>
            </div>

            <div v-if="bulkMethod === 'team'" class="form-control">
              <label class="label">
                <span class="label-text font-medium">Team</span>
              </label>
              <select v-model="bulkTeam" class="select select-bordered">
                <option v-for="team in uniqueTeams" :key="team" :value="team">{{ team }}</option>
              </select>
            </div>

            <button @click="generateBulkCards" :disabled="bulkGenerating" class="btn btn-primary w-full">
              <span v-if="bulkGenerating" class="loading loading-spinner loading-sm"></span>
              {{ bulkGenerating ? 'Generating Cards...' : 'Generate Bulk Cards' }}
            </button>
          </div>

          <div class="space-y-4">
            <h4 class="font-bold">Bulk Export Progress</h4>
            <div v-if="bulkProgress.total > 0" class="space-y-2">
              <progress class="progress progress-primary" :value="bulkProgress.completed" :max="bulkProgress.total"></progress>
              <p class="text-sm">{{ bulkProgress.completed }} / {{ bulkProgress.total }} cards generated</p>
            </div>
            <div v-if="bulkCards.length > 0" class="max-h-48 overflow-y-auto">
              <div class="grid grid-cols-3 gap-2">
                <div v-for="card in bulkCards.slice(0, 9)" :key="card.player.name" 
                     class="bg-base-200 p-2 rounded text-center">
                  <img :src="`data:image/png;base64,${card.image_base64}`" 
                       alt="Card" class="w-full rounded mb-1">
                  <p class="text-xs truncate">{{ card.player.name }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Table Export Tab -->
      <div v-if="activeTab === 'table'" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <h4 class="font-bold">Export Current Table</h4>
            
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Export Format</span>
              </label>
              <select v-model="exportFormat" class="select select-bordered">
                <option value="csv">CSV (Excel)</option>
                <option value="json">JSON</option>
                <option value="pdf">PDF Report</option>
                <option value="excel">Excel Workbook</option>
              </select>
            </div>

            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Include Columns</span>
              </label>
              <div class="space-y-1 max-h-32 overflow-y-auto">
                <label v-for="column in availableColumns" :key="column" class="cursor-pointer flex items-center">
                  <input type="checkbox" v-model="selectedColumns" :value="column" class="checkbox checkbox-primary checkbox-sm">
                  <span class="label-text ml-2 text-sm">{{ column }}</span>
                </label>
              </div>
            </div>

            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Filename</span>
              </label>
              <input v-model="exportFilename" type="text" class="input input-bordered" 
                     :placeholder="`basketball_stats_${new Date().toISOString().split('T')[0]}`">
            </div>

            <button @click="exportTable" class="btn btn-success w-full">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export {{ exportFormat.toUpperCase() }}
            </button>
          </div>

          <div class="space-y-4">
            <h4 class="font-bold">Export Preview</h4>
            <div class="bg-base-200 p-4 rounded-lg max-h-64 overflow-auto">
              <table class="table table-xs">
                <thead>
                  <tr>
                    <th v-for="col in selectedColumns.slice(0, 4)" :key="col">{{ col }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="player in filteredPlayers.slice(0, 5)" :key="player.name">
                    <td v-for="col in selectedColumns.slice(0, 4)" :key="col">
                      {{ getPlayerValue(player, col) }}
                    </td>
                  </tr>
                </tbody>
              </table>
              <p v-if="filteredPlayers.length > 5" class="text-xs opacity-50 mt-2">
                ... and {{ filteredPlayers.length - 5 }} more rows
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-action">
        <button @click="$emit('close')" class="btn">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  showModal: Boolean,
  playersData: Array,
  filteredPlayers: Array
})

const emit = defineEmits(['close'])

const activeTab = ref('single')

// Single card state
const selectedPlayer = ref(null)
const cardStyle = ref('vintage')
const cardSize = ref('standard')
const generating = ref(false)
const generatedCard = ref(null)

// Bulk export state
const bulkMethod = ref('top')
const bulkCount = ref(10)
const bulkCategory = ref('statBesteWerferArchiv')
const bulkTeam = ref('')
const bulkGenerating = ref(false)
const bulkCards = ref([])
const bulkProgress = ref({ completed: 0, total: 0 })

// Table export state
const exportFormat = ref('csv')
const exportFilename = ref('')
const selectedColumns = ref(['name', 'mannschaft', 'punkte', 'spiele'])

const availableColumns = ref([
  'name', 'mannschaft', 'liga', 'punkte', 'spiele', 'kategorie', 'saison',
  'field_goals', 'field_goal_attempts', 'freiwuerfe', 'freiwurf_versuche',
  'dreier', 'dreier_versuche'
])

const topPlayers = computed(() => {
  if (!props.playersData) return []
  return props.playersData
    .slice()
    .sort((a, b) => (parseFloat(b.punkte) || 0) - (parseFloat(a.punkte) || 0))
    .slice(0, 50)
})

const uniqueTeams = computed(() => {
  if (!props.playersData) return []
  return [...new Set(props.playersData.map(p => p.mannschaft))].filter(Boolean).sort()
})

const generateCard = async () => {
  if (!selectedPlayer.value) return
  
  generating.value = true
  try {
    // Simulate API call to Python backend for card generation
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Mock response - in real implementation, this would call the Python API
    generatedCard.value = {
      image_base64: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==', // 1x1 transparent pixel as placeholder
      player: selectedPlayer.value,
      advanced_stats: {
        PPG: (parseFloat(selectedPlayer.value.punkte) / parseFloat(selectedPlayer.value.spiele)).toFixed(1),
        PER: 15.0,
        TS_PCT: 55.5
      }
    }
  } catch (error) {
    console.error('Error generating card:', error)
  } finally {
    generating.value = false
  }
}

const downloadCard = () => {
  if (!generatedCard.value) return
  
  const link = document.createElement('a')
  link.href = `data:image/png;base64,${generatedCard.value.image_base64}`
  link.download = `${selectedPlayer.value.name.replace(/[^a-zA-Z0-9]/g, '_')}_card.png`
  link.click()
}

const generateBulkCards = async () => {
  bulkGenerating.value = true
  bulkCards.value = []
  
  let playersToProcess = []
  
  if (bulkMethod.value === 'top') {
    playersToProcess = topPlayers.value.slice(0, bulkCount.value)
  } else if (bulkMethod.value === 'category') {
    playersToProcess = props.playersData.filter(p => p.kategorie === bulkCategory.value).slice(0, 20)
  } else if (bulkMethod.value === 'team') {
    playersToProcess = props.playersData.filter(p => p.mannschaft === bulkTeam.value).slice(0, 20)
  }
  
  bulkProgress.value = { completed: 0, total: playersToProcess.length }
  
  for (const player of playersToProcess) {
    try {
      selectedPlayer.value = player
      await generateCard()
      if (generatedCard.value) {
        bulkCards.value.push({ ...generatedCard.value })
      }
      bulkProgress.value.completed++
      await new Promise(resolve => setTimeout(resolve, 500)) // Rate limiting
    } catch (error) {
      console.error(`Error generating card for ${player.name}:`, error)
    }
  }
  
  bulkGenerating.value = false
}

const exportTable = () => {
  const dataToExport = props.filteredPlayers.map(player => {
    const row = {}
    selectedColumns.value.forEach(col => {
      row[col] = getPlayerValue(player, col)
    })
    return row
  })
  
  const filename = exportFilename.value || `basketball_stats_${new Date().toISOString().split('T')[0]}`
  
  if (exportFormat.value === 'csv') {
    exportCSV(dataToExport, filename)
  } else if (exportFormat.value === 'json') {
    exportJSON(dataToExport, filename)
  }
}

const exportCSV = (data, filename) => {
  const headers = selectedColumns.value.join(',')
  const rows = data.map(row => selectedColumns.value.map(col => `"${row[col] || ''}"`).join(','))
  const csv = [headers, ...rows].join('\n')
  
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${filename}.csv`
  link.click()
  URL.revokeObjectURL(link.href)
}

const exportJSON = (data, filename) => {
  const json = JSON.stringify(data, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${filename}.json`
  link.click()
  URL.revokeObjectURL(link.href)
}

const getPlayerValue = (player, column) => {
  return player[column] || ''
}

// Initialize default filename
watch(() => props.showModal, (newVal) => {
  if (newVal && !exportFilename.value) {
    exportFilename.value = `basketball_stats_${new Date().toISOString().split('T')[0]}`
  }
})
</script>
