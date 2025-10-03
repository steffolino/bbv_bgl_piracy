/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{vue,js,ts}',
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.{vue,js,ts}',
    './app.vue',
  ],
  theme: {
    extend: {},
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: [
      {
        mybasketball: {
          ...require('daisyui/src/theming/themes')['[data-theme=lofi]'],
          primary: '#F7931E',
          secondary: '#1e293b',
          accent: '#ff6b35',
          neutral: '#23272a',
          'base-100': '#f8fafc',
          info: '#3b82f6',
          success: '#22c55e',
          warning: '#facc15',
          error: '#ef4444',
        },
        mybasketballdark: {
          ...require('daisyui/src/theming/themes')['[data-theme=synthwave]'],
          primary: '#F7931E',
          secondary: '#23272a',
          accent: '#ff6b35',
          neutral: '#1e293b',
          'base-100': '#18181b',
          info: '#60a5fa',
          success: '#22c55e',
          warning: '#facc15',
          error: '#ef4444',
        },
      },
      'lofi', 'synthwave', 'cupcake', 'business'
    ],
    darkTheme: 'mybasketballdark',
    base: true,
    styled: true,
    utils: true,
    logs: false,
    rtl: false,
    prefix: '',
  },
}
