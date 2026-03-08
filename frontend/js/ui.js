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
        // TODO: Append text to transcript panel
        // TODO: Auto-scroll to bottom
        // TODO: Style differently for interim vs final results
    }

    /**
     * Add a simplified term to the terms panel
     * 
     * @param {string} term - Medical term
     * @param {string} explanation - Plain-language explanation
     */
    addSimplification(term, explanation) {
        // TODO: Create term element with highlighting
        // TODO: Add to terms panel
        // TODO: Animate entry
    }

    /**
     * Update suggested questions (replace, not append)
     * 
     * @param {Array<string>} questions - List of questions
     */
    updateQuestions(questions) {
        // TODO: Clear existing questions
        // TODO: Add new questions as numbered list
    }

    /**
     * Show translated text in translation panel
     * 
     * @param {string} text - Translated text
     */
    showTranslation(text) {
        // TODO: Display text in translation panel
        // TODO: Make panel visible
    }

    /**
     * Display visit summary in modal
     * 
     * @param {Object} summary - Summary data object
     */
    displaySummary(summary) {
        // TODO: Format summary with all fields
        // TODO: Show modal
    }

    /**
     * Set recording state and update UI
     * 
     * @param {boolean} isRecording - Whether recording is active
     */
    setRecordingState(isRecording) {
        // TODO: Toggle recording indicator
        // TODO: Enable/disable buttons
    }

    /**
     * Show error message to user
     * 
     * @param {string} message - Error message
     */
    showError(message) {
        // TODO: Display error notification
    }

    /**
     * Clear session UI for new session
     */
    clearSession() {
        // TODO: Clear all panels
        // TODO: Reset UI state
    }
}
