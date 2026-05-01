// Strip trailing slash from env var to prevent double-slash URLs
export const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

export const WS_URL = () => {
  const base = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
  if (base) {
    return base.replace(/^https/, 'wss').replace(/^http/, 'ws') + '/ws/session'
  }
  return `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/session`
}
