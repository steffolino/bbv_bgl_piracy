export default defineNuxtConfig({
  modules: [
    '@nuxtjs/tailwindcss'
  ],
  
  runtimeConfig: {
    public: {
      apiBase: process.env.PUBLIC_API_BASE || 'http://localhost:8082'
    }
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