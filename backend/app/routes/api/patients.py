from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.users import User
from app.models.patients import Patient, MedicalRecord, VitalSigns
from app.utils.decorators import role_required

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('', methods=['GET'])
@jwt_required()
def get_patients():
    patients = Patient.query.filter_by(is_deleted=False).all()
    return jsonify({
        'success': True,
        'patients': [p.to_dict() for p in patients]
    }), 200

@patients_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_patient(id):
    patient = Patient.query.get_or_404(id)
    return jsonify({
        'success': True,
        'patient': patient.to_dict()
    }), 200

@patients_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@role_required('doctor', 'admin', 'super_admin')
def update_patient(id):
    patient = Patient.query.get_or_404(id)
    data = request.get_json()
    patient.blood_type = data.get('blood_type', patient.blood_type)
    patient.emergency_contact_name = data.get('emergency_contact_name', patient.emergency_contact_name)
    patient.emergency_contact_phone = data.get('emergency_contact_phone', patient.emergency_contact_phone)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Patient updated', 'patient': patient.to_dict()}), 200

@patients_bp.route('/<int:id>/vitals', methods=['GET'])
@jwt_required()
def get_vitals(id):
    vitals = VitalSigns.query.filter_by(patient_id=id).order_by(VitalSigns.recorded_at.desc()).limit(10).all()
    return jsonify({
        'success': True,
        'vitals': [{'id': v.id, 'temperature': v.temperature, 'heart_rate': v.heart_rate,
                     'bp': f'{v.blood_pressure_systolic}/{v.blood_pressure_diastolic}',
                     'spo2': v.oxygen_saturation, 'recorded_at': v.recorded_at.isoformat()} for v in vitals]
    }), 200

@patients_bp.route('/<int:id>/vitals', methods=['POST'])
@jwt_required()
@role_required('doctor', 'nurse', 'admin')
def add_vitals(id):
    data = request.get_json()
    vital = VitalSigns(
        patient_id=id,
        recorded_by=get_jwt_identity(),
        temperature=data.get('temperature'),
        heart_rate=data.get('heart_rate'),
        blood_pressure_systolic=data.get('bp_systolic'),
        blood_pressure_diastolic=data.get('bp_diastolic'),
        respiratory_rate=data.get('respiratory_rate'),
        oxygen_saturation=data.get('spo2'),
        notes=data.get('notes')
    )
    db.session.add(vital)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Vitals recorded', 'vital_id': vital.id}), 201