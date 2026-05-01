// Backend URL — set VITE_API_URL in Render environment variables
// In dev: empty string (Vite proxy handles /api and /ws)
// In production: https://sidekick-backend.onrender.com
export const API_BASE = import.meta.env.VITE_API_URL || ''

export const WS_URL = () => {
  const base = import.meta.env.VITE_API_URL || ''
  if (base) {
    // Convert https:// → wss:// for WebSocket
    return base.replace(/^https/, 'wss').replace(/^http/, 'ws') + '/ws/session'
  }
  // Dev: use current host with Vite proxy
  return `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/session`
}
