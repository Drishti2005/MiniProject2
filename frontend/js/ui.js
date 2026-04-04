// ============================================================
// SIDEKICK — UIManager
// Manages all DOM updates for the Clinical Concierge design
// ============================================================

class UIManager {
    constructor() {
        // Transcript panel
        this.transcriptContent    = document.getElementById('transcript-content');
        this.translationCard      = document.getElementById('translation-card');
        this.translationText      = document.getElementById('translation-text');
        this.aiThinking           = document.getElementById('ai-thinking');

        // Insights panel
        this.termsList            = document.getElementById('terms-list');
        this.termsCount           = document.getElementById('terms-count');
        this.questionsContent     = document.getElementById('questions-content');
        this.questionsCount       = document.getElementById('questions-count');

        // Session info
        this.sessionDuration      = document.getElementById('session-duration');
        this.phraseCount          = document.getElementById('phrase-count');
        this.aiRequestCount       = document.getElementById('ai-request-count');

        // Topbar recording badge
        this.recordingBadge       = document.getElementById('recording-badge');
        this.recordingBadgeDot    = document.getElementById('recording-badge-dot');
        this.recordingStatusText  = document.getElementById('recording-status-text');

        // Sidebar status
        this.sidebarStatus        = document.getElementById('sidebar-status');
        this.sidebarStatusText    = document.getElementById('sidebar-status-text');

        // Bottom pill rec indicator
        this.recIndicator         = document.getElementById('rec-indicator');

        // Buttons
        this.startBtn             = document.getElementById('start-recording');
        this.stopBtn              = document.getElementById('stop-recording');

        // Summary modal
        this.summaryModal         = document.getElementById('summary-modal');
        this.summaryContent       = document.getElementById('summary-content');
        this.summaryStats         = document.getElementById('summary-stats');
        this.modalSubtitle        = document.getElementById('modal-subtitle');

        // Toast container
        this.toastContainer       = document.getElementById('toast-container');

        // State
        this._interimEl           = null;
        this._hasTranscript       = false;
        this._termCount           = 0;
        this._questionCount       = 0;
        this._phraseCount         = 0;
        this._aiRequestCount      = 0;
        this._sessionStartTime    = null;
        this._durationTimer       = null;
    }

    // ──────────────────────────────────────────────
    // TRANSCRIPT
    // ──────────────────────────────────────────────

    updateTranscript(text, isFinal) {
        const empty = this.transcriptContent.querySelector('.transcript-empty');
        if (empty) empty.remove();

        if (!isFinal) {
            if (!this._interimEl) {
                this._interimEl = document.createElement('div');
                this._interimEl.className = 'transcript-interim';
                this._interimEl.setAttribute('aria-live', 'polite');
                this.transcriptContent.appendChild(this._interimEl);
            }
            this._interimEl.textContent = text + '…';
        } else {
            if (this._interimEl) {
                this._interimEl.remove();
                this._interimEl = null;
            }

            const entry = document.createElement('div');
            entry.className = 'transcript-entry';
            const now = new Date();
            const timestamp = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            entry.innerHTML = `
                <div class="transcript-entry-header">
                    <span class="transcript-entry-speaker">Transcript</span>
                    <span class="transcript-entry-time">${timestamp}</span>
                </div>
                <div class="transcript-entry-text">${this._escapeHtml(text)}</div>
            `;
            this.transcriptContent.appendChild(entry);
            this._hasTranscript = true;

            this._phraseCount++;
            if (this.phraseCount) this.phraseCount.textContent = this._phraseCount;
        }

        this.transcriptContent.scrollTop = this.transcriptContent.scrollHeight;
    }

    // ──────────────────────────────────────────────
    // TERMS
    // ──────────────────────────────────────────────

    addSimplification(term, explanation) {
        const empty = this.termsList.querySelector('.terms-empty');
        if (empty) empty.remove();

        const item = document.createElement('div');
        item.className = 'term-item';
        item.innerHTML = `
            <span class="term-chip">${this._escapeHtml(term)}</span>
            <p class="term-explanation">${this._escapeHtml(explanation)}</p>
        `;
        this.termsList.appendChild(item);

        this._termCount++;
        if (this.termsCount) {
            this.termsCount.textContent = this._termCount;
            this.termsCount.style.display = 'inline-flex';
        }

        this._aiRequestCount++;
        if (this.aiRequestCount) this.aiRequestCount.textContent = this._aiRequestCount;

        this.hideAiThinking();
    }

    // ──────────────────────────────────────────────
    // QUESTIONS
    // ──────────────────────────────────────────────

    updateQuestions(questions) {
        this.questionsContent.innerHTML = '';

        if (!questions || questions.length === 0) {
            this.questionsContent.innerHTML = '<p class="questions-empty">Suggested questions will appear as the conversation develops.</p>';
            if (this.questionsCount) this.questionsCount.style.display = 'none';
            return;
        }

        const list = document.createElement('ol');
        list.className = 'questions-list';

        questions.forEach((q, idx) => {
            const li = document.createElement('li');
            li.className = 'question-item';
            li.setAttribute('role', 'button');
            li.setAttribute('tabindex', '0');
            li.setAttribute('title', 'Click to copy');
            li.innerHTML = `
                <span class="question-num">${idx + 1}</span>
                <span class="question-text">${this._escapeHtml(q)}</span>
            `;
            const copy = () => {
                navigator.clipboard.writeText(q).catch(() => {});
                this.showToast('Question copied to clipboard!', 'success');
            };
            li.addEventListener('click', copy);
            li.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') copy(); });
            list.appendChild(li);
        });

        this.questionsContent.appendChild(list);

        this._questionCount = questions.length;
        if (this.questionsCount) {
            this.questionsCount.textContent = this._questionCount;
            this.questionsCount.style.display = 'inline-flex';
        }

        this._aiRequestCount++;
        if (this.aiRequestCount) this.aiRequestCount.textContent = this._aiRequestCount;
    }

    // ──────────────────────────────────────────────
    // TRANSLATION
    // ──────────────────────────────────────────────

    showTranslation(text) {
        if (!this.translationCard || !this.translationText) return;
        this.translationText.textContent = text;
        this.translationCard.classList.add('visible');
    }

    hideTranslation() {
        if (this.translationCard) this.translationCard.classList.remove('visible');
    }

    // ──────────────────────────────────────────────
    // AI THINKING
    // ──────────────────────────────────────────────

    showAiThinking() {
        if (this.aiThinking) this.aiThinking.classList.add('visible');
    }

    hideAiThinking() {
        if (this.aiThinking) this.aiThinking.classList.remove('visible');
    }

    // ──────────────────────────────────────────────
    // RECORDING STATE
    // ──────────────────────────────────────────────

    setRecordingState(isRecording) {
        // Start/stop button states
        if (this.startBtn) {
            this.startBtn.disabled = isRecording;
            if (isRecording) {
                this.startBtn.innerHTML = `
                    <span class="rec-dot" style="width:8px;height:8px;background:var(--tertiary-fixed)" aria-hidden="true"></span>
                    Recording…
                `;
            } else {
                this.startBtn.innerHTML = `
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="12" cy="12" r="6"/></svg>
                    Start Recording
                `;
                this.startBtn.disabled = false;
            }
        }

        if (this.stopBtn) {
            this.stopBtn.disabled = !isRecording;
        }

        // Topbar badge
        if (this.recordingBadge) {
            this.recordingBadge.classList.toggle('is-live', isRecording);
        }
        if (this.recordingStatusText) {
            this.recordingStatusText.textContent = isRecording ? 'Recording' : 'Ready';
        }

        // Sidebar status
        if (this.sidebarStatus) {
            this.sidebarStatus.classList.toggle('is-live', isRecording);
        }
        if (this.sidebarStatusText) {
            this.sidebarStatusText.textContent = isRecording ? 'Session live' : 'Session ready';
        }

        // Rec indicator inside pill
        if (this.recIndicator) {
            this.recIndicator.classList.toggle('visible', isRecording);
        }

        // Session timer
        if (isRecording) {
            this._sessionStartTime = Date.now();
            this._startDurationTimer();
        } else {
            this._stopDurationTimer();
        }
    }

    _startDurationTimer() {
        this._stopDurationTimer();
        this._durationTimer = setInterval(() => {
            if (!this._sessionStartTime) return;
            const elapsed = Math.floor((Date.now() - this._sessionStartTime) / 1000);
            const m = Math.floor(elapsed / 60);
            const s = elapsed % 60;
            if (this.sessionDuration) {
                this.sessionDuration.textContent = `${m}:${s.toString().padStart(2, '0')}`;
            }
        }, 1000);
    }

    _stopDurationTimer() {
        if (this._durationTimer) {
            clearInterval(this._durationTimer);
            this._durationTimer = null;
        }
    }

    // ──────────────────────────────────────────────
    // SUMMARY MODAL
    // ──────────────────────────────────────────────

