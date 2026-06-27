let currentUser = null;
let currentSection = 'home';
let notificationsList = [];

// تعريف القوائم لكل دور
const menuConfig = {
    super_admin: ['home', 'patients', 'doctors', 'appointments', 'laboratory', 'radiology', 'pharmacy', 'nursing', 'dental', 'admin', 'reports'],
    admin: ['home', 'patients', 'doctors', 'appointments', 'laboratory', 'radiology', 'pharmacy', 'nursing', 'dental', 'admin', 'reports'],
    doctor: ['home', 'patients', 'appointments', 'laboratory', 'radiology', 'pharmacy', 'nursing', 'dental', 'telemedicine'],
    patient: ['home', 'appointments', 'laboratory', 'radiology', 'pharmacy', 'telemedicine'],
    nurse: ['home', 'patients', 'nursing'],
    lab_technician: ['home', 'laboratory'],
    radiologist: ['home', 'radiology'],
    pharmacist: ['home', 'pharmacy'],
    receptionist: ['home', 'appointments', 'patients']
};

const menuLabels = {
    home: { icon: 'fa-tachometer-alt', text: 'Dashboard' },
    patients: { icon: 'fa-procedures', text: 'Patients' },
    doctors: { icon: 'fa-user-md', text: 'Doctors' },
    appointments: { icon: 'fa-calendar-alt', text: 'Appointments' },
    laboratory: { icon: 'fa-flask', text: 'Laboratory' },
    radiology: { icon: 'fa-x-ray', text: 'Radiology' },
    pharmacy: { icon: 'fa-prescription-bottle-alt', text: 'Pharmacy' },
    nursing: { icon: 'fa-user-nurse', text: 'Nursing' },
    dental: { icon: 'fa-tooth', text: 'Dental' },
    admin: { icon: 'fa-shield-alt', text: 'Admin' },
    telemedicine: { icon: 'fa-video', text: 'Telemedicine' },
    reports: { icon: 'fa-chart-bar', text: 'Reports' }
};

document.addEventListener('DOMContentLoaded', async () => {
    if (!api.getToken()) { window.location.href = '/static/pages/login.html'; return; }
    try {
        const me = await api.get('/auth/me');
        currentUser = me.user;
        updateUserUI();
        buildSidebar(currentUser.role);
        navigateTo('home');
        document.getElementById('sidebarCollapse').addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('active');
        });
        document.getElementById('darkModeToggle').addEventListener('click', () => {
            document.body.classList.toggle('dark');
        });
    } catch (e) { window.location.href = '/static/pages/login.html'; }
});

function updateUserUI() {
    document.getElementById('userNameTop').textContent = currentUser.full_name;
    document.getElementById('sidebarUser').textContent = currentUser.full_name;
    document.getElementById('sidebarRoleText').textContent = currentUser.role;
    document.getElementById('sidebarRole').textContent = currentUser.role;
    document.getElementById('userInitials').textContent = currentUser.full_name.charAt(0).toUpperCase();
}

function buildSidebar(role) {
    const menu = document.getElementById('sidebarMenu');
    const sections = menuConfig[role] || ['home'];
    let html = '';
    sections.forEach(section => {
        const label = menuLabels[section] || { icon: 'fa-circle', text: section };
        html += `<li><a href="#" onclick="navigateTo('${section}'); return false;" data-section="${section}">
                    <i class="fas ${label.icon}"></i> ${label.text}
                </a></li>`;
    });
    menu.innerHTML = html;
}

async function navigateTo(section) {
    currentSection = section;
    document.querySelectorAll('#sidebarMenu li a').forEach(a => a.classList.remove('active'));
    document.querySelector(`[data-section="${section}"]`)?.classList.add('active');
    const content = document.getElementById('dynamicContent');
    switch(section) {
        case 'home': content.innerHTML = await loadHome(); break;
        case 'patients': content.innerHTML = await loadPatients(); break;
        case 'appointments': content.innerHTML = await loadAppointments(); break;
        case 'laboratory': content.innerHTML = await loadLab(); break;
        case 'radiology': content.innerHTML = await loadRad(); break;
        case 'pharmacy': content.innerHTML = await loadPharmacy(); break;
        case 'nursing': content.innerHTML = await loadNursing(); break;
        case 'dental': content.innerHTML = await loadDental(); break;
        case 'admin': content.innerHTML = await loadAdmin(); break;
        case 'telemedicine': content.innerHTML = await loadTelemedicine(); break;
        case 'reports': content.innerHTML = await loadAdminReports(); break;
        default: content.innerHTML = '<h3>Section not found</h3>';
    }
}

