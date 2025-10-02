<template>
  <div class="container mx-auto px-4 py-6">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Crawl Logs</h1>
      <p class="text-gray-600">Monitor and search through basketball data crawling sessions</p>
    </div>

    <!-- Statistics Overview -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-blue-100 text-blue-500">
            <Icon name="heroicons:play-circle" class="w-6 h-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Active Sessions</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.session_stats?.running_sessions || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-green-100 text-green-500">
            <Icon name="heroicons:chart-bar" class="w-6 h-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Success Rate</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.success_rate?.toFixed(1) || 0 }}%</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-purple-100 text-purple-500">
            <Icon name="heroicons:magnifying-glass" class="w-6 h-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Discoveries</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.session_stats?.total_discoveries || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-red-100 text-red-500">
            <Icon name="heroicons:exclamation-triangle" class="w-6 h-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Errors</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.session_stats?.failed_requests || 0 }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Sessions Table -->
    <div class="bg-white rounded-lg shadow mb-8">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-medium text-gray-900">Recent Crawl Sessions</h2>
          <button 
            @click="refreshSessions"
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Icon name="heroicons:arrow-path" class="w-4 h-4 mr-2" :class="{ 'animate-spin': refreshing }" />
            Refresh
          </button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Session</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progress</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Discoveries</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="session in sessions" :key="session.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ session.session_name }}</div>
                    <div class="text-sm text-gray-500">{{ session.spider_name }}</div>
                    <div class="text-xs text-gray-400">{{ formatDate(session.start_time) }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusColor(session.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                  {{ session.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatDuration(session.duration_minutes) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-16 bg-gray-200 rounded-full h-2 mr-3">
                    <div 
                      class="bg-blue-600 h-2 rounded-full" 
                      :style="{ width: getProgressPercentage(session) + '%' }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-600">{{ session.successful_requests }}/{{ session.total_requests }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ session.leagues_discovered }}</div>
                <div class="text-sm text-gray-500">{{ session.items_scraped }} items</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button 
                  @click="viewSessionDetails(session.id)"
                  class="text-blue-600 hover:text-blue-900 mr-3"
                >
                  View Details
                </button>
                <button 
                  @click="viewSessionLogs(session.id)"
                  class="text-green-600 hover:text-green-900"
                >
                  View Logs
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Log Search Panel -->
    <div class="bg-white rounded-lg shadow" v-if="showLogSearch">
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-medium text-gray-900">Search Logs</h2>
      </div>
      
      <div class="p-6">
        <!-- Search Filters -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Session</label>
            <select v-model="logFilters.session_id" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
              <option value="">All Sessions</option>
              <option v-for="session in sessions" :key="session.id" :value="session.id">
                {{ session.session_name }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Level</label>
            <select v-model="logFilters.level" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
              <option value="">All Levels</option>
              <option value="ERROR">ERROR</option>
              <option value="WARNING">WARNING</option>
              <option value="INFO">INFO</option>
              <option value="DEBUG">DEBUG</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Search Term</label>
            <input 
              v-model="logFilters.search"
              type="text" 
              placeholder="Search in messages..."
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
          </div>
          
          <div class="flex items-end">
            <button 
              @click="searchLogs"
              class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Icon name="heroicons:magnifying-glass" class="w-4 h-4 mr-2" />
              Search
            </button>
          </div>
        </div>

        <!-- Log Results -->
        <div class="space-y-2 max-h-96 overflow-y-auto">
          <div 
            v-for="log in logResults" 
            :key="log.id" 
            class="flex items-start space-x-4 p-3 rounded-lg border border-gray-200 hover:bg-gray-50"
            :class="getLogLevelColor(log.level)"
          >
            <div class="flex-shrink-0">
              <span :class="getLogLevelBadgeColor(log.level)" class="inline-flex px-2 py-1 text-xs font-semibold rounded">
                {{ log.level }}
              </span>
            </div>
            <div class="flex-grow min-w-0">
              <div class="text-sm font-medium text-gray-900 truncate">
                {{ log.message }}
              </div>
              <div class="text-xs text-gray-500 mt-1">
                {{ formatDate(log.timestamp) }} • {{ log.logger_name }}
                <span v-if="log.url" class="ml-2">• {{ log.url }}</span>
                <span v-if="log.league_id" class="ml-2">• League {{ log.league_id }}</span>
              </div>
            </div>
            <div v-if="log.response_status" class="flex-shrink-0">
              <span :class="getStatusCodeColor(log.response_status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded">
                {{ log.response_status }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface CrawlSession {
  id: string
  session_name: string
  spider_name: string
  start_time: string
  end_time?: string
  status: string
  total_requests: number
  successful_requests: number
  failed_requests: number
  items_scraped: number
  leagues_discovered: number
  duration_minutes?: number
}

interface LogEntry {
  id: string
  timestamp: string
  level: string
  logger_name: string
  message: string
  url?: string
  response_status?: number
  league_id?: string
  season_year?: number
}

interface CrawlStats {
  session_stats?: {
    running_sessions: number
    total_discoveries: number
    failed_requests: number
  }
  success_rate?: number
}

// Reactive data
const sessions = ref<CrawlSession[]>([])
const stats = ref<CrawlStats>({})
const logResults = ref<LogEntry[]>([])
const refreshing = ref(false)
const showLogSearch = ref(false)

const logFilters = ref({
  session_id: '',
  level: '',
  search: '',
  league_id: ''
})

// Methods
const refreshSessions = async () => {
  refreshing.value = true
  try {
    const [sessionsResponse, statsResponse] = await Promise.all([
      $fetch('/api/crawl/sessions'),
      $fetch('/api/crawl/statistics')
    ])
    
    sessions.value = sessionsResponse.sessions || []
    stats.value = statsResponse
  } catch (error) {
    console.error('Failed to fetch crawl data:', error)
  } finally {
    refreshing.value = false
  }
}

const searchLogs = async () => {
  try {
    const params = new URLSearchParams()
    Object.entries(logFilters.value).forEach(([key, value]) => {
      if (value) params.append(key, value)
    })
    
    const response = await $fetch(`/api/crawl/logs/search?${params.toString()}`)
    logResults.value = response.logs || []
  } catch (error) {
    console.error('Failed to search logs:', error)
  }
}

const viewSessionDetails = (sessionId: string) => {
  navigateTo(`/crawl-logs/${sessionId}`)
}

const viewSessionLogs = (sessionId: string) => {
  logFilters.value.session_id = sessionId
  showLogSearch.value = true
  searchLogs()
}

// Utility methods
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

const formatDuration = (minutes?: number) => {
  if (!minutes) return '-'
  
  if (minutes < 60) {
    return `${minutes}m`
  } else {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return `${hours}h ${mins}m`
  }
}

const getProgressPercentage = (session: CrawlSession) => {
  if (session.total_requests === 0) return 0
  return (session.successful_requests / session.total_requests) * 100
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'running': return 'bg-blue-100 text-blue-800'
    case 'completed': return 'bg-green-100 text-green-800'
    case 'failed': return 'bg-red-100 text-red-800'
    case 'aborted': return 'bg-yellow-100 text-yellow-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getLogLevelColor = (level: string) => {
  switch (level) {
    case 'ERROR': return 'border-red-300 bg-red-50'
    case 'WARNING': return 'border-yellow-300 bg-yellow-50'
    case 'INFO': return 'border-blue-300 bg-blue-50'
    case 'DEBUG': return 'border-gray-300 bg-gray-50'
    default: return 'border-gray-300'
  }
}

const getLogLevelBadgeColor = (level: string) => {
  switch (level) {
    case 'ERROR': return 'bg-red-100 text-red-800'
    case 'WARNING': return 'bg-yellow-100 text-yellow-800'
    case 'INFO': return 'bg-blue-100 text-blue-800'
    case 'DEBUG': return 'bg-gray-100 text-gray-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getStatusCodeColor = (status: number) => {
  if (status >= 200 && status < 300) return 'bg-green-100 text-green-800'
  if (status >= 400 && status < 500) return 'bg-yellow-100 text-yellow-800'
  if (status >= 500) return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-800'
}

// Lifecycle
onMounted(() => {
  refreshSessions()
  // Auto-refresh every 30 seconds for running sessions
  setInterval(refreshSessions, 30000)
})

// Define page meta
definePageMeta({
  middleware: 'auth'
})
</script>
