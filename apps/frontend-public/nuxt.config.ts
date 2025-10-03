export default defineNuxtConfig({
  css: [
    '@/assets/css/main.css',
  ],
  modules: [
    '@nuxtjs/tailwindcss',
    'nuxt-icon',
    'nuxt-head',
    'nuxt-i18n',
  ],
  tailwindcss: {
    viewer: false,
  },
  app: {
    baseURL: '/',
  },
  i18n: {
    locales: [
      {
        code: 'de',
        name: 'Deutsch',
        file: 'de.json',
      },
      {
        code: 'en',
        name: 'English',
        file: 'en.json',
      },
    ],
    langDir: 'locales/',
    defaultLocale: 'de',
  },
  devtools: { enabled: true },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'https://basketball-api.inequality.workers.dev',
    },
  },
})