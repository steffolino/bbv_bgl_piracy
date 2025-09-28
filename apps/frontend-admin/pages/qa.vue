<template>
  <div>
    <h1 class="text-3xl font-bold mb-8">QA Issues</h1>
    
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <div class="flex justify-between items-center mb-4">
          <h2 class="card-title">Issues List</h2>
          <button @click="refreshIssues" class="btn btn-primary btn-sm" :disabled="loading">
            <span v-if="loading" class="loading loading-spinner loading-sm"></span>
            Refresh
          </button>
        </div>
        
        <div v-if="loading && issues.length === 0" class="flex justify-center py-8">
          <span class="loading loading-spinner loading-lg"></span>
        </div>
        
        <div v-else-if="issues.length === 0" class="text-center py-8">
          <p class="text-base-content/70">No QA issues found</p>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="table table-sm">
            <thead>
              <tr>
                <th>Type</th>
                <th>Description</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="issue in issues" :key="issue.id" class="hover">
                <td>
                  <div class="badge badge-outline">{{ issue.type }}</div>
                </td>
                <td class="max-w-xs truncate">{{ issue.description }}</td>
                <td>
                  <div 
                    class="badge" 
                    :class="{
                      'badge-error': issue.status === 'open',
                      'badge-success': issue.status === 'confirmed',
                      'badge-neutral': issue.status === 'ignored'
                    }"
                  >
                    {{ issue.status }}
                  </div>
                </td>
                <td>{{ formatDate(issue.created_at) }}</td>
                <td>
                  <div class="flex gap-2">
                    <button 
                      v-if="issue.status === 'open'"
                      @click="updateIssueStatus(issue.id, 'confirm')"
                      class="btn btn-success btn-xs"
                    >
                      Confirm
                    </button>
                    <button 
                      v-if="issue.status === 'open'"
                      @click="updateIssueStatus(issue.id, 'ignore')"
                      class="btn btn-neutral btn-xs"
                    >
                      Ignore
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface QAIssue {
  id: string
  type: string
  description: string
  status: 'open' | 'confirmed' | 'ignored'
  created_at: string
  matchId?: string
  seasonId?: string
}

const config = useRuntimeConfig()
const issues = ref<QAIssue[]>([])
const loading = ref(true)

// Mock data for development
const mockIssues: QAIssue[] = [
  {
    id: '1',
    type: 'sum_check',
    description: 'Season totals do not match boxscore sum for player John Doe (±5 pts/game)',
    status: 'open',
    created_at: new Date().toISOString(),
    seasonId: '2023-24'
  },
  {
    id: '2',
    type: 'duplicate',
    description: 'Duplicate match found: BG Litzendorf vs Team A on 2023-12-15',
    status: 'open',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    matchId: 'match-123'
  },
  {
    id: '3',
    type: 'outlier',
    description: 'Outlier detected: Max Mustermann scored 45 points (z-score: 4.2)',
    status: 'confirmed',
    created_at: new Date(Date.now() - 172800000).toISOString(),
    matchId: 'match-456'
  }
]

async function refreshIssues() {
  loading.value = true
  
  try {
    // In production, this would fetch from the API
    // const response = await fetch(`${config.public.apiBase}/qa/issues`)
    // issues.value = await response.json()
    
    // Mock data for development
    await new Promise(resolve => setTimeout(resolve, 500))
    issues.value = mockIssues
  } catch (error) {
    console.error('Error fetching issues:', error)
  } finally {
    loading.value = false
  }
}

async function updateIssueStatus(issueId: string, action: 'confirm' | 'ignore') {
  try {
    // In production, this would call the API
    // const response = await fetch(`${config.public.apiBase}/admin/qa/${issueId}/${action}`, {
    //   method: 'POST'
    // })
    
    // Mock update for development
    const issue = issues.value.find(i => i.id === issueId)
    if (issue) {
      issue.status = action === 'confirm' ? 'confirmed' : 'ignored'
    }
  } catch (error) {
    console.error('Error updating issue status:', error)
  }
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  refreshIssues()
})
</script>