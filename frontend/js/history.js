// ============================================================
// SIDEKICK — History.js
// Session history page logic — Clinical Concierge design
// ============================================================

const API_BASE = window.location.origin;
let sessionToDelete = null;

// ── Load all sessions ─────────────────────────────────────────
async function loadSessions() {
    const listEl    = document.getElementById('sessions-list');
    const loadingEl = document.getElementById('sessions-loading');
    const emptyEl   = document.getElementById('sessions-empty');
    const statsEl   = document.getElementById('history-stats');

    // Show skeleton
    if (loadingEl) loadingEl.style.display = 'flex';
    if (listEl)    listEl.innerHTML = '';
    if (emptyEl)   emptyEl.classList.add('hidden');
    if (statsEl)   statsEl.style.display = 'none';

    try {
        const res  = await fetch(`${API_BASE}/api/sessions`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const sessions = data.sessions || [];

        // Hide skeleton
        if (loadingEl) loadingEl.style.display = 'none';

        if (sessions.length === 0) {
            if (emptyEl) emptyEl.classList.remove('hidden');
            const subtitle = document.getElementById('sessions-subtitle');
            if (subtitle) subtitle.textContent = 'No sessions recorded yet.';
            return;
        }

        // Sort newest first
        sessions.sort((a, b) =>
            new Date(b.started_at || b.created_at || 0) - new Date(a.started_at || a.created_at || 0)
        );

        // Populate stats
        populateStats(sessions, statsEl);

        // Update subtitle
        const subtitle = document.getElementById('sessions-subtitle');
        if (subtitle) subtitle.textContent = `${sessions.length} appointment session${sessions.length !== 1 ? 's' : ''} recorded.`;

        // Render cards
        sessions.forEach(session => {
            const card = buildSessionCard(session);
            listEl.appendChild(card);
        });

    } catch (err) {
        console.error('[History] Failed to load sessions:', err);
        if (loadingEl) loadingEl.style.display = 'none';
        if (listEl) {
            listEl.innerHTML = `
                <div class="sessions-empty" style="display:flex">
                    <div class="sessions-empty-orb" style="background:#fef2f2">⚠️</div>
                    <h3>Could not load sessions</h3>
                    <p>Make sure the backend server is running at <strong>localhost:8000</strong></p>
                    <button class="btn btn-primary btn-sm" onclick="loadSessions()" style="margin-top:0.5rem">
                        ↺ Retry
                    </button>
                </div>`;
        }
    }
}

// ── Populate stats row ────────────────────────────────────────
function populateStats(sessions, statsEl) {
    if (!statsEl) return;

    const total      = sessions.length;
    const withSummary = sessions.filter(s => s.has_summary || s.summary_preview).length;
    const most_recent = sessions[0];
    const recentLabel = most_recent
        ? new Date(most_recent.started_at || most_recent.created_at).toLocaleDateString([], {
            month: 'short', day: 'numeric'
          })
        : '—';

    const totalEl   = document.getElementById('stat-total');
    const summaryEl = document.getElementById('stat-summaries');
    const recentEl  = document.getElementById('stat-recent');

    if (totalEl)   totalEl.textContent   = total;
    if (summaryEl) summaryEl.textContent = withSummary;
    if (recentEl)  recentEl.textContent  = recentLabel;

    statsEl.style.display = 'grid';
}

// ── Build session card ────────────────────────────────────────
function buildSessionCard(session) {
    const card    = document.createElement('div');
    card.className = 'session-card';
    card.setAttribute('data-session-id', session.id);

    const date     = formatDate(session.started_at || session.created_at);
    const duration = session.ended_at
        ? formatDuration(session.started_at || session.created_at, session.ended_at)
        : 'Ongoing';
    const preview  = session.summary_preview || session.transcript_preview || 'No content available';
    const isEnded  = !!session.ended_at;
    const hasSummary = !!(session.has_summary || session.summary_preview);

    card.innerHTML = `
        <div class="session-card-icon" aria-hidden="true">🩺</div>
        <div class="session-card-body">
            <div class="session-card-top">
                <div class="session-card-date">${escapeHtml(date)}</div>
                <div style="display:flex;gap:0.4rem;flex-wrap:wrap;justify-content:flex-end">
                    <span class="badge badge-${isEnded ? 'ended' : 'active'}">${isEnded ? 'Ended' : '● Active'}</span>
                    ${hasSummary ? '<span class="badge badge-summary">Summary ✓</span>' : ''}
                </div>
            </div>
            <div class="session-card-meta">Duration: ${escapeHtml(duration)}</div>
            <div class="session-card-summary">${escapeHtml(String(preview).substring(0, 130))}${String(preview).length > 130 ? '…' : ''}</div>
        </div>
        <div class="session-card-actions">
            <button class="btn btn-secondary btn-sm" data-action="view" aria-label="View session details">View</button>
            <button class="btn btn-danger btn-sm" data-action="delete" aria-label="Delete session">Delete</button>
        </div>
    `;

    card.querySelector('[data-action="view"]').addEventListener('click', e => {
        e.stopPropagation();
        showSessionDetail(session.id);
    });

    card.querySelector('[data-action="delete"]').addEventListener('click', e => {
        e.stopPropagation();
        confirmDelete(session.id);
    });

    card.addEventListener('click', () => showSessionDetail(session.id));

    return card;
}

// ── Show session detail ───────────────────────────────────────
async function showSessionDetail(sessionId) {
    const listView   = document.getElementById('sessions-list-view');
    const detailView = document.getElementById('session-detail-view');
    const sectionsEl = document.getElementById('detail-sections');
    const titleEl    = document.getElementById('history-page-title');
    const backBtn    = document.getElementById('back-btn');

    // Switch to detail view
    if (listView)   listView.style.display  = 'none';
    if (detailView) detailView.classList.add('visible');
    if (backBtn)    backBtn.style.display    = 'inline-flex';
    if (titleEl)    titleEl.textContent      = 'Session Detail';

    // Show skeleton loading
    sectionsEl.innerHTML = `
        <div class="detail-card">
            <div class="skeleton" style="width:40%;height:14px;margin-bottom:12px"></div>
            <div class="skeleton" style="width:100%;height:12px;margin-bottom:8px"></div>
            <div class="skeleton" style="width:90%;height:12px;margin-bottom:8px"></div>
            <div class="skeleton" style="width:75%;height:12px"></div>
        </div>
        <div class="detail-card">
            <div class="skeleton" style="width:30%;height:14px;margin-bottom:12px"></div>
            <div class="skeleton" style="width:100%;height:12px;margin-bottom:8px"></div>
            <div class="skeleton" style="width:85%;height:12px"></div>
        </div>`;

    try {
        const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const session = await res.json();
        renderSessionDetail(sectionsEl, session);
    } catch (err) {
        console.error('[History] Failed to load detail:', err);
        sectionsEl.innerHTML = `
            <div class="detail-card" style="text-align:center;padding:2rem">
                <div style="font-size:2rem;margin-bottom:0.75rem">⚠️</div>
                <h3 style="font-family:var(--font-headline);font-size:1rem;margin-bottom:0.5rem">Could not load session</h3>
                <p style="font-size:0.875rem;color:var(--on-surface-variant)">${escapeHtml(err.message)}</p>
            </div>`;
    }
}

// ── Render session detail content ─────────────────────────────
function renderSessionDetail(container, session) {
    const date     = formatDate(session.started_at || session.created_at);
    const duration = session.ended_at
        ? formatDuration(session.started_at || session.created_at, session.ended_at)
        : 'Ongoing';

    let html = '';

    // ── Session metadata card
    html += `
        <div class="detail-card">
            <div class="detail-card-title">Session Overview</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                <div>
                    <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--on-surface-variant);margin-bottom:4px">Date</div>
                    <div style="font-size:0.875rem;font-weight:600;color:var(--on-surface)">${escapeHtml(date)}</div>
                </div>
                <div>
                    <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--on-surface-variant);margin-bottom:4px">Duration</div>
                    <div style="font-size:0.875rem;font-weight:600;color:var(--on-surface)">${escapeHtml(duration)}</div>
                </div>
                <div>
                    <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--on-surface-variant);margin-bottom:4px">Session ID</div>
                    <div style="font-size:0.72rem;font-family:monospace;color:var(--on-surface-variant)">${escapeHtml(String(session.id || '—').substring(0, 24))}…</div>
                </div>
                <div>
                    <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--on-surface-variant);margin-bottom:4px">Status</div>
                    <span class="badge badge-${session.ended_at ? 'ended' : 'active'}">${session.ended_at ? 'Completed' : '● Active'}</span>
                </div>
            </div>
        </div>`;

    // ── Transcript card
    const transcriptText = session.transcript
        || (Array.isArray(session.transcript_chunks) ? session.transcript_chunks.join(' ') : '')
        || '';

    html += `
        <div class="detail-card">
            <div class="detail-card-title">Full Transcript</div>
            ${transcriptText
                ? `<p class="detail-transcript-text">${escapeHtml(transcriptText)}</p>`
                : `<p style="color:var(--on-surface-variant);font-size:0.875rem;font-style:italic;">No transcript was recorded for this session.</p>`}
        </div>`;

    // ── Simplified terms card
    const simplifications = session.simplifications || [];
    if (simplifications.length > 0) {
        const termsHtml = simplifications.map(s => `
            <div class="term-item">
                <span class="term-chip">${escapeHtml(s.term || s.medical_term || '')}</span>
                <p class="term-explanation">${escapeHtml(s.explanation || s.simplified_explanation || '')}</p>
            </div>`).join('');
        html += `
            <div class="detail-card">
                <div class="detail-card-title">AI-Simplified Terms (${simplifications.length})</div>
                <div class="terms-list">${termsHtml}</div>
            </div>`;
    }

    // ── Summary card
    const summary = session.summary;
    if (summary) {
        let summaryHtml = '';

        if (summary.title) {
            summaryHtml += `
                <div class="summary-section">
                    <div class="summary-section-label">Visit Title</div>
                    <p class="summary-text" style="font-weight:700">${escapeHtml(summary.title)}</p>
                </div>`;
        }
        if (summary.diagnosis) {
            summaryHtml += `
                <div class="summary-section">
                    <div class="summary-section-label">Diagnosis</div>
                    <p class="summary-text">${escapeHtml(summary.diagnosis)}</p>
                </div>`;
        }
        if (summary.chief_complaint) {
            summaryHtml += `
                <div class="summary-section">
                    <div class="summary-section-label">Chief Complaint</div>
                    <p class="summary-text">${escapeHtml(summary.diagnosis)}</p>
                </div>`;
        }
        if (summary.key_points && summary.key_points.length) {
            summaryHtml += `
                <div class="summary-section">
                    <div class="summary-section-label">Key Points</div>
                    <ul class="summary-list">${summary.key_points.map(p => `<li><span>${escapeHtml(p)}</span></li>`).join('')}</ul>
                </div>`;
        }
        if (summary.medications && summary.medications.length) {
            summaryHtml += `
                <div class="summary-section">
                    <div class="summary-section-label">Medications</div>
                    <ul class="summary-list">${summary.medications.map(m => `<li><span>${escapeHtml(m)}</span></li>`).join('')}</ul>
                </div>`;
        }
        if (summary.instructions && summary.instructions.length) {
            summaryHtml += `
                <div class="summary-section">
                    <div class="summary-section-label">Patient Instructions</div>
                    <ul class="summary-list">${summary.instructions.map(i => `<li><span>${escapeHtml(i)}</span></li>`).join('')}</ul>
                </div>`;
        }
        if (summary.follow_up || (summary.follow_up_actions && summary.follow_up_actions.length)) {
            const followUpText = summary.follow_up || (summary.follow_up_actions || []).join('; ');
            summaryHtml += `
                <div class="summary-section">
                    <div class="summary-section-label">Follow-up</div>
                    <p class="summary-text">${escapeHtml(followUpText)}</p>
                </div>`;
        }

        if (summaryHtml) {
            html += `
                <div class="detail-card">
                    <div class="detail-card-title">AI Visit Summary</div>
                    <div style="display:flex;flex-direction:column;gap:0.75rem;">${summaryHtml}</div>
                </div>`;
        }
    } else {
        html += `
            <div class="detail-card" style="border:1.5px dashed rgba(195,198,214,0.5)">
                <div class="detail-card-title">AI Visit Summary</div>
                <p style="font-size:0.875rem;color:var(--on-surface-variant);font-style:italic">
                    No summary was generated for this session. Summary is created when you press <strong>Stop &amp; Summarise</strong>.
                </p>
            </div>`;
    }

    container.innerHTML = html;
}

// ── Confirm delete ────────────────────────────────────────────
function confirmDelete(sessionId) {
    sessionToDelete = sessionId;
    const modal = document.getElementById('delete-modal');
    if (modal) modal.classList.add('visible');
}

// ── Delete session API call ───────────────────────────────────
async function deleteSession(sessionId) {
    try {
        const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        // If we're in list view, remove the card
        const card = document.querySelector(`[data-session-id="${sessionId}"]`);
        if (card) {
            card.style.transform = 'translateX(20px)';
            card.style.opacity   = '0';
            card.style.transition = 'all 0.3s ease';
            setTimeout(() => {
                card.remove();
                _checkEmptyList();
                // Re-load to refresh stats
                loadSessions();
            }, 320);
        }

        // If we're in detail view, go back to list
        const detailView = document.getElementById('session-detail-view');
        if (detailView && detailView.classList.contains('visible')) {
            goBackToList();
            loadSessions();
        }

        showToast('Session permanently deleted', 'success');
    } catch (err) {
        showToast('Failed to delete: ' + err.message, 'error');
    }
}

function _checkEmptyList() {
    const listEl = document.getElementById('sessions-list');
    if (listEl && listEl.children.length === 0) {
        const emptyEl = document.getElementById('sessions-empty');
        if (emptyEl) emptyEl.classList.remove('hidden');
    }
}

// ── Navigation back to list ───────────────────────────────────
function goBackToList() {
    const listView   = document.getElementById('sessions-list-view');
    const detailView = document.getElementById('session-detail-view');
    const titleEl    = document.getElementById('history-page-title');
    const backBtn    = document.getElementById('back-btn');

    if (listView)   listView.style.display = '';
    if (detailView) detailView.classList.remove('visible');
    if (titleEl)    titleEl.textContent = 'Session History';
    if (backBtn)    backBtn.style.display = 'none';
}

// ── Toast (standalone — no UIManager on this page) ────────────
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const icons = { info: 'ℹ', success: '✓', error: '✕', warning: '⚠' };
    const toast  = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <span style="font-size:1rem;" aria-hidden="true">${icons[type] || icons.info}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
    `;
    container.appendChild(toast);

    const dismiss = () => {
        toast.style.animation = 'toast-slide-out 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    };
    setTimeout(dismiss, 4500);
    toast.addEventListener('click', dismiss);
}

// ── Utils ─────────────────────────────────────────────────────
function escapeHtml(text) {
    if (typeof text !== 'string') return String(text || '');
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function formatDate(isoString) {
    if (!isoString) return 'Unknown date';
    try {
        return new Date(isoString).toLocaleString([], {
            weekday: 'short', year: 'numeric', month: 'short',
            day: 'numeric', hour: '2-digit', minute: '2-digit'
        });
    } catch { return String(isoString); }
}

function formatDuration(startIso, endIso) {
    try {
        const diffMs = new Date(endIso) - new Date(startIso);
        if (isNaN(diffMs) || diffMs < 0) return 'Unknown';
        const mins = Math.floor(diffMs / 60000);
        const secs = Math.floor((diffMs % 60000) / 1000);
        if (mins === 0) return `${secs}s`;
        return `${mins}m ${secs}s`;
    } catch { return 'Unknown'; }
}

// ── Boot ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadSessions();

    // Back button
    document.getElementById('back-btn')?.addEventListener('click', goBackToList);

    // Delete modal — confirm
    document.getElementById('delete-confirm-btn')?.addEventListener('click', () => {
        const modal = document.getElementById('delete-modal');
        if (sessionToDelete) {
            deleteSession(sessionToDelete);
            sessionToDelete = null;
        }
        if (modal) modal.classList.remove('visible');
    });

    // Delete modal — cancel
    const cancelHandler = () => {
        sessionToDelete = null;
        const modal = document.getElementById('delete-modal');
        if (modal) modal.classList.remove('visible');
    };
    document.getElementById('delete-cancel')?.addEventListener('click', cancelHandler);
    document.getElementById('delete-cancel-btn')?.addEventListener('click', cancelHandler);

    // Delete modal — backdrop click
    document.getElementById('delete-modal')?.addEventListener('click', e => {
        if (e.target === document.getElementById('delete-modal')) cancelHandler();
    });

    // Keyboard escape to close modals / go back
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            const deleteModal = document.getElementById('delete-modal');
            if (deleteModal?.classList.contains('visible')) {
                cancelHandler();
                return;
            }
            const detailView = document.getElementById('session-detail-view');
            if (detailView?.classList.contains('visible')) {
                goBackToList();
            }
        }
    });
});
