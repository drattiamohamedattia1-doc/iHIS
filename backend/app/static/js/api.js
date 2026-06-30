const API_BASE = 'http://127.0.0.1:5000/api/v1';

const api = {
    token: null,
    setToken(token) { this.token = token; localStorage.setItem('token', token); },
    getToken() { return this.token || localStorage.getItem('token'); },
    clearToken() { this.token = null; localStorage.removeItem('token'); },
    async request(method, endpoint, data = null) {
        const headers = { 'Content-Type': 'application/json' };
        const token = this.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;
        const config = { method, headers };
        if (data) config.body = JSON.stringify(data);
        const response = await fetch(`${API_BASE}${endpoint}`, config);
        const json = await response.json();
        if (!response.ok) {
            if (response.status === 401) { this.clearToken(); window.location.href = '/static/pages/login.html'; }
            throw new Error(json.message || 'Request failed');
        }
        return json;
    },
    get(endpoint) { return this.request('GET', endpoint); },
    post(endpoint, data) { return this.request('POST', endpoint, data); },
    put(endpoint, data) { return this.request('PUT', endpoint, data); },
    delete(endpoint) { return this.request('DELETE', endpoint); }
};