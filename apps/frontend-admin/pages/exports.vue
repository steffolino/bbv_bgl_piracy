<template>
  <div>
    <h1 class="text-3xl font-bold mb-8">Data Exports</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Boxscores Export</h2>
          <p class="text-sm text-base-content/70 mb-4">
            Export all boxscore data in NDJSON format with provenance fields
          </p>
          <div class="card-actions justify-end">
            <a 
              :href="`${config.public.apiBase}/exports/boxscores.ndjson`" 
              class="btn btn-primary"
              download="boxscores.ndjson"
            >
              Download NDJSON
            </a>
          </div>
        </div>
      </div>
      
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Season Stats Export</h2>
          <p class="text-sm text-base-content/70 mb-4">
            Export all season statistics in CSV format
          </p>
          <div class="card-actions justify-end">
            <a 
              :href="`${config.public.apiBase}/exports/season.csv`" 
              class="btn btn-primary"
              download="season-stats.csv"
            >
              Download CSV
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
</script>