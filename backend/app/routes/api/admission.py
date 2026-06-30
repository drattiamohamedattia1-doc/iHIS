from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.admission import Admission

admission_bp = Blueprint('admission', __name__)

@admission_bp.route('', methods=['POST'])
@jwt_required()
def create_admission():
    data = request.get_json()
    admission = Admission(
        patient_name=data['patient_name'],
        age=data['age'],
        mrn=data['mrn'],
        diagnosis=data.get('diagnosis', ''),
        department=data['department'],
        notes=data.get('notes', '')
    )
    db.session.add(admission)
    db.session.commit()
    return jsonify({'success': True, 'admission': admission.to_dict()}), 201

@admission_bp.route('', methods=['GET'])
@jwt_required()
def get_admissions():
    admissions = Admission.query.order_by(Admission.admission_date.desc()).all()
    return jsonify({'success': True, 'admissions': [a.to_dict() for a in admissions]}), 200