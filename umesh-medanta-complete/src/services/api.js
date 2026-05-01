import { API_BASE } from './config'
const B = `${API_BASE}/api`
const h = () => ({ 'Content-Type':'application/json', ...(localStorage.getItem('mc_token') ? { Authorization:`Bearer ${localStorage.getItem('mc_token')}` } : {}) })

async function req(path, opts = {}) {
  const r = await fetch(`${B}${path}`, { headers: h(), ...opts })
  const d = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(d.detail || `HTTP ${r.status}`)
  return d
}

export const authAPI     = {
  login:  (email, pw)        => req('/auth/login',  { method:'POST', body: JSON.stringify({ email, password: pw }) }),
  signup: (name, email, pw)  => req('/auth/signup', { method:'POST', body: JSON.stringify({ name, email, password: pw }) }),
}
export const sessionsAPI = {
  list:   ()   => req('/sessions'),
  get:    (id) => req(`/sessions/${id}`),
  del:    (id) => req(`/sessions/${id}`, { method:'DELETE' }),
}
export const healthAPI   = { ai: () => req('/health/ai') }
