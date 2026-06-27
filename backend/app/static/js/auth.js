async function login(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    try {
        const res = await api.post('/auth/login', { username, password });
        api.setToken(res.access_token);
        // Redirect based on role (from /me)
        const me = await api.get('/auth/me');
        const role = me.user.roles[0]; // assuming single role
        const pages = {
            'patient': '/static/pages/patient.html',
            'doctor': '/static/pages/doctor.html',
            'lab_technician': '/static/pages/lab.html',
            'radiologist': '/static/pages/radiology.html',
            'pharmacist': '/static/pages/pharmacy.html',
            'nurse': '/static/pages/nursing.html',
            'admin': '/static/pages/admin.html',
            'super_admin': '/static/pages/admin.html'
        };
        window.location.href = pages[role] || '/static/pages/patient.html';
    } catch (err) {
        document.getElementById('error').textContent = err.message;
    }
}