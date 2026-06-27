from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.patients import MedicalRecord, Diagnosis
from datetime import datetime

emr_bp = Blueprint('emr', __name__)

@emr_bp.route('/records', methods=['POST'])
@jwt_required()
def create_record():
    data = request.get_json()
    record = MedicalRecord(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        visit_type=data.get('visit_type', 'regular'),
        chief_complaint=data.get('chief_complaint', ''),
        subjective=data.get('subjective', ''),
        objective=data.get('objective', ''),
        assessment=data.get('assessment', ''),
        plan=data.get('plan', ''),
        clinical_notes=data.get('clinical_notes', '')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'success': True, 'record_id': record.id}), 201

@emr_bp.route('/records/<int:id>', methods=['GET'])
@jwt_required()
def get_record(id):
    record = MedicalRecord.query.get_or_404(id)
    return jsonify({
        'success': True,
        'record': {
            'id': record.id,
            'patient_id': record.patient_id,
            'doctor_id': record.doctor_id,
            'visit_date': record.visit_date.isoformat(),
            'subjective': record.subjective,
            'objective': record.objective,
            'assessment': record.assessment,
            'plan': record.plan
        }
    }), 200

@emr_bp.route('/diagnoses', methods=['POST'])
@jwt_required()
def add_diagnosis():
    data = request.get_json()
    diagnosis = Diagnosis(
        medical_record_id=data['record_id'],
        patient_id=data['patient_id'],
        icd10_code=data['icd10_code'],
        diagnosis_name=data['diagnosis_name'],
        diagnosis_type=data.get('type', 'primary'),
        severity=data.get('severity'),
        diagnosed_date=datetime.strptime(data['date'], '%Y-%m-%d').date()
    )
    db.session.add(diagnosis)
    db.session.commit()
    return jsonify({'success': True, 'diagnosis_id': diagnosis.id}), 201