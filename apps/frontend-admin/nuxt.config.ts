export default defineNuxtConfig({
  modules: [
    '@nuxtjs/tailwindcss'
  ],
  
  runtimeConfig: {
    githubClientSecret: process.env.GITHUB_CLIENT_SECRET,
    public: {
      // In production, default to the deployed Cloudflare Worker; in dev override with PUBLIC_API_BASE
      apiBase: process.env.PUBLIC_API_BASE || 'https://basketball-api.inequality.workers.dev',
      githubClientId: process.env.GITHUB_CLIENT_ID || 'your-github-client-id',
      // Use '/' as a safer default for baseUrl in hosted environments; override with BASE_URL for local dev
      baseUrl: process.env.BASE_URL || '/',
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