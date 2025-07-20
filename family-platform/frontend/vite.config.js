import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'
import eslint from 'vite-plugin-eslint'
import { resolve } from 'path'

export default defineConfig(({ command, mode }) => {
  const isDev = mode === 'development'
  const isProd = mode === 'production'
  
  return {
    // Root and base configuration
    root: '.',
    base: '/',
    
    // Development server configuration
    server: {
      host: '0.0.0.0',
      port: 3000,
      strictPort: true,
      open: false,
      cors: true,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path
        },
        '/ws': {
          target: 'ws://localhost:8000',
          ws: true,
          changeOrigin: true
        }
      },
      hmr: {
        overlay: true
      }
    },
    
    // Preview server (for production builds)
    preview: {
      port: 3001,
      strictPort: true,
      host: '0.0.0.0'
    },
    
    // Build configuration
    build: {
      outDir: 'dist',
      emptyOutDir: true,
      sourcemap: isDev ? 'inline' : false,
      minify: isProd ? 'terser' : false,
      target: ['es2020', 'edge88', 'firefox78', 'chrome87', 'safari13'],
      
      // Chunk splitting strategy
      rollupOptions: {
        input: {
          main: resolve(__dirname, 'index.html'),
          login: resolve(__dirname, 'pages/login.html'),
          register: resolve(__dirname, 'pages/register.html'),
          dashboard: resolve(__dirname, 'pages/dashboard.html'),
          profile: resolve(__dirname, 'pages/profile.html'),
          matching: resolve(__dirname, 'pages/matching.html'),
          messages: resolve(__dirname, 'pages/messages.html'),
          admin: resolve(__dirname, 'pages/admin.html')
        },
        output: {
          // Chunk splitting for better caching
          manualChunks: {
            'vendor': ['axios', 'socket.io-client', 'date-fns'],
            'ui': ['intersection-observer', 'resize-observer-polyfill'],
            'utils': ['fuse.js', 'idb']
          },
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name.split('.')
            const extType = info[info.length - 1]
            if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
              return `assets/images/[name]-[hash][extname]`
            }
            if (/woff|woff2|eot|ttf|otf/i.test(extType)) {
              return `assets/fonts/[name]-[hash][extname]`
            }
            return `assets/[ext]/[name]-[hash][extname]`
          }
        }
      },
      
      // Terser options for production
      terserOptions: isProd ? {
        compress: {
          drop_console: true,
          drop_debugger: true,
          passes: 2
        },
        mangle: {
          safari10: true
        },
        format: {
          safari10: true
        }
      } : {},
      
      // Asset optimization
      assetsInlineLimit: 4096,
      cssCodeSplit: true,
      cssMinify: isProd,
      
      // Performance warnings
      chunkSizeWarningLimit: 1000
    },
    
    // CSS configuration
    css: {
      devSourcemap: isDev,
      modules: {
        localsConvention: 'camelCase'
      },
      preprocessorOptions: {
        css: {
          charset: false
        }
      },
      postcss: {
        plugins: [
          require('autoprefixer'),
          ...(isProd ? [require('cssnano')] : [])
        ]
      }
    },
    
    // Asset handling
    assetsInclude: ['**/*.pdf', '**/*.txt'],
    
    // Plugin configuration
    plugins: [
      // ESLint integration
      eslint({
        failOnError: isProd,
        failOnWarning: isProd,
        emitWarning: isDev,
        emitError: isProd
      }),
      
      // Progressive Web App
      VitePWA({
        registerType: 'autoUpdate',
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
          cleanupOutdatedCaches: true,
          clientsClaim: true,
          skipWaiting: true,
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/api\.familyplatform\.com\/.*/i,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'api-cache',
                expiration: {
                  maxEntries: 100,
                  maxAgeSeconds: 60 * 60 * 24 // 24 hours
                },
                cacheKeyWillBeUsed: async ({ request }) => {
                  return `${request.url}?version=${Date.now()}`
                }
              }
            },
            {
              urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
              handler: 'CacheFirst',
              options: {
                cacheName: 'images-cache',
                expiration: {
                  maxEntries: 500,
                  maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
                }
              }
            },
            {
              urlPattern: /\.(?:woff|woff2|eot|ttf|otf)$/,
              handler: 'CacheFirst',
              options: {
                cacheName: 'fonts-cache',
                expiration: {
                  maxEntries: 50,
                  maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
                }
              }
            }
          ]
        },
        includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
        manifest: {
          name: 'Family Platform',
          short_name: 'FamilyPlatform',
          description: 'Building meaningful relationships for family-focused adults',
          theme_color: '#2D5A8A',
          background_color: '#ffffff',
          display: 'standalone',
          start_url: '/',
          icons: [
            {
              src: 'icons/icon-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            },
            {
              src: 'icons/icon-512x512.png',
              sizes: '512x512',
              type: 'image/png'
            },
            {
              src: 'icons/icon-512x512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'any maskable'
            }
          ]
        },
        devOptions: {
          enabled: true
        }
      })
    ],
    
    // Dependency optimization
    optimizeDeps: {
      include: [
        'axios',
        'socket.io-client',
        'date-fns',
        'fuse.js',
        'idb'
      ],
      exclude: [
        'workbox-sw',
        'workbox-strategies'
      ]
    },
    
    // Define global constants
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
      __DEV__: isDev,
      __PROD__: isProd
    },
    
    // Environment variables
    envPrefix: ['VITE_', 'FAMILY_PLATFORM_'],
    
    // Worker configuration
    worker: {
      format: 'es',
      plugins: []
    },
    
    // Experimental features
    experimental: {
      renderBuiltUrl(filename) {
        return `/${filename}`
      }
    },
    
    // Logging
    logLevel: isDev ? 'info' : 'warn',
    clearScreen: false
  }
})