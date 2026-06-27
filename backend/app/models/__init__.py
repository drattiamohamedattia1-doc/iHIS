"""
Application Factory
Creates and configures the Flask application.
"""
import os
from flask import Flask, jsonify
from config import config


def create_app(config_name='default'):
    """
    Create and configure the Flask application.
    
    Args:
        config_name: Configuration environment (development, testing, production)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__, template_folder='templates')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    from app.extensions import db, migrate, cors, mail, jwt
    
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    
    # Import models to register them with SQLAlchemy
    with app.app_context():
        # Import all models
        from app.models.base import BaseModel, TimestampMixin
        from app.models.users import User, Role, Permission, UserSession
        from app.models.patients import Patient, MedicalRecord, Diagnosis, Vaccination, VitalSigns
        from app.models.doctors import Doctor, Specialty, DoctorSchedule
        from app.models.appointments import Appointment
        
        # Create all tables
        db.create_all()
    
    # Register blueprints
    from app.routes.api.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    
    # Create required directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'name': 'iHIS API',
            'version': '1.0.0',
            'status': 'running',
            'health': '/api/health',
            'dashboard': '/dashboard',
            'api_login': '/api/v1/auth/login',
            'test_users': {
                'admin': {'username': 'admin', 'password': 'Admin@123', 'role': 'super_admin'},
                'doctor': {'username': 'dr.smith', 'password': 'Doctor@123', 'role': 'doctor'},
                'patient': {'username': 'patient1', 'password': 'Patient@123', 'role': 'patient'}
            }
        })
    
    # Dashboard endpoint
    @app.route('/dashboard')
    def dashboard():
        """System dashboard showing database status and tables"""
        from app.extensions import db
        from app.models.users import User, Role, Permission
        from app.models.patients import Patient
        from app.models.doctors import Doctor, Specialty
        from app.models.appointments import Appointment
        
        # Get counts
        users_count = User.query.count()
        roles_count = Role.query.count()
        patients_count = Patient.query.count()
        doctors_count = Doctor.query.count()
        specialties_count = Specialty.query.count()
        appointments_count = Appointment.query.count()
        permissions_count = Permission.query.count()
        
        # Get table info
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Database info
        db_status = 'Connected'
        db_type = app.config['SQLALCHEMY_DATABASE_URI'].split('://')[0]
        
        # Get users list
        users = User.query.all()
        users_rows = ""
        for user in users:
            user_roles = ", ".join([role.name for role in user.roles])
            status_badge = "success" if user.is_active else "danger"
            users_rows += f"""
            <tr>
                <td>{user.id}</td>
                <td><strong>{user.username}</strong></td>
                <td>{user.email}</td>
                <td>{user.get_full_name()}</td>
                <td><span class="badge bg-info">{user_roles}</span></td>
                <td><span class="badge bg-{status_badge}">{'Active' if user.is_active else 'Inactive'}</span></td>
            </tr>
            """
        
        # Get specialties list
        specialties = Specialty.query.all()
        specialties_rows = ""
        for spec in specialties:
            specialties_rows += f"""
            <tr>
                <td>{spec.id}</td>
                <td><i class="fas fa-stethoscope text-primary me-2"></i>{spec.name}</td>
                <td>{spec.category or 'N/A'}</td>
                <td><span class="badge bg-success">Active</span></td>
            </tr>
            """
        
        dashboard_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>iHIS - System Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding-bottom: 50px;
                }}
                .navbar-custom {{
                    background: rgba(255,255,255,0.95) !important;
                    box-shadow: 0 2px 20px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                }}
                .dashboard-header {{
                    background: rgba(255,255,255,0.95);
                    border-radius: 15px;
                    padding: 30px;
                    margin: 30px 0;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                }}
                .stat-card {{
                    background: rgba(255,255,255,0.95);
                    border-radius: 15px;
                    padding: 25px;
                    text-align: center;
                    transition: all 0.3s ease;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                    cursor: pointer;
                    text-decoration: none;
                    display: block;
                    color: inherit;
                }}
                .stat-card:hover {{
                    transform: translateY(-8px);
                    box-shadow: 0 15px 40px rgba(0,0,0,0.2);
                    text-decoration: none;
                    color: inherit;
                }}
                .stat-icon {{
                    font-size: 2.5rem;
                    margin-bottom: 15px;
                    transition: transform 0.3s;
                }}
                .stat-card:hover .stat-icon {{
                    transform: scale(1.2);
                }}
                .stat-value {{
                    font-size: 2.5rem;
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .stat-label {{
                    color: #6c757d;
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .section-card {{
                    background: rgba(255,255,255,0.95);
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                }}
                .table-container {{
                    max-height: 400px;
                    overflow-y: auto;
                    border-radius: 10px;
                }}
                .badge-status {{
                    font-size: 0.9rem;
                    padding: 8px 15px;
                }}
                .system-health {{
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: white;
                    padding: 15px 25px;
                    border-radius: 50px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                    z-index: 1000;
                }}
                .pulse {{
                    animation: pulse 2s infinite;
                }}
                @keyframes pulse {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.5; }}
                    100% {{ opacity: 1; }}
                }}
                .method-badge {{
                    display: inline-block;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 0.75rem;
                    min-width: 55px;
                    text-align: center;
                }}
                .method-post {{ background: #28a745; color: white; }}
                .method-get {{ background: #007bff; color: white; }}
                .btn-action {{
                    border-radius: 10px;
                    padding: 10px 20px;
                    font-weight: 600;
                    transition: all 0.3s;
                }}
                .btn-action:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }}
                .code-box {{
                    background: #1e1e1e;
                    color: #d4d4d4;
                    padding: 15px;
                    border-radius: 10px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.85rem;
                    margin-bottom: 10px;
                }}
                .nav-pills .nav-link {{
                    border-radius: 10px;
                    margin: 0 5px;
                }}
                .nav-pills .nav-link.active {{
                    background: linear-gradient(135deg, #667eea, #764ba2);
                }}
                ::-webkit-scrollbar {{
                    width: 8px;
                }}
                ::-webkit-scrollbar-track {{
                    background: #f1f1f1;
                    border-radius: 10px;
                }}
                ::-webkit-scrollbar-thumb {{
                    background: #888;
                    border-radius: 10px;
                }}
            </style>
        </head>
        <body>
            <!-- Navigation -->
            <nav class="navbar navbar-expand-lg navbar-custom">
                <div class="container">
                    <a class="navbar-brand fw-bold" href="/dashboard">
                        <i class="fas fa-hospital-alt text-primary me-2"></i>
                        <span class="text-dark">iHIS Dashboard</span>
                    </a>
                    <div class="ms-auto">
                        <a href="/api/health" class="btn btn-sm btn-outline-success me-2" target="_blank">
                            <i class="fas fa-heartbeat me-1"></i>Health Check
                        </a>
                        <a href="/api/v1/auth/login" class="btn btn-sm btn-outline-primary" target="_blank">
                            <i class="fas fa-plug me-1"></i>API Login
                        </a>
                    </div>
                </div>
            </nav>
            
            <div class="container">
                <!-- Header -->
                <div class="dashboard-header">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <h1 class="mb-2">
                                <i class="fas fa-chart-line text-primary me-2"></i>
                                System Dashboard
                            </h1>
                            <p class="text-muted mb-0">
                                Intelligent Health Information System - v1.0.0
                            </p>
                        </div>
                        <div class="col-md-4 text-end">
                            <span class="badge bg-success badge-status">
                                <i class="fas fa-check-circle me-1"></i>
                                {db_status} • {db_type.upper()}
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- Stats Cards Row 1 -->
                <div class="row">
                    <div class="col-md-3">
                        <a href="#users-table" class="stat-card">
                            <div class="stat-icon text-primary">
                                <i class="fas fa-users"></i>
                            </div>
                            <div class="stat-value text-primary">{users_count}</div>
                            <div class="stat-label">Users</div>
                        </a>
                    </div>
                    <div class="col-md-3">
                        <a href="#users-table" class="stat-card">
                            <div class="stat-icon text-success">
                                <i class="fas fa-user-tag"></i>
                            </div>
                            <div class="stat-value text-success">{roles_count}</div>
                            <div class="stat-label">Roles</div>
                        </a>
                    </div>
                    <div class="col-md-3">
                        <a href="#users-table" class="stat-card">
                            <div class="stat-icon text-info">
                                <i class="fas fa-procedures"></i>
                            </div>
                            <div class="stat-value text-info">{patients_count}</div>
                            <div class="stat-label">Patients</div>
                        </a>
                    </div>
                    <div class="col-md-3">
                        <a href="#users-table" class="stat-card">
                            <div class="stat-icon text-warning">
                                <i class="fas fa-user-md"></i>
                            </div>
                            <div class="stat-value text-warning">{doctors_count}</div>
                            <div class="stat-label">Doctors</div>
                        </a>
                    </div>
                </div>
                
                <!-- Stats Cards Row 2 -->
                <div class="row">
                    <div class="col-md-3">
                        <a href="#specialties-table" class="stat-card">
                            <div class="stat-icon text-danger">
                                <i class="fas fa-stethoscope"></i>
                            </div>
                            <div class="stat-value text-danger">{specialties_count}</div>
                            <div class="stat-label">Specialties</div>
                        </a>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card" style="cursor: default;">
                            <div class="stat-icon text-secondary">
                                <i class="fas fa-calendar-check"></i>
                            </div>
                            <div class="stat-value text-secondary">{appointments_count}</div>
                            <div class="stat-label">Appointments</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card" style="cursor: default;">
                            <div class="stat-icon text-success">
                                <i class="fas fa-shield-alt"></i>
                            </div>
                            <div class="stat-value text-success">{permissions_count}</div>
                            <div class="stat-label">Permissions</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <a href="#tables-table" class="stat-card">
                            <div class="stat-icon text-info">
                                <i class="fas fa-database"></i>
                            </div>
                            <div class="stat-value text-info">{len(tables)}</div>
                            <div class="stat-label">Tables</div>
                        </a>
                    </div>
                </div>
                
                <!-- Quick Actions -->
                <div class="section-card">
                    <h4 class="mb-4">
                        <i class="fas fa-bolt text-warning me-2"></i>
                        Quick Actions
                    </h4>
                    <div class="row">
                        <div class="col-md-3 mb-2">
                            <a href="/api/health" target="_blank" class="btn btn-success btn-action w-100">
                                <i class="fas fa-heartbeat me-2"></i>Health Check API
                            </a>
                        </div>
                        <div class="col-md-3 mb-2">
                            <a href="/api/v1/auth/login" target="_blank" class="btn btn-primary btn-action w-100">
                                <i class="fas fa-sign-in-alt me-2"></i>Login Endpoint
                            </a>
                        </div>
                        <div class="col-md-3 mb-2">
                            <a href="/api/v1/auth/register" target="_blank" class="btn btn-info btn-action w-100 text-white">
                                <i class="fas fa-user-plus me-2"></i>Register Endpoint
                            </a>
                        </div>
                        <div class="col-md-3 mb-2">
                            <button class="btn btn-dark btn-action w-100" onclick="window.location.reload()">
                                <i class="fas fa-sync-alt me-2"></i>Refresh Dashboard
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Test Credentials -->
                <div class="section-card">
                    <h4 class="mb-4">
                        <i class="fas fa-key text-warning me-2"></i>
                        Test Credentials
                    </h4>
                    <div class="row">
                        <div class="col-md-4">
                            <div class="code-box">
                                <strong style="color: #4ec9b0;">Super Admin</strong><br>
                                👤 Username: <span style="color: #ce9178;">admin</span><br>
                                🔑 Password: <span style="color: #ce9178;">Admin@123</span><br>
                                🏷️ Role: <span style="color: #569cd6;">super_admin</span>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="code-box">
                                <strong style="color: #4ec9b0;">Doctor</strong><br>
                                👤 Username: <span style="color: #ce9178;">dr.smith</span><br>
                                🔑 Password: <span style="color: #ce9178;">Doctor@123</span><br>
                                🏷️ Role: <span style="color: #569cd6;">doctor</span>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="code-box">
                                <strong style="color: #4ec9b0;">Patient</strong><br>
                                👤 Username: <span style="color: #ce9178;">patient1</span><br>
                                🔑 Password: <span style="color: #ce9178;">Patient@123</span><br>
                                🏷️ Role: <span style="color: #569cd6;">patient</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- API Endpoints -->
                <div class="section-card">
                    <h4 class="mb-4">
                        <i class="fas fa-plug text-primary me-2"></i>
                        API Endpoints
                    </h4>
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>Method</th>
                                    <th>Endpoint</th>
                                    <th>Description</th>
                                    <th>Auth</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><span class="method-badge method-post">POST</span></td>
                                    <td><code>/api/v1/auth/register</code></td>
                                    <td>Register new user</td>
                                    <td><span class="badge bg-secondary">Public</span></td>
                                    <td><a href="/api/v1/auth/register" target="_blank" class="btn btn-sm btn-outline-secondary">Test</a></td>
                                </tr>
                                <tr>
                                    <td><span class="method-badge method-post">POST</span></td>
                                    <td><code>/api/v1/auth/login</code></td>
                                    <td>Login & get JWT token</td>
                                    <td><span class="badge bg-secondary">Public</span></td>
                                    <td><a href="/api/v1/auth/login" target="_blank" class="btn btn-sm btn-outline-primary">Test</a></td>
                                </tr>
                                <tr>
                                    <td><span class="method-badge method-get">GET</span></td>
                                    <td><code>/api/v1/auth/me</code></td>
                                    <td>Get current user info</td>
                                    <td><span class="badge bg-warning text-dark">JWT Required</span></td>
                                    <td><a href="/api/v1/auth/me" target="_blank" class="btn btn-sm btn-outline-warning">Test</a></td>
                                </tr>
                                <tr>
                                    <td><span class="method-badge method-post">POST</span></td>
                                    <td><code>/api/v1/auth/refresh</code></td>
                                    <td>Refresh access token</td>
                                    <td><span class="badge bg-warning text-dark">JWT Required</span></td>
                                    <td><a href="/api/v1/auth/refresh" target="_blank" class="btn btn-sm btn-outline-info">Test</a></td>
                                </tr>
                                <tr>
                                    <td><span class="method-badge method-post">POST</span></td>
                                    <td><code>/api/v1/auth/logout</code></td>
                                    <td>Logout & blacklist token</td>
                                    <td><span class="badge bg-warning text-dark">JWT Required</span></td>
                                    <td><a href="/api/v1/auth/logout" target="_blank" class="btn btn-sm btn-outline-danger">Test</a></td>
                                </tr>
                                <tr>
                                    <td><span class="method-badge method-get">GET</span></td>
                                    <td><code>/api/health</code></td>
                                    <td>System health check</td>
                                    <td><span class="badge bg-secondary">Public</span></td>
                                    <td><a href="/api/health" target="_blank" class="btn btn-sm btn-outline-success">Test</a></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Users Table -->
                <div class="section-card" id="users-table">
                    <h4 class="mb-4">
                        <i class="fas fa-users text-primary me-2"></i>
                        Registered Users ({users_count})
                    </h4>
                    <div class="table-container">
                        <table class="table table-hover">
                            <thead class="table-primary">
                                <tr>
                                    <th>ID</th>
                                    <th>Username</th>
                                    <th>Email</th>
                                    <th>Full Name</th>
                                    <th>Roles</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Specialties Table -->
                <div class="section-card" id="specialties-table">
                    <h4 class="mb-4">
                        <i class="fas fa-stethoscope text-danger me-2"></i>
                        Medical Specialties ({specialties_count})
                    </h4>
                    <div class="table-container">
                        <table class="table table-hover">
                            <thead class="table-danger">
                                <tr>
                                    <th>ID</th>
                                    <th>Specialty Name</th>
                                    <th>Category</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {specialties_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Database Tables -->
                <div class="section-card" id="tables-table">
                    <h4 class="mb-4">
                        <i class="fas fa-database text-info me-2"></i>
                        Database Tables ({len(tables)})
                    </h4>
                    <div class="table-container">
                        <table class="table table-hover">
                            <thead class="table-info">
                                <tr>
                                    <th>#</th>
                                    <th>Table Name</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        # Add table rows
        for idx, table in enumerate(tables, 1):
            dashboard_html += f"""
                                <tr>
                                    <td>{idx}</td>
                                    <td>
                                        <i class="fas fa-table text-primary me-2"></i>
                                        <strong>{table}</strong>
                                    </td>
                                    <td>
                                        <span class="badge bg-success">
                                            <i class="fas fa-check me-1"></i>Active
                                        </span>
                                    </td>
                                </tr>
            """
        
        dashboard_html += """
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- System Health Indicator -->
            <div class="system-health">
                <span class="text-success me-2">
                    <i class="fas fa-circle pulse"></i>
                </span>
                <strong>System Online</strong>
                <span class="text-muted ms-2">|</span>
                <span class="text-muted ms-2">""" + db_type.upper() + """</span>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """
        
        return dashboard_html
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        from app.extensions import db
        from app.models.users import User, Role, Permission
        
        # Test database connection
        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        # Count records
        users_count = User.query.count()
        roles_count = Role.query.count()
        permissions_count = Permission.query.count()
        
        # Get table list
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        return jsonify({
            'status': 'healthy',
            'message': 'System is running normally',
            'version': '1.0.0',
            'database': {
                'status': db_status,
                'type': app.config['SQLALCHEMY_DATABASE_URI'].split('://')[0],
                'tables_count': len(tables),
                'tables': tables
            },
            'counts': {
                'users': users_count,
                'roles': roles_count,
                'permissions': permissions_count
            }
        })
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'The requested resource was not found on this server'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Method Not Allowed',
            'message': 'The HTTP method used is not allowed for this resource'
        }), 405
    
    @app.errorhandler(500)
    def server_error(error):
        from app.extensions import db
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Our team has been notified.'
        }), 500
    
    return app