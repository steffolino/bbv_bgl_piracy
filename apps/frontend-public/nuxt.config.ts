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
  app: {
    head: {
      link: [
        { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/favicon-32.png' },
        { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/favicon-16.png' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
        { rel: 'manifest', href: '/site.webmanifest' }
      ]
    }
  },
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
        themes: [
          {
            graffiti: {
              primary: '#C9A227',     // warm gold
              secondary: '#F5F3E7',   // chalk white
              accent: '#C53030',      // blood red
              neutral: '#111111',     // deep black
              'base-100': '#ffffff',  // more white-ish for light base
              info: '#2563EB',        // electric blue scribbles
              success: '#22C55E',     // optional green
              warning: '#DA7635',     // ochre/orange
              error: '#C53030',       // reuse blood red
            },
            graffitiDark: {
              primary: '#C9A227',
              secondary: '#F5F3E7',
              accent: '#C53030',
              neutral: '#111111',
              'base-100': '#111111',
              info: '#2563EB',
              success: '#22C55E',
              warning: '#DA7635',
              error: '#C53030',
            }
          },
          'dark', 'cupcake'
        ],
        darkTheme: 'graffitiDark',
        base: true,
        styled: true,
        utils: true,
        logs: false,
        rtl: false,
        prefix: '',
      }
    }
  }
})