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
    
    # Set session secret key
    app.config['SECRET_KEY'] = app.config.get('SECRET_KEY', 'dev-secret-key-for-sessions')
    
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
    
    # Register API blueprints
    from app.routes.api.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    
    from app.routes.api.patients import patients_bp
    app.register_blueprint(patients_bp, url_prefix='/api/v1/patients')
    
    from app.routes.api.doctors import doctors_bp
    app.register_blueprint(doctors_bp, url_prefix='/api/v1/doctors')
    
    from app.routes.api.appointments import appointments_bp
    app.register_blueprint(appointments_bp, url_prefix='/api/v1/appointments')
    
    from app.routes.api.emr import emr_bp
    app.register_blueprint(emr_bp, url_prefix='/api/v1/emr')
    
    from app.routes.api.laboratory import lab_bp
    app.register_blueprint(lab_bp, url_prefix='/api/v1/laboratory')
    
    # Register web routes (Protected Dashboard)
    from app.routes.web import web_bp
    app.register_blueprint(web_bp)
    
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
            'api_endpoints': {
                'auth': '/api/v1/auth',
                'patients': '/api/v1/patients',
                'doctors': '/api/v1/doctors',
                'appointments': '/api/v1/appointments',
                'emr': '/api/v1/emr',
                'laboratory': '/api/v1/laboratory'
            },
            'test_users': {
                'admin': {'username': 'admin', 'password': 'Admin@123', 'role': 'super_admin'},
                'doctor': {'username': 'dr.smith', 'password': 'Doctor@123', 'role': 'doctor'},
                'patient': {'username': 'patient1', 'password': 'Patient@123', 'role': 'patient'}
            }
        })
    
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