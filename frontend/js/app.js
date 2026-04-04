// TEAM: Frontend
// WebSocket client and main application logic

class WebSocketClient {
    /**
     * 
     * @param {string} url - WebSocket URL (ws://localhost:8000/ws/session)
     */
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 3;
        this.reconnectDelay = 1000; // Start with 1 second
        this.heartbeatInterval = null;
        this.messageQueue = [];
    }

    /**
     * Establish WebSocket connection
     */
    connect() {
        try {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;
                this.startHeartbeat();

                // Send queued messages
                while (this.messageQueue.length > 0) {
                    const message = this.messageQueue.shift();
                    this.send(message);
                }
            };

            this.ws.onmessage = (event) => this.onMessage(event);

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.stopHeartbeat();
                this.reconnect();
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.reconnect();
        }
    }

    /**
     * Disconnect WebSocket
     */
    disconnect() {
        this.stopHeartbeat();
        this.reconnectAttempts = this.maxReconnectAttempts; // Prevent reconnection
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    /**
     * Send message via WebSocket
     * 
     * @param {Object} message - Message object to send
     */
    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.log('WebSocket not connected, queuing message');
            this.messageQueue.push(message);
        }
    }

    /**
     * Handle incoming WebSocket messages
     * 
     * @param {Event} event - WebSocket message event
     */
    onMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('Received message:', data);

            // Route message by type
            switch (data.type) {
                case 'session_created':
                    if (window.uiManager) {
                        window.sessionId = data.session_id;
                    }
                    break;
                case 'simplification':
                    if (window.uiManager) {
                        window.uiManager.addSimplification(data.term, data.explanation);
                        if (data.translation && window.currentLanguage !== 'en') {
                            window.uiManager.showTranslation(data.translation);
                        }
                    }
                    break;
                case 'questions':
                    if (window.uiManager) {
                        window.uiManager.updateQuestions(data.questions);
                    }
                    break;
                case 'translation':
                    if (window.uiManager) {
                        window.uiManager.showTranslation(data.text);
                    }
                    break;
                case 'summary':
                    if (window.uiManager) {
                        window.uiManager.displaySummary(data.summary);
                    }
                    break;
                case 'error':
                    if (window.uiManager) {
                        window.uiManager.showError(data.message || 'An error occurred');
                    }
                    break;
                case 'pong':
                    // Heartbeat response
                    break;
                default:
                    console.warn('Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    /**
     * Attempt to reconnect with exponential backoff
     */
    reconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            if (window.uiManager) {
                window.uiManager.showError('Connection lost. Please refresh the page.');
            }
            return;
        }

        this.reconnectAttempts++;
        console.log(`Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

        setTimeout(() => {
            this.connect();
        }, this.reconnectDelay);

        // Exponential backoff: 1s, 2s, 4s
        this.reconnectDelay *= 2;
    }

    /**
     * Send heartbeat ping to keep connection alive
     */
    sendHeartbeat() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.send({ type: 'ping' });
        }
    }

    /**
     * Start heartbeat interval
     */
    startHeartbeat() {
        this.stopHeartbeat();
        this.heartbeatInterval = setInterval(() => {
            this.sendHeartbeat();
        }, 30000); // 30 seconds
    }

    /**
     * Stop heartbeat interval
     */
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
}

// Application initialization
document.addEventListener('DOMContentLoaded', () => {
    // Initialize UI manager
    window.uiManager = new UIManager();

    // Initialize WebSocket client
    const wsUrl = `ws://${window.location.hostname}:8000/ws/session`;
    window.wsClient = new WebSocketClient(wsUrl);
    window.wsClient.connect();

    // Initialize Speech recognition manager
    window.speechManager = new SpeechRecognitionManager(
        (text, isFinal) => {
            // Update UI with transcript
            window.uiManager.updateTranscript(text, isFinal);

            // Send final transcripts to backend
            if (isFinal && window.sessionId) {
                window.wsClient.send({
                    type: 'transcript',
                    session_id: window.sessionId,
                    text: text,
                    language: window.currentLanguage || 'en'
                });
            }
        },
        (error) => {
            // Handle speech recognition errors
            window.uiManager.showError(error.message);
            if (error.error === 'not-allowed' || error.error === 'audio-capture') {
                window.uiManager.setRecordingState(false);
            }
        }
    );

    // Set up recording controls
    const startBtn = document.getElementById('start-recording');
    const stopBtn = document.getElementById('stop-recording');

    startBtn.addEventListener('click', () => {
        if (!window.speechManager.isSupported()) {
            window.uiManager.showError('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
            return;
        }

        window.uiManager.clearSession();
        window.speechManager.start();
        window.uiManager.setRecordingState(true);
    });

    stopBtn.addEventListener('click', () => {
        window.speechManager.stop();
        window.uiManager.setRecordingState(false);

        // Send end_session message
        if (window.sessionId) {
            window.wsClient.send({
                type: 'end_session',
                session_id: window.sessionId
            });
        }
    });

    // Set up language selection
    const languageSelect = document.getElementById('language');
    window.currentLanguage = 'en';

    languageSelect.addEventListener('change', (e) => {
        window.currentLanguage = e.target.value;

        // Show/hide translation panel
        if (window.currentLanguage !== 'en') {
            document.getElementById('translation-panel').classList.remove('hidden');
        } else {
            document.getElementById('translation-panel').classList.add('hidden');
        }
    });

    // Set up summary modal close button
    const summaryModal = document.getElementById('summary-modal');
    const closeBtn = summaryModal.querySelector('.close');
    closeBtn.addEventListener('click', () => {
        summaryModal.classList.add('hidden');
    });

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === summaryModal) {
            summaryModal.classList.add('hidden');
        }
    });
});