    displaySummary(summary) {
        if (!this.summaryContent) return;

        // Subtitle with timestamp
        if (this.modalSubtitle) {
            this.modalSubtitle.textContent = new Date().toLocaleDateString([], {
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
            });
        }

        // Stats row
        if (this.summaryStats) {
            const keyPointCount = (summary.key_points && summary.key_points.length) || 0;
            const medCount = (summary.medications && summary.medications.length) || 0;
            const instCount = (summary.instructions && summary.instructions.length) || 0;
            this.summaryStats.innerHTML = `
                <div class="stat-chip">
                    <div class="stat-chip-value">${keyPointCount}</div>
                    <div class="stat-chip-label">Key Points</div>
                </div>
                <div class="stat-chip">
                    <div class="stat-chip-value">${medCount}</div>
                    <div class="stat-chip-label">Medications</div>
                </div>
                <div class="stat-chip">
                    <div class="stat-chip-value">${instCount}</div>
                    <div class="stat-chip-label">Instructions</div>
                </div>
            `;
            this.summaryStats.style.display = 'flex';
        }

        let html = '';

        if (summary.title) {
            html += `
                <div class="summary-section">
                    <div class="summary-section-label">Visit Title</div>
                    <p class="summary-text" style="font-weight:700;font-size:1rem;">${this._escapeHtml(summary.title)}</p>
                </div>`;
        }

        if (summary.diagnosis) {
            html += `
                <div class="summary-section">
                    <div class="summary-section-label">Diagnosis</div>
                    <p class="summary-text">${this._escapeHtml(summary.diagnosis)}</p>
                </div>`;
        }

        if (summary.key_points && summary.key_points.length > 0) {
            const points = summary.key_points
                .map(p => `<li><span>${this._escapeHtml(p)}</span></li>`)
                .join('');
            html += `
                <div class="summary-section">
                    <div class="summary-section-label">Key Points</div>
                    <ul class="summary-list">${points}</ul>
                </div>`;
        }

        if (summary.medications && summary.medications.length > 0) {
            const meds = summary.medications
                .map(m => `<li><span>${this._escapeHtml(m)}</span></li>`)
                .join('');
            html += `
                <div class="summary-section">
                    <div class="summary-section-label">Medications Prescribed</div>
                    <ul class="summary-list">${meds}</ul>
                </div>`;
        }

        if (summary.instructions && summary.instructions.length > 0) {
            const inst = summary.instructions
                .map(i => `<li><span>${this._escapeHtml(i)}</span></li>`)
                .join('');
            html += `
                <div class="summary-section">
                    <div class="summary-section-label">Patient Instructions</div>
                    <ul class="summary-list">${inst}</ul>
                </div>`;
        }

        if (summary.follow_up) {
            html += `
                <div class="summary-section">
                    <div class="summary-section-label">Follow-up</div>
                    <p class="summary-text">${this._escapeHtml(summary.follow_up)}</p>
                </div>`;
        }

        if (!html) {
            html = '<p class="summary-text" style="padding:.5rem 0;">Summary generated — no structured data returned from AI.</p>';
        }

        this.summaryContent.innerHTML = html;
        if (this.summaryModal) this.summaryModal.classList.add('visible');
    }

    hideSummary() {
        if (this.summaryModal) this.summaryModal.classList.remove('visible');
    }

    // ──────────────────────────────────────────────
    // SESSION RESET
    // ──────────────────────────────────────────────

    clearSession() {
        if (this.transcriptContent) {
            this.transcriptContent.innerHTML = `
                <div class="transcript-empty" id="transcript-empty">
                    <div class="transcript-empty-orb" aria-hidden="true">🎙️</div>
                    <h3>Ready to listen</h3>
                    <p>Press <strong>Start Recording</strong> below to begin capturing the appointment conversation.</p>
                </div>`;
        }
        if (this.termsList) {
            this.termsList.innerHTML = '<p class="terms-empty">Medical terms will be explained here as they are spoken.</p>';
        }
        if (this.questionsContent) {
            this.questionsContent.innerHTML = '<p class="questions-empty">Suggested questions will appear as the conversation develops.</p>';
        }
        if (this.termsCount) { this.termsCount.textContent = '0'; this.termsCount.style.display = 'none'; }
        if (this.questionsCount) { this.questionsCount.textContent = '0'; this.questionsCount.style.display = 'none'; }
        if (this.phraseCount) this.phraseCount.textContent = '0';
        if (this.aiRequestCount) this.aiRequestCount.textContent = '0';
        if (this.sessionDuration) this.sessionDuration.textContent = '—';

        this._interimEl = null;
        this._hasTranscript = false;
        this._termCount = 0;
        this._questionCount = 0;
        this._phraseCount = 0;
        this._aiRequestCount = 0;

        this.hideTranslation();
        this.hideSummary();
        this.hideAiThinking();
        this._stopDurationTimer();
    }

    // ──────────────────────────────────────────────
    // TOASTS
    // ──────────────────────────────────────────────

    showToast(message, type = 'info') {
        if (!this.toastContainer) return;

        const icons = {
            info:    '&#8505;',
            success: '&#10003;',
            error:   '&#10007;',
            warning: '&#9651;'
        };

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <span style="font-size:1rem;" aria-hidden="true">${icons[type] || icons.info}</span>
            <span class="toast-message">${this._escapeHtml(message)}</span>
        `;
        this.toastContainer.appendChild(toast);

        const dismiss = () => {
            toast.style.animation = 'toast-slide-out 0.3s forwards';
            setTimeout(() => toast.remove(), 300);
        };
        setTimeout(dismiss, 4500);
        toast.addEventListener('click', dismiss);
    }

    showError(message) { this.showToast(message, 'error'); }

    // ──────────────────────────────────────────────
    // HELPERS
    // ──────────────────────────────────────────────

    _escapeHtml(text) {
        if (typeof text !== 'string') return String(text || '');
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}
