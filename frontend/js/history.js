// TEAM: Frontend
// Session history page logic

/**
 * Fetch and display all sessions
 */
async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        if (!response.ok) {
            throw new Error('Failed to fetch sessions');
        }

        const sessions = await response.json();
        renderSessionsList(sessions);
    } catch (error) {
        console.error('Error loading sessions:', error);
        showError('Failed to load sessions. Please try again.');
    }
}

/**
 * Render sessions list in the UI
 * 
 * @param {Array} sessions - Array of session objects
 */
function renderSessionsList(sessions) {
    const sessionsList = document.getElementById('sessions-list');
    
    if (!sessions || sessions.length === 0) {
        sessionsList.innerHTML = '<p class="no-sessions">No sessions found.</p>';
        return;
    }

    // Sort by created_at descending (most recent first)
    sessions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    sessionsList.innerHTML = '';
    
    sessions.forEach(session => {
        const sessionCard = document.createElement('div');
        sessionCard.className = 'session-card';
        
        const date = new Date(session.created_at).toLocaleString();
        const summaryPreview = session.summary 
            ? (session.summary.title || 'No title')
            : 'No summary available';
        
        sessionCard.innerHTML = `
            <div class="session-header">
                <h3>${summaryPreview}</h3>
                <button class="btn-delete" data-session-id="${session.id}" aria-label="Delete session">🗑️</button>
            </div>
            <p class="session-date">${date}</p>
            <p class="session-preview">${session.summary?.diagnosis || 'Click to view details'}</p>
        `;
        
        // Click to view details
        sessionCard.addEventListener('click', (e) => {
            if (!e.target.classList.contains('btn-delete')) {
                showSessionDetail(session.id);
            }
        });
        
        // Delete button
        const deleteBtn = sessionCard.querySelector('.btn-delete');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteSession(session.id);
        });
        
        sessionsList.appendChild(sessionCard);
    });
}

/**
 * Display session details
 * 
 * @param {string} sessionId - UUID of session to display
 */
async function showSessionDetail(sessionId) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch session details');
        }

        const session = await response.json();
        
        const sessionsList = document.getElementById('sessions-list');
        const sessionDetail = document.getElementById('session-detail');
        const sessionDetailContent = document.getElementById('session-detail-content');
        
        // Hide list, show detail
        sessionsList.classList.add('hidden');
        sessionDetail.classList.remove('hidden');
        
        // Render session details
        let html = `
            <div class="session-full">
                <h2>${session.summary?.title || 'Session Details'}</h2>
                <p class="session-date">${new Date(session.created_at).toLocaleString()}</p>
                
                <section class="detail-section">
                    <h3>Transcript</h3>
                    <div class="transcript-text">${session.transcript || 'No transcript available'}</div>
                </section>
        `;
        
        // Display simplifications
        if (session.simplifications && session.simplifications.length > 0) {
            html += `
                <section class="detail-section">
                    <h3>Simplified Terms</h3>
                    <div class="simplifications-list">
            `;
            session.simplifications.forEach(simp => {
                html += `
                    <div class="term-item">
                        <span class="term-highlight">${simp.term}</span>: ${simp.explanation}
                    </div>
                `;
            });
            html += `</div></section>`;
        }
        
        // Display summary
        if (session.summary) {
            html += `
                <section class="detail-section">
                    <h3>Visit Summary</h3>
                    <div class="summary-content">
            `;
            const fields = [
                { label: 'Diagnosis', value: session.summary.diagnosis },
                { label: 'Medications', value: session.summary.medications },
                { label: 'Instructions', value: session.summary.instructions },
                { label: 'Follow-up', value: session.summary.follow_up },
                { label: 'Key Points', value: session.summary.key_points }
            ];
            
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
            html += `</div></section>`;
        }
        
        html += `</div>`;
        sessionDetailContent.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading session details:', error);
        showError('Failed to load session details. Please try again.');
    }
}

/**
 * Delete a session with confirmation
 * 
 * @param {string} sessionId - UUID of session to delete
 */
async function deleteSession(sessionId) {
    const modal = document.getElementById('delete-modal');
    const confirmBtn = document.getElementById('confirm-delete');
    const cancelBtn = document.getElementById('cancel-delete');
    
    // Show confirmation modal
    modal.classList.remove('hidden');
    
    // Handle confirmation
    const handleConfirm = async () => {
        try {
            const response = await fetch(`/api/sessions/${sessionId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete session');
            }
            
            // Remove from UI immediately
            modal.classList.add('hidden');
            loadSessions(); // Reload the list
            
        } catch (error) {
            console.error('Error deleting session:', error);
            showError('Failed to delete session. Please try again.');
            modal.classList.add('hidden');
        }
        
        cleanup();
    };
    
    const handleCancel = () => {
        modal.classList.add('hidden');
        cleanup();
    };
    
    const cleanup = () => {
        confirmBtn.removeEventListener('click', handleConfirm);
        cancelBtn.removeEventListener('click', handleCancel);
    };
    
    confirmBtn.addEventListener('click', handleConfirm);
    cancelBtn.addEventListener('click', handleCancel);
}

/**
 * Show error message
 * 
 * @param {string} message - Error message to display
 */
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-notification';
    errorDiv.textContent = message;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.style.opacity = '0';
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 300);
    }, 5000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadSessions();
    
    // Set up back to list button
    const backBtn = document.getElementById('back-to-list');
    backBtn.addEventListener('click', () => {
        document.getElementById('session-detail').classList.add('hidden');
        document.getElementById('sessions-list').classList.remove('hidden');
    });
});
