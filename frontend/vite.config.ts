import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// Check if SSL certificates exist
const sslCertPath = path.resolve(__dirname, 'ssl/cert.pem')
const sslKeyPath = path.resolve(__dirname, 'ssl/key.pem')
const hasSSL = fs.existsSync(sslCertPath) && fs.existsSync(sslKeyPath)

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Listen on all network interfaces
    port: 5173,
    strictPort: true,
    https: hasSSL ? {
      key: fs.readFileSync(sslKeyPath),
      cert: fs.readFileSync(sslCertPath),
    } : undefined,
  },
})
