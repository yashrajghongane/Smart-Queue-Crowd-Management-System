document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const deptId = params.get('dept');
    const errorDiv = document.getElementById('error-message');

    if (!deptId) {
        document.getElementById('dept-name').textContent = "ERROR: No department specified";
        return;
    }

    async function fetchDisplay() {
        try {
            const data = await apiFetch(`/api/display/${deptId}`);
            renderDisplay(data);
            errorDiv.style.display = 'none';
        } catch (err) {
            errorDiv.style.display = 'block';
        }
    }

    function renderDisplay(data) {
        document.getElementById('dept-name').textContent = data.department.toUpperCase();
        document.getElementById('current-token').textContent = data.current_token || '--';
        document.getElementById('room-name').textContent = data.room || '-';
        document.getElementById('next-token').textContent = data.next_token || '--';
    }

    // Initial fetch and poll
    fetchDisplay();
    setInterval(fetchDisplay, 3000); // 3 second polling
});