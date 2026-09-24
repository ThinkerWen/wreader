import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: { outDir: 'dist' },
  server: { proxy: { '/novel': 'http://127.0.0.1:8000', '/api': 'http://127.0.0.1:8000' } },
})