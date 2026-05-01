import { useState, useCallback, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
  Stethoscope, Mic, Square, History, LogOut,
  Lightbulb, MessageSquare, BarChart3, Loader2,
  Globe, ChevronDown, Activity, Play, Check, Send,
  Loader, Volume2, X
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { createWS } from '../services/ws'
import { createSpeech, LANGUAGES, tts } from '../services/speech'
import { healthAPI } from '../services/api'

// ── Importance chip ───────────────────────────────────────────
const IMP = {
  high:   { chip:'bg-red-50 text-red-700 border-red-200',    bar:'border-l-red-500',   dot:'🔴', label:'Critical'  },
  medium: { chip:'bg-amber-50 text-amber-700 border-amber-200', bar:'border-l-amber-400', dot:'🟡', label:'Important' },
  low:    { chip:'bg-teal-50 text-teal-700 border-teal-200', bar:'border-l-teal-400',  dot:'🟢', label:'General'   },
}

function TermCard({ term }) {
  const s = IMP[term.importance] || IMP.medium
  return (
    <motion.div initial={{ opacity:0, x:10 }} animate={{ opacity:1, x:0 }} whileHover={{ scale:1.01 }}
      className={`rounded-xl p-3 border-l-2 bg-white border border-gray-100 shadow-sm ${s.bar}`}>
      <div className="flex items-center gap-2 mb-1.5">
        <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${s.chip}`}>{term.term}</span>
        <span className="text-xs text-gray-400 ml-auto">{s.dot} {s.label}</span>
      </div>
      <p className="text-xs text-gray-600 leading-relaxed">{term.explanation}</p>
    </motion.div>
  )
}

// ── PromptCard — OUTSIDE component to prevent focus loss ─────
// Shows: selected language (large) → English (small) → Play + Ask buttons
function PromptCard({ question, bilingual, activeLang, onAsk, onPause, onResume }) {
  const [asked,    setAsked]    = useState(false)
  const [speaking, setSpeaking] = useState(false)

  const isBi      = bilingual && typeof question === 'object' && question.translated
  const englishTx = isBi ? question.english : (typeof question === 'string' ? question : question?.english || '')
  const translated = isBi ? question.translated : null
  const langCode   = isBi ? question.language : (activeLang && activeLang !== 'en' ? activeLang : null)
  // Always show TTS if any non-English language is active
  const showTTS    = !!(langCode)
  const speakText  = translated || englishTx

  const handlePlay = () => {
    if (speaking) return
    setSpeaking(true)
    onPause?.()
    tts(speakText, langCode, () => { setSpeaking(false); onResume?.() })
  }

  const handleAsk = () => {
    if (asked) return
    setAsked(true)
    onAsk?.(englishTx)
  }

  return (
    <motion.div initial={{ opacity:0, y:6 }} animate={{ opacity:1, y:0 }}
      className={`rounded-xl border transition-all ${asked ? 'bg-teal-50 border-teal-200' : 'bg-white border-gray-200 hover:border-navy/30 hover:shadow-sm'}`}>
      <div className="p-3 pb-2">
        {/* Selected language first (large, bold) */}
        {translated && (
          <p className="text-sm font-semibold text-navy leading-snug mb-1">{translated}</p>
        )}
        {/* English below (smaller, muted) */}
        <p className={`leading-snug ${translated ? 'text-xs text-gray-400 italic' : 'text-sm text-gray-800'}`}>
          {englishTx}
        </p>
      </div>
      <div className="flex items-center gap-2 px-3 pb-3">
        {/* TTS — always visible when non-English language active */}
        {showTTS && (
          <motion.button whileTap={{ scale:0.92 }} onClick={handlePlay} disabled={speaking}
            className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full transition-all border ${
              speaking
                ? 'bg-teal-100 text-teal-700 border-teal-300'
                : 'bg-teal-50 text-teal-700 border-teal-200 hover:bg-teal-100'
            }`}>
            {speaking
              ? <><Loader size={11} className="animate-spin" /> Speaking…</>
              : <><Volume2 size={11} /> Speak</>
            }
          </motion.button>
        )}
        <button onClick={handleAsk}
          className={`ml-auto flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full transition-all border ${
            asked
              ? 'bg-teal-100 text-teal-700 border-teal-200 cursor-default'
              : 'bg-navy/10 text-navy border-navy/20 hover:bg-navy/20'
          }`}>
          {asked ? <><Check size={11} /> Asked</> : <><Send size={11} /> Ask</>}
        </button>
      </div>
    </motion.div>
  )
}

