"""
iHIS Application Entry Point
Run this file to start the Flask development server.
In production, Gunicorn imports 'app' from this module.
"""
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Get configuration from environment
config_name = os.environ.get('FLASK_ENV', 'development')

# Create the application instance at module level so Gunicorn can import it
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    print("=" * 60)
    print("  iHIS - Intelligent Health Information System")
    print("=" * 60)
    print(f"  Environment: {config_name}")
    print(f"  Server: http://localhost:{port}")
    print(f"  Health Check: http://localhost:{port}/api/health")
    print("=" * 60)
    print("  Press CTRL+C to stop the server")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False)
    )