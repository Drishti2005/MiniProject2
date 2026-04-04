// TEAM: Frontend
// UI manager for updating DOM elements

class UIManager {
    /**
     * Manages all UI updates and DOM manipulation
     */
    constructor() {
        // TODO: Get references to DOM elements
        this.transcriptContent = document.getElementById('transcript-content');
        this.termsContent = document.getElementById('terms-content');
        this.questionsContent = document.getElementById('questions-content');
        this.translationPanel = document.getElementById('translation-panel');
        this.translationContent = document.getElementById('translation-content');
        this.summaryModal = document.getElementById('summary-modal');
        this.summaryContent = document.getElementById('summary-content');
    }

    /**
     * Update transcript panel with new text
     * 
     * @param {string} text - Transcript text
     * @param {boolean} isFinal - Whether this is a final result
     */
    updateTranscript(text, isFinal) {
        if (!this.transcriptContent) return;

        if (isFinal) {
            const p = document.createElement('p');
            p.className = 'transcript-final';
            p.textContent = text;
            this.transcriptContent.appendChild(p);
        } else {
            // Update or create interim result element
            let interim = this.transcriptContent.querySelector('.transcript-interim');
            if (!interim) {
                interim = document.createElement('p');
                interim.className = 'transcript-interim';
                this.transcriptContent.appendChild(interim);
            }
            interim.textContent = text;
        }

        // Auto-scroll to bottom
        this.transcriptContent.scrollTop = this.transcriptContent.scrollHeight;
    }

    /**
     * Add a simplified term to the terms panel
     * 
     * @param {string} term - Medical term
     * @param {string} explanation - Plain-language explanation
     */
    addSimplification(term, explanation) {
        if (!this.termsContent) return;

        const termDiv = document.createElement('div');
        termDiv.className = 'term-item';
        
        const termSpan = document.createElement('span');
        termSpan.className = 'term-highlight';
        termSpan.textContent = term;
        
        const explanationSpan = document.createElement('span');
        explanationSpan.className = 'term-explanation';
        explanationSpan.textContent = `: ${explanation}`;
        
        termDiv.appendChild(termSpan);
        termDiv.appendChild(explanationSpan);
        
        // Animate entry
        termDiv.style.opacity = '0';
        this.termsContent.appendChild(termDiv);
        
        setTimeout(() => {
            termDiv.style.transition = 'opacity 0.3s ease-in';
            termDiv.style.opacity = '1';
        }, 10);
    }

    /**
     * Update suggested questions (replace, not append)
     * 
     * @param {Array<string>} questions - List of questions
     */
    updateQuestions(questions) {
        if (!this.questionsContent) return;

        // Clear existing questions
        this.questionsContent.innerHTML = '';

        // Add new questions as numbered list
        questions.forEach((question) => {
            const li = document.createElement('li');
            li.textContent = question;
            this.questionsContent.appendChild(li);
        });
    }

    /**
     * Show translated text in translation panel
     * 
     * @param {string} text - Translated text
     */
    showTranslation(text) {
        if (!this.translationContent || !this.translationPanel) return;

        this.translationContent.textContent = text;
        this.translationPanel.classList.remove('hidden');
    }

    /**
     * Display visit summary in modal
     * 
     * @param {Object} summary - Summary data object
     */
    displaySummary(summary) {
        if (!this.summaryContent || !this.summaryModal) return;

        // Format summary with all fields
        const fields = [
            { label: 'Title', value: summary.title },
            { label: 'Diagnosis', value: summary.diagnosis },
            { label: 'Medications', value: summary.medications },
            { label: 'Instructions', value: summary.instructions },
            { label: 'Follow-up', value: summary.follow_up },
            { label: 'Key Points', value: summary.key_points }
        ];

        let html = '';
        fields.forEach(field => {
            if (field.value) {
                html += `
                    <div class="summary-field">
                        <strong>${field.label}:</strong>
                        <p>${field.value}</p>
                    </div>
                `;
            }
        });

        this.summaryContent.innerHTML = html;
        this.summaryModal.classList.remove('hidden');
    }

    /**
     * Set recording state and update UI
     * 
     * @param {boolean} isRecording - Whether recording is active
     */
    setRecordingState(isRecording) {
        const startBtn = document.getElementById('start-recording');
        const stopBtn = document.getElementById('stop-recording');
        const indicator = document.getElementById('recording-indicator');

        if (isRecording) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
            indicator.classList.remove('hidden');
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
            indicator.classList.add('hidden');
        }
    }

    /**
     * Show error message to user
     * 
     * @param {string} message - Error message
     */
    showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            errorDiv.style.opacity = '0';
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.parentNode.removeChild(errorDiv);
                }
            }, 300);
        }, 5000);
    }

    /**
     * Clear session UI for new session
     */
    clearSession() {
        if (this.transcriptContent) this.transcriptContent.innerHTML = '';
        if (this.termsContent) this.termsContent.innerHTML = '';
        if (this.questionsContent) this.questionsContent.innerHTML = '';
        if (this.translationContent) this.translationContent.textContent = '';
        if (this.translationPanel) this.translationPanel.classList.add('hidden');
        if (this.summaryModal) this.summaryModal.classList.add('hidden');
    }
}
