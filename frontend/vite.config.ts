import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Allow external access
  },
  build: {
    outDir: 'dist',
    sourcemap: false, // Disable sourcemaps in production
  },
  preview: {
    port: 5173,
    host: true,
  }
})