"""
Flask Extensions Initialization
All extensions are initialized here to avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail
from flask_jwt_extended import JWTManager

# Database
db = SQLAlchemy()

# Database migrations
migrate = Migrate()

# Cross-Origin Resource Sharing
cors = CORS()

# Email service
mail = Mail()

# JWT Authentication
jwt = JWTManager()