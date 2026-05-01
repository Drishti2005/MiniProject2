import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Stethoscope, Zap, Globe, FileText, Shield, Clock, Brain, ChevronRight } from 'lucide-react'

const features = [
  {icon:Brain,   title:'AI Term Simplification', desc:'Medical jargon explained in plain language, color-coded by clinical importance.'},
  {icon:Globe,   title:'Real-time Translation',  desc:'Full bilingual transcript — patient reads their language, doctor reads English.'},
  {icon:Zap,     title:'Instant Insights',       desc:'Groq-powered LLM delivers terms, questions, and summaries in under 2 seconds.'},
  {icon:FileText,title:'Visit Summaries',        desc:'Structured summaries with diagnosis, medications, and follow-up instructions.'},
  {icon:Shield,  title:'Privacy First',          desc:'No audio stored. PII redacted from logs. Keys stay in your .env file.'},
  {icon:Clock,   title:'Session History',        desc:'Browse past sessions, view transcripts, and review AI-generated summaries.'},
]

export default function Landing() {
  return (
    <div className="min-h-screen font-sans">
      {/* Nav */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-white/90 backdrop-blur-xl border-b border-slate-border/50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-navy flex items-center justify-center"><Stethoscope size={16} className="text-white"/></div>
            <span className="font-bold text-lg text-navy">Sidekick</span>
            <span className="text-xs text-slate-muted hidden sm:block ml-1">by Medanta AI</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/auth" className="text-sm font-medium text-slate-muted hover:text-navy transition-colors px-4 py-2">Sign in</Link>
            <Link to="/auth?mode=signup" className="text-sm font-bold bg-navy text-white px-5 py-2 rounded-full hover:bg-navy-light transition-colors shadow-card">Get started</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative min-h-screen flex items-center overflow-hidden">
        <div className="absolute inset-0 bg-cover bg-center" style={{backgroundImage:"url('https://images.unsplash.com/photo-1551190822-a9333d879b1f?w=1800&q=80')"}}/>
        <div className="absolute inset-0" style={{background:'linear-gradient(135deg,rgba(11,42,70,0.93) 0%,rgba(11,42,70,0.82) 60%,rgba(7,30,51,0.95) 100%)'}}/>
        <div className="relative max-w-6xl mx-auto px-6 pt-24 pb-16 w-full grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <motion.div initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{duration:0.6}}>
              <span className="inline-flex items-center gap-2 bg-white/15 border border-white/25 text-white px-4 py-1.5 rounded-full text-sm font-semibold mb-6">
                <Zap size={14}/> Powered by Groq · Gemini
              </span>
            </motion.div>
            <motion.h1 initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{duration:0.6,delay:0.1}}
              className="text-5xl lg:text-6xl font-extrabold text-white leading-tight mb-6">
              Your AI<br/>Clinical<br/><span className="text-teal-300">Concierge</span>
            </motion.h1>
            <motion.p initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{duration:0.6,delay:0.2}}
              className="text-white/75 text-lg leading-relaxed mb-10 max-w-lg">
              Real-time transcription, medical term simplification, bilingual patient prompts, and AI-generated visit summaries.
            </motion.p>
            <motion.div initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{duration:0.6,delay:0.3}} className="flex flex-col sm:flex-row gap-4">
              <Link to="/auth?mode=signup" className="inline-flex items-center justify-center gap-2 bg-cred text-white font-bold px-8 py-4 rounded-full shadow-lg hover:bg-cred-light transition-all">
                Start free session <ChevronRight size={18}/>
              </Link>
              <Link to="/auth" className="inline-flex items-center justify-center gap-2 bg-white/15 border border-white/30 text-white font-semibold px-8 py-4 rounded-full hover:bg-white/25 transition-all">
                Sign in
              </Link>
            </motion.div>
          </div>
          {/* Demo card */}
          <motion.div initial={{opacity:0,x:30}} animate={{opacity:1,x:0}} transition={{duration:0.7,delay:0.4}}>
            <div className="glass-dark rounded-3xl border border-white/15 overflow-hidden shadow-glass">
              <div className="bg-white/10 px-5 py-3 flex items-center gap-3 border-b border-white/10">
                <div className="flex gap-1.5">{['bg-red-400/70','bg-yellow-400/70','bg-green-400/70'].map(c=><div key={c} className={`w-3 h-3 rounded-full ${c}`}/>)}</div>
                <span className="text-xs text-white/60 font-medium">Live Session</span>
                <div className="ml-auto flex items-center gap-1.5">
                  <motion.span animate={{opacity:[1,0.3,1]}} transition={{repeat:Infinity,duration:1.2}} className="w-2 h-2 rounded-full bg-green-400"/>
                  <span className="text-xs text-green-300 font-semibold">Recording</span>
                </div>
              </div>
              <div className="p-5 space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-white/10 border border-white/20 rounded-xl p-3">
                    <p className="text-xs font-bold text-teal-300 mb-1">🌐 HINDI</p>
                    <p className="text-sm text-white">आपका रक्तचाप 160/95 है। आपको <span className="bg-red-500/30 px-1 rounded font-semibold text-red-300">उच्च रक्तचाप</span> है।</p>
                  </div>
                  <div className="bg-navy-muted/60 border border-white/10 rounded-xl p-3">
                    <p className="text-xs font-bold text-slate-300 mb-1">🇬🇧 EN</p>
                    <p className="text-sm text-white/80">Your BP is 160/95. You have <span className="bg-red-500/20 px-1 rounded font-semibold text-red-300">hypertension</span>.</p>
                  </div>
                </div>
                <div className="flex gap-2 flex-wrap">
                  <span className="text-xs bg-red-500/20 text-red-300 border border-red-500/30 px-2.5 py-1 rounded-full font-semibold">🔴 hypertension</span>
                  <span className="text-xs bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2.5 py-1 rounded-full font-semibold">🟡 lisinopril</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 px-6 bg-slate-panel">
        <div className="max-w-6xl mx-auto">
          <motion.div initial={{opacity:0,y:20}} whileInView={{opacity:1,y:0}} viewport={{once:true}} className="text-center mb-16">
            <h2 className="text-4xl font-extrabold text-navy mb-4">Everything you need</h2>
            <p className="text-slate-muted text-lg max-w-xl mx-auto">Built for real clinical environments — fast, private, and multilingual.</p>
          </motion.div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f,i)=>(
              <motion.div key={f.title} initial={{opacity:0,y:20}} whileInView={{opacity:1,y:0}} viewport={{once:true}} transition={{delay:i*0.08}}
                whileHover={{y:-4}} className="bg-white rounded-2xl p-6 shadow-card hover:shadow-card-hv transition-all border border-slate-border/30">
                <div className="w-10 h-10 rounded-xl bg-navy/10 flex items-center justify-center mb-4"><f.icon size={20} className="text-navy"/></div>
                <h3 className="font-bold text-navy mb-2">{f.title}</h3>
                <p className="text-sm text-slate-muted leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative py-24 px-6 overflow-hidden">
        <div className="absolute inset-0 bg-cover bg-center opacity-10" style={{backgroundImage:"url('https://images.unsplash.com/photo-1504813184591-01572f98c85f?w=1400&q=80')"}}/>
        <div className="absolute inset-0 bg-navy/95"/>
        <motion.div initial={{opacity:0,scale:0.97}} whileInView={{opacity:1,scale:1}} viewport={{once:true}} className="relative max-w-2xl mx-auto text-center">
          <h2 className="text-4xl font-extrabold text-white mb-4">Ready to start?</h2>
          <p className="text-white/60 text-lg mb-8">Create your free account and run your first session in under a minute.</p>
          <Link to="/auth?mode=signup" className="inline-flex items-center gap-2 bg-cred text-white font-bold px-10 py-4 rounded-full hover:bg-cred-light transition-all shadow-lg text-lg">
            Create free account <ChevronRight size={20}/>
          </Link>
        </motion.div>
      </section>

      <footer className="py-8 text-center text-sm text-slate-muted border-t border-slate-border/30 bg-white">
        © 2026 Sidekick · Medanta Clinical AI · Built with Groq + Gemini
      </footer>
    </div>
  )
}
