<template>
  <div class="modal modal-open">
    <div class="modal-box w-11/12 max-w-5xl">
      <h3 class="font-bold text-lg mb-6">
        Team Management - {{ verein.name }}
      </h3>

      <!-- Tabs -->
      <div class="tabs tabs-boxed mb-6">
        <button 
          @click="activeTab = 'current'" 
          :class="['tab', { 'tab-active': activeTab === 'current' }]"
        >
          Current Teams ({{ currentTeams.length }})
        </button>
        <button 
          @click="activeTab = 'suggestions'" 
          :class="['tab', { 'tab-active': activeTab === 'suggestions' }]"
        >
          Suggestions ({{ suggestions.length }})
        </button>
        <button 
          @click="activeTab = 'create'" 
          :class="['tab', { 'tab-active': activeTab === 'create' }]"
        >
          Create New Team
        </button>
      </div>

      <!-- Current Teams Tab -->
      <div v-if="activeTab === 'current'" class="space-y-4">
        <div v-for="team in currentTeams" :key="team.id" 
             class="card bg-base-200 shadow-sm">
          <div class="card-body p-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-4">
                <!-- Team Colors -->
                <div class="flex space-x-1">
                  <div 
                    class="w-4 h-8 rounded-sm"
                    :style="{ backgroundColor: team.jersey_home_color || verein.primary_color || '#ddd' }"
                    title="Home Jersey"
                  ></div>
                  <div 
                    class="w-4 h-8 rounded-sm"
                    :style="{ backgroundColor: team.jersey_away_color || verein.secondary_color || '#fff', border: '1px solid #ddd' }"
                    title="Away Jersey"
                  ></div>
                </div>

                <!-- Team Info -->
                <div>
                  <h4 class="font-semibold">{{ team.name }}</h4>
                  <div class="flex items-center space-x-3 text-sm text-base-content/70">
                    <span v-if="team.category" class="badge badge-outline badge-sm">
                      {{ team.category }}
                    </span>
                    <span v-if="team.gender">{{ team.gender }}</span>
                    <span v-if="team.league_level">{{ team.league_level }}</span>
                    <span v-if="!team.is_active" class="badge badge-error badge-sm">Inactive</span>
                  </div>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex space-x-2">
                <button @click="editTeam(team)" class="btn btn-sm btn-outline">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                  Edit
                </button>
                <button @click="confirmRemoveTeam(team)" class="btn btn-sm btn-error btn-outline">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                  Remove
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!currentTeams.length" class="text-center py-8">
          <div class="text-4xl mb-2">👥</div>
          <p class="text-base-content/70">No teams assigned yet</p>
          <p class="text-sm text-base-content/50">Check suggestions or create a new team</p>
        </div>
      </div>

      <!-- Suggestions Tab -->
      <div v-if="activeTab === 'suggestions'" class="space-y-4">
        <div class="flex justify-between items-center mb-4">
          <p class="text-sm text-base-content/70">
            AI-powered suggestions based on team names in our database
          </p>
          <button @click="refreshSuggestions" class="btn btn-sm btn-outline">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            Refresh
          </button>
        </div>

        <div v-for="suggestion in suggestions" :key="suggestion.id" 
             class="card bg-base-200 shadow-sm">
          <div class="card-body p-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-4">
                <!-- Confidence Badge -->
                <div class="flex flex-col items-center">
                  <div 
                    class="radial-progress text-sm" 
                    :style="`--value:${suggestion.confidence}`"
                    :class="{
                      'text-success': suggestion.confidence >= 80,
                      'text-warning': suggestion.confidence >= 60 && suggestion.confidence < 80,
                      'text-error': suggestion.confidence < 60
                    }"
                  >
                    {{ suggestion.confidence }}%
                  </div>
                  <span class="text-xs mt-1">Match</span>
                </div>

                <!-- Team Info -->
                <div>
                  <h4 class="font-semibold">{{ suggestion.name }}</h4>
                  <div class="flex items-center space-x-3 text-sm text-base-content/70">
                    <span v-if="suggestion.suggested_category" class="badge badge-outline badge-sm">
                      {{ suggestion.suggested_category }}
                    </span>
                    <span v-if="suggestion.suggested_team_number > 1">
                      Team #{{ suggestion.suggested_team_number }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex space-x-2">
                <button @click="addTeamToVerein(suggestion)" class="btn btn-sm btn-primary">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                  </svg>
                  Add Team
                </button>
                <button @click="dismissSuggestion(suggestion)" class="btn btn-sm btn-ghost">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Bulk Actions -->
        <div v-if="suggestions.length > 1" class="card bg-primary/10 border border-primary/20">
          <div class="card-body p-4">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="font-semibold">Bulk Import</h4>
                <p class="text-sm opacity-70">Add multiple high-confidence matches at once</p>
              </div>
              <button @click="bulkImportHighConfidence" class="btn btn-primary btn-sm">
                Import All 80%+ Matches
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!suggestions.length" class="text-center py-8">
          <div class="text-4xl mb-2">🔍</div>
          <p class="text-base-content/70">No suggestions found</p>
          <p class="text-sm text-base-content/50">All matching teams may already be assigned</p>
        </div>
      </div>

      <!-- Create New Team Tab -->
      <div v-if="activeTab === 'create'">
        <TeamCreateForm 
          :verein="verein"
          @created="onTeamCreated"
        />
      </div>

      <!-- Modal Actions -->
      <div class="modal-action">
        <button @click="$emit('close')" class="btn btn-ghost">
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Props & Emits
const props = defineProps<{
  verein: any
}>()

