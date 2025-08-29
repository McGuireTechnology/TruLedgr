import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools';
// https://vite.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        vueDevTools(),
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        },
    },
    build: {
        // Optimize for production
        minify: 'terser',
        cssMinify: true,
        rollupOptions: {
            output: {
                // Manual chunks for better caching
                manualChunks: {
                    vendor: ['vue', 'vue-router']
                }
            }
        }
    },
    // Ensure proper base URL for deployment
    base: '/',
});
