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
     * 
     * @returns {boolean} True if supported, false otherwise
     */
    isSupported() {
        return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    }

    /**
     * Start speech recognition in continuous mode with interim results
     */
    start() {
        if (!this.isSupported()) {
            this.onError({ error: 'not-supported', message: 'Web Speech API not supported in this browser' });
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        this.recognition.onresult = (event) => this.handleResult(event);
        this.recognition.onerror = (event) => this.handleError(event);
        this.recognition.onend = () => {
            if (this.isRecording && this.restartAttempts < this.maxRestartAttempts) {
                this.restart();
            }
        };

        try {
            this.recognition.start();
            this.isRecording = true;
            this.restartAttempts = 0;
        } catch (error) {
            this.onError({ error: 'start-failed', message: error.message });
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
            } catch (error) {
                console.error('Error stopping recognition:', error);
            }
        }
    }

    /**
     * Handle speech recognition results
     * 
     * @param {Event} event - Speech recognition result event
     */
    handleResult(event) {
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            const transcript = result[0].transcript;
            const isFinal = result.isFinal;
            
            if (this.onTranscript) {
                this.onTranscript(transcript, isFinal);
            }
        }
    }

    /**
     * Handle speech recognition errors with automatic restart
     * 
     * @param {Event} event - Speech recognition error event
     */
    handleError(event) {
        console.error('Speech recognition error:', event.error);
        
        const errorMessages = {
            'no-speech': 'No speech detected. Please try speaking again.',
            'network': 'Network error occurred. Please check your connection.',
            'not-allowed': 'Microphone access denied. Please allow microphone access.',
            'audio-capture': 'No microphone found. Please connect a microphone.',
            'aborted': 'Speech recognition was aborted.'
        };

        const message = errorMessages[event.error] || `Speech recognition error: ${event.error}`;
        
        if (this.onError) {
            this.onError({ error: event.error, message });
        }

        // Don't restart for permission or hardware errors
        if (event.error === 'not-allowed' || event.error === 'audio-capture') {
            this.isRecording = false;
            return;
        }

        // Attempt automatic restart for recoverable errors
        if (this.isRecording && this.restartAttempts < this.maxRestartAttempts) {
            if (event.error === 'no-speech' || event.error === 'network' || event.error === 'aborted') {
                this.restart();
            }
        }
    }

    /**
     * Automatically restart recognition after error
     */
    restart() {
        this.restartAttempts++;
        console.log(`Restarting speech recognition (attempt ${this.restartAttempts}/${this.maxRestartAttempts})`);
        
        setTimeout(() => {
            if (this.isRecording) {
                try {
                    this.recognition.start();
                } catch (error) {
                    console.error('Error restarting recognition:', error);
                }
            }
        }, 1000);
    }
}
