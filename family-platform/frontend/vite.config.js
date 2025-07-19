import { defineConfig } from 'vite'

export default defineConfig({
  root: '.',
  base: '/',
  publicDir: 'public',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    minify: 'terser',
    rollupOptions: {
      input: {
        main: 'index.html',
        register: 'pages/register.html',
        login: 'pages/login.html',
        profile: 'pages/profile.html',
        browse: 'pages/browse.html',
        messages: 'pages/messages.html',
        admin: 'pages/admin.html'
      }
    }
  },
  server: {
    port: 5173,
    host: true,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  css: {
    devSourcemap: true
  },
  optimizeDeps: {
    include: ['axios']
  }
})