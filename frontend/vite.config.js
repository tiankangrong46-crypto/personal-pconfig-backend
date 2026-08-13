import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  // Cloudflare Pages serves Vite assets from the site root; Django collects
  // the same build under /static/ for its standalone deployment.
  base: process.env.CF_PAGES === '1' ? '/' : '/static/',
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8002',
    },
  },
})
