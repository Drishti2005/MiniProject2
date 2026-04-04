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
    });

    // Recording buttons
    document.getElementById('start-recording')?.addEventListener('click', startSession);
    document.getElementById('stop-recording')?.addEventListener('click', stopSession);
}

// ── Start session ─────────────────────────────────────────────
function startSession() {
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
        ui.showError('Speech recognition is not supported. Please use Google Chrome or Microsoft Edge.');
        resetSession();
        return;
    }

    // Brief delay to let WS handshake complete
    setTimeout(() => {
        speechMgr.start();
        ui.setRecordingState(true);
        ui.showToast('🎙️ Recording started', 'success');
    }, 500);
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
    wsClient         = null;
    speechMgr        = null;
    currentSessionId = null;
    ui.setRecordingState(false);
    ui.hideAiThinking();
}

// ── Transcript callback ───────────────────────────────────────
function onTranscript(text, isFinal) {
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
                data.terms.forEach(t => ui.addSimplification(t.term, t.explanation));
            }
            break;

        case 'questions':
            if (Array.isArray(data.suggestions)) {
                ui.updateQuestions(data.suggestions);
            }
            break;

        case 'translation':
            if (data.text) ui.showTranslation(data.text);
            break;

        case 'summary':
            ui.hideAiThinking();
            if (data.data) ui.displaySummary(data.data);
            setTimeout(() => { if (wsClient) { wsClient.disconnect(); wsClient = null; } }, 500);
            break;

        case 'error':
            ui.hideAiThinking();
            ui.showError(data.message || 'An error occurred');
            setTimeout(() => resetSession(), 400);
            break;

        case 'pong':
            // Heartbeat — no action needed
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
