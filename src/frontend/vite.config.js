import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '127.0.0.1',
    allowedHosts: ['porridge-shorthand-shorty.ngrok-free.dev'],
    proxy: {
      '/api': {
        target: process.env.PIPELINE_API_TARGET || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
