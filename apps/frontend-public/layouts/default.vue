<template>
  <div class="min-h-screen">
    <!-- Navigation -->
    <div class="navbar bg-base-200">
      <div class="navbar-start">
        <NuxtLink to="/" class="btn btn-ghost text-xl">BGL Stats</NuxtLink>
      </div>
      
      <div class="navbar-center hidden lg:flex">
        <ul class="menu menu-horizontal px-1">
          <li><NuxtLink to="/">{{ $t('nav.dashboard') }}</NuxtLink></li>
          <li><NuxtLink to="/players">{{ $t('nav.players') }}</NuxtLink></li>
          <li><NuxtLink to="/explorer">{{ $t('nav.explorer') }}</NuxtLink></li>
        </ul>
      </div>
      
      <div class="navbar-end gap-2">
        <!-- Language Switch -->
        <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn btn-ghost btn-sm">
            {{ currentLocale.toUpperCase() }}
          </div>
          <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-24">
            <li><a @click="switchLocale('de')">DE</a></li>
            <li><a @click="switchLocale('en')">EN</a></li>
          </ul>
        </div>
        
        <!-- Theme Switch -->
        <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn btn-ghost btn-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
            </svg>
          </div>
          <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-28">
            <li><a @click="setTheme('light')">{{ $t('theme.light') }}</a></li>
            <li><a @click="setTheme('dark')">{{ $t('theme.dark') }}</a></li>
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
const { locale, setLocale } = useI18n()

const currentLocale = computed(() => locale.value || 'de')

function switchLocale(newLocale: string) {
  setLocale(newLocale)
}

function setTheme(theme: string) {
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }
}

onMounted(() => {
  if (typeof localStorage !== 'undefined') {
    const savedTheme = localStorage.getItem('theme') || 'light'
    setTheme(savedTheme)
  }
})
</script>