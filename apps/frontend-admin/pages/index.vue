<template>
  <div>
    <h1 class="text-3xl font-bold mb-8">Admin Dashboard</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- QA Issues Card -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">QA Issues</h2>
          <p class="text-2xl font-bold text-error">{{ qaIssuesCount }}</p>
          <p class="text-sm text-base-content/70">Open issues</p>
          <div class="card-actions justify-end">
            <NuxtLink to="/qa" class="btn btn-primary btn-sm">View All</NuxtLink>
          </div>
        </div>
      </div>
      
      <!-- Database Stats Card -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Database</h2>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span>Players:</span>
              <span class="font-bold">{{ stats.players }}</span>
            </div>
            <div class="flex justify-between">
              <span>Teams:</span>
              <span class="font-bold">{{ stats.teams }}</span>
            </div>
            <div class="flex justify-between">
              <span>Matches:</span>
              <span class="font-bold">{{ stats.matches }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- System Status Card -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">System Status</h2>
          <div class="badge badge-success">API: Online</div>
          <div class="badge badge-success">DB: Connected</div>
          <div class="badge badge-warning">Scraper: Idle</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const qaIssuesCount = ref(0)
const stats = ref({
  players: 0,
  teams: 0,
  matches: 0
})

// Mock data for development
onMounted(() => {
  qaIssuesCount.value = 3
  stats.value = {
    players: 45,
    teams: 8,
    matches: 156
  }
})
</script>