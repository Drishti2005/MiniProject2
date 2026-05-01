import { createContext, useContext, useState, useCallback } from 'react'
import { authAPI } from '../services/api'
const Ctx = createContext(null)
export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => { try{return JSON.parse(localStorage.getItem('mc_user'))}catch{return null} })
  const login  = useCallback(async (email,pw) => {
    if(!email||!pw) throw new Error('Email and password are required')
    const d = await authAPI.login(email,pw)
    localStorage.setItem('mc_user', JSON.stringify(d.user)); localStorage.setItem('mc_token', d.token); setUser(d.user)
  },[])
  const signup = useCallback(async (name,email,pw) => {
    if(!name||!email||!pw) throw new Error('All fields are required')
    if(pw.length<6) throw new Error('Password must be at least 6 characters')
    const d = await authAPI.signup(name,email,pw)
    localStorage.setItem('mc_user', JSON.stringify(d.user)); localStorage.setItem('mc_token', d.token); setUser(d.user)
  },[])
  const logout = useCallback(() => { localStorage.removeItem('mc_user'); localStorage.removeItem('mc_token'); setUser(null) },[])
  return <Ctx.Provider value={{user,login,signup,logout}}>{children}</Ctx.Provider>
}
export const useAuth = () => useContext(Ctx)
