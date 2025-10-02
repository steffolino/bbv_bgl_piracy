<template>
  <div class="modal modal-open">
    <div class="modal-box w-11/12 max-w-4xl">
      <h3 class="font-bold text-lg mb-6">
        {{ verein ? 'Edit Verein' : 'Create New Verein' }}
      </h3>

      <form @submit.prevent="saveVerein" class="space-y-6">
        <!-- Basic Information -->
        <div class="card bg-base-200">
          <div class="card-body">
            <h4 class="card-title text-base mb-4">Basic Information</h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Verein Name *</span>
                </label>
                <input 
                  v-model="form.name" 
                  type="text" 
                  placeholder="e.g. BG Litzendorf e.V."
                  class="input input-bordered" 
                  required
                >
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Short Name</span>
                </label>
                <input 
                  v-model="form.short_name" 
                  type="text" 
                  placeholder="e.g. BG Litzendorf"
                  class="input input-bordered"
                >
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Founded Year</span>
                </label>
                <input 
                  v-model.number="form.founded_year" 
                  type="number" 
                  placeholder="e.g. 1995"
                  min="1900"
                  max="2030"
                  class="input input-bordered"
                >
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Status</span>
                </label>
                <select v-model="form.status" class="select select-bordered">
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="merged">Merged</option>
                </select>
              </div>
            </div>

            <div class="form-control">
              <label class="label">
                <span class="label-text">Description</span>
              </label>
              <textarea 
                v-model="form.description" 
                placeholder="Club history, achievements, notable information..."
                class="textarea textarea-bordered h-24"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Contact Information -->
        <div class="card bg-base-200">
          <div class="card-body">
            <h4 class="card-title text-base mb-4">Contact Information</h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Website</span>
                </label>
                <input 
                  v-model="form.website" 
                  type="url" 
                  placeholder="https://bg-litzendorf.de"
                  class="input input-bordered"
                >
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Email</span>
                </label>
                <input 
                  v-model="form.email" 
                  type="email" 
                  placeholder="info@bg-litzendorf.de"
                  class="input input-bordered"
                >
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Phone</span>
                </label>
                <input 
                  v-model="form.phone" 
                  type="tel" 
                  placeholder="+49 9505 123456"
                  class="input input-bordered"
                >
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Instagram</span>
                </label>
                <div class="input-group">
                  <span class="bg-base-300 px-3 flex items-center">@</span>
                  <input 
                    v-model="form.instagram" 
                    type="text" 
                    placeholder="bg_litzendorf"
                    class="input input-bordered flex-1"
                  >
                </div>
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Facebook</span>
                </label>
                <input 
                  v-model="form.facebook" 
                  type="text" 
                  placeholder="BGLitzendorf or full URL"
                  class="input input-bordered"
                >
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Twitter</span>
                </label>
                <div class="input-group">
                  <span class="bg-base-300 px-3 flex items-center">@</span>
                  <input 
                    v-model="form.twitter" 
                    type="text" 
                    placeholder="BGLitzendorf"
                    class="input input-bordered flex-1"
                  >
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Address -->
        <div class="card bg-base-200">
          <div class="card-body">
            <h4 class="card-title text-base mb-4">Address</h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="form-control md:col-span-2">
                <label class="label">
                  <span class="label-text">Street Address</span>
                </label>
                <input 
                  v-model="form.address_street" 
                  type="text" 
                  placeholder="Sportstraße 12"
                  class="input input-bordered"
                >
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">City</span>
                </label>
                <input 
                  v-model="form.address_city" 
                  type="text" 
                  placeholder="Litzendorf"
                  class="input input-bordered"
                >
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Postal Code</span>
                </label>
                <input 
                  v-model="form.address_postal_code" 
                  type="text" 
                  placeholder="96215"
                  class="input input-bordered"
                >
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">State</span>
                </label>
                <select v-model="form.address_state" class="select select-bordered">
                  <option value="">Select State</option>
                  <option value="Bayern">Bayern</option>
                  <option value="Baden-Württemberg">Baden-Württemberg</option>
                  <option value="Hessen">Hessen</option>
                  <option value="Nordrhein-Westfalen">Nordrhein-Westfalen</option>
                  <option value="Niedersachsen">Niedersachsen</option>
                  <option value="Rheinland-Pfalz">Rheinland-Pfalz</option>
                  <option value="Sachsen">Sachsen</option>
                  <option value="Sachsen-Anhalt">Sachsen-Anhalt</option>
                  <option value="Thüringen">Thüringen</option>
                  <option value="Brandenburg">Brandenburg</option>
                  <option value="Mecklenburg-Vorpommern">Mecklenburg-Vorpommern</option>
                  <option value="Berlin">Berlin</option>
                  <option value="Bremen">Bremen</option>
                  <option value="Hamburg">Hamburg</option>
                  <option value="Saarland">Saarland</option>
                  <option value="Schleswig-Holstein">Schleswig-Holstein</option>
                </select>
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Region</span>
                </label>
                <input 
                  v-model="form.region" 
                  type="text" 
                  placeholder="e.g. Oberfranken"
                  class="input input-bordered"
                >
              </div>
            </div>
          </div>
        </div>

        <!-- Visual Identity -->
        <div class="card bg-base-200">
          <div class="card-body">
            <h4 class="card-title text-base mb-4">Visual Identity</h4>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <!-- Logo Upload -->
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Logo</span>
                </label>
                <div class="border-2 border-dashed border-base-300 rounded-lg p-4 text-center">
                  <div v-if="form.logo_url" class="mb-2">
                    <img :src="form.logo_url" alt="Logo" class="w-16 h-16 mx-auto rounded">
                  </div>
                  <input 
                    type="file" 
                    accept="image/*" 
                    @change="handleLogoUpload"
                    class="file-input file-input-bordered file-input-sm w-full"
                  >
                  <p class="text-xs mt-2 opacity-70">PNG, JPG up to 2MB</p>
                </div>
              </div>

              <!-- Colors -->
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Primary Color</span>
                </label>
                <div class="flex items-center space-x-2">
                  <input 
                    v-model="form.primary_color" 
                    type="color" 
                    class="w-12 h-12 rounded cursor-pointer"
                  >
                  <input 
                    v-model="form.primary_color" 
                    type="text" 
                    placeholder="#FF0000"
                    class="input input-bordered input-sm flex-1"
                  >
                </div>
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Secondary Color</span>
                </label>
                <div class="flex items-center space-x-2">
                  <input 
                    v-model="form.secondary_color" 
                    type="color" 
                    class="w-12 h-12 rounded cursor-pointer"
                  >
                  <input 
                    v-model="form.secondary_color" 
                    type="text" 
                    placeholder="#FFFFFF"
                    class="input input-bordered input-sm flex-1"
                  >
                </div>
              </div>
            </div>

            <!-- Color Preview -->
            <div class="mt-4">
              <label class="label">
                <span class="label-text">Preview</span>
              </label>
              <div class="flex items-center space-x-4 p-4 bg-base-100 rounded-lg">
                <div 
                  class="w-12 h-12 rounded-lg flex items-center justify-center text-white font-bold"
                  :style="{ backgroundColor: form.primary_color || '#ddd' }"
                >
                  {{ form.short_name?.charAt(0) || form.name.charAt(0) || 'V' }}
                </div>
                <div>
                  <div class="font-bold">{{ form.name || 'Verein Name' }}</div>
                  <div class="text-sm opacity-70">{{ form.short_name || 'Short Name' }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Facilities -->
        <div class="card bg-base-200">
          <div class="card-body">
            <h4 class="card-title text-base mb-4">Home Facilities</h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Gym Name</span>
                </label>
                <input 
                  v-model="form.home_gym_name" 
                  type="text" 
                  placeholder="Sporthalle Litzendorf"
                  class="input input-bordered"
                >
              </div>

              <div class="form-control">
                <label class="label">
                  <span class="label-text">Capacity</span>
                </label>
                <input 
                  v-model.number="form.home_gym_capacity" 
                  type="number" 
                  placeholder="500"
                  min="0"
                  class="input input-bordered"
                >
              </div>

              <div class="form-control md:col-span-2">
                <label class="label">
                  <span class="label-text">Gym Address</span>
                </label>
                <input 
                  v-model="form.home_gym_address" 
                  type="text" 
                  placeholder="If different from club address"
                  class="input input-bordered"
                >
              </div>
            </div>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="modal-action">
          <button type="button" @click="$emit('close')" class="btn btn-ghost">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="saving">
            <span v-if="saving" class="loading loading-spinner loading-sm"></span>
            {{ saving ? 'Saving...' : (verein ? 'Update Verein' : 'Create Verein') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'

// Props & Emits
const props = defineProps<{
  verein?: any
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

// Form data
const form = reactive({
  name: '',
  short_name: '',
  website: '',
  email: '',
  phone: '',
  instagram: '',
  facebook: '',
  twitter: '',
  address_street: '',
  address_city: '',
  address_postal_code: '',
  address_state: '',
  region: '',
  country: 'Deutschland',
  founded_year: null,
  status: 'active',
  description: '',
  logo_url: '',
  primary_color: '#FF0000',
  secondary_color: '#FFFFFF',
  home_gym_name: '',
  home_gym_address: '',
  home_gym_capacity: null
})

const saving = ref(false)

// Watch for verein prop changes (edit mode)
watch(() => props.verein, (verein) => {
  if (verein) {
    Object.assign(form, {
      name: verein.name || '',
      short_name: verein.short_name || '',
      website: verein.website || '',
      email: verein.email || '',
      phone: verein.phone || '',
      instagram: verein.instagram || '',
      facebook: verein.facebook || '',
      twitter: verein.twitter || '',
      address_street: verein.address_street || '',
      address_city: verein.address_city || '',
      address_postal_code: verein.address_postal_code || '',
      address_state: verein.address_state || '',
      region: verein.region || '',
      country: verein.country || 'Deutschland',
      founded_year: verein.founded_year || null,
      status: verein.status || 'active',
      description: verein.description || '',
      logo_url: verein.logo_url || '',
      primary_color: verein.primary_color || '#FF0000',
      secondary_color: verein.secondary_color || '#FFFFFF',
      home_gym_name: verein.home_gym_name || '',
      home_gym_address: verein.home_gym_address || '',
      home_gym_capacity: verein.home_gym_capacity || null
    })
  }
}, { immediate: true })

// Methods
const handleLogoUpload = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (file) {
    // TODO: Implement actual file upload
    // For now, create a temporary URL for preview
    form.logo_url = URL.createObjectURL(file)
  }
}

const saveVerein = async () => {
  saving.value = true
  
  try {
    const method = props.verein ? 'PUT' : 'POST'
    const url = props.verein 
      ? `/api/admin/vereine/${props.verein.id}`
      : '/api/admin/vereine'

    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`
      },
      body: JSON.stringify(form)
    })

    if (response.ok) {
      emit('saved')
    } else {
      const error = await response.json()
      console.error('Failed to save verein:', error)
      // TODO: Show error message to user
    }
  } catch (error) {
    console.error('Error saving verein:', error)
  } finally {
    saving.value = false
  }
}

const getAuthToken = (): string => {
  return localStorage.getItem('admin_token') || 'demo-token'
}
</script>

<style scoped>
.modal-box {
  max-height: 90vh;
  overflow-y: auto;
}

.card {
  margin-bottom: 0;
}

.input-group span {
  font-size: 0.875rem;
}
</style>
