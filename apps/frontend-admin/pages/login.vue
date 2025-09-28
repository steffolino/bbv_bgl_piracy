<template>
  <div class="min-h-screen bg-base-200 flex items-center justify-center">
    <div class="card w-full max-w-sm bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title justify-center">Admin Login</h2>
        
        <form @submit.prevent="handleLogin">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Username</span>
            </label>
            <input 
              v-model="username" 
              type="text" 
              placeholder="Enter username" 
              class="input input-bordered" 
              required 
            />
          </div>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">Password</span>
            </label>
            <input 
              v-model="password" 
              type="password" 
              placeholder="Enter password" 
              class="input input-bordered" 
              required 
            />
          </div>
          
          <div v-if="error" class="alert alert-error mt-4">
            <span>{{ error }}</span>
          </div>
          
          <div class="form-control mt-6">
            <button 
              type="submit" 
              class="btn btn-primary" 
              :class="{ 'loading': loading }"
              :disabled="loading"
            >
              {{ loading ? 'Logging in...' : 'Login' }}
            </button>
          </div>
        </form>
        
        <div class="text-center mt-4">
          <p class="text-sm text-base-content/70">
            Demo: admin / password
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false
})

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  error.value = ''
  
  try {
    // Simple demo authentication
    if (username.value === 'admin' && password.value === 'password') {
      const authCookie = useCookie('admin-auth', {
        default: () => null,
        secure: true,
        httpOnly: false,
        sameSite: 'strict',
        maxAge: 60 * 60 * 24 // 24 hours
      })
      
      authCookie.value = 'authenticated'
      
      await navigateTo('/')
    } else {
      error.value = 'Invalid credentials'
    }
  } catch (err) {
    error.value = 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>