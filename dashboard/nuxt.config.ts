// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  sourcemap: {
    server: false,
    client: false
  },
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
    build: {
      sourcemap: false,
      rollupOptions: {
        onwarn(warning, defaultHandler) {
          if (warning.code === 'SOURCEMAP_ERROR' || warning.message.includes('Sourcemap is likely to be incorrect')) {
            return
          }
          defaultHandler(warning)
        }
      }
    }
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
