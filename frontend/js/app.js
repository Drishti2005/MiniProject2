// ============================================================
// SIDEKICK — App.js
// WebSocket client + main application logic
// Clinical Concierge — fully wired to backend
// ============================================================

const WS_URL = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/session`;

// ── WebSocket Client ──────────────────────────────────────────
class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.ws  = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 3;
        this.reconnectDelay  = 1000;
        this.heartbeatTimer  = null;
        this.messageQueue    = [];
        this.onMessage       = null;
    }

    connect() {
        try {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                console.log('[WS] Connected');
                this.reconnectAttempts = 0;
                this.reconnectDelay    = 1000;
                while (this.messageQueue.length) this._send(this.messageQueue.shift());
                this._startHeartbeat();
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (this.onMessage) this.onMessage(data);
                } catch (e) {
                    console.error('[WS] Parse error:', e);
                }
            };

            this.ws.onerror = (e) => console.error('[WS] Error:', e);

            this.ws.onclose = (event) => {
                console.log('[WS] Closed, code:', event.code);
                this._stopHeartbeat();
                if (event.code !== 1000) this._reconnect();
            };
        } catch (e) {
            console.error('[WS] Cannot connect:', e);
            this._reconnect();
        }
    }

    disconnect() {
        this._stopHeartbeat();
        this.reconnectAttempts = this.maxReconnectAttempts; // prevent auto-reconnect
        if (this.ws) { this.ws.close(1000, 'client-disconnect'); this.ws = null; }
    }

    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this._send(message);
        } else {
            this.messageQueue.push(message);
        }
    }

    _send(message) {
        try { this.ws.send(JSON.stringify(message)); }
        catch (e) { console.error('[WS] Send error:', e); }
    }

    _reconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.warn('[WS] Max reconnect attempts reached');
            if (window._ui) window._ui.showError('Connection lost. Please refresh the page.');
            return;
        }
        this.reconnectAttempts++;
        console.log(`[WS] Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts})`);
        setTimeout(() => this.connect(), this.reconnectDelay);
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, 10000);
    }

    _startHeartbeat() {
        this._stopHeartbeat();
        this.heartbeatTimer = setInterval(() => this.send({ type: 'ping' }), 30000);
    }

    _stopHeartbeat() {
        if (this.heartbeatTimer) { clearInterval(this.heartbeatTimer); this.heartbeatTimer = null; }
    }

    get isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

// ── Application globals ───────────────────────────────────────
let wsClient          = null;
let speechMgr         = null;
let ui                = null;
let currentSessionId  = null;
let selectedLanguage  = 'en';

// ── Initialisation ────────────────────────────────────────────
function initApp() {
    ui         = new UIManager();
    window._ui = ui;
    ui.clearSession();

    // Modal close handlers
    const summaryModal = document.getElementById('summary-modal');
    document.getElementById('modal-close')?.addEventListener('click', () => ui.hideSummary());
    document.getElementById('modal-close-btn')?.addEventListener('click', () => ui.hideSummary());
    summaryModal?.addEventListener('click', e => { if (e.target === summaryModal) ui.hideSummary(); });

    // Language selector
    document.getElementById('language')?.addEventListener('change', e => {
        selectedLanguage = e.target.value;
        if (selectedLanguage === 'en') ui.hideTranslation();
        // Notify backend so it uses the right translation target
        if (wsClient && wsClient.isConnected) {
            wsClient.send({ type: 'language_change', language: selectedLanguage });
        }
        // Show which language is active
        const langNames = {
            hi:'Hindi', es:'Spanish', fr:'French', de:'German', zh:'Chinese',
            ar:'Arabic', bn:'Bengali', ta:'Tamil', te:'Telugu', mr:'Marathi', gu:'Gujarati'
        };
        if (selectedLanguage !== 'en') {
            ui.showToast(`🌐 Translation: ${langNames[selectedLanguage] || selectedLanguage}`, 'info');
        }
    });

    // Recording buttons
    document.getElementById('start-recording')?.addEventListener('click', startSession);
    document.getElementById('stop-recording')?.addEventListener('click', stopSession);

    // Fetch and display active AI provider
    fetchAIProvider();
}

// ── AI Provider Badge ─────────────────────────────────────────
async function fetchAIProvider() {
    try {
        const res = await fetch('/api/health/ai');
        if (!res.ok) return;
        const data = await res.json();
        const badge = document.getElementById('ai-provider-badge');
        const name  = document.getElementById('ai-provider-name');
        if (!badge || !name) return;
        const providerName = data.provider
            ? data.provider.replace('Provider', '').replace('Service', '')
            : 'AI';
        name.textContent = providerName;
        const isMock = providerName.toLowerCase().includes('mock');
        const isGroq = providerName.toLowerCase().includes('groq');
        badge.className = 'ai-provider-badge ' + (isMock ? 'mock' : isGroq ? 'groq' : 'gemini');
        badge.title = `Active AI provider: ${providerName}`;

        // Show a persistent warning banner if running in demo/mock mode
        if (isMock) {
            const existing = document.getElementById('mock-banner');
            if (!existing) {
                const banner = document.createElement('div');
                banner.id = 'mock-banner';
                banner.className = 'mock-banner';
                banner.innerHTML = `
                    <span>⚠️ Demo mode — Gemini quota exhausted.</span>
                    <span>Add a valid <strong>GROQ_API_KEY</strong> to <code>.env</code> for real AI insights.</span>
                `;
                document.querySelector('.topbar')?.after(banner);
            }
        }
    } catch (_) { /* non-critical */ }
}

// ── Start session ─────────────────────────────────────────────
function startSession() {
    // Show connecting overlay
    const overlay = document.getElementById('connection-overlay');
    if (overlay) overlay.classList.add('visible');

    // Connect WebSocket
    wsClient = new WebSocketClient(WS_URL);
    wsClient.onMessage = handleServerMessage;
    wsClient.connect();

    // Init speech recognition
    speechMgr = new SpeechRecognitionManager(
        (text, isFinal) => onTranscript(text, isFinal),
        (msg) => ui.showError(msg)
    );

    if (!speechMgr.isSupported()) {
        if (overlay) overlay.classList.remove('visible');
        ui.showError('Speech recognition is not supported. Please use Google Chrome or Microsoft Edge.');
        resetSession();
        return;
    }

    // Brief delay to let WS handshake complete
    setTimeout(() => {
        if (overlay) overlay.classList.remove('visible');
        speechMgr.start(selectedLanguage);
        window._speechMgr = speechMgr;   // expose for TTS mic-pause
        ui.setRecordingState(true);
        ui.showToast('🎙️ Recording started', 'success');
    }, 600);
}

// ── Stop session ──────────────────────────────────────────────
function stopSession() {
    if (speechMgr) { speechMgr.stop(); speechMgr = null; }
    ui.setRecordingState(false);
    ui.showAiThinking(); // Show "generating summary…"

    if (wsClient && wsClient.isConnected) {
        wsClient.send({ type: 'end_session' });
        ui.showToast('Generating visit summary… this may take a moment', 'info');
    } else {
        ui.hideAiThinking();
        ui.showToast('Session ended. No connection to server.', 'warning');
        resetSession();
    }
}

// ── Reset ─────────────────────────────────────────────────────
function resetSession() {
    try { if (wsClient)  { wsClient.disconnect();  } } catch(e) {}
    try { if (speechMgr) { speechMgr.stop();       } } catch(e) {}
    wsClient          = null;
    speechMgr         = null;
    window._speechMgr = null;
    currentSessionId  = null;
    ui.setRecordingState(false);
    ui.hideAiThinking();
}

// ── Transcript callback ───────────────────────────────────────
function onTranscript(text, isFinal) {
    // Block transcript display and backend send while TTS is playing
    // so the spoken audio doesn't appear in the live transcript
    if (window._speechMgr && window._speechMgr.isMuted) return;

    ui.updateTranscript(text, isFinal);

    if (isFinal && wsClient && wsClient.isConnected) {
        ui.showAiThinking();
        wsClient.send({
            type: 'transcript',
            text: text,
            language: selectedLanguage
        });
    }
}

// ── Server message handler ────────────────────────────────────
function handleServerMessage(data) {
    switch (data.type) {

        case 'session_created':
            currentSessionId = data.session_id;
            console.log('[App] Session created:', currentSessionId);
            break;

        case 'simplification':
            ui.hideAiThinking();
            if (Array.isArray(data.terms)) {
                data.terms.forEach(t => ui.addSimplification(t.term, t.explanation, t.importance || 'medium'));
            }
            break;

        case 'transcript_translation':
            // Bilingual transcript — attach translation under the matching entry
            if (data.original && data.translated) {
                ui.attachTranslationToEntry(data.original, data.translated, data.language);
            }
            break;

        case 'questions':
            if (Array.isArray(data.suggestions)) {
                ui.updateQuestions(data.suggestions, data.bilingual || false, (question) => {
                    // Always send the English version to backend for AI explanation
                    const englishQ = typeof question === 'object' ? question.english : question;
                    if (wsClient && wsClient.isConnected) {
                        wsClient.send({ type: 'question_ask', question: englishQ });
                        ui.showAiThinking();
                    }
                });
            }
            break;

        case 'translation':
            if (data.text) ui.showTranslation(data.text, selectedLanguage);
            break;

        case 'question_explanation':
            ui.hideAiThinking();
            if (data.question && data.explanation) {
                ui.showQuestionExplanation(data.question, data.explanation, false, null);
                window._onDoctorReply = (question, reply) => {
                    if (wsClient && wsClient.isConnected) {
                        wsClient.send({ type: 'doctor_reply', question, reply });
                        ui.showAiThinking();
                    }
                };
            }
            break;

        case 'question_explanation_translated':
            if (data.question && data.explanation) {
                ui.showQuestionExplanation(data.question, data.explanation, true, data.language || selectedLanguage);
            }
            break;

        case 'doctor_reply_simplified':
            ui.hideAiThinking();
            if (data.reply !== undefined) {
                const langCode = (data.language && data.language !== 'en') ? data.language : null;
                ui.showDoctorReplySimplified(
                    data.question,
                    data.reply,
                    data.reply_translated || null,
                    data.terms || [],
                    langCode
                );
                ui.showToast('Doctor\'s reply simplified ✓', 'success');
            }
            break;

        case 'session_info':
            // Live-update Session Info card counters
            ui.updateSessionInfo(data.phrase_count, data.ai_requests);
            break;

        case 'summary':
            ui.hideAiThinking();
            if (data.data) ui.displaySummary(data.data);
            setTimeout(() => { if (wsClient) { wsClient.disconnect(); wsClient = null; } }, 500);
            break;

        case 'ai_error':
            // Non-fatal AI error — show warning toast but keep session alive
            ui.hideAiThinking();
            ui.showToast(data.message || 'AI analysis unavailable for this phrase', 'warning');
            break;

        case 'error':
            // Fatal session error — show and reset
            ui.hideAiThinking();
            ui.showError(data.message || 'An error occurred');
            setTimeout(() => resetSession(), 1500);
            break;

        case 'pong':
            break;

        default:
            console.log('[App] Unknown message type:', data.type);
    }
}

// ── Boot ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', initApp);

window.addEventListener('beforeunload', () => {
    try { if (speechMgr) speechMgr.stop(); } catch(e) {}
    try { if (wsClient)  wsClient.disconnect(); } catch(e) {}
});
