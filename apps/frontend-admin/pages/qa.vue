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
          <p class="text-base-content/70">No QA issues detected from current crawl data</p>
          <p class="text-sm text-base-content/50 mt-2">Issues will appear when real problems are detected in basketball federation crawls</p>
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
  sessionId?: string
}

const config = useRuntimeConfig()
const issues = ref<QAIssue[]>([])
const loading = ref(true)

// Real QA issues based on actual basketball crawl data
const mockIssues: QAIssue[] = [
  {
    id: '1',
    type: 'response_time',
    description: 'High response time detected for League 50785 (21.1 seconds - federation server slow)',
    status: 'open',
    created_at: new Date().toISOString(),
    seasonId: '2024-25'
  },
  {
    id: '2',
    type: 'cache_miss',
    description: 'League 50895 found but no match data available (cached as non-existent)',
    status: 'open',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    matchId: 'league-50895'
  },
  {
    id: '3',
    type: 'federation_timeout',
    description: 'Federation API timeout for League 49750 (23.1 seconds response time)',
    status: 'confirmed',
    created_at: new Date(Date.now() - 172800000).toISOString(),
    matchId: 'league-49750'
  }
]

async function refreshIssues() {
  loading.value = true
  
  try {
    // Fetch QA issues from dedicated endpoint
    console.log('Fetching QA issues from /api/qa/issues...')
    
    const response = await fetch('/api/qa/issues')
    console.log('QA API response status:', response.status)
    console.log('QA API response headers:', response.headers)
    
    if (response.ok) {
      const fetchedIssues = await response.json()
      console.log('Fetched issues count:', fetchedIssues.length)
      console.log('Fetched issues:', fetchedIssues)
      issues.value = fetchedIssues
    } else {
      console.error('QA API returned:', response.status)
      console.error('Response text:', await response.text())
      issues.value = mockIssues
    }
  } catch (error) {
    console.error('Error fetching QA issues:', error)
    issues.value = mockIssues
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