import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

const frontendPort = process.env.KOULU_FRONTEND_PORT !== undefined && process.env.KOULU_FRONTEND_PORT !== ''
  ? parseInt(process.env.KOULU_FRONTEND_PORT)
  : 5173;

const backendPort = process.env.KOULU_BACKEND_PORT !== undefined && process.env.KOULU_BACKEND_PORT !== ''
  ? process.env.KOULU_BACKEND_PORT
  : '8000';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: frontendPort,
    proxy: {
      '/api': {
        target: `http://localhost:${backendPort}`,
        changeOrigin: true,
      },
    },
  },
});
