<template>
  <div class="min-h-screen">
    <!-- Navigation -->
    <div class="navbar bg-base-200">
      <div class="navbar-start">
        <NuxtLink to="/" class="btn btn-ghost text-xl">🏀 Basketball Admin</NuxtLink>
      </div>
      
      <div class="navbar-center hidden lg:flex">
        <ul class="menu menu-horizontal px-1">
          <li><NuxtLink to="/">Dashboard</NuxtLink></li>
          <li><NuxtLink to="/crawl-logs">Crawl Logs</NuxtLink></li>
          <li><NuxtLink to="/qa">QA Issues</NuxtLink></li>
          <li><NuxtLink to="/aliases">Aliases</NuxtLink></li>
          <li><NuxtLink to="/exports">Exports</NuxtLink></li>
        </ul>
      </div>
      
      <div class="navbar-end">
        <!-- User Profile Dropdown -->
        <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar">
            <div class="w-8 rounded-full">
              <img 
                :src="userInfo?.user?.avatar || 'https://github.com/github.png'" 
                :alt="userInfo?.user?.name || 'User'" 
              />
            </div>
          </div>
          <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
            <li class="menu-title">
              <span>{{ userInfo?.user?.name || 'User' }}</span>
              <span class="text-xs text-base-content/50">{{ userInfo?.user?.username || '' }}</span>
            </li>
            <li><a @click="logout" class="text-error">Logout</a></li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
const userInfo = ref<{ authenticated: boolean; user?: any } | null>(null)

// Fetch user info on mount
onMounted(async () => {
  try {
    userInfo.value = await $fetch<{ authenticated: boolean; user?: any }>('/api/auth/me')
  } catch (error) {
    console.error('Failed to fetch user info:', error)
  }
})

async function logout() {
  try {
    await $fetch('/api/auth/logout', { method: 'POST' })
    await navigateTo('/login')
  } catch (error) {
    console.error('Logout failed:', error)
    // Fallback to cookie clearing
    const authCookie = useCookie('admin-auth')
    authCookie.value = null
    await navigateTo('/login')
  }
}
</script>