<template>
  <div class="min-h-screen bg-base-100">
    <!-- Admin Header -->
    <div class="navbar bg-primary text-primary-content shadow-lg">
      <div class="flex-1">
        <h1 class="text-xl font-bold">🏀 Admin Dashboard - Vereine Management</h1>
      </div>
      <div class="flex-none">
        <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn btn-ghost">
            Admin User
            <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </div>
          <ul class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52 text-base-content">
            <li><a @click="logout">Logout</a></li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mx-auto p-6">
      <!-- Action Bar -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold">Vereine Management</h2>
        <button @click="showCreateModal = true" class="btn btn-primary">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Create New Verein
        </button>
      </div>

      <!-- Vereine List -->
      <div class="grid gap-6">
        <div v-for="verein in vereine" :key="verein.id" class="card bg-base-200 shadow-xl">
          <div class="card-body">
            <div class="flex items-start justify-between">
              <!-- Verein Info -->
              <div class="flex items-center space-x-4">
                <!-- Logo -->
                <div class="avatar">
                  <div class="w-16 h-16 rounded-lg" :style="{ backgroundColor: verein.primary_color || '#ddd' }">
                    <img v-if="verein.logo_url" :src="verein.logo_url" :alt="verein.name" class="rounded-lg">
                    <div v-else class="flex items-center justify-center text-white font-bold text-xl">
                      {{ verein.short_name?.charAt(0) || verein.name.charAt(0) }}
                    </div>
                  </div>
                </div>
                
                <!-- Details -->
                <div>
                  <h3 class="card-title text-lg">{{ verein.name }}</h3>
                  <p class="text-sm opacity-70">{{ verein.short_name }}</p>
                  <div class="flex items-center space-x-4 mt-2 text-sm">
                    <span class="badge badge-outline">{{ verein.team_count }} Teams</span>
                    <span v-if="verein.address_city" class="opacity-70">📍 {{ verein.address_city }}</span>
                    <span v-if="verein.founded_year" class="opacity-70">📅 Since {{ verein.founded_year }}</span>
                  </div>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex space-x-2">
                <button @click="editVerein(verein)" class="btn btn-sm btn-outline">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                  Edit
                </button>
                <button @click="manageTeams(verein)" class="btn btn-sm btn-primary">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                  </svg>
                  Teams
                </button>
              </div>
            </div>

            <!-- Quick Team Overview -->
            <div v-if="verein.teams?.length" class="mt-4">
              <h4 class="font-semibold mb-2">Teams:</h4>
              <div class="flex flex-wrap gap-2">
                <span v-for="team in verein.teams.slice(0, 5)" :key="team.id" 
                      class="badge badge-primary badge-sm">
                  {{ team.name }}
                </span>
                <span v-if="verein.teams.length > 5" class="badge badge-outline badge-sm">
                  +{{ verein.teams.length - 5 }} more
                </span>
              </div>
            </div>

            <!-- Contact Info -->
            <div class="flex items-center space-x-4 mt-4 text-sm">
              <a v-if="verein.website" :href="verein.website" target="_blank" 
                 class="link link-primary">
                🌐 Website
              </a>
              <a v-if="verein.instagram" :href="`https://instagram.com/${verein.instagram.replace('@', '')}`" 
                 target="_blank" class="link link-secondary">
                📸 Instagram
              </a>
              <span v-if="verein.email" class="opacity-70">✉️ {{ verein.email }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!vereine.length" class="text-center py-12">
        <div class="text-6xl mb-4">🏀</div>
        <h3 class="text-xl font-bold mb-2">No Vereine Found</h3>
        <p class="text-base-content/70 mb-4">Create your first verein to get started</p>
        <button @click="showCreateModal = true" class="btn btn-primary">
          Create New Verein
        </button>
      </div>
    </div>

    <!-- Create/Edit Verein Modal -->
    <VereineFormModal 
      v-if="showCreateModal || editingVerein"
      :verein="editingVerein"
      @close="closeModal"
      @saved="onVereinSaved"
    />

    <!-- Team Management Modal -->
    <TeamManagementModal
      v-if="managingTeamsVerein"
      :verein="managingTeamsVerein"
      @close="managingTeamsVerein = null"
      @updated="refreshVereine"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Types
interface Verein {
  id: string
  name: string
  short_name?: string
  website?: string
  email?: string
  instagram?: string
  address_city?: string
  founded_year?: number
  logo_url?: string
  primary_color?: string
  team_count: number
  teams?: Array<{
    id: string
    name: string
    category?: string
    team_number?: number
  }>
}

// Reactive state
const vereine = ref<Verein[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const editingVerein = ref<Verein | null>(null)
const managingTeamsVerein = ref<Verein | null>(null)

// Methods
const fetchVereine = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/admin/vereine', {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      vereine.value = data.vereine
    } else {
      console.error('Failed to fetch vereine')
    }
  } catch (error) {
    console.error('Error fetching vereine:', error)
  } finally {
    loading.value = false
  }
}

const editVerein = (verein: Verein) => {
  editingVerein.value = verein
}

const manageTeams = (verein: Verein) => {
  managingTeamsVerein.value = verein
}

const closeModal = () => {
  showCreateModal.value = false
  editingVerein.value = null
}

const onVereinSaved = () => {
  closeModal()
  refreshVereine()
}

const refreshVereine = () => {
  fetchVereine()
}

const logout = () => {
  // Clear auth token and redirect
  localStorage.removeItem('admin_token')
  navigateTo('/admin/login')
}

const getAuthToken = (): string => {
  return localStorage.getItem('admin_token') || 'demo-token'
}

// Lifecycle
onMounted(() => {
  fetchVereine()
})
</script>

<style scoped>
.card {
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-2px);
}

.badge {
  font-size: 0.75rem;
}
</style>
