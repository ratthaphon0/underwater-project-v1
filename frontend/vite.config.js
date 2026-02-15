import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    // 👇 บรรทัดนี้สำคัญมากสำหรับ Cloudflare Tunnel / Domain ภายนอก
    allowedHosts: ['submarines.app'], 
    // หรือถ้าขี้เกียจใส่ชื่อโดเมน ให้ใช้ true (ไม่แนะนำสำหรับ Production แต่ง่ายสำหรับ Dev)
    // allowedHosts: true, 
    origin: 'https://submarines.app',
    hmr: {
      clientPort: 443,
    },
    watch: {
      usePolling: true,
    },
  },
})