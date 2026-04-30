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
    // SESSION INFO — live counter updates from backend
    // ──────────────────────────────────────────────

    updateSessionInfo(phraseCount, aiRequests) {
        // Sync backend-authoritative counts to the Session Info card
        if (phraseCount !== undefined && this.phraseCount) {
            this._phraseCount = phraseCount;
            this.phraseCount.textContent = phraseCount;
        }
        if (aiRequests !== undefined && this.aiRequestCount) {
            this._aiRequestCount = aiRequests;
            this.aiRequestCount.textContent = aiRequests;
        }
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
            entry.dataset.text = text; // used by attachTranslationToEntry
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

    // ── Attach bilingual translation under a transcript entry ─
    attachTranslationToEntry(originalText, translatedText, langCode) {
        const langNames = {
            hi:'Hindi', es:'Spanish', fr:'French', de:'German', zh:'Chinese',
            ar:'Arabic', bn:'Bengali', ta:'Tamil', te:'Telugu', mr:'Marathi', gu:'Gujarati'
        };
        const langLabel = langNames[langCode] || langCode.toUpperCase();

        // Find the most recent entry whose text matches
        const entries = this.transcriptContent.querySelectorAll('.transcript-entry');
        let target = null;
        for (let i = entries.length - 1; i >= 0; i--) {
            if (entries[i].dataset.text === originalText) {
                target = entries[i];
                break;
            }
        }
        // Fall back to last entry if no exact match
        if (!target && entries.length > 0) target = entries[entries.length - 1];
        if (!target) return;

        // Remove any existing translation on this entry
        target.querySelector('.transcript-translation')?.remove();

        const div = document.createElement('div');
        div.className = 'transcript-translation';
        div.innerHTML = `
            <span class="transcript-translation-lang">🌐 ${this._escapeHtml(langLabel)}</span>
            <span class="transcript-translation-text">${this._escapeHtml(translatedText)}</span>
        `;
        target.appendChild(div);
        this.transcriptContent.scrollTop = this.transcriptContent.scrollHeight;
    }

    // ──────────────────────────────────────────────
    // TERMS
    // ──────────────────────────────────────────────

    addSimplification(term, explanation, importance = 'medium') {
        const empty = this.termsList.querySelector('.terms-empty');
        if (empty) empty.remove();

        const item = document.createElement('div');
        item.className = `term-item importance-${importance}`;
        item.innerHTML = `
            <span class="term-chip importance-${importance}">${this._escapeHtml(term)}</span>
            <p class="term-explanation">${this._escapeHtml(explanation)}</p>
        `;
        this.termsList.appendChild(item);

        this._termCount++;
        if (this.termsCount) {
            this.termsCount.textContent = this._termCount;
            this.termsCount.style.display = 'inline-flex';
        }
        // Show importance legend on first term
        const legend = document.getElementById('importance-legend');
        if (legend) legend.style.display = 'flex';

        this._aiRequestCount++;
        if (this.aiRequestCount) this.aiRequestCount.textContent = this._aiRequestCount;

        this.hideAiThinking();
    }

    // ──────────────────────────────────────────────
    // QUESTIONS — bilingual display + speak + click to ask
    // ──────────────────────────────────────────────

    updateQuestions(questions, bilingual, onQuestionClick) {
        this.questionsContent.innerHTML = '';
        this._onQuestionClick = onQuestionClick || null;

        if (!questions || questions.length === 0) {
            this.questionsContent.innerHTML = '<p class="questions-empty">Suggested questions will appear as the conversation develops.</p>';
            if (this.questionsCount) this.questionsCount.style.display = 'none';
            return;
        }

        const list = document.createElement('ol');
        list.className = 'questions-list';

        questions.forEach((q, idx) => {
            // q is either a plain string (English only) or { english, translated, language }
            const isBilingual = bilingual && typeof q === 'object' && q.translated;
            const englishText     = isBilingual ? q.english    : (typeof q === 'string' ? q : q.english);
            const translatedText  = isBilingual ? q.translated : null;
            const langCode        = isBilingual ? q.language   : null;

            const li = document.createElement('li');
            li.className = 'question-item' + (isBilingual ? ' question-item-bilingual' : '');
            li.setAttribute('role', 'button');
            li.setAttribute('tabindex', '0');
            li.setAttribute('title', isBilingual ? 'Click to ask — speak button reads aloud in your language' : 'Click to ask this question');
            li.dataset.english = englishText;

            if (isBilingual) {
                // Bilingual layout: translated (patient reads) + English (doctor reads) + speak button
                li.innerHTML = `
                    <span class="question-num">${idx + 1}</span>
                    <div class="question-bilingual-body">
                        <span class="question-translated-text">${this._escapeHtml(translatedText)}</span>
                        <span class="question-english-text">${this._escapeHtml(englishText)}</span>
                    </div>
                    <div class="question-actions">
                        <span class="question-speak-btn" role="button" tabindex="0" title="Speak in your language" aria-label="Read question aloud">
                            🔊
                        </span>
                        <span class="question-ask-btn" aria-label="Ask this question" title="Send to doctor">
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                        </span>
                    </div>
                `;

                // Speak button — TTS in patient's language
                const speakBtn = li.querySelector('.question-speak-btn');
                const doSpeak = (e) => {
                    e.stopPropagation();
                    this._speakText(translatedText, langCode);
                    speakBtn.textContent = '🔊…';
                    setTimeout(() => { speakBtn.textContent = '🔊'; }, 2500);
                };
                speakBtn.addEventListener('click', doSpeak);
                speakBtn.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); doSpeak(e); } });
            } else {
                // English-only layout
                li.innerHTML = `
                    <span class="question-num">${idx + 1}</span>
                    <span class="question-text">${this._escapeHtml(englishText)}</span>
                    <span class="question-ask-btn" aria-label="Ask this question" title="Ask doctor">
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                    </span>
                `;
            }

            const ask = () => {
                if (this._onQuestionClick) this._onQuestionClick(isBilingual ? q : englishText);
                li.classList.add('question-asked');
                const askBtn = li.querySelector('.question-ask-btn');
                if (askBtn) askBtn.innerHTML = '✓';
                const preview = (translatedText || englishText).slice(0, 50);
                this.showToast(`"${preview}…"`, 'info');
            };

            li.addEventListener('click', ask);
            li.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') ask(); });
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

    // ── Text-to-Speech helper ─────────────────────────────────
    // Pauses live speech recognition while speaking so the mic
    // doesn't pick up the TTS audio and add it to the transcript.
    _speakText(text, langCode) {
        if (!text) return;

        const langMap = {
            hi:'hi-IN', es:'es-ES', fr:'fr-FR', de:'de-DE', zh:'zh-CN',
            ar:'ar-SA', bn:'bn-IN', ta:'ta-IN', te:'te-IN', mr:'mr-IN', gu:'gu-IN',
            pt:'pt-BR', ru:'ru-RU', ja:'ja-JP', ko:'ko-KR',
        };
        const bcp47 = langMap[langCode] || 'en-US';

        // Pause mic before speaking
        this._pauseMic();

        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();

            const trySpeak = () => {
                const voices = window.speechSynthesis.getVoices();
                const match  = voices.find(v => v.lang === bcp47)
                            || voices.find(v => v.lang.startsWith(langCode));

                if (!match && voices.length > 0) {
                    console.warn(`[TTS] No voice for ${bcp47}, using audio fallback`);
                    this._speakViaAudio(text, langCode);
                    return;
                }

                const utter    = new SpeechSynthesisUtterance(text);
                utter.lang     = bcp47;
                utter.rate     = 0.88;
                utter.pitch    = 1;
                utter.volume   = 1;
                if (match) utter.voice = match;

                utter.onend   = () => this._resumeMic();
                utter.onerror = (e) => {
                    console.warn('[TTS] Web Speech error:', e.error);
                    this._resumeMic();
                    this._speakViaAudio(text, langCode);
                };

                window.speechSynthesis.speak(utter);
            };

            const voices = window.speechSynthesis.getVoices();
            if (voices.length === 0) {
                window.speechSynthesis.onvoiceschanged = () => {
                    window.speechSynthesis.onvoiceschanged = null;
                    trySpeak();
                };
            } else {
                trySpeak();
            }
        } else {
            this._speakViaAudio(text, langCode);
        }
    }

    // ── Mic pause/resume helpers ──────────────────────────────
    _pauseMic() {
        // window._speechMgr is set by app.js so ui.js can reach it
        if (window._speechMgr && typeof window._speechMgr.pause === 'function') {
            window._speechMgr.pause();
        }
    }

    _resumeMic() {
        if (window._speechMgr && typeof window._speechMgr.resume === 'function') {
            // Small extra delay so audio output fully stops before mic opens
            setTimeout(() => window._speechMgr.resume(), 200);
        }
    }

    // ── Audio fallback via backend TTS proxy ─────────────────
    // Routes through /api/tts to avoid CORS/autoplay browser blocks
    _speakViaAudio(text, langCode) {
        try {
            // Google Translate TTS only needs the 2-letter code (hi, not hi-IN)
            const lang  = langCode.split('-')[0];
            const chunk = encodeURIComponent(text.slice(0, 200));
            const url   = `/api/tts?text=${chunk}&lang=${lang}`;

            let audio = document.getElementById('_tts_audio');
            if (!audio) {
                audio = document.createElement('audio');
                audio.id = '_tts_audio';
                audio.style.display = 'none';
                document.body.appendChild(audio);
            }
            audio.src = url;
            audio.onended = () => this._resumeMic();
            audio.onerror = () => {
                this._resumeMic();
                this.showToast(`Audio unavailable for ${langCode.toUpperCase()}`, 'warning');
            };
            audio.load();
            audio.play().catch(err => {
                this._resumeMic();
                console.warn('[TTS] play() blocked:', err);
                this.showToast('Tap the 🔊 button again to hear audio', 'warning');
            });
        } catch (e) {
            this._resumeMic();
            console.warn('[TTS] Audio fallback failed:', e);
        }
    }

    // ── Show AI explanation for a clicked question ────────────
    showQuestionExplanation(question, explanation, isTranslated = false, langCode = null) {
        let panel = document.getElementById('question-explanation-panel');

        if (!isTranslated) {
            // Build the panel fresh — attach to body as a fixed overlay
            if (panel) panel.remove();

            panel = document.createElement('div');
            panel.id = 'question-explanation-panel';
            panel.className = 'question-explanation-panel';
            document.body.appendChild(panel);

            panel.innerHTML = `
                <div class="qe-header">
                    <span class="qe-icon">🤔</span>
                    <span class="qe-label">Why ask this?</span>
                    <button class="qe-close" aria-label="Close" id="qe-close-btn">✕</button>
                </div>
                <div class="qe-question">${this._escapeHtml(question)}</div>
                <div class="qe-explanation" id="qe-explanation-en">${this._escapeHtml(explanation)}</div>
                <div id="qe-explanation-translated" style="display:none"></div>
                <div class="qe-doctor-reply-section">
                    <div class="qe-reply-label">Doctor's reply</div>
                    <div class="qe-reply-input-row">
                        <input type="text" class="qe-reply-input" id="doctor-reply-input"
                               placeholder="Type the doctor's answer…"
                               aria-label="Doctor's reply to patient question" />
                        <span class="qe-reply-send" id="doctor-reply-send"
                              role="button" tabindex="0" aria-label="Send doctor reply">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                        </span>
                    </div>
                </div>
            `;

            // Close button
            panel.querySelector('#qe-close-btn').addEventListener('click', () => panel.remove());

            // Send reply
            const input   = panel.querySelector('#doctor-reply-input');
            const sendBtn = panel.querySelector('#doctor-reply-send');
            const sendReply = () => {
                const reply = input.value.trim();
                if (!reply) return;
                if (window._onDoctorReply) window._onDoctorReply(question, reply);
                input.value = '';
                sendBtn.style.opacity = '0.4';
            };
            sendBtn.addEventListener('click', sendReply);
            sendBtn.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') sendReply(); });
            input.addEventListener('keydown', e => { if (e.key === 'Enter') sendReply(); });

            panel.classList.add('visible');
            input.focus();

        } else {
            // Add translated explanation below English
            if (!panel) return;
            const translatedDiv = panel.querySelector('#qe-explanation-translated');
            if (translatedDiv) {
                translatedDiv.style.display = 'block';
                translatedDiv.innerHTML = `
                    <div class="qe-translation-label">🌐 In your language:</div>
                    <div class="qe-explanation qe-explanation-translated-text">${this._escapeHtml(explanation)}</div>
                `;
                if (langCode) this._speakText(explanation, langCode);
            }
        }
    }

    // ── Show simplified doctor reply ──────────────────────────
    showDoctorReplySimplified(question, reply, replyTranslated, terms, langCode = null) {
        const panel = document.getElementById('question-explanation-panel');
        if (!panel) return;

        const replySection = panel.querySelector('.qe-doctor-reply-section');
        if (replySection) {
            let termsHtml = '';
            if (terms && terms.length > 0) {
                termsHtml = `<div class="qe-terms">
                    ${terms.map(t => `
                        <div class="qe-term-item">
                            <span class="term-chip importance-${t.importance || 'medium'}">${this._escapeHtml(t.term)}</span>
                            <span class="qe-term-exp">${this._escapeHtml(t.explanation)}</span>
                        </div>`).join('')}
                </div>`;
            }

            // Show translated reply prominently if available, English below
            const translatedBlock = replyTranslated ? `
                <div class="qe-reply-translated">
                    <div class="qe-translation-label">🌐 In your language:</div>
                    <div class="qe-reply-text qe-reply-text-translated">${this._escapeHtml(replyTranslated)}</div>
                </div>` : '';

            const englishBlock = replyTranslated
                ? `<div class="qe-reply-english-small">${this._escapeHtml(reply)}</div>`
                : `<div class="qe-reply-text">${this._escapeHtml(reply)}</div>`;

            replySection.innerHTML = `
                <div class="qe-reply-label">Doctor said:</div>
                ${translatedBlock}
                ${englishBlock}
                ${termsHtml}
                ${(replyTranslated && langCode) ? `
                <span class="qe-speak-reply-btn" role="button" tabindex="0"
                      title="Hear in your language" aria-label="Speak doctor reply">
                    🔊 Hear in your language
                </span>` : ''}
            `;

            // Auto-speak the translated reply
            if (replyTranslated && langCode) {
                this._speakText(replyTranslated, langCode);
                const speakBtn = replySection.querySelector('.qe-speak-reply-btn');
                speakBtn?.addEventListener('click', () => this._speakText(replyTranslated, langCode));
                speakBtn?.addEventListener('keydown', e => {
                    if (e.key === 'Enter' || e.key === ' ') this._speakText(replyTranslated, langCode);
                });
            }
        }

        if (terms && terms.length > 0) {
            terms.forEach(t => this.addSimplification(t.term, t.explanation, t.importance || 'medium'));
        }
    }

    // ──────────────────────────────────────────────
    // TRANSLATION
    // ──────────────────────────────────────────────

    showTranslation(text, langCode) {
        if (!this.translationCard || !this.translationText) return;
        const langNames = {
            hi:'Hindi', es:'Spanish', fr:'French', de:'German', zh:'Chinese',
            ar:'Arabic', bn:'Bengali', ta:'Tamil', te:'Telugu', mr:'Marathi', gu:'Gujarati'
        };
        const langLabel = langNames[langCode] || (langCode ? langCode.toUpperCase() : 'Translation');
        // Update the label to show which language
        const labelEl = this.translationCard.querySelector('.translation-label');
        if (labelEl) labelEl.textContent = `🌐 ${langLabel}`;
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
        const legend = document.getElementById('importance-legend');
        if (legend) legend.style.display = 'none';
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

        // Remove any stale question explanation panel
        const qep = document.getElementById('question-explanation-panel');
        if (qep) qep.remove();
        this._onQuestionClick = null;
        window._onDoctorReply = null;
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
