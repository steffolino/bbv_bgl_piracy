<template>
  <div class="min-h-screen">
    <!-- Navigation -->
    <div class="navbar bg-base-200">
      <div class="navbar-start">
        <div class="dropdown">
          <div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16"></path>
            </svg>
          </div>
          <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
            <li><NuxtLink to="/">{{ $t('nav.dashboard') }}</NuxtLink></li>
            <li><NuxtLink to="/basketball">🏀 Basketball Stats</NuxtLink></li>
            <li><NuxtLink to="/players">{{ $t('nav.players') }}</NuxtLink></li>
            <li><NuxtLink to="/teams">{{ $t('nav.teams') }}</NuxtLink></li>
            <li><NuxtLink to="/leaders">{{ $t('nav.leaders') }}</NuxtLink></li>
            <li><NuxtLink to="/explorer">{{ $t('nav.explorer') }}</NuxtLink></li>
          </ul>
        </div>
        <NuxtLink to="/" class="btn btn-ghost px-2">
          <svg width="40" height="40" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" class="animate-bounce">
            <circle cx="60" cy="60" r="56" stroke="#C9A227" stroke-width="8" fill="#111111" />
            <text x="50%" y="50%" text-anchor="middle" dy=".35em" font-size="24" font-family="Impact, Arial Black, sans-serif" fill="#C53030" stroke="#F5F3E7" stroke-width="1.5">BBV</text>
          </svg>
        </NuxtLink>
      </div>
      
      <div class="navbar-center hidden lg:flex">
        <ul class="menu menu-horizontal px-1">
          <li><NuxtLink to="/">
            <span class="inline-flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="#C9A227" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke-width="2"/></svg>
              {{ $t('nav.dashboard') }}
            </span>
          </NuxtLink></li>
          <li><NuxtLink to="/basketball">
            <span class="inline-flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="#C53030" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke-width="2"/><text x="12" y="16" text-anchor="middle" font-size="10" fill="#C53030">🏀</text></svg>
              Basketball Stats
            </span>
          </NuxtLink></li>
          <li><NuxtLink to="/players">
            <span class="inline-flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="#2563EB" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke-width="2"/><text x="12" y="16" text-anchor="middle" font-size="10" fill="#2563EB">👤</text></svg>
              {{ $t('nav.players') }}
            </span>
          </NuxtLink></li>
          <li><NuxtLink to="/teams">
            <span class="inline-flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="#22C55E" viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" stroke-width="2"/><text x="12" y="16" text-anchor="middle" font-size="10" fill="#22C55E">👥</text></svg>
              {{ $t('nav.teams') }}
            </span>
          </NuxtLink></li>
          <li><NuxtLink to="/leaders">
            <span class="inline-flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="#DA7635" viewBox="0 0 24 24"><polygon points="12,2 22,22 2,22" stroke-width="2"/><text x="12" y="16" text-anchor="middle" font-size="10" fill="#DA7635">⭐</text></svg>
              {{ $t('nav.leaders') }}
            </span>
          </NuxtLink></li>
          <li><NuxtLink to="/explorer">
            <span class="inline-flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="#F5F3E7" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" stroke-width="2"/><text x="12" y="16" text-anchor="middle" font-size="10" fill="#F5F3E7">🔍</text></svg>
              {{ $t('nav.explorer') }}
            </span>
          </NuxtLink></li>
        </ul>
      </div>
      
      <div class="navbar-end gap-2">
        <!-- Language Switch -->
        <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn btn-ghost btn-sm">
            DE
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
            <li><a @click="setTheme('light')">Light</a></li>
            <li><a @click="setTheme('dark')">Dark</a></li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
  <GraffitiHero />
  <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import GraffitiHero from '~/components/GraffitiHero.vue'
const { t } = useI18n()
const currentLocale = ref('de')
function switchLocale(newLocale: string) {
  currentLocale.value = newLocale
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