document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    const errorDiv = document.getElementById('error-message');
    const submitBtn = document.getElementById('submit-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.classList.add('hidden');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Authenticating...';

        const payload = {
            username: document.getElementById('username').value,
            password: document.getElementById('password').value,
        };

        try {
            const result = await apiFetch('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            window.location.href = 'dashboard.html';
        } catch (err) {
            let msg = err.message;
            try {
                const parsed = JSON.parse(err.message);
                msg = parsed.detail || parsed.message || parsed.error || msg;
            } catch (e) {}
            errorDiv.textContent = msg;
            errorDiv.classList.remove('hidden');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Sign In';
        }
    });
});