// ── Skeleton ──────────────────────────────────────────────────
function Skel({ lines = 2 }) {
  return (
    <div className="space-y-2.5 p-3">
      <div className="skeleton h-3 rounded-full w-2/5" />
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className={`skeleton h-2.5 rounded-full ${i === lines - 1 ? 'w-3/5' : 'w-full'}`} />
      ))}
    </div>
  )
}

// ── Widget header ─────────────────────────────────────────────
function WH({ icon: I, bg, ic, title, count }) {
  return (
    <div className="widget-hdr">
      <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 ${bg}`}>
        <I size={15} className={ic} />
      </div>
      <span className="text-xs font-bold uppercase tracking-widest text-navy">{title}</span>
      {count > 0 && (
        <motion.span initial={{ scale:0 }} animate={{ scale:1 }}
          className="ml-auto text-xs font-bold bg-navy/10 text-navy px-2 py-0.5 rounded-full border border-navy/15">
          {count}
        </motion.span>
      )}
    </div>
  )
}

// ── Question Explanation Panel ────────────────────────────────
// Shown when patient clicks Ask — AI returns explanation + doctor reply input
function ExplanationPanel({ question, explanation, langCode, onDoctorReply, onClose, onPause, onResume }) {
  const [reply,    setReply]    = useState('')
  const [sending,  setSending]  = useState(false)
  const [speaking, setSpeaking] = useState(false)

  const handleSpeak = () => {
    if (speaking || !explanation) return
    setSpeaking(true); onPause?.()
    tts(explanation, langCode || 'en', () => { setSpeaking(false); onResume?.() })
  }

  const handleSend = () => {
    if (!reply.trim() || sending) return
    setSending(true)
    onDoctorReply?.(question, reply.trim())
    setReply('')
    setTimeout(() => setSending(false), 500)
  }

  return (
    <motion.div initial={{ opacity:0, y:8, scale:0.98 }} animate={{ opacity:1, y:0, scale:1 }}
      className="fixed bottom-24 right-6 w-96 max-w-[calc(100vw-2rem)] bg-white rounded-2xl shadow-[0_8px_40px_rgba(11,42,70,0.18)] border border-gray-200 z-40 overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 bg-navy text-white">
        <MessageSquare size={15} />
        <span className="text-xs font-bold uppercase tracking-wide flex-1">AI Explanation</span>
        {langCode && (
          <button onClick={handleSpeak} disabled={speaking}
            className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full border transition-all ${speaking ? 'bg-white/20 border-white/30' : 'bg-white/10 border-white/20 hover:bg-white/20'}`}>
            {speaking ? <><Loader size={10} className="animate-spin" /> Speaking</> : <><Volume2 size={10} /> Hear</>}
          </button>
        )}
        <button onClick={onClose} className="p-1 rounded-full hover:bg-white/20 transition-colors"><X size={14} /></button>
      </div>

      {/* Question */}
      <div className="px-4 pt-3 pb-2">
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Question asked</p>
        <p className="text-sm font-semibold text-navy">{question}</p>
      </div>

      {/* Explanation */}
      {explanation && (
        <div className="px-4 pb-3">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">AI Explanation</p>
          <p className="text-sm text-gray-700 leading-relaxed bg-gray-50 rounded-xl p-3 border border-gray-100">{explanation}</p>
        </div>
      )}

      {/* Doctor reply input */}
      <div className="px-4 pb-4 border-t border-gray-100 pt-3">
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">Doctor's reply</p>
        <div className="flex gap-2">
          <input
            value={reply} onChange={e => setReply(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Type doctor's answer…"
            className="flex-1 text-sm border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:border-navy transition-colors"
          />
          <button onClick={handleSend} disabled={!reply.trim() || sending}
            className="flex items-center gap-1 text-xs font-bold px-3 py-2 rounded-xl bg-navy text-white hover:bg-navy-light transition-colors disabled:opacity-40">
            <Send size={12} />
          </button>
        </div>
      </div>
    </motion.div>
  )
}

