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
    """
    Get list of patients.
    Optional query parameter 'q' for searching by name or MRN.
    """
    q = request.args.get('q', '').strip()
    
    if q:
        # Search by first name, last name, or patient_id (MRN)
        patients = Patient.query.join(User).filter(
            db.or_(
                User.first_name.contains(q),
                User.last_name.contains(q),
                Patient.patient_id.contains(q)
            ),
            Patient.is_deleted == False
        ).all()
    else:
        patients = Patient.query.filter_by(is_deleted=False).all()
    
    # إضافة معلومات إضافية لتسهيل العرض في الواجهة الأمامية
    result = []
    for p in patients:
        data = p.to_dict()
        data['user_name'] = p.user.get_full_name() if p.user else 'N/A'
        data['age'] = p.get_age()
        result.append(data)
    
    return jsonify({
        'success': True,
        'patients': result
    }), 200


@patients_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_patient(id):
    """Get single patient details"""
    patient = Patient.query.get_or_404(id)
    data = patient.to_dict()
    data['user_name'] = patient.user.get_full_name() if patient.user else 'N/A'
    data['age'] = patient.get_age()
    return jsonify({
        'success': True,
        'patient': data
    }), 200


@patients_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@role_required('doctor', 'admin', 'super_admin')
def update_patient(id):
    """Update patient information"""
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
    """Get latest vitals for a patient"""
    vitals = VitalSigns.query.filter_by(patient_id=id).order_by(VitalSigns.recorded_at.desc()).limit(10).all()
    return jsonify({
        'success': True,
        'vitals': [{
            'id': v.id,
            'temperature': v.temperature,
            'heart_rate': v.heart_rate,
            'bp': f'{v.blood_pressure_systolic}/{v.blood_pressure_diastolic}',
            'spo2': v.oxygen_saturation,
            'recorded_at': v.recorded_at.isoformat()
        } for v in vitals]
    }), 200


@patients_bp.route('/<int:id>/vitals', methods=['POST'])
@jwt_required()
@role_required('doctor', 'nurse', 'admin')
def add_vitals(id):
    """Record new vital signs"""
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