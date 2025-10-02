export default defineNuxtConfig({
  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/i18n'
  ],
  
  runtimeConfig: {
    public: {
      apiBase: process.env.PUBLIC_API_BASE || 'https://basketball-api.inequality.workers.dev'
    }
  },

  // GitHub Pages configuration
  target: 'static',
  ssr: false,
  nitro: {
    prerender: {
      routes: ['/basketball']
    }
  },

  app: {
    baseURL: '/'
  },

  i18n: {
    locales: [
      {
        code: 'de',
        name: 'Deutsch',
        file: 'de.json'
      },
      {
        code: 'en',
        name: 'English', 
        file: 'en.json'
      }
    ],
    langDir: 'locales/',
    defaultLocale: 'de'
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