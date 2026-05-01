import { WS_URL } from './config'
export function createWS(onMsg) {
  let ws=null, q=[], n=0
  const connect = () => {
    ws = new WebSocket(WS_URL())
    ws.onopen    = () => { n=0; q.forEach(m=>ws.send(JSON.stringify(m))); q=[] }
    ws.onmessage = e => { try { onMsg(JSON.parse(e.data)) } catch {} }
    ws.onclose   = ev => { if(ev.code!==1000&&n<3){n++;setTimeout(connect,1000*n)} }
  }
  const send  = m => ws?.readyState===1 ? ws.send(JSON.stringify(m)) : q.push(m)
  const close = () => { n=99; ws?.close(1000); ws=null }
  const isOpen= () => ws?.readyState===1
  return { connect, send, close, isOpen }
}