// ── Main Session Page ─────────────────────────────────────────
export default function Session() {
  const { user, logout } = useAuth()
  const [recording,   setRecording]   = useState(false)
  const [thinking,    setThinking]    = useState(false)
  const [language,    setLanguage]    = useState('en')
  const [aiProvider,  setAiProvider]  = useState('AI')
  const [transcript,  setTranscript]  = useState([])
  const [terms,       setTerms]       = useState([])
  const [questions,   setQuestions]   = useState([])
  const [bilingual,   setBilingual]   = useState(false)
  const [summary,     setSummary]     = useState(null)
  const [showSummary, setShowSummary] = useState(false)
  const [phraseCount, setPhraseCount] = useState(0)
  const [aiRequests,  setAiRequests]  = useState(0)
  const [duration,    setDuration]    = useState(0)
  const [langOpen,    setLangOpen]    = useState(false)
  // Explanation panel state
  const [explanation, setExplanation] = useState(null) // { question, text, lang }

  const durRef  = useRef(null)
  const wsRef   = useRef(null)
  const spRef   = useRef(null)
  const langRef = useRef(language)   // always current language without stale closure
  useEffect(() => { langRef.current = language }, [language])

  useEffect(() => {
    healthAPI.ai()
      .then(d => setAiProvider((d.provider || 'AI').replace('Provider','').replace('Service','')))
      .catch(() => {})
  }, [])

  // Close language dropdown on outside click
  // Using document capture listener avoids the stopPropagation / z-index double-click issue
  useEffect(() => {
    if (!langOpen) return
    const close = (e) => {
      // Don't close if clicking inside the dropdown itself
      const dropdown = document.getElementById('lang-dropdown')
      if (dropdown && dropdown.contains(e.target)) return
      setLangOpen(false)
    }
    // Small delay so the button's own click doesn't immediately close it
    const t = setTimeout(() => document.addEventListener('click', close), 10)
    return () => { clearTimeout(t); document.removeEventListener('click', close) }
  }, [langOpen])

  const handleMsg = useCallback(data => {
    switch (data.type) {
      case 'simplification':
        setThinking(false)
        if (Array.isArray(data.terms)) setTerms(p => [...p, ...data.terms])
        break
      case 'transcript_translation':
        // Attach translation — transcript shows English first, then selected language below
        setTranscript(p => p.map((e, i) =>
          i === p.length - 1 ? { ...e, translated: data.translated, lang: data.language } : e
        ))
        break
      case 'questions':
        setQuestions(data.suggestions || [])
        setBilingual(data.bilingual || false)
        break
      case 'session_info':
        setPhraseCount(data.phrase_count || 0)
        setAiRequests(data.ai_requests  || 0)
        break
      // AI explanation for a clicked patient prompt
      case 'question_explanation':
        setThinking(false)
        setExplanation({ question: data.question, text: data.explanation, lang: null })
        break
      case 'question_explanation_translated':
        setExplanation(prev => prev ? { ...prev, text: data.explanation, lang: data.language } : prev)
        break
      // Doctor reply simplified
      case 'doctor_reply_simplified':
        setThinking(false)
        if (Array.isArray(data.terms) && data.terms.length > 0) {
          setTerms(p => [...p, ...data.terms])
        }
        break
      case 'summary':
        setThinking(false)
        setSummary(data.data)
        setShowSummary(true)
        wsRef.current?.close()
        break
      case 'ai_error':
      case 'error':
        setThinking(false)
        break
      default: break
    }
  }, [])

  const onT = useCallback((text, isFinal) => {
    if (spRef.current?.isPaused()) return
    if (!isFinal) {
      setTranscript(p => {
        const last = p[p.length - 1]
        if (last?.interim) return [...p.slice(0, -1), { text, interim: true, ts: Date.now() }]
        return [...p, { text, interim: true, ts: Date.now() }]
      })
    } else {
      setTranscript(p => [...p.filter(e => !e.interim), { text, interim: false, ts: Date.now() }])
      setThinking(true)
      // Use langRef so we always send the current language, not a stale closure value
      wsRef.current?.send({ type: 'transcript', text, language: langRef.current })
    }
  }, [])  // no dependency on language — langRef handles it

  const startSession = () => {
    const sp = createSpeech(onT)
    if (!sp.isSupported()) { alert('Speech recognition requires Chrome or Edge.'); return }
    spRef.current = sp
    setTranscript([]); setTerms([]); setQuestions([])
    setSummary(null); setPhraseCount(0); setAiRequests(0); setDuration(0); setExplanation(null)
    const ws = createWS(handleMsg); wsRef.current = ws; ws.connect()
    setTimeout(() => {
      sp.start(language); setRecording(true)
      durRef.current = setInterval(() => setDuration(d => d + 1), 1000)
    }, 600)
  }

  const stopSession = () => {
    spRef.current?.stop(); setRecording(false)
    clearInterval(durRef.current); setThinking(true)
    wsRef.current?.send({ type: 'end_session' })
  }

  const onLang = val => {
    setLanguage(val); setLangOpen(false)
    if (wsRef.current?.isOpen()) wsRef.current.send({ type: 'language_change', language: val })
  }

  const handleAsk = eq => {
    wsRef.current?.send({ type: 'question_ask', question: eq })
    setThinking(true)
    setExplanation({ question: eq, text: null, lang: language !== 'en' ? language : null })
  }

  const handleDoctorReply = (question, reply) => {
    wsRef.current?.send({ type: 'doctor_reply', question, reply })
    setThinking(true)
  }

  const fmt = s => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
  const langLabel = LANGUAGES.find(l => l.code === language)?.label || 'English'

  return (
    <div className="h-screen w-screen overflow-hidden flex flex-col bg-gray-50 font-sans">

      {/* ── Topbar — clean white ── */}
      <header className="flex-shrink-0 h-16 bg-white border-b border-gray-200 flex items-center px-5 gap-4 z-20 shadow-sm">
        <div className="flex items-center gap-3 mr-auto">
          <div className="w-9 h-9 rounded-xl bg-navy flex items-center justify-center shadow-sm">
            <Stethoscope size={18} className="text-white" />
          </div>
          <div>
            <span className="font-bold text-navy text-base leading-none">Sidekick</span>
            <p className="text-xs text-gray-400 leading-none mt-0.5">Clinical AI</p>
          </div>
          <AnimatePresence>
            {recording && (
              <motion.div initial={{ opacity:0, scale:0.8 }} animate={{ opacity:1, scale:1 }} exit={{ opacity:0 }}
                className="flex items-center gap-2 bg-red-50 border border-red-200 px-3 py-1.5 rounded-full ml-2">
                <span className="relative flex items-center justify-center w-3 h-3">
                  <span className="absolute w-full h-full rounded-full bg-red-500 animate-pulse-ring" />
                  <span className="relative w-2 h-2 rounded-full bg-red-500" />
                </span>
                <span className="text-xs font-bold text-red-600 tracking-widest">LIVE</span>
                <Activity size={12} className="text-red-500 animate-ecg" />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Language dropdown */}
        <div className="relative">
          <button onClick={() => setLangOpen(v => !v)}
            className="flex items-center gap-2 bg-gray-50 border border-gray-200 text-gray-700 text-sm font-medium px-3 py-2 rounded-xl hover:bg-gray-100 transition-colors">
            <Globe size={14} className="text-gray-400" />
            {langLabel}
            <ChevronDown size={13} className={`text-gray-400 transition-transform ${langOpen ? 'rotate-180' : ''}`} />
          </button>
          <AnimatePresence>
            {langOpen && (
              <motion.div id="lang-dropdown" initial={{ opacity:0, y:-8, scale:0.97 }} animate={{ opacity:1, y:0, scale:1 }} exit={{ opacity:0, y:-8 }}
                className="absolute right-0 top-full mt-2 w-44 bg-white border border-gray-200 rounded-2xl shadow-lg overflow-hidden z-50">
                {LANGUAGES.map(l => (
                  <button key={l.code} onClick={e => { e.stopPropagation(); onLang(l.code) }}
                    className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${language === l.code ? 'bg-navy/5 text-navy font-semibold' : 'text-gray-600 hover:bg-gray-50 hover:text-navy'}`}>
                    {l.label}
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <span className="hidden sm:flex items-center gap-1.5 bg-green-50 border border-green-200 text-green-700 text-xs font-semibold px-3 py-1.5 rounded-full">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500" />{aiProvider}
        </span>

        <Link to="/history" className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-navy" title="Session History">
          <History size={18} />
        </Link>
        <button onClick={logout} className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-navy" title="Sign out">
          <LogOut size={18} />
        </button>
      </header>

      {/* ── Workspace ── */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_360px] overflow-hidden min-h-0">

        {/* Left — Transcript */}
        <div className="flex flex-col overflow-hidden border-r border-gray-200 bg-white">
          {/* Panel header */}
          <div className="flex-shrink-0 px-5 py-3 flex items-center justify-between border-b border-gray-100 bg-white">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-widest text-gray-400">Live Transcript</span>
              {language !== 'en' && (
                <span className="text-xs bg-teal-50 text-teal-700 border border-teal-200 px-2 py-0.5 rounded-full font-semibold">
                  {langLabel} + English
                </span>
              )}
            </div>
            <AnimatePresence>
              {thinking && (
                <motion.span initial={{ opacity:0 }} animate={{ opacity:1 }} exit={{ opacity:0 }}
                  className="flex items-center gap-1.5 text-xs text-navy font-medium">
                  <Loader2 size={12} className="animate-spin" /> AI analysing…
                </motion.span>
              )}
            </AnimatePresence>
          </div>

          {/* Transcript entries */}
          {transcript.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 select-none">
              <motion.div animate={{ y:[0,-10,0] }} transition={{ repeat:Infinity, duration:3.5, ease:'easeInOut' }}
                className="w-20 h-20 rounded-full bg-navy/5 border border-navy/10 flex items-center justify-center text-4xl mb-5">
                🎙️
              </motion.div>
              <h3 className="font-bold text-navy text-lg mb-2">Ready to listen</h3>
              <p className="text-gray-400 text-sm max-w-xs leading-relaxed">
                Press <strong className="text-navy">Start Recording</strong> to begin capturing the appointment.
              </p>
              {language !== 'en' && (
                <p className="text-gray-300 text-xs mt-2">Bilingual view active · {langLabel} + English</p>
              )}
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto scroll-light px-5 py-4 space-y-4">
              <AnimatePresence initial={false}>
                {transcript.map((e, i) => (
                  <motion.div key={i} initial={{ opacity:0, y:10 }} animate={{ opacity:1, y:0 }} transition={{ duration:0.3 }}
                    className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-navy/10 border border-navy/15 flex items-center justify-center flex-shrink-0 mt-1">
                      <Stethoscope size={13} className="text-navy" />
                    </div>
                    <div className="flex-1 min-w-0">
                      {e.interim ? (
                        <div className="bg-gray-50 border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-2.5 max-w-[85%]">
                          <p className="text-sm text-gray-400 italic">{e.text}…</p>
                        </div>
                      ) : e.translated ? (
                        /* Bilingual: English first (top), selected language below */
                        <div className="space-y-2 max-w-[90%]">
                          <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                            <p className="text-xs font-bold text-gray-400 mb-1">🇬🇧 English</p>
                            <p className="text-sm text-gray-800 leading-relaxed">{e.text}</p>
                          </div>
                          <div className="bg-teal-50 border border-teal-200 rounded-2xl px-4 py-3">
                            <p className="text-xs font-bold text-teal-600 mb-1">
                              🌐 {LANGUAGES.find(l => l.code === (e.lang || language))?.label || langLabel}
                            </p>
                            <p className="text-sm text-teal-900 leading-relaxed">{e.translated}</p>
                          </div>
                        </div>
                      ) : (
                        <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[85%] shadow-sm">
                          <p className="text-sm text-gray-800 leading-relaxed">{e.text}</p>
                        </div>
                      )}
                      <span className="text-xs text-gray-300 mt-1 block pl-1">
                        {new Date(e.ts).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit', second:'2-digit' })}
                      </span>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}

          {/* Controls */}
          <div className="flex-shrink-0 border-t border-gray-100 bg-white">
            <div className="flex items-center justify-center gap-4 p-5">
              {!recording ? (
                <motion.button whileHover={{ scale:1.03 }} whileTap={{ scale:0.97 }} onClick={startSession}
                  className="relative flex items-center gap-3 font-bold text-base px-10 py-4 rounded-2xl text-white shadow-lg bg-navy hover:bg-navy-light transition-colors">
                  <span className="absolute inset-0 rounded-2xl animate-pulse-ring" style={{ background:'rgba(11,42,70,0.25)' }} />
                  <Mic size={20} className="relative" />
                  <span className="relative">Start Recording</span>
                </motion.button>
              ) : (
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2 bg-red-50 border border-red-200 px-4 py-2.5 rounded-xl">
                    <Activity size={14} className="text-red-500 animate-ecg" />
                    <span className="text-red-700 font-bold tabular-nums text-sm">{fmt(duration)}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    {[0,1,2,3,4].map(i => (
                      <motion.div key={i} animate={{ scaleY:[0.3,1,0.3] }} transition={{ repeat:Infinity, duration:0.8, delay:i*0.12 }}
                        className="w-1 bg-red-500 rounded-full" style={{ height:20 }} />
                    ))}
                  </div>
                  <motion.button whileHover={{ scale:1.02 }} whileTap={{ scale:0.97 }} onClick={stopSession}
                    className="flex items-center gap-2 bg-gray-100 text-gray-700 font-semibold text-sm px-6 py-3 rounded-xl hover:bg-gray-200 transition-colors border border-gray-200">
                    <Square size={14} /> Stop & Summarise
                  </motion.button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right — Insights */}
        <div className="overflow-y-auto scroll-light p-4 space-y-3 bg-gray-50">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-400 px-1 mb-1">AI Insights</p>

          {/* Terms Explained */}
          <div className="widget">
            <WH icon={Lightbulb} bg="bg-yellow-50" ic="text-yellow-600" title="Terms Explained" count={terms.length} />
            <div className="p-3 max-h-64 overflow-y-auto scroll-light space-y-2">
              {thinking && terms.length === 0 ? <Skel lines={3} />
                : terms.length === 0
                  ? <p className="text-xs text-gray-400 text-center py-5">Medical terms will appear here as they are spoken.</p>
                  : terms.map((t, i) => <TermCard key={i} term={t} />)
              }
            </div>
          </div>

          {/* Patient Prompts */}
          <div className="widget">
            <WH icon={MessageSquare} bg="bg-teal-50" ic="text-teal-600" title="Patient Prompts" count={questions.length} />
            <div className="p-3 max-h-72 overflow-y-auto scroll-light space-y-2">
              {thinking && questions.length === 0 ? <Skel lines={2} />
                : questions.length === 0
                  ? <p className="text-xs text-gray-400 text-center py-5">Questions will appear as the conversation develops.</p>
                  : questions.map((q, i) => (
                      <PromptCard
                        key={typeof q === 'string' ? q : (q.english || i)}
                        question={q} bilingual={bilingual} activeLang={language}
                        onPause={() => spRef.current?.pause()}
                        onResume={() => spRef.current?.resume()}
                        onAsk={handleAsk} />
                    ))
              }
            </div>
          </div>

          {/* Session Info */}
          <div className="widget">
            <WH icon={BarChart3} bg="bg-blue-50" ic="text-blue-600" title="Session Info" count={0} />
            <div className="p-4 space-y-2.5">
              {[
                ['Duration',  recording ? fmt(duration) : '—'],
                ['Phrases',   phraseCount],
                ['AI requests', aiRequests],
                ['Language',  langLabel],
                ['Provider',  aiProvider],
              ].map(([l, v]) => (
                <div key={l} className="flex justify-between text-xs">
                  <span className="text-gray-400">{l}</span>
                  <span className="font-semibold text-navy">{v}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Explanation panel — fixed bottom-right */}
      <AnimatePresence>
        {explanation && (
          <ExplanationPanel
            question={explanation.question}
            explanation={explanation.text}
            langCode={explanation.lang || (language !== 'en' ? language : null)}
            onDoctorReply={handleDoctorReply}
            onClose={() => setExplanation(null)}
            onPause={() => spRef.current?.pause()}
            onResume={() => spRef.current?.resume()}
          />
        )}
      </AnimatePresence>

      {/* Summary modal */}
      <AnimatePresence>
        {showSummary && summary && (
          <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }} exit={{ opacity:0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
            onClick={e => e.target === e.currentTarget && setShowSummary(false)}>
            <motion.div initial={{ opacity:0, y:28, scale:0.96 }} animate={{ opacity:1, y:0, scale:1 }} exit={{ opacity:0, y:28 }}
              className="bg-white rounded-3xl shadow-[0_32px_80px_rgba(11,42,70,0.2)] w-full max-w-lg max-h-[88vh] overflow-y-auto scroll-light">
              <div className="flex items-center justify-between p-6 pb-4 border-b border-gray-100">
                <h2 className="text-xl font-bold text-navy">Visit Summary</h2>
                <button onClick={() => setShowSummary(false)} className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors text-gray-500">✕</button>
              </div>
              <div className="flex gap-3 px-6 py-4">
                {[['Key Points',(summary.key_points||[]).length],['Medications',(summary.medications||[]).length],['Instructions',(summary.instructions||[]).length]].map(([l,v]) => (
                  <div key={l} className="flex-1 bg-gray-50 rounded-xl p-3 text-center border border-gray-100">
                    <p className="text-2xl font-bold text-navy">{v}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{l}</p>
                  </div>
                ))}
              </div>
              <div className="px-6 pb-6 space-y-3">
                {summary.title     && <div className="bg-gray-50 rounded-xl p-4 border border-gray-100"><p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">Visit Title</p><p className="font-bold text-navy">{summary.title}</p></div>}
                {summary.diagnosis && <div className="bg-gray-50 rounded-xl p-4 border border-gray-100"><p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">Diagnosis</p><p className="text-sm text-gray-700">{summary.diagnosis}</p></div>}
                {summary.key_points?.length > 0 && <div className="bg-gray-50 rounded-xl p-4 border border-gray-100"><p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">Key Points</p><ul className="space-y-1.5">{summary.key_points.map((p,i) => <li key={i} className="flex items-start gap-2 text-sm text-gray-700"><span className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-1.5 flex-shrink-0"/>{p}</li>)}</ul></div>}
                {summary.medications?.length > 0 && <div className="bg-gray-50 rounded-xl p-4 border border-gray-100"><p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">Medications</p><ul className="space-y-1.5">{summary.medications.map((m,i) => <li key={i} className="flex items-start gap-2 text-sm text-gray-700"><span className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-1.5 flex-shrink-0"/>{m}</li>)}</ul></div>}
                {summary.follow_up && <div className="bg-gray-50 rounded-xl p-4 border border-gray-100"><p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">Follow-up</p><p className="text-sm text-gray-700">{summary.follow_up}</p></div>}
              </div>
              <div className="flex justify-end gap-3 px-6 pb-6 border-t border-gray-100 pt-4">
                <button onClick={() => setShowSummary(false)} className="text-sm font-semibold px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors">Close</button>
                <button onClick={() => window.print()} className="text-sm font-semibold px-4 py-2 rounded-xl bg-navy text-white hover:bg-navy-light transition-colors">Print</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  )
}
