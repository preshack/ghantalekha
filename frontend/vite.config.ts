import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// Proxy API calls to Flask backend on :8000 during dev
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
