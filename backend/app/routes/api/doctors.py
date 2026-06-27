from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.doctors import Doctor, Specialty

doctors_bp = Blueprint('doctors', __name__)

@doctors_bp.route('', methods=['GET'])
@jwt_required()
def get_doctors():
    specialty = request.args.get('specialty')
    query = Doctor.query.filter_by(is_deleted=False)
    if specialty:
        spec = Specialty.query.filter_by(name=specialty).first()
        if spec:
            query = query.filter_by(specialty_id=spec.id)
    doctors = query.all()
    return jsonify({
        'success': True,
        'doctors': [d.to_dict() for d in doctors]
    }), 200

@doctors_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    return jsonify({
        'success': True,
        'doctor': doctor.to_dict()
    }), 200

@doctors_bp.route('/specialties', methods=['GET'])
@jwt_required()
def get_specialties():
    specialties = Specialty.query.all()
    return jsonify({
        'success': True,
        'specialties': [{'id': s.id, 'name': s.name, 'category': s.category} for s in specialties]
    }), 200