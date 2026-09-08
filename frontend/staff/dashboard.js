document.addEventListener('DOMContentLoaded', async () => {
    const userNameEl = document.getElementById('user-name');
    const container = document.getElementById('queue-container');
    const logoutBtn = document.getElementById('logout-btn');
    const errorDiv = document.getElementById('error-message');

    let currentTokenId = null;

    // Verify session
    try {
        const me = await apiFetch('/api/auth/me');
        userNameEl.textContent = `${me.staff.display_name} (${me.staff.role})`;
    } catch (err) {
        window.location.href = 'login.html';
        return;
    }

    logoutBtn.addEventListener('click', async () => {
        try {
            await apiFetch('/api/auth/logout', { method: 'POST' });
        } catch(e) {}
        window.location.href = 'login.html';
    });

    async function fetchQueues() {
        try {
            const data = await apiFetch('/api/staff/queues');
            renderQueues(data.departments);
            errorDiv.classList.add('hidden');
        } catch (err) {
            errorDiv.textContent = 'Failed to load queues. Retrying...';
            errorDiv.classList.remove('hidden');
        }
    }

    function renderQueues(departments) {
        container.innerHTML = '';
        departments.forEach(dept => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h3>${dept.name}</h3>
                <p>Waiting: <strong>${dept.waiting_count}</strong></p>
                <p>Current Token: <strong style="font-size: 1.5rem;">${dept.current_token || '--'}</strong></p>
                <p>Room: ${dept.room}</p>
                <div class="actions">
                    <button class="btn-call" onclick="action('${dept.department_id}', 'next')">Call Next</button>
                    <button class="btn-complete" onclick="actionToken('complete', '${dept.current_token_id || ''}')">Complete</button>
                    <button class="btn-hold" onclick="actionToken('hold', '${dept.current_token_id || ''}')">Hold</button>
                </div>
            `;
            container.appendChild(card);
        });
    }

    window.action = async (deptId, type) => {
        try {
            const result = await apiFetch(`/api/staff/queue/${deptId}/${type}`, { method: 'POST' });
            currentTokenId = result.token_id;
            fetchQueues();
        } catch (err) {
            let msg = err.message;
            try { msg = JSON.parse(msg).detail.message || msg; } catch(e){}
            alert(msg);
        }
    };

    window.actionToken = async (type, tokenId) => {
        const idToUse = tokenId || currentTokenId;
        if (!idToUse) {
            alert("No token currently active to perform this action.");
            return;
        }
        try {
            await apiFetch(`/api/staff/token/${idToUse}/${type}`, { method: 'POST' });
            if (type === 'complete') currentTokenId = null;
            fetchQueues();
        } catch (err) {
            let msg = err.message;
            try { msg = JSON.parse(msg).detail.message || msg; } catch(e){}
            alert(msg);
        }
    };

    fetchQueues();
    setInterval(fetchQueues, 4000);
});