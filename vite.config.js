import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
    root: resolve(__dirname, 'meet_assistant/src'),
    build: {
        outDir: resolve(__dirname, 'meet_assistant/dist'),
        emptyOutDir: true,
    },
    server: {
        port: 5173,
        proxy: {
            '/ws': {
                target: 'ws://localhost:8088',
                ws: true,
            },
        },
    },
})
