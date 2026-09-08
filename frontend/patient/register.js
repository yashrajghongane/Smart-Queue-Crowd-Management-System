document.addEventListener('DOMContentLoaded', async () => {
    const deptSelect = document.getElementById('department');
    const form = document.getElementById('register-form');
    const errorDiv = document.getElementById('error-message');
    const submitBtn = document.getElementById('submit-btn');

    // Load departments
    try {
        const data = await apiFetch('/api/departments');
        deptSelect.innerHTML = '<option value="">Select Department</option>';
        data.departments.forEach(dept => {
            const opt = document.createElement('option');
            opt.value = dept.id;
            opt.textContent = dept.name;
            deptSelect.appendChild(opt);
        });
    } catch (err) {
        showError("Failed to load departments.");
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.classList.add('hidden');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Registering...';

        const payload = {
            name: document.getElementById('name').value,
            date_of_birth: document.getElementById('dob').value,
            mobile: document.getElementById('mobile').value,
            patient_type: document.getElementById('patient-type').value,
            department_id: document.getElementById('department').value,
            registration_location_id: "loc_opaque_id", // Mocked for now
        };

        try {
            const result = await apiFetch('/api/register', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            showSuccess(result);
        } catch (err) {
            let msg = err.message;
            try {
                const parsed = JSON.parse(err.message);
                msg = parsed.message || parsed.error || msg;
                // Handle duplicate active visit gracefully if backend returns the active token
                if (parsed.error === 'ACTIVE_VISIT_EXISTS' && parsed.display_token) {
                    showSuccess(parsed);
                    return;
                }
            } catch (e) {}
            showError(msg);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Join Queue';
        }
    });

    function showError(msg) {
        errorDiv.textContent = msg;
        errorDiv.classList.remove('hidden');
    }

    function showSuccess(data) {
        document.getElementById('registration-container').classList.add('hidden');
        document.getElementById('success-container').classList.remove('hidden');

        document.getElementById('success-token').textContent = data.display_token;
        document.getElementById('success-dept').textContent = data.department;
        document.getElementById('success-room').textContent = data.room;
        document.getElementById('status-link').href = data.status_url;
    }
});