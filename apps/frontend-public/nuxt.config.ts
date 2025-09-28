export default defineNuxtConfig({
  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/i18n'
  ],
  
  runtimeConfig: {
    public: {
      apiBase: process.env.PUBLIC_API_BASE || 'http://localhost:8082'
    }
  },

  i18n: {
    locales: [
      {
        code: 'en',
        name: 'English',
        file: 'en.json'
      },
      {
        code: 'de', 
        name: 'Deutsch',
        file: 'de.json'
      }
    ],
    lazy: true,
    langDir: 'locales/',
    defaultLocale: 'de',
    strategy: 'prefix_except_default'
  },

  css: ['~/assets/css/main.css'],

  devtools: { enabled: true },

  tailwindcss: {
    config: {
      plugins: [require('daisyui')],
      daisyui: {
        themes: ['light', 'dark'],
        darkTheme: 'dark'
      }
    }
  }
})