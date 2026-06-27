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
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    from app.extensions import db, migrate, cors, mail, jwt
    
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    
    # Create required directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    # Will add blueprints as we create them
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'name': 'iHIS API',
            'version': '1.0.0',
            'status': 'running',
            'health': '/api/health'
        })
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'System is running normally',
            'version': '1.0.0'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    
    return app