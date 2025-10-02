<template>
  <div class="min-h-screen bg-base-200 flex items-center justify-center">
    <div class="card w-full max-w-sm bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title justify-center">Admin Login</h2>
        <p class="text-center text-base-content/70 mb-6">
          Secure access to basketball crawl logs
        </p>
        
        <div v-if="error" class="alert alert-error mb-4">
          <span>{{ error }}</span>
        </div>
        
        <!-- GitHub OAuth Login -->
        <button 
          @click="loginWithGitHub"
          class="btn btn-primary btn-block mb-4"
          :class="{ 'loading': loading }"
          :disabled="loading"
        >
          <svg v-if="!loading" class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
          </svg>
          {{ loading ? 'Connecting...' : 'Login with GitHub' }}
        </button>
        
        <div class="divider">OR</div>
        
        <!-- Fallback Demo Login -->
        <form @submit.prevent="handleDemoLogin">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Demo Username</span>
            </label>
            <input 
              v-model="username" 
              type="text" 
              placeholder="Enter demo username" 
              class="input input-bordered input-sm" 
              required 
            />
          </div>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">Demo Password</span>
            </label>
            <input 
              v-model="password" 
              type="password" 
              placeholder="Enter demo password" 
              class="input input-bordered input-sm" 
              required 
            />
          </div>
          
          <div class="form-control mt-4">
            <button 
              type="submit" 
              class="btn btn-outline btn-sm" 
              :class="{ 'loading': demoLoading }"
              :disabled="demoLoading"
            >
              {{ demoLoading ? 'Logging in...' : 'Demo Login' }}
            </button>
          </div>
        </form>
        
        <div class="text-center mt-4">
          <p class="text-xs text-base-content/50">
            Demo credentials set via environment variables
          </p>
          <p class="text-xs text-base-content/50 mt-1">
            GitHub login requires OAuth app setup
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
const demoLoading = ref(false)

async function loginWithGitHub() {
  loading.value = true
  error.value = ''
  
  try {
    // Redirect to GitHub OAuth
    await navigateTo('/api/auth/github', { external: true })
  } catch (err) {
    error.value = 'GitHub login failed. Please try demo login.'
    loading.value = false
  }
}

async function handleDemoLogin() {
  demoLoading.value = true
  error.value = ''
  
  try {
    const config = useRuntimeConfig()
    const validUsername = config.public.demoUsername || 'admin'
    const validPassword = config.public.demoPassword || 'password'
    
    // Environment-based demo authentication
    if (username.value === validUsername && password.value === validPassword) {
      const sessionData = {
        user: {
          id: 1,
          username: validUsername,
          name: 'Demo Admin',
          email: 'admin@demo.com',
          avatar: 'https://github.com/github.png'
        },
        authenticated: true,
        loginTime: new Date().toISOString()
      }
      
      // Set demo session cookie
      const sessionToken = btoa(JSON.stringify(sessionData))
      const authCookie = useCookie('admin-auth', {
        secure: true,
        httpOnly: false,
        sameSite: 'strict',
        maxAge: 60 * 60 * 24 // 24 hours
      })
      
      authCookie.value = sessionToken
      
      await navigateTo('/')
    } else {
      error.value = 'Invalid demo credentials'
    }
  } catch (err) {
    error.value = 'Demo login failed'
  } finally {
    demoLoading.value = false
  }
}
</script>