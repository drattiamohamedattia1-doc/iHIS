from flask import Blueprint, request, redirect, url_for, session
from app.extensions import db
from app.models.users import User, Role
from app.models.patients import Patient
from app.models.doctors import Doctor, Specialty
from functools import wraps

web_bp = Blueprint('web', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'dashboard_user' not in session:
            return redirect(url_for('web.login_page'))
        return f(*args, **kwargs)
    return decorated_function

@web_bp.route('/dashboard/login', methods=['GET', 'POST'])
def login_page():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'Admin@123':
            session['dashboard_user'] = username
            return redirect(url_for('web.dashboard'))
        else:
            error = 'Invalid username or password'
    
    return f'''<!DOCTYPE html><html><head><title>iHIS - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>body{{background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:sans-serif}}
    .box{{background:white;border-radius:20px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,0.3);width:380px}}
    .btn-login{{background:linear-gradient(135deg,#667eea,#764ba2);border:none;padding:12px;font-weight:bold;border-radius:10px;color:white;width:100%}}
    </style></head><body>
    <div class="box"><div class="text-center mb-4"><i class="fas fa-hospital-alt fa-3x" style="color:#667eea"></i>
    <h3 class="mt-3">iHIS Dashboard</h3><p class="text-muted">Sign in to continue</p></div>
    {f'<div class="alert alert-danger">{error}</div>' if error else ''}
    <form method="POST"><div class="mb-3"><label class="form-label">Username</label>
    <input type="text" name="username" class="form-control" required placeholder="admin"></div>
    <div class="mb-4"><label class="form-label">Password</label>
    <input type="password" name="password" class="form-control" required placeholder="Admin@123"></div>
    <button type="submit" class="btn btn-login"><i class="fas fa-sign-in-alt me-2"></i>Sign In</button></form>
    <div class="text-center mt-3"><small class="text-muted">Demo: admin / Admin@123</small></div></div></body></html>'''

@web_bp.route('/dashboard/logout')
def logout():
    session.clear()
    return redirect(url_for('web.login_page'))

@web_bp.route('/dashboard')
@login_required
def dashboard():
    users_count = User.query.count()
    roles_count = Role.query.count()
    patients_count = Patient.query.count()
    doctors_count = Doctor.query.count()
    specialties = Specialty.query.all()
    users = User.query.all()
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    username = session.get('dashboard_user', '')
    
    html = f'''<!DOCTYPE html><html><head><title>iHIS Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>body{{background:#f5f6fa;font-family:sans-serif}}.navbar-custom{{background:linear-gradient(135deg,#667eea,#764ba2)}}
    .stat-card{{background:white;border-radius:15px;padding:25px;text-align:center;margin-bottom:20px;box-shadow:0 5px 20px rgba(0,0,0,0.05)}}
    .section-card{{background:white;border-radius:15px;padding:25px;margin-bottom:30px;box-shadow:0 5px 20px rgba(0,0,0,0.05)}}
    </style></head><body>
    <nav class="navbar navbar-dark navbar-custom"><div class="container">
    <a class="navbar-brand fw-bold" href="/dashboard"><i class="fas fa-hospital-alt me-2"></i>iHIS Dashboard</a>
    <div><span class="text-white me-3"><i class="fas fa-user me-1"></i>{username}</span>
    <a href="/dashboard/logout" class="btn btn-outline-light btn-sm"><i class="fas fa-sign-out-alt me-1"></i>Logout</a></div></div></nav>
    <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
    <h3><i class="fas fa-tachometer-alt me-2"></i>System Dashboard</h3>
    <div><button class="btn btn-primary me-2" data-bs-toggle="modal" data-bs-target="#addPatientModal"><i class="fas fa-user-plus me-1"></i>Add Patient</button>
    <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#addDoctorModal"><i class="fas fa-user-md me-1"></i>Add Doctor</button></div></div>
    <div class="row"><div class="col-md-3"><div class="stat-card"><i class="fas fa-users fa-2x text-primary mb-2"></i><h2>{users_count}</h2><small class="text-muted">Users</small></div></div>
    <div class="col-md-3"><div class="stat-card"><i class="fas fa-user-tag fa-2x text-success mb-2"></i><h2>{roles_count}</h2><small class="text-muted">Roles</small></div></div>
    <div class="col-md-3"><div class="stat-card"><i class="fas fa-procedures fa-2x text-info mb-2"></i><h2>{patients_count}</h2><small class="text-muted">Patients</small></div></div>
    <div class="col-md-3"><div class="stat-card"><i class="fas fa-user-md fa-2x text-warning mb-2"></i><h2>{doctors_count}</h2><small class="text-muted">Doctors</small></div></div></div>
    <div class="section-card"><h5><i class="fas fa-users me-2"></i>Users ({users_count})</h5><table class="table table-hover mt-3"><thead class="table-dark"><tr><th>ID</th><th>Username</th><th>Email</th><th>Name</th><th>Roles</th></tr></thead><tbody>'''
    
    for user in users:
        roles = ", ".join([r.name for r in user.roles])
        html += f'<tr><td>{user.id}</td><td><strong>{user.username}</strong></td><td>{user.email}</td><td>{user.get_full_name()}</td><td><span class="badge bg-info">{roles}</span></td></tr>'
    
    html += f'''</tbody></table></div>
    <div class="section-card"><h5><i class="fas fa-table me-2"></i>Database Tables ({len(tables)})</h5><div class="row mt-3">'''
    
    for table in tables:
        html += f'<div class="col-md-3 mb-2"><span class="badge bg-success p-2 w-100"><i class="fas fa-check me-1"></i>{table}</span></div>'
    
    html += '''</div></div></div>
    <div class="modal fade" id="addPatientModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content">
    <div class="modal-header bg-primary text-white"><h5 class="modal-title"><i class="fas fa-user-plus me-2"></i>Add New Patient</h5><button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button></div>
    <form method="POST" action="/dashboard/add-patient"><div class="modal-body">
    <div class="mb-3"><label class="form-label">First Name *</label><input type="text" name="first_name" class="form-control" required></div>
    <div class="mb-3"><label class="form-label">Last Name *</label><input type="text" name="last_name" class="form-control" required></div>
    <div class="mb-3"><label class="form-label">Email *</label><input type="email" name="email" class="form-control" required></div>
    <div class="mb-3"><label class="form-label">Phone</label><input type="text" name="phone" class="form-control"></div>
    <div class="mb-3"><label class="form-label">Blood Type</label><select name="blood_type" class="form-select"><option value="">Select...</option><option>A+</option><option>A-</option><option>B+</option><option>B-</option><option>AB+</option><option>AB-</option><option>O+</option><option>O-</option></select></div></div>
    <div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button><button type="submit" class="btn btn-primary">Save Patient</button></div></form></div></div></div>
    <div class="modal fade" id="addDoctorModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content">
    <div class="modal-header bg-success text-white"><h5 class="modal-title"><i class="fas fa-user-md me-2"></i>Add New Doctor</h5><button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button></div>
    <form method="POST" action="/dashboard/add-doctor"><div class="modal-body">
    <div class="mb-3"><label class="form-label">First Name *</label><input type="text" name="first_name" class="form-control" required></div>
    <div class="mb-3"><label class="form-label">Last Name *</label><input type="text" name="last_name" class="form-control" required></div>
    <div class="mb-3"><label class="form-label">Email *</label><input type="email" name="email" class="form-control" required></div>
    <div class="mb-3"><label class="form-label">Specialty *</label><select name="specialty_id" class="form-select" required><option value="">Select...</option>'''
    
    for spec in specialties:
        html += f'<option value="{spec.id}">{spec.name}</option>'
    
    html += '''</select></div><div class="mb-3"><label class="form-label">Qualification</label><input type="text" name="qualification" class="form-control" placeholder="e.g., MD"></div>
    <div class="mb-3"><label class="form-label">Experience (Years)</label><input type="number" name="experience_years" class="form-control" value="0"></div></div>
    <div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button><button type="submit" class="btn btn-success">Save Doctor</button></div></form></div></div></div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script></body></html>'''
    
    return html

@web_bp.route('/dashboard/add-patient', methods=['POST'])
def add_patient():
    import random
    try:
        user = User(username=f"patient_{random.randint(1000,9999)}", email=request.form.get('email'), first_name=request.form.get('first_name'), last_name=request.form.get('last_name'), phone=request.form.get('phone',''), is_active=True, is_verified=True)
        user.set_password('Patient@123')
        user.roles.append(Role.query.filter_by(name='patient').first())
        db.session.add(user)
        db.session.flush()
        patient = Patient(user_id=user.id, patient_id=f"PT-{random.randint(10000,99999)}", blood_type=request.form.get('blood_type',''), status='active')
        db.session.add(patient)
        db.session.commit()
        return redirect(url_for('web.dashboard'))
    except Exception as e:
        db.session.rollback()
        return f"Error: {e}", 500

@web_bp.route('/dashboard/add-doctor', methods=['POST'])
def add_doctor():
    import random
    try:
        user = User(username=f"dr_{request.form.get('last_name','').lower()}_{random.randint(100,999)}", email=request.form.get('email'), first_name=request.form.get('first_name'), last_name=request.form.get('last_name'), is_active=True, is_verified=True)
        user.set_password('Doctor@123')
        user.roles.append(Role.query.filter_by(name='doctor').first())
        db.session.add(user)
        db.session.flush()
        doctor = Doctor(user_id=user.id, specialty_id=int(request.form.get('specialty_id')), license_number=f"LIC-{random.randint(10000,99999)}", qualification=request.form.get('qualification',''), experience_years=int(request.form.get('experience_years',0)))
        db.session.add(doctor)
        db.session.commit()
        return redirect(url_for('web.dashboard'))
    except Exception as e:
        db.session.rollback()
        return f"Error: {e}", 500