// ---------- HOME ----------
async function loadHome() {
    const patients = await api.get('/patients');
    const doctors = await api.get('/doctors');
    const appts = await api.get('/appointments');
    const totalPatients = patients.patients.length;
    const totalDoctors = doctors.doctors.length;
    const pendingAppts = appts.appointments.filter(a => a.status === 'scheduled').length;
    const revenue = totalPatients * 150;

    // تأخير تنفيذ الرسم البياني بعد إدراج DOM
    setTimeout(() => {
        const chartEl = document.querySelector("#patientChart");
        if (chartEl && typeof ApexCharts !== 'undefined') {
            new ApexCharts(chartEl, {
                chart: { type: 'bar', height: 300 },
                series: [{ name: 'Patients', data: [totalPatients, 0, 0, 0] }],
                xaxis: { categories: ['This Week', 'Last Week', 'This Month', 'Last Month'] },
                colors: ['#3b82f6']
            }).render();
        }
    }, 100);

    return `
        <div class="row">
            <div class="col-md-3" onclick="showDetailSection('patients')" style="cursor:pointer;">
                <div class="stat-card"><i class="fas fa-procedures text-primary"></i><h3>${totalPatients}</h3><p>Total Patients</p></div>
            </div>
            <div class="col-md-3" onclick="showDetailSection('doctors')" style="cursor:pointer;">
                <div class="stat-card"><i class="fas fa-user-md text-success"></i><h3>${totalDoctors}</h3><p>Active Doctors</p></div>
            </div>
            <div class="col-md-3" onclick="showDetailSection('pendingAppointments')" style="cursor:pointer;">
                <div class="stat-card"><i class="fas fa-calendar-alt text-warning"></i><h3>${pendingAppts}</h3><p>Pending Appointments</p></div>
            </div>
            <div class="col-md-3">
                <div class="stat-card"><i class="fas fa-dollar-sign text-info"></i><h3>$${revenue.toLocaleString()}</h3><p>Est. Revenue</p></div>
            </div>
        </div>
        <div class="row mt-4">
            <div class="col-md-8"><div class="card p-3"><div id="patientChart" style="height:300px;"></div></div></div>
            <div class="col-md-4"><div class="card p-3"><h5>Quick Actions</h5>
                <button class="btn btn-primary w-100 mb-2" onclick="showNewPatientForm()"><i class="fas fa-plus me-2"></i>New Patient</button>
                <button class="btn btn-success w-100 mb-2" onclick="showBookAppointmentForm()"><i class="fas fa-calendar-plus me-2"></i>Book Appointment</button>
                <button class="btn btn-warning w-100" onclick="showPrescriptionForm()"><i class="fas fa-prescription me-2"></i>Write Prescription</button>
            </div></div>
        </div>
        <div id="homeDetailContainer" class="mt-4"></div>
    `;
}

async function showDetailSection(type) {
    const container = document.getElementById('homeDetailContainer');
    switch(type) {
        case 'patients': container.innerHTML = await loadPatientsList(); break;
        case 'doctors': container.innerHTML = await loadDoctorsList(); break;
        case 'pendingAppointments': container.innerHTML = await loadPendingAppointmentsList(); break;
    }
}

