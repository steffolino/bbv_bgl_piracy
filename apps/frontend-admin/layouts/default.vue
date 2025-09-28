<template>
  <div class="min-h-screen">
    <!-- Navigation -->
    <div class="navbar bg-base-200">
      <div class="navbar-start">
        <NuxtLink to="/" class="btn btn-ghost text-xl">Admin Panel</NuxtLink>
      </div>
      
      <div class="navbar-center hidden lg:flex">
        <ul class="menu menu-horizontal px-1">
          <li><NuxtLink to="/">Dashboard</NuxtLink></li>
          <li><NuxtLink to="/qa">QA Issues</NuxtLink></li>
          <li><NuxtLink to="/aliases">Aliases</NuxtLink></li>
          <li><NuxtLink to="/exports">Exports</NuxtLink></li>
        </ul>
      </div>
      
      <div class="navbar-end">
        <button @click="logout" class="btn btn-ghost btn-sm">
          Logout
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
function logout() {
  const authCookie = useCookie('admin-auth')
  authCookie.value = null
  
  navigateTo('/login')
}
</script>