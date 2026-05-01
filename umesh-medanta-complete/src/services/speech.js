import { API_BASE } from './config'

export const LANG_MAP = { en:'en-US',hi:'hi-IN',es:'es-ES',fr:'fr-FR',de:'de-DE',zh:'zh-CN',ar:'ar-SA',bn:'bn-IN',ta:'ta-IN',te:'te-IN',mr:'mr-IN',gu:'gu-IN' }
export const LANGUAGES = [
  {code:'en',label:'English'},{code:'hi',label:'Hindi'},{code:'es',label:'Spanish'},
  {code:'fr',label:'French'},{code:'de',label:'German'},{code:'zh',label:'Chinese'},
  {code:'ar',label:'Arabic'},{code:'bn',label:'Bengali'},{code:'ta',label:'Tamil'},
  {code:'te',label:'Telugu'},{code:'mr',label:'Marathi'},{code:'gu',label:'Gujarati'},
]

export function createSpeech(onT) {
  let rec=null, active=false, paused=false
  const start = (lang='en') => {
    const SR = window.SpeechRecognition||window.webkitSpeechRecognition
    if(!SR) return false
    rec=new SR(); rec.continuous=true; rec.interimResults=true
    // Always recognize in English — backend handles translation to selected language
    rec.lang = 'en-US'
    rec.onresult = e => {
      if(paused) return
      let i='',f=''
      for(let x=e.resultIndex;x<e.results.length;x++){const t=e.results[x][0].transcript; e.results[x].isFinal?(f+=t):(i+=t)}
      if(i) onT(i,false); if(f.trim()) onT(f.trim(),true)
    }
    rec.onend = () => { if(active&&!paused) setTimeout(()=>{try{rec?.start()}catch{}},200) }
    active=true; paused=false; try{rec.start();return true}catch{return false}
  }
  const stop   = () => { active=false; try{rec?.stop()}catch{}; rec=null }
  const pause  = () => { paused=true;  try{rec?.stop()}catch{} }
  const resume = () => { setTimeout(()=>{ paused=false; if(active) setTimeout(()=>{try{rec?.start()}catch{}},200) },800) }
  return { start, stop, pause, resume, isSupported:()=>!!(window.SpeechRecognition||window.webkitSpeechRecognition), isPaused:()=>paused }
}

export function tts(text, lang, onEnd) {
  const audio = new Audio(`${API_BASE}/api/tts?text=${encodeURIComponent(text.slice(0,200))}&lang=${lang.split('-')[0]}`)
  audio.onended = () => onEnd?.()
  audio.onerror = () => {
    if(!window.speechSynthesis){onEnd?.();return}
    window.speechSynthesis.cancel()
    const u=new SpeechSynthesisUtterance(text); u.lang=LANG_MAP[lang]||lang; u.rate=0.88
    u.onend=()=>onEnd?.()
    const vs=window.speechSynthesis.getVoices()
    const m=vs.find(v=>v.lang===(LANG_MAP[lang]||lang))||vs.find(v=>v.lang.startsWith(lang))
    if(m) u.voice=m
    if(vs.length===0){window.speechSynthesis.onvoiceschanged=()=>{window.speechSynthesis.onvoiceschanged=null;window.speechSynthesis.speak(u)}}
    else window.speechSynthesis.speak(u)
  }
  audio.play().catch(()=>audio.onerror())
}
