// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],
  modules: [
    '@primevue/nuxt-module',
    '@nuxtjs/google-fonts'
  ],
  googleFonts: {
    families: {
      Poppins: [300, 400, 500, 600, 700, 800],
      'Kantumruy+Pro': [300, 400, 500, 600, 700]
    },
    subsets: ['khmer', 'latin'],
    display: 'swap',
    prefetch: true,
    preconnect: true,
    preload: true
  },
  vite: {
    plugins: [
      tailwindcss(),
    ],
  },
  primevue: {
    options: {
      theme: {
        preset: 'Aura',
        options: {
          darkModeSelector: '[data-bs-theme="dark"]'
        }
      }
    }
  }
})
