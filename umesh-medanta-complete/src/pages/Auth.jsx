import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Stethoscope, Mail, Lock, User, AlertTriangle, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

// OUTSIDE component — prevents focus loss on re-render
function Field({ id, label, type, icon, placeholder, autoComplete, value, onChange, showPw, onTogglePw }) {
  return (
    <div>
      <label htmlFor={id} className="text-xs font-bold text-white/60 uppercase tracking-widest mb-1.5 block">{label}</label>
      <div className="relative">
        <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/40 pointer-events-none">{icon}</span>
        <input id={id} name={id} type={id==='password'?(showPw?'text':'password'):type}
          required autoComplete={autoComplete} value={value} onChange={onChange}
          className="w-full pl-10 pr-10 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/30 text-sm focus:outline-none focus:border-white/50 focus:bg-white/15 transition-all"
          placeholder={placeholder}/>
        {id==='password'&&<button type="button" onClick={onTogglePw} className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70 transition-colors">{showPw?<EyeOff size={15}/>:<Eye size={15}/>}</button>}
      </div>
    </div>
  )
}

export default function Auth() {
  const {login,signup,user} = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [mode,setMode]     = useState(params.get('mode')==='signup'?'signup':'login')
  const [form,setForm]     = useState({name:'',email:'',password:''})
  const [error,setError]   = useState('')
  const [loading,setLoading] = useState(false)
  const [showPw,setShowPw] = useState(false)
  const [shake,setShake]   = useState(false)

  useEffect(()=>{ if(user) navigate('/session',{replace:true}) },[user])

  const set = k => e => setForm(f=>({...f,[k]:e.target.value}))

  const submit = async e => {
    e.preventDefault(); setError(''); setLoading(true)
    try {
      if(mode==='login') await login(form.email,form.password)
      else               await signup(form.name,form.email,form.password)
      navigate('/session')
    } catch(err) {
      setError(err.message); setShake(true); setTimeout(()=>setShake(false),600)
    } finally { setLoading(false) }
  }

  const toggle = () => { setMode(m=>m==='login'?'signup':'login'); setError(''); setForm({name:'',email:'',password:''}) }

  return (
    <div className="min-h-screen relative flex items-center justify-center px-4 overflow-hidden font-sans">
      <div className="absolute inset-0 bg-cover bg-center" style={{backgroundImage:"url('https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1600&q=80')"}}/>
      <div className="absolute inset-0" style={{background:'linear-gradient(135deg,rgba(11,42,70,0.92) 0%,rgba(11,42,70,0.82) 100%)'}}/>

      <motion.div initial={{opacity:0,y:28}} animate={{opacity:1,y:0}} transition={{duration:0.5}} className="relative w-full max-w-md z-10">
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-cred flex items-center justify-center mx-auto mb-4 shadow-lg">
            <Stethoscope size={28} className="text-white"/>
          </div>
          <h1 className="text-3xl font-extrabold text-white">{mode==='login'?'Welcome back':'Create account'}</h1>
          <p className="text-white/60 text-sm mt-1">{mode==='login'?'Sign in to Sidekick Clinical AI':'Start your first clinical session'}</p>
        </div>

        <motion.div animate={shake?{x:[-6,6,-6,6,-4,4,-2,2,0]}:{}} transition={{duration:0.5}}
          className="glass-dark rounded-3xl border border-white/15 p-8 shadow-glass">
          <AnimatePresence>
            {error&&(
              <motion.div initial={{opacity:0,y:-8,scale:0.97}} animate={{opacity:1,y:0,scale:1}} exit={{opacity:0,y:-8}}
                className="flex items-start gap-3 bg-cred/15 border border-cred/40 text-red-300 rounded-2xl p-4 mb-5">
                <AlertTriangle size={18} className="flex-shrink-0 mt-0.5 text-red-400"/>
                <div>
                  <p className="font-semibold text-sm">{mode==='login'?'Authentication failed':'Could not create account'}</p>
                  <p className="text-xs mt-0.5 text-red-400/80">{error}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={submit} className="space-y-4">
            <AnimatePresence>
              {mode==='signup'&&(
                <motion.div initial={{opacity:0,height:0}} animate={{opacity:1,height:'auto'}} exit={{opacity:0,height:0}}>
                  <Field id="name" label="Full name" type="text" icon={<User size={15}/>} placeholder="Dr. Jane Smith" autoComplete="name" value={form.name} onChange={set('name')} showPw={showPw} onTogglePw={()=>setShowPw(v=>!v)}/>
                </motion.div>
              )}
            </AnimatePresence>
            <Field id="email"    label="Email"    type="email"    icon={<Mail size={15}/>} placeholder="doctor@hospital.com" autoComplete="email"                          value={form.email}    onChange={set('email')}    showPw={showPw} onTogglePw={()=>setShowPw(v=>!v)}/>
            <Field id="password" label="Password" type="password" icon={<Lock size={15}/>} placeholder={mode==='signup'?'Min. 6 characters':'••••••••'} autoComplete={mode==='signup'?'new-password':'current-password'} value={form.password} onChange={set('password')} showPw={showPw} onTogglePw={()=>setShowPw(v=>!v)}/>
            <button type="submit" disabled={loading}
              className="w-full bg-cred hover:bg-cred-light text-white font-bold py-3.5 rounded-xl transition-all disabled:opacity-50 shadow-lg flex items-center justify-center gap-2 mt-1">
              {loading?<><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"/>{mode==='login'?'Signing in…':'Creating…'}</>:mode==='login'?'Sign in':'Create account'}
            </button>
          </form>

          <p className="text-center text-sm text-white/50 mt-6">
            {mode==='login'?'No account? ':'Already have an account? '}
            <button onClick={toggle} className="text-white font-bold hover:underline">{mode==='login'?'Create one free':'Sign in'}</button>
          </p>
        </motion.div>

        <p className="text-center mt-5"><Link to="/" className="text-sm text-white/40 hover:text-white/70 transition-colors">← Back to home</Link></p>
      </motion.div>
    </div>
  )
}
