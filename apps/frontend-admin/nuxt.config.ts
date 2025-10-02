export default defineNuxtConfig({
  modules: [
    '@nuxtjs/tailwindcss'
  ],
  
  runtimeConfig: {
    githubClientSecret: process.env.GITHUB_CLIENT_SECRET,
    public: {
      apiBase: process.env.PUBLIC_API_BASE || 'http://localhost:8082',
      githubClientId: process.env.GITHUB_CLIENT_ID || 'your-github-client-id',
      baseUrl: process.env.BASE_URL || 'http://localhost:8081',
      demoUsername: process.env.DEMO_USERNAME || 'admin',
      demoPassword: process.env.DEMO_PASSWORD || 'password'
    }
  },

  css: ['~/assets/css/main.css'],

  devtools: { enabled: true },

  tailwindcss: {
    config: {
      plugins: [require('daisyui')],
      daisyui: {
        themes: ['silk', 'dark'],
        darkTheme: 'dark'
      }
    }
  },
  
  compatibilityDate: '2025-09-29'
})