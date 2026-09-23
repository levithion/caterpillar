import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes, req) => {
            if (req.url?.includes('/live/stream')) {
              proxyRes.headers['cache-control'] = 'no-cache';
            }
          });
        },
      },
      '/health': 'http://localhost:8000',
      '/ready': 'http://localhost:8000',
    },
  },
})
