import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
  port: 3001,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:7777',
      changeOrigin: true,
    },
    '/ws': {
      target: 'ws://127.0.0.1:7777',
      ws: true,
    },
  },
},
})
