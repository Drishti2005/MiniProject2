import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Stethoscope, ArrowLeft, Trash2, ChevronRight, FileText, Loader2, Search, LogOut } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { sessionsAPI } from '../services/api'

const norm = s => s ? String(s).replace(' ','T')+(String(s).includes('Z')?'':'Z') : null
const fmtDate = iso => { if(!iso) return '—'; try{return new Date(norm(iso)).toLocaleString([],{weekday:'short',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})}catch{return iso} }
const fmtDur  = (s,e) => { if(!s||!e) return '—'; try{const ms=new Date(norm(e))-new Date(norm(s)); if(isNaN(ms)||ms<0) return '—'; const m=Math.floor(ms/60000),sec=Math.floor((ms%60000)/1000); return m?`${m}m ${sec}s`:`${sec}s`}catch{return '—'} }

export default function History() {
  const {logout}=useAuth()
  const [sessions,setSessions]=useState([])
  const [loading,setLoading]=useState(true)
  const [detail,setDetail]=useState(null)
  const [detailLoading,setDetailLoading]=useState(false)
  const [search,setSearch]=useState('')

  useEffect(()=>{ sessionsAPI.list().then(d=>{setSessions(d.sessions||[]);setLoading(false)}).catch(()=>setLoading(false)) },[])

  const loadDetail=async id=>{ setDetailLoading(true); try{setDetail(await sessionsAPI.get(id))}catch{}; setDetailLoading(false) }
  const del=async id=>{ await sessionsAPI.del(id).catch(()=>{}); setSessions(p=>p.filter(s=>s.id!==id)); if(detail?.session?.id===id) setDetail(null) }

  const filtered=sessions.filter(s=>!search||(s.title||'').toLowerCase().includes(search.toLowerCase())||fmtDate(s.created_at).toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="min-h-screen bg-slate-panel font-sans">
      <header className="sticky top-0 z-10 bg-white/90 backdrop-blur-xl border-b border-slate-border/50 h-16 flex items-center px-6 gap-3">
        <div className="flex items-center gap-2 mr-auto">
          <div className="w-7 h-7 rounded-lg bg-navy flex items-center justify-center"><Stethoscope size={14} className="text-white"/></div>
          <span className="font-bold text-navy">Sidekick</span>
          <span className="text-xs text-slate-muted hidden sm:block">· Session History</span>
        </div>
        <Link to="/session" className="flex items-center gap-1.5 text-sm font-bold bg-navy text-white px-4 py-2 rounded-full hover:bg-navy-light transition-colors">New Session</Link>
        <button onClick={logout} className="p-2 rounded-lg hover:bg-slate-panel transition-colors text-slate-muted hover:text-navy"><LogOut size={17}/></button>
      </header>

      <div className="max-w-5xl mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          {detail?(
            <motion.div key="detail" initial={{opacity:0,x:20}} animate={{opacity:1,x:0}} exit={{opacity:0,x:-20}}>
              <button onClick={()=>setDetail(null)} className="flex items-center gap-1.5 text-sm text-slate-muted hover:text-navy mb-6 transition-colors"><ArrowLeft size={16}/> Back to sessions</button>
              {detailLoading?<div className="flex justify-center py-16"><Loader2 size={24} className="animate-spin text-navy"/></div>:(
                <div className="space-y-4">
                  <div className="bg-white rounded-2xl shadow-card p-6 border border-slate-border/30">
                    <p className="text-xs font-bold uppercase tracking-widest text-slate-muted mb-4">Session Overview</p>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                      {[['Date',fmtDate(detail.session?.created_at)],['Duration',fmtDur(detail.session?.created_at,detail.session?.ended_at)],['Phrases',detail.transcript?.length||0],['Status',detail.session?.ended_at?'Completed':'Active']].map(([l,v])=>(
                        <div key={l}><p className="text-xs text-slate-muted mb-0.5">{l}</p><p className="font-semibold text-navy">{v}</p></div>
                      ))}
                    </div>
                  </div>
                  <div className="bg-white rounded-2xl shadow-card p-6 border border-slate-border/30">
                    <p className="text-xs font-bold uppercase tracking-widest text-slate-muted mb-3">Full Transcript ({detail.transcript?.length||0} phrases)</p>
                    {detail.transcript?.length>0?<p className="text-sm text-gray-700 leading-relaxed">{detail.transcript.map(c=>c.text).join(' ')}</p>:<p className="text-sm text-slate-muted italic">No transcript recorded.</p>}
                  </div>
                  {detail.simplifications?.length>0&&(
                    <div className="bg-white rounded-2xl shadow-card p-6 border border-slate-border/30">
                      <p className="text-xs font-bold uppercase tracking-widest text-slate-muted mb-3">AI Terms ({detail.simplifications.length})</p>
                      <div className="space-y-2">{detail.simplifications.map((s,i)=>(
                        <div key={i} className="flex gap-3 items-start">
                          <span className="text-xs font-bold bg-navy/10 text-navy px-2.5 py-0.5 rounded-full whitespace-nowrap">{s.term}</span>
                          <span className="text-xs text-slate-muted">{s.explanation}</span>
                        </div>
                      ))}</div>
                    </div>
                  )}
                  {detail.summary?(
                    <div className="bg-white rounded-2xl shadow-card p-6 border border-slate-border/30 space-y-3">
                      <p className="text-xs font-bold uppercase tracking-widest text-slate-muted">AI Visit Summary</p>
                      {detail.summary.title&&<div><p className="text-xs text-slate-muted">Title</p><p className="font-bold text-navy">{detail.summary.title}</p></div>}
                      {detail.summary.diagnosis&&<div><p className="text-xs text-slate-muted">Diagnosis</p><p className="text-sm text-gray-700">{detail.summary.diagnosis}</p></div>}
                      {detail.summary.key_points?.length>0&&<div><p className="text-xs text-slate-muted mb-1">Key Points</p><ul className="space-y-1">{detail.summary.key_points.map((p,i)=><li key={i} className="text-sm text-gray-700 flex gap-2"><span className="text-teal-500">•</span>{p}</li>)}</ul></div>}
                      {detail.summary.medications?.length>0&&<div><p className="text-xs text-slate-muted mb-1">Medications</p><ul className="space-y-1">{detail.summary.medications.map((m,i)=><li key={i} className="text-sm text-gray-700 flex gap-2"><span className="text-teal-500">•</span>{m}</li>)}</ul></div>}
                      {detail.summary.follow_up&&<div><p className="text-xs text-slate-muted">Follow-up</p><p className="text-sm text-gray-700">{detail.summary.follow_up}</p></div>}
                    </div>
                  ):(
                    <div className="bg-white rounded-2xl shadow-card p-6 border-2 border-dashed border-slate-border/50">
                      <p className="text-sm text-slate-muted italic text-center">No summary generated for this session.</p>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          ):(
            <motion.div key="list" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h1 className="text-2xl font-extrabold text-navy">Session History</h1>
                  <p className="text-sm text-slate-muted mt-0.5">{sessions.length} session{sessions.length!==1?'s':''} recorded</p>
                </div>
                <div className="relative hidden sm:block">
                  <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-muted"/>
                  <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search sessions…"
                    className="pl-9 pr-4 py-2 text-sm border border-slate-border rounded-xl bg-white focus:outline-none focus:border-navy transition-colors w-52"/>
                </div>
              </div>
              {loading?<div className="flex justify-center py-16"><Loader2 size={24} className="animate-spin text-navy"/></div>
                :filtered.length===0?<div className="text-center py-16 text-slate-muted"><FileText size={40} className="mx-auto mb-3 opacity-30"/><p className="font-semibold">{search?'No matching sessions':'No sessions yet'}</p>{!search&&<Link to="/session" className="inline-block mt-4 bg-navy text-white text-sm font-semibold px-6 py-2.5 rounded-full hover:bg-navy-light transition-colors">Start first session</Link>}</div>
                :(
                  <div className="space-y-3">
                    {filtered.map((s,i)=>(
                      <motion.div key={s.id} initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} transition={{delay:i*0.04}}
                        className="bg-white rounded-2xl shadow-card hover:shadow-card-hv transition-all p-5 flex items-center gap-4 cursor-pointer border border-slate-border/30"
                        onClick={()=>loadDetail(s.id)}>
                        <div className="w-10 h-10 rounded-xl bg-navy/10 flex items-center justify-center flex-shrink-0"><Stethoscope size={18} className="text-navy"/></div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-0.5">
                            <p className="font-semibold text-navy text-sm truncate">{fmtDate(s.created_at)}</p>
                            {s.has_summary&&<span className="text-xs bg-teal-50 text-teal-700 border border-teal-200 px-2 py-0.5 rounded-full font-semibold flex-shrink-0">Summary ✓</span>}
                            {s.transcript_count===0&&<span className="text-xs bg-slate-panel text-slate-muted px-2 py-0.5 rounded-full flex-shrink-0">Empty</span>}
                          </div>
                          <p className="text-xs text-slate-muted">{fmtDur(s.created_at,s.ended_at)} · {s.transcript_count||0} phrase{s.transcript_count!==1?'s':''} · {(s.language||'en').toUpperCase()}</p>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          <button onClick={e=>{e.stopPropagation();del(s.id)}} className="p-2 rounded-lg hover:bg-red-50 text-slate-muted hover:text-red-500 transition-colors"><Trash2 size={15}/></button>
                          <ChevronRight size={16} className="text-slate-border"/>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