async function loadPatientsList() {
    const res = await api.get('/patients');
    let rows = res.patients.map(p => `<tr><td>${p.patient_id}</td><td>${p.user_name}</td><td>${p.blood_type||'-'}</td><td>${p.age||'-'}</td><td>${p.status}</td><td><button class="btn btn-sm btn-outline-info" onclick="viewPatientDetails(${p.id})">View</button></td></tr>`).join('');
    return `<div class="card p-3"><h5>Patients (${res.patients.length})</h5><table class="table"><thead><tr><th>MRN</th><th>Name</th><th>Blood</th><th>Age</th><th>Status</th><th>Actions</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

async function loadDoctorsList() {
    const res = await api.get('/doctors');
    let rows = res.doctors.map(d => `<tr><td>${d.name}</td><td>${d.specialty}</td><td>${d.experience_years || '-'} yrs</td><td>${d.is_available ? '<span class="badge bg-success">Available</span>' : '<span class="badge bg-secondary">Unavailable</span>'}</td></tr>`).join('');
    return `<div class="card p-3"><h5>Doctors (${res.doctors.length})</h5><table class="table"><thead><tr><th>Name</th><th>Specialty</th><th>Experience</th><th>Availability</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

async function loadPendingAppointmentsList() {
    const res = await api.get('/appointments');
    const pending = res.appointments.filter(a => a.status === 'scheduled');
    let rows = pending.map(a => `<tr><td>${a.id}</td><td>${a.patient_id}</td><td>${a.doctor_id}</td><td>${a.date} ${a.time}</td><td>${a.reason||''}</td><td>
        <button class="btn btn-sm btn-outline-success me-1" onclick="confirmAppointment(${a.id})">Confirm</button>
        <button class="btn btn-sm btn-outline-danger" onclick="cancelAppointment(${a.id})">Cancel</button>
    </td></tr>`).join('');
    return `<div class="card p-3"><h5>Pending Appointments (${pending.length})</h5><table class="table"><thead><tr><th>ID</th><th>Patient</th><th>Doctor</th><th>Date/Time</th><th>Reason</th><th>Actions</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

async function confirmAppointment(id) {
    await api.put(`/appointments/${id}`, { status: 'confirmed' });
    addNotification(`Appointment #${id} confirmed`);
    showDetailSection('pendingAppointments');
}
async function cancelAppointment(id) {
    await api.put(`/appointments/${id}`, { status: 'cancelled' });
    addNotification(`Appointment #${id} cancelled`);
    showDetailSection('pendingAppointments');
}

// ---------- PATIENTS ----------
async function loadPatients() {
    const res = await api.get('/patients');
    let rows = res.patients.map(p => `<tr><td>${p.patient_id}</td><td>${p.user_name}</td><td>${p.blood_type||'-'}</td><td>${p.age||'-'}</td><td>${p.status}</td><td><button class="btn btn-sm btn-outline-primary" onclick="viewPatientDetails(${p.id})"><i class="fas fa-edit"></i></button></td></tr>`).join('');
    return `<div class="card p-3"><h5>Patient List</h5><input type="text" class="form-control mb-3" placeholder="Search patients..." onkeyup="searchTable(this, 'patientsTable')"><table class="table" id="patientsTable"><thead><tr><th>MRN</th><th>Name</th><th>Blood</th><th>Age</th><th>Status</th><th>Actions</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

function searchTable(input, tableId) {
    const filter = input.value.toUpperCase();
    document.querySelectorAll(`#${tableId} tbody tr`).forEach(row => {
        row.style.display = row.textContent.toUpperCase().includes(filter) ? '' : 'none';
    });
}

async function viewPatientDetails(patientId) {
    const patient = await api.get(`/patients/${patientId}`);
    const prescriptions = await api.get(`/pharmacy/prescriptions?patient_id=${patientId}`);
    const labOrders = await api.get(`/laboratory/orders?patient_id=${patientId}`);
    const radOrders = await api.get(`/radiology/orders?patient_id=${patientId}`);
    const p = patient.patient;
    const rxList = prescriptions.prescriptions.map(r => `<li class="list-group-item"><strong>${r.drug_code}</strong> - ${r.dosage}, ${r.frequency}, ${r.duration} (${r.status})</li>`).join('');
    const labList = labOrders.orders.map(o => `<li class="list-group-item"><strong>${o.test_code}</strong> - ${o.status}</li>`).join('');
    const radList = radOrders.orders.map(o => `<li class="list-group-item"><strong>${o.modality}</strong> - ${o.body_part} (${o.status})</li>`).join('');
    openModal('Patient Details', `<h6>${p.user_name} (MRN: ${p.patient_id})</h6><p>Blood: ${p.blood_type||'N/A'} | Age: ${p.age||'N/A'}</p><hr><h6>Prescriptions</h6><ul class="list-group mb-2">${rxList||'<li class="list-group-item text-muted">None</li>'}</ul><h6>Lab Orders</h6><ul class="list-group mb-2">${labList||'<li class="list-group-item text-muted">None</li>'}</ul><h6>Radiology Orders</h6><ul class="list-group">${radList||'<li class="list-group-item text-muted">None</li>'}</ul>`);
}

// ---------- APPOINTMENTS (مع زر التقييم) ----------
async function loadAppointments() {
    let res;
    if (currentUser.patient_id) res = await api.get(`/appointments?patient_id=${currentUser.patient_id}`);
    else if (currentUser.doctor_id) res = await api.get(`/appointments?doctor_id=${currentUser.doctor_id}`);
    else res = await api.get('/appointments');
    let rows = res.appointments.map(a => `
        <tr>
            <td>${a.id}</td>
            <td>${a.patient_id}</td>
            <td>${a.doctor_id}</td>
            <td>${a.date} ${a.time}</td>
            <td><span class="badge bg-${a.status==='scheduled'?'warning':'success'}">${a.status}</span></td>
            <td>
                ${a.status === 'completed' ? `<button class="btn btn-sm btn-outline-warning me-1" onclick="showRateDoctor(${a.doctor_id}, ${a.patient_id})">Rate</button>` : ''}
                <button class="btn btn-sm btn-outline-danger" onclick="cancelAppointment(${a.id})"><i class="fas fa-times"></i></button>
            </td>
        </tr>
    `).join('');
    return `<div class="card p-3"><h5>Appointments</h5><table class="table"><thead><tr><th>ID</th><th>Patient</th><th>Doctor</th><th>Date/Time</th><th>Status</th><th>Action</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

// ---------- LABORATORY ----------
async function loadLab() {
    const orders = await api.get('/laboratory/orders');
    const pending = orders.orders.filter(o => o.status !== 'completed');
    const rows = pending.map(o => `<tr><td>${o.id}</td><td>${o.patient_id}</td><td>${o.test_code}</td><td>${o.status}</td><td><button class="btn btn-sm btn-primary" onclick="processLabOrder(${o.id})">Process</button></td></tr>`).join('');
    return `<div class="card p-3"><h5>Pending Orders</h5><table class="table"><thead><tr><th>ID</th><th>Patient</th><th>Test</th><th>Status</th><th>Action</th></tr></thead><tbody>${rows}</tbody></table><div id="labForm"></div></div>`;
}
window.processLabOrder = async function(id) {
    document.getElementById('labForm').innerHTML = `
        <div class="card p-3 mt-3"><h5>Process Order #${id}</h5>
            <select id="labStatus" class="form-select mb-2"><option value="collected">Collected</option><option value="processing">Processing</option><option value="completed">Completed</option></select>
            <div id="resultFields" style="display:none;"><input type="text" id="resultValue" class="form-control mb-2" placeholder="Value"><input type="text" id="resultUnit" class="form-control mb-2" placeholder="Unit"></div>
            <button class="btn btn-success" onclick="submitLabResult(${id})">Submit</button></div>`;
    document.getElementById('labStatus').addEventListener('change', function(){ document.getElementById('resultFields').style.display = this.value === 'completed' ? 'block' : 'none'; });
}
window.submitLabResult = async function(id) {
    const status = document.getElementById('labStatus').value;
    await api.put(`/laboratory/orders/${id}/status`, { status });
    if (status === 'completed') {
        await api.post('/laboratory/results', { order_id: id, test_code: '', value: document.getElementById('resultValue').value, unit: document.getElementById('resultUnit').value, is_abnormal: false, notes: '' });
    }
    addNotification(`Lab order #${id} processed`);
    navigateTo('laboratory');
}

// ---------- RADIOLOGY ----------
async function loadRad() {
    const orders = await api.get('/radiology/orders');
    const pending = orders.orders.filter(o => o.status !== 'reported');
    const rows = pending.map(o => `<tr><td>${o.id}</td><td>${o.patient_id}</td><td>${o.modality}</td><td>${o.status}</td><td><button class="btn btn-sm btn-primary" onclick="writeReport(${o.id})">Report</button></td></tr>`).join('');
    return `<div class="card p-3"><h5>Pending Orders</h5><table class="table"><thead><tr><th>ID</th><th>Patient</th><th>Modality</th><th>Status</th><th>Action</th></tr></thead><tbody>${rows}</tbody></table><div id="radForm"></div></div>`;
}
window.writeReport = function(id) {
    document.getElementById('radForm').innerHTML = `<div class="card p-3 mt-3"><h5>Report #${id}</h5><textarea id="findings" class="form-control mb-2" placeholder="Findings"></textarea><textarea id="impression" class="form-control mb-2" placeholder="Impression"></textarea><button class="btn btn-primary" onclick="submitRadReport(${id})">Submit</button></div>`;
}
window.submitRadReport = async function(id) {
    await api.post('/radiology/reports', { order_id: id, findings: document.getElementById('findings').value, impression: document.getElementById('impression').value, conclusion: '', is_critical: false });
    await api.put(`/radiology/orders/${id}/status`, { status: 'reported' });
    addNotification(`Radiology report #${id} submitted`);
    navigateTo('radiology');
}

