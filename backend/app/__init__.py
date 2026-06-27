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
            'api_docs': '/api/v1/auth/login (POST)',
            'test_users': {
                'admin': 'Admin@123',
                'doctor': 'dr.smith / Doctor@123',
                'patient': 'patient1 / Patient@123'
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
        
        # Get table info
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Database info
        db_status = 'Connected'
        db_type = app.config['SQLALCHEMY_DATABASE_URI'].split('://')[0]
        
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
                body {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
                    transition: transform 0.3s, box-shadow 0.3s;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }}
                .stat-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }}
                .stat-icon {{
                    font-size: 3rem;
                    margin-bottom: 15px;
                }}
                .stat-value {{
                    font-size: 2.5rem;
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .stat-label {{
                    color: #6c757d;
                    font-size: 1rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .table-card {{
                    background: rgba(255,255,255,0.95);
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                }}
                .table-list {{
                    max-height: 400px;
                    overflow-y: auto;
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
                }}
                .pulse {{
                    animation: pulse 2s infinite;
                }}
                @keyframes pulse {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.5; }}
                    100% {{ opacity: 1; }}
                }}
                .api-section {{
                    background: rgba(255,255,255,0.95);
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                }}
                .code-block {{
                    background: #1e1e1e;
                    color: #d4d4d4;
                    padding: 15px;
                    border-radius: 8px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9rem;
                }}
                .method-badge {{
                    display: inline-block;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 0.8rem;
                }}
                .method-post {{ background: #28a745; color: white; }}
                .method-get {{ background: #007bff; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="dashboard-header">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <h1 class="mb-2">
                                <i class="fas fa-hospital-alt text-primary me-2"></i>
                                iHIS Dashboard
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
                
                <!-- Stats Cards -->
                <div class="row">
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-icon text-primary">
                                <i class="fas fa-users"></i>
                            </div>
                            <div class="stat-value text-primary">{users_count}</div>
                            <div class="stat-label">Users</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-icon text-success">
                                <i class="fas fa-user-tag"></i>
                            </div>
                            <div class="stat-value text-success">{roles_count}</div>
                            <div class="stat-label">Roles</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-icon text-info">
                                <i class="fas fa-procedures"></i>
                            </div>
                            <div class="stat-value text-info">{patients_count}</div>
                            <div class="stat-label">Patients</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-icon text-warning">
                                <i class="fas fa-user-md"></i>
                            </div>
                            <div class="stat-value text-warning">{doctors_count}</div>
                            <div class="stat-label">Doctors</div>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-icon text-danger">
                                <i class="fas fa-stethoscope"></i>
                            </div>
                            <div class="stat-value text-danger">{specialties_count}</div>
                            <div class="stat-label">Specialties</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-icon text-secondary">
                                <i class="fas fa-calendar-check"></i>
                            </div>
                            <div class="stat-value text-secondary">{appointments_count}</div>
                            <div class="stat-label">Appointments</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-icon text-success">
                                <i class="fas fa-shield-alt"></i>
                            </div>
                            <div class="stat-value text-success">{Permission.query.count() if 'Permission' in dir() else 0}</div>
                            <div class="stat-label">Permissions</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-icon text-info">
                                <i class="fas fa-database"></i>
                            </div>
                            <div class="stat-value text-info">{len(tables)}</div>
                            <div class="stat-label">Tables</div>
                        </div>
                    </div>
                </div>
                
                <!-- API Endpoints -->
                <div class="api-section">
                    <h4 class="mb-4">
                        <i class="fas fa-plug text-primary me-2"></i>
                        API Endpoints
                    </h4>
                    <table class="table table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>Method</th>
                                <th>Endpoint</th>
                                <th>Description</th>
                                <th>Auth</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><span class="method-badge method-post">POST</span></td>
                                <td><code>/api/v1/auth/register</code></td>
                                <td>Register new user</td>
                                <td><span class="badge bg-secondary">No</span></td>
                            </tr>
                            <tr>
                                <td><span class="method-badge method-post">POST</span></td>
                                <td><code>/api/v1/auth/login</code></td>
                                <td>Login & get JWT token</td>
                                <td><span class="badge bg-secondary">No</span></td>
                            </tr>
                            <tr>
                                <td><span class="method-badge method-get">GET</span></td>
                                <td><code>/api/v1/auth/me</code></td>
                                <td>Get current user info</td>
                                <td><span class="badge bg-warning">JWT</span></td>
                            </tr>
                            <tr>
                                <td><span class="method-badge method-post">POST</span></td>
                                <td><code>/api/v1/auth/refresh</code></td>
                                <td>Refresh access token</td>
                                <td><span class="badge bg-warning">JWT</span></td>
                            </tr>
                            <tr>
                                <td><span class="method-badge method-post">POST</span></td>
                                <td><code>/api/v1/auth/logout</code></td>
                                <td>Logout & blacklist token</td>
                                <td><span class="badge bg-warning">JWT</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <!-- Test Credentials -->
                <div class="api-section">
                    <h4 class="mb-4">
                        <i class="fas fa-key text-warning me-2"></i>
                        Test Credentials
                    </h4>
                    <div class="row">
                        <div class="col-md-4">
                            <div class="code-block">
                                <strong>Super Admin</strong><br>
                                Username: <span style="color: #4ec9b0;">admin</span><br>
                                Password: <span style="color: #4ec9b0;">Admin@123</span><br>
                                Role: super_admin
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="code-block">
                                <strong>Doctor</strong><br>
                                Username: <span style="color: #4ec9b0;">dr.smith</span><br>
                                Password: <span style="color: #4ec9b0;">Doctor@123</span><br>
                                Role: doctor
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="code-block">
                                <strong>Patient</strong><br>
                                Username: <span style="color: #4ec9b0;">patient1</span><br>
                                Password: <span style="color: #4ec9b0;">Patient@123</span><br>
                                Role: patient
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Database Tables -->
                <div class="table-card">
                    <h4 class="mb-4">
                        <i class="fas fa-database text-primary me-2"></i>
                        Database Tables ({len(tables)})
                    </h4>
                    <div class="table-list">
                        <table class="table table-hover">
                            <thead class="table-dark">
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
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': 'Unprocessable Entity',
            'message': 'The request was well-formed but could not be processed'
        }), 422
    
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