document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const statusId = params.get('id');
    const errorDiv = document.getElementById('error-message');

    if (!statusId) {
        showError("Invalid status link.");
        return;
    }

    async function fetchStatus() {
        try {
            const data = await apiFetch(`/api/status/${statusId}`);
            renderStatus(data);
            errorDiv.classList.add('hidden');
        } catch (err) {
            showError("Failed to update status. Retrying...");
        }
    }

    function renderStatus(data) {
        document.getElementById('my-token').textContent = data.display_token;
        document.getElementById('dept-name').textContent = data.department;
        document.getElementById('room-name').textContent = data.room || '-';
        document.getElementById('current-token').textContent = data.current_token || '--';
        document.getElementById('patients-ahead').textContent = data.patients_ahead;
        document.getElementById('est-wait').textContent = data.estimated_wait_minutes + ' min';

        const statusEl = document.getElementById('my-status');
        statusEl.textContent = data.status;
        statusEl.className = data.status === 'SERVING' ? 'status-serving' : 'status-waiting';
    }

    function showError(msg) {
        errorDiv.textContent = msg;
        errorDiv.classList.remove('hidden');
    }

    // Initial fetch and poll
    fetchStatus();
    setInterval(fetchStatus, 4000); // 4 second polling
});