const emit = defineEmits<{
  close: []
  updated: []
}>()

// State
const activeTab = ref('current')
const currentTeams = ref([])
const suggestions = ref([])
const loading = ref(false)

// Methods
const fetchCurrentTeams = async () => {
  try {
    const response = await fetch(`/api/admin/vereine/${props.verein.id}`, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      currentTeams.value = data.teams || []
    }
  } catch (error) {
    console.error('Error fetching teams:', error)
  }
}

const fetchSuggestions = async () => {
  try {
    const response = await fetch(`/api/admin/vereine/${props.verein.id}/team-suggestions`, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      suggestions.value = data.suggestions || []
    }
  } catch (error) {
    console.error('Error fetching suggestions:', error)
  }
}

const refreshSuggestions = () => {
  fetchSuggestions()
}

const addTeamToVerein = async (team: any) => {
  loading.value = true
  try {
    const response = await fetch(`/api/admin/vereine/${props.verein.id}/import-teams`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`
      },
      body: JSON.stringify({ team_ids: [team.id] })
    })

    if (response.ok) {
      // Remove from suggestions and refresh current teams
      suggestions.value = suggestions.value.filter(s => s.id !== team.id)
      await fetchCurrentTeams()
      emit('updated')
    }
  } catch (error) {
    console.error('Error adding team:', error)
  } finally {
    loading.value = false
  }
}

const dismissSuggestion = (team: any) => {
  suggestions.value = suggestions.value.filter(s => s.id !== team.id)
}

const bulkImportHighConfidence = async () => {
  const highConfidenceTeams = suggestions.value.filter(s => s.confidence >= 80)
  
  if (!highConfidenceTeams.length) return

  const teamIds = highConfidenceTeams.map(t => t.id)
  
  loading.value = true
  try {
    const response = await fetch(`/api/admin/vereine/${props.verein.id}/import-teams`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`
      },
      body: JSON.stringify({ team_ids: teamIds })
    })

    if (response.ok) {
      // Remove imported teams from suggestions
      suggestions.value = suggestions.value.filter(s => s.confidence < 80)
      await fetchCurrentTeams()
      emit('updated')
    }
  } catch (error) {
    console.error('Error bulk importing teams:', error)
  } finally {
    loading.value = false
  }
}

const editTeam = (team: any) => {
  // TODO: Implement team editing
  console.log('Edit team:', team)
}

const confirmRemoveTeam = (team: any) => {
  if (confirm(`Remove "${team.name}" from this verein?`)) {
    removeTeam(team)
  }
}

const removeTeam = async (team: any) => {
  try {
    const response = await fetch(`/api/admin/teams/${team.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`
      },
      body: JSON.stringify({ ...team, verein_id: null })
    })

    if (response.ok) {
      await fetchCurrentTeams()
      await fetchSuggestions() // Team might appear in suggestions again
      emit('updated')
    }
  } catch (error) {
    console.error('Error removing team:', error)
  }
}

const onTeamCreated = () => {
  fetchCurrentTeams()
  activeTab.value = 'current'
  emit('updated')
}

const getAuthToken = (): string => {
  return localStorage.getItem('admin_token') || 'demo-token'
}

// Lifecycle
onMounted(() => {
  fetchCurrentTeams()
  fetchSuggestions()
})
</script>

<style scoped>
.radial-progress {
  --size: 3rem;
  --thickness: 4px;
}

.modal-box {
  max-height: 90vh;
  overflow-y: auto;
}
</style>
