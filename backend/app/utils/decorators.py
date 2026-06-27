"""
Custom decorators for Role-Based Access Control
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.users import User


def role_required(*required_roles):
    """Decorator to check if user has required role(s)"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404
            
            # Check if user has any of the required roles
            user_roles = [role.name for role in user.roles]
            if not any(role in required_roles for role in user_roles):
                return jsonify({
                    'success': False,
                    'message': 'Insufficient permissions'
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Decorator for admin-only endpoints"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper