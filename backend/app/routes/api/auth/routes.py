"""
Authentication API Routes
Login, Register, Refresh Token, Logout
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import datetime
from app.extensions import db
from app.models.users import User, Role, user_roles
from app.models.patients import Patient
from app.models.doctors import Doctor, Specialty

auth_bp = Blueprint('auth', __name__)

# Token blacklist (for logout)
token_blacklist = set()


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'{field} is required'}), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'message': 'Email already exists'}), 400

        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone', ''),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None
        )
        user.set_password(data['password'])

        # ابحث عن الدور
        role = Role.query.filter_by(name=data['role']).first()
        if not role:
            return jsonify({'success': False, 'message': f'Role {data["role"]} not found'}), 400

        db.session.add(user)
        db.session.flush()  # لنحصل على user.id

        # إدراج الصلة في جدول user_roles يدويًا
        db.session.execute(
            user_roles.insert().values(user_id=user.id, role_id=role.id)
        )

        import random
        if data['role'] == 'patient':
            patient_id = f"PT-{random.randint(10000, 99999)}"
            patient = Patient(
                user_id=user.id,
                patient_id=patient_id,
                blood_type=data.get('blood_type', ''),
                emergency_contact_name=data.get('emergency_contact_name', ''),
                emergency_contact_phone=data.get('emergency_contact_phone', '')
            )
            db.session.add(patient)
        elif data['role'] == 'doctor':
            specialty = Specialty.query.filter_by(name=data.get('specialty', 'General Medicine')).first()
            if not specialty:
                specialty = Specialty.query.first()
            doctor = Doctor(
                user_id=user.id,
                specialty_id=specialty.id,
                license_number=f"LIC-{random.randint(10000, 99999)}",
                qualification=data.get('qualification', ''),
                experience_years=data.get('experience_years', 0)
            )
            db.session.add(doctor)

        db.session.commit()

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return tokens"""
    try:
        data = request.get_json()
        if 'username' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400

        user = User.query.filter_by(username=data['username']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        if not user.is_active:
            return jsonify({'success': False, 'message': 'Account deactivated'}), 401

        user.last_login = datetime.utcnow()
        user.failed_login_attempts = 0
        db.session.commit()

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'username': user.username,
                'roles': [role.name for role in user.roles]
            }
        )
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'username': user.username,
                'roles': [role.name for role in user.roles]
            }
        )
        return jsonify({'success': True, 'access_token': access_token}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    jti = get_jwt()['jti']
    token_blacklist.add(jti)
    return jsonify({'success': True, 'message': 'Successfully logged out'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info with patient_id / doctor_id if exists"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        user_data = user.to_dict()
        # Add primary role
        user_data['role'] = [role.name for role in user.roles][0] if user.roles else None

        # Check for patient profile
        patient = Patient.query.filter_by(user_id=user.id).first()
        if patient:
            user_data['patient_id'] = patient.id

        # Check for doctor profile
        doctor = Doctor.query.filter_by(user_id=user.id).first()
        if doctor:
            user_data['doctor_id'] = doctor.id

        return jsonify({'success': True, 'user': user_data}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500