// ---------- PHARMACY ----------
async function loadPharmacy() {
    const rx = await api.get('/pharmacy/prescriptions?status=pending');
    const inv = await api.get('/pharmacy/inventory');
    const rows = rx.prescriptions.map(p => `<tr><td>${p.id}</td><td>${p.patient_id}</td><td>${p.drug_code}</td><td>${p.dosage}</td><td><button class="btn btn-sm btn-success" onclick="dispenseRx(${p.id},'${p.drug_code}')">Dispense</button></td></tr>`).join('');
    const invItems = inv.inventory.map(i => `<li class="list-group-item d-flex justify-content-between">${i.name} <span class="badge bg-${i.stock<50?'warning':'success'}">${i.stock}</span></li>`).join('');
    return `<div class="row"><div class="col-md-6"><div class="card p-3"><h5>Prescriptions</h5><table class="table"><thead><tr><th>ID</th><th>Patient</th><th>Drug</th><th>Dosage</th><th>Action</th></tr></thead><tbody>${rows}</tbody></table></div></div><div class="col-md-6"><div class="card p-3"><h5>Inventory</h5><ul class="list-group">${invItems}</ul></div></div></div>`;
}
window.dispenseRx = async function(rxId, drugCode) {
    const qty = prompt("Quantity:");
    if (!qty) return;
    const res = await api.post('/pharmacy/dispense', { drug_code: drugCode, quantity: parseInt(qty) });
    if (res.success) {
        await api.put(`/pharmacy/prescriptions/${rxId}/status`, { status: 'dispensed' });
        addNotification(`Prescription #${rxId} dispensed`);
        navigateTo('pharmacy');
    } else alert(res.message);
}

// ---------- NURSING ----------
async function loadNursing() {
    const tasks = await api.get('/nursing/tasks');
    const rows = tasks.tasks.map(t => `<tr><td>${t.task}</td><td>${t.patient_id}</td><td>${t.status}</td></tr>`).join('');
    return `<div class="row"><div class="col-md-6"><div class="card p-3"><h5>Tasks</h5><table class="table"><thead><tr><th>Task</th><th>Patient</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table></div></div><div class="col-md-6"><div class="card p-3"><h5>Record Vitals</h5><input type="number" id="vitalPatientId" class="form-control mb-2" placeholder="Patient ID"><input type="text" id="temp" class="form-control mb-2" placeholder="Temp"><input type="text" id="hr" class="form-control mb-2" placeholder="HR"><input type="text" id="bp" class="form-control mb-2" placeholder="BP (sys/dia)"><input type="text" id="spo2" class="form-control mb-2" placeholder="SpO2"><button class="btn btn-primary" onclick="recordVitalsNurse()">Save</button></div></div></div>`;
}
window.recordVitalsNurse = async function() {
    const pid = document.getElementById('vitalPatientId').value;
    const bp = document.getElementById('bp').value.split('/');
    await api.post(`/patients/${pid}/vitals`, { patient_id: parseInt(pid), temperature: document.getElementById('temp').value, heart_rate: document.getElementById('hr').value, bp_systolic: bp[0]||'', bp_diastolic: bp[1]||'', spo2: document.getElementById('spo2').value });
    addNotification(`Vitals recorded for patient #${pid}`);
}

// ---------- DENTAL ----------
async function loadDental() {
    const chart = await api.get('/dental/chart/1');
    const procs = await api.get('/dental/procedures');
    const teeth = chart.records.map(r => `<li class="list-group-item">Tooth ${r.tooth}: ${r.condition} (${r.treatment||''})</li>`).join('');
    const procItems = procs.procedures.map(p => `<li class="list-group-item">${p.name} - $${p.cost}</li>`).join('');
    return `<div class="row"><div class="col-md-6"><div class="card p-3"><h5>Chart</h5><ul class="list-group">${teeth}</ul></div></div><div class="col-md-6"><div class="card p-3"><h5>Procedures</h5><ul class="list-group">${procItems}</ul></div></div></div>`;
}

// ---------- ADMIN ----------
async function loadAdmin() {
    const health = await (await fetch('/api/health')).json();
    return `<div class="card p-3"><h5>System Info</h5><p>Tables: ${health.database.tables.join(', ')}</p><p>Users: ${health.counts.users} | Roles: ${health.counts.roles}</p></div>`;
}

// ---------- TELEMEDICINE ----------
async function loadTelemedicine() {
    // استخدام innerHTML مع تأخير لضمان تنفيذ السكربت الداخلي
    const container = document.createElement('div');
    container.innerHTML = `
        <div class="card p-3">
            <h5><i class="fas fa-video me-2"></i>Video Consultation</h5>
            <p>Schedule a virtual visit with your doctor.</p>
            <form id="teleForm">
                <select id="teleDoctor" class="form-select mb-2">
                    <option value="">Select Doctor</option>
                </select>
                <input type="date" id="teleDate" class="form-control mb-2" required>
                <input type="time" id="teleTime" class="form-control mb-2" required>
                <button type="submit" class="btn btn-primary"><i class="fas fa-video me-2"></i>Book Video Call</button>
            </form>
            <div id="teleLink" class="mt-3"></div>
        </div>
    `;
    // تحميل الأطباء وربط الحدث
    setTimeout(async () => {
        const doctors = await api.get('/doctors');
        const sel = document.getElementById('teleDoctor');
        if (sel) sel.innerHTML = doctors.doctors.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
        document.getElementById('teleForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const doctorId = document.getElementById('teleDoctor').value;
            const date = document.getElementById('teleDate').value;
            const time = document.getElementById('teleTime').value;
            if (!doctorId || !date || !time) return alert('Please fill all fields');
            const link = `https://telemed.ihis.com/room/${doctorId}_${Date.now()}`;
            document.getElementById('teleLink').innerHTML = `<div class="alert alert-success">Consultation booked! <a href="${link}" target="_blank">Join Video Call</a></div>`;
            addNotification(`Teleconsultation booked for ${date} ${time}`);
        });
    }, 50);
    return container.innerHTML;
}

// ---------- ADMIN REPORTS ----------
async function loadAdminReports() {
    const patients = await api.get('/patients');
    const doctors = await api.get('/doctors');
    const appts = await api.get('/appointments');
    const totalPatients = patients.patients.length;
    const totalDoctors = doctors.doctors.length;
    const scheduledAppts = appts.appointments.filter(a => a.status === 'scheduled').length;
    const completedAppts = appts.appointments.filter(a => a.status === 'completed').length;
    const revenue = completedAppts * 150;

    // تأجيل إرفاق حدث التصدير
    setTimeout(() => {
        const exportBtn = document.getElementById('exportReportBtn');
        if (exportBtn) {
            exportBtn.onclick = () => {
                const csv = `Metric,Value\nTotal Patients,${totalPatients}\nActive Doctors,${totalDoctors}\nScheduled Appointments,${scheduledAppts}\nRevenue,$${revenue}`;
                const blob = new Blob([csv], {type: 'text/csv'});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'weekly_report.csv';
                a.click();
            };
        }
    }, 100);

    return `
        <div class="card p-3">
            <h5><i class="fas fa-chart-bar me-2"></i>Weekly Report</h5>
            <div class="row">
                <div class="col-md-3"><div class="stat-card"><i class="fas fa-procedures text-primary"></i><h3>${totalPatients}</h3><p>Total Patients</p></div></div>
                <div class="col-md-3"><div class="stat-card"><i class="fas fa-user-md text-success"></i><h3>${totalDoctors}</h3><p>Active Doctors</p></div></div>
                <div class="col-md-3"><div class="stat-card"><i class="fas fa-calendar-alt text-warning"></i><h3>${scheduledAppts}</h3><p>Scheduled Appointments</p></div></div>
                <div class="col-md-3"><div class="stat-card"><i class="fas fa-dollar-sign text-info"></i><h3>$${revenue.toLocaleString()}</h3><p>Est. Revenue</p></div></div>
            </div>
            <button id="exportReportBtn" class="btn btn-outline-primary mt-3"><i class="fas fa-download me-2"></i>Export CSV</button>
        </div>
    `;
}

// ---------- RATE DOCTOR ----------
function showRateDoctor(doctorId, patientId) {
    const html = `
        <h5>Rate Your Doctor</h5>
        <div class="rating">
            <input type="radio" id="star5" name="rating" value="5"><label for="star5">★</label>
            <input type="radio" id="star4" name="rating" value="4"><label for="star4">★</label>
            <input type="radio" id="star3" name="rating" value="3"><label for="star3">★</label>
            <input type="radio" id="star2" name="rating" value="2"><label for="star2">★</label>
            <input type="radio" id="star1" name="rating" value="1"><label for="star1">★</label>
        </div>
        <textarea id="ratingComment" class="form-control mt-2" placeholder="Comment (optional)"></textarea>
        <button class="btn btn-primary mt-2" onclick="submitRating(${doctorId}, ${patientId})">Submit Rating</button>
    `;
    openModal('Rate Doctor', html);
}

async function submitRating(doctorId, patientId) {
    const rating = document.querySelector('input[name="rating"]:checked')?.value;
    const comment = document.getElementById('ratingComment')?.value;
    if (!rating) { alert('Please select a rating'); return; }
    addNotification(`Rating ${rating} stars submitted for doctor #${doctorId}`);
    bootstrap.Modal.getInstance(document.getElementById('genericModal')).hide();
}

// ---------- MEDICATION REMINDERS (Patient) ----------
async function loadMedicationReminders(patientId) {
    const prescriptions = await api.get(`/pharmacy/prescriptions?patient_id=${patientId}`);
    const activeRx = prescriptions.prescriptions.filter(p => p.status !== 'dispensed');
    let html = '';
    activeRx.forEach(rx => {
        html += `<li class="list-group-item d-flex justify-content-between">
            ${rx.drug_code} - ${rx.dosage}, ${rx.frequency}
            <button class="btn btn-sm btn-outline-info" onclick="remindMedication('${rx.drug_code}', '${rx.frequency}')">Remind Me</button>
        </li>`;
    });
    return `
        <div class="card p-3 mt-3">
            <h5><i class="fas fa-clock me-2"></i>Medication Reminders</h5>
            <button class="btn btn-sm btn-outline-primary mb-2" onclick="enableNotifications()">Enable Browser Notifications</button>
            <ul class="list-group">${html || '<li class="list-group-item text-muted">No active medications</li>'}</ul>
        </div>`;
}

function enableNotifications() {
    if (!("Notification" in window)) {
        alert("This browser does not support desktop notifications");
        return;
    }
    Notification.requestPermission().then(perm => {
        if (perm === "granted") {
            addNotification("Notifications enabled! You will be reminded for medications.");
            new Notification("iHIS Reminder", { body: "Don't forget to take your medication!" });
        }
    });
}

function remindMedication(drug, frequency) {
    if (Notification.permission === "granted") {
        new Notification("Medication Reminder", { body: `Time to take ${drug} (${frequency})` });
    } else {
        alert(`Reminder set for ${drug} (${frequency})`);
    }
}

// ---------- CHATBOT ----------
function toggleChatbot() {
    const win = document.getElementById('chatbot-window');
    win.style.display = win.style.display === 'none' ? 'block' : 'none';
}

function sendChatMessage() {
    const input = document.getElementById('chatbot-input');
    const msg = input.value.trim().toLowerCase();
    if (!msg) return;
    const messagesDiv = document.getElementById('chatbot-messages');
    messagesDiv.innerHTML += `<div class="text-end text-primary"><strong>You:</strong> ${msg}</div>`;
    input.value = '';

    let reply = '';
    if (msg.includes('appointment') || msg.includes('book')) {
        reply = 'You can book an appointment using the "Quick Actions" section on the Dashboard.';
    } else if (msg.includes('prescription') || msg.includes('drug')) {
        reply = 'Your doctor can write a prescription. Pharmacists can dispense them from the Pharmacy section.';
    } else if (msg.includes('lab') || msg.includes('test')) {
        reply = 'Lab tests are ordered by doctors. You can view your results in the Laboratory section.';
    } else if (msg.includes('hello') || msg.includes('hi')) {
        reply = 'Hello! I am your medical assistant. How can I help?';
    } else {
        reply = 'I am not sure about that. Please contact your healthcare provider.';
    }
    messagesDiv.innerHTML += `<div class="text-success"><strong>Bot:</strong> ${reply}</div>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// ---------- MODAL & NOTIFICATIONS ----------
function openModal(title, bodyHTML = '') {
    document.getElementById('modalTitle').innerHTML = title;
    document.getElementById('modalBody').innerHTML = bodyHTML;
    new bootstrap.Modal(document.getElementById('genericModal')).show();
}

function addNotification(message) {
    const now = new Date();
    notificationsList.unshift({ text: message, time: now.toLocaleTimeString() });
    updateNotifications();
}

function updateNotifications() {
    const badge = document.getElementById('notificationCount');
    const list = document.getElementById('notificationList');
    if (!badge || !list) return;
    badge.textContent = notificationsList.length;
    if (notificationsList.length === 0) {
        list.innerHTML = '<a class="dropdown-item text-muted">No notifications</a>';
        return;
    }
    list.innerHTML = notificationsList.slice(0, 10).map(n => `<a class="dropdown-item" href="#">${n.text}<br><small class="text-muted">${n.time}</small></a>`).join('');
}

// ========== QUICK ACTION FORMS ==========
function showNewPatientForm() {
    openModal('New Patient', `
        <input type="text" id="newFirstName" class="form-control mb-2" placeholder="First Name" required>
        <input type="text" id="newLastName" class="form-control mb-2" placeholder="Last Name" required>
        <input type="number" id="newAge" class="form-control mb-2" placeholder="Age" min="0" max="120">
        <select id="newGender" class="form-select mb-2">
            <option value="">Select Gender</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
        </select>
        <textarea id="newDiagnosis" class="form-control mb-2" rows="2" placeholder="Initial Diagnosis"></textarea>
        <button class="btn btn-primary" onclick="createPatient()">Save Patient</button>
    `);
}

async function createPatient() {
    const firstName = document.getElementById('newFirstName').value;
    const lastName = document.getElementById('newLastName').value;
    const age = document.getElementById('newAge').value;
    const gender = document.getElementById('newGender').value;
    const diagnosis = document.getElementById('newDiagnosis').value;
    const birthYear = age ? new Date().getFullYear() - parseInt(age) : 1990;
    const data = {
        username: 'pt_' + Date.now(),
        email: `patient_${Date.now()}@ihis.com`,
        password: 'Patient@123',
        first_name: firstName,
        last_name: lastName,
        phone: '',
        role: 'patient',
        date_of_birth: `${birthYear}-01-01`
    };
    try {
        const res = await api.post('/auth/register', data);
        if (res.user.patient_id && (gender || diagnosis)) {
            await api.put(`/patients/${res.user.patient_id}`, {
                emergency_contact_name: gender ? `Gender: ${gender}` : '',
                emergency_contact_phone: diagnosis ? `Diagnosis: ${diagnosis}` : ''
            });
        }
        addNotification(`New patient ${firstName} ${lastName} registered`);
        bootstrap.Modal.getInstance(document.getElementById('genericModal')).hide();
        navigateTo('patients');
    } catch(e) { alert(e.message); }
}

async function showBookAppointmentForm() {
    const doctors = await api.get('/doctors');
    let docOptions = doctors.doctors.map(d => `<option value="${d.id}">${d.name} (${d.specialty})</option>`).join('');
    openModal('Book Appointment', `
        <input type="number" id="apptPatientId" class="form-control mb-2" placeholder="Patient ID" value="${currentUser.patient_id || ''}">
        <select id="apptDoctorId" class="form-select mb-2"><option value="">Choose Doctor</option>${docOptions}</select>
        <input type="date" id="apptDate" class="form-control mb-2">
        <input type="time" id="apptTime" class="form-control mb-2">
        <input type="text" id="apptReason" class="form-control mb-2" placeholder="Reason">
        <button class="btn btn-success" onclick="createAppointment()">Book</button>
    `);
}

async function createAppointment() {
    const data = {
        patient_id: parseInt(document.getElementById('apptPatientId').value),
        doctor_id: parseInt(document.getElementById('apptDoctorId').value),
        date: document.getElementById('apptDate').value,
        time: document.getElementById('apptTime').value,
        type: 'regular',
        reason: document.getElementById('apptReason').value
    };
    try {
        await api.post('/appointments', data);
        addNotification(`Appointment booked for Patient #${data.patient_id}`);
        bootstrap.Modal.getInstance(document.getElementById('genericModal')).hide();
        navigateTo('appointments');
    } catch(e) { alert(e.message); }
}

function showPrescriptionForm() {
    openModal('Write Prescription', `
        <input type="number" id="rxPatientId" class="form-control mb-2" placeholder="Patient ID" value="${currentUser.patient_id || ''}">
        <input type="text" id="rxDrugCode" class="form-control mb-2" placeholder="Drug Code (e.g., PARA500)">
        <input type="text" id="rxDosage" class="form-control mb-2" placeholder="Dosage">
        <input type="text" id="rxFrequency" class="form-control mb-2" placeholder="Frequency">
        <input type="text" id="rxDuration" class="form-control mb-2" placeholder="Duration">
        <button class="btn btn-warning" onclick="createPrescription()">Send Prescription</button>
    `);
}

async function createPrescription() {
    const data = {
        patient_id: parseInt(document.getElementById('rxPatientId').value),
        doctor_id: currentUser.doctor_id || 1,
        drug_code: document.getElementById('rxDrugCode').value,
        dosage: document.getElementById('rxDosage').value,
        frequency: document.getElementById('rxFrequency').value,
        duration: document.getElementById('rxDuration').value
    };
    try {
        await api.post('/pharmacy/prescriptions', data);
        addNotification(`Prescription created for Patient #${data.patient_id}`);
        bootstrap.Modal.getInstance(document.getElementById('genericModal')).hide();
        navigateTo('pharmacy');
    } catch(e) { alert(e.message); }
}

function logout() { api.clearToken(); window.location.href = '/static/pages/login.html'; }