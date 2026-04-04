// TEAM: Frontend
// Speech recognition module using Web Speech API

class SpeechRecognitionManager {
    /**
     * Manages browser-based speech recognition
     *
     * @param {Function} onTranscript - Callback when transcript is received (text, isFinal)
     * @param {Function} onError - Callback when error occurs
     */
    constructor(onTranscript, onError) {
        this.onTranscript = onTranscript;
        this.onError = onError;
        this.recognition = null;
        this.isRecording = false;
        this.restartAttempts = 0;
        this.maxRestartAttempts = 3;
    }

    /**
     * Check if Web Speech API is supported in the browser
     * @returns {boolean}
     */
    isSupported() {
        return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    }

    /**
     * Start speech recognition in continuous mode with interim results
     */
    start() {
        if (!this.isSupported()) {
            this.onError('Speech recognition is not supported in this browser. Please use Chrome.');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';
        this.recognition.maxAlternatives = 1;

        this.recognition.onresult = (event) => this.handleResult(event);
        this.recognition.onerror  = (event) => this.handleError(event);
        this.recognition.onend    = () => {
            // Auto-restart if still in recording mode
            if (this.isRecording) {
                setTimeout(() => {
                    if (this.isRecording && this.recognition) {
                        try { this.recognition.start(); } catch(e) {}
                    }
                }, 200);
            }
        };

        try {
            this.recognition.start();
            this.isRecording = true;
            this.restartAttempts = 0;
        } catch (e) {
            this.onError('Could not start speech recognition: ' + e.message);
        }
    }

    /**
     * Stop speech recognition and clean up
     */
    stop() {
        this.isRecording = false;
        this.restartAttempts = 0;
        if (this.recognition) {
            try {
                this.recognition.stop();
            } catch (e) { /* ignore */ }
            this.recognition = null;
        }
    }

    /**
     * Handle speech recognition results
     * @param {Event} event
     */
    handleResult(event) {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcriptPart = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcriptPart;
            } else {
                interimTranscript += transcriptPart;
            }
        }

        // Send interim results for live display
        if (interimTranscript) {
            this.onTranscript(interimTranscript, false);
        }

        // Send final results to backend
        if (finalTranscript.trim()) {
            this.onTranscript(finalTranscript.trim(), true);
        }
    }

    /**
     * Handle speech recognition errors with automatic restart
     * @param {Event} event
     */
    handleError(event) {
        const errorType = event.error;
        console.warn('Speech recognition error:', errorType);

        // Non-fatal errors
        if (errorType === 'no-speech') {
            // Silence detected – not a real error, recognition will auto-restart
            return;
        }

        if (errorType === 'network') {
            if (this.restartAttempts < this.maxRestartAttempts) {
                this.restart();
            } else {
                this.onError('Network error during speech recognition. Please check your connection.');
            }
            return;
        }

        if (errorType === 'not-allowed' || errorType === 'service-not-allowed') {
            this.isRecording = false;
            this.onError('Microphone access denied. Please allow microphone permission and try again.');
            return;
        }

        if (errorType === 'audio-capture') {
            this.isRecording = false;
            this.onError('Microphone not found. Please connect a microphone and try again.');
            return;
        }

        // Generic error – attempt restart
        if (this.restartAttempts < this.maxRestartAttempts) {
            this.restart();
        } else {
            this.onError('Speech recognition failed. Please stop and start again.');
        }
    }

    /**
     * Automatically restart recognition after error
     */
    restart() {
        this.restartAttempts++;
        setTimeout(() => {
            if (this.isRecording) {
                try { this.recognition.start(); } catch(e) {}
            }
        }, 1000);
    }
}
