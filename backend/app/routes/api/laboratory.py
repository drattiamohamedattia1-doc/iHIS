from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.lab import LabOrder, LabResult
from datetime import datetime

lab_bp = Blueprint('laboratory', __name__)

LAB_TESTS = {
    'CBC': {'name': 'Complete Blood Count', 'category': 'Hematology', 'normal_range': '4.5-11.0 x10³/µL'},
    'HbA1c': {'name': 'Glycated Hemoglobin', 'category': 'Chemistry', 'normal_range': '< 5.7%'},
    'Lipid Profile': {'name': 'Lipid Profile', 'category': 'Chemistry', 'normal_range': 'Total < 200 mg/dL'},
    'LFT': {'name': 'Liver Function Test', 'category': 'Chemistry', 'normal_range': 'ALT 7-56 U/L'},
    'KFT': {'name': 'Kidney Function Test', 'category': 'Chemistry', 'normal_range': 'Creatinine 0.6-1.2 mg/dL'},
    'TSH': {'name': 'Thyroid Stimulating Hormone', 'category': 'Endocrinology', 'normal_range': '0.4-4.0 mIU/L'},
    'PT/INR': {'name': 'Prothrombin Time', 'category': 'Coagulation', 'normal_range': '11-13.5 seconds'},
    'Urinalysis': {'name': 'Urinalysis', 'category': 'Microbiology', 'normal_range': 'Negative'},
    'Blood Culture': {'name': 'Blood Culture', 'category': 'Microbiology', 'normal_range': 'No growth'},
    'Biopsy': {'name': 'Tissue Biopsy', 'category': 'Pathology', 'normal_range': 'Benign'}
}

@lab_bp.route('/tests', methods=['GET'])
@jwt_required()
def get_tests():
    return jsonify({'success': True, 'tests': [{'code': c, **info} for c, info in LAB_TESTS.items()]}), 200

@lab_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    data = request.get_json()
    order = LabOrder(
        patient_id=data['patient_id'],
        doctor_id=data.get('doctor_id'),
        test_code=data['test_code']
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'success': True, 'order_id': order.id}), 201

@lab_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    patient_id = request.args.get('patient_id')
    query = LabOrder.query
    if patient_id:
        query = query.filter_by(patient_id=int(patient_id))
    orders = query.all()
    return jsonify({'success': True, 'orders': [{
        'id': o.id, 'patient_id': o.patient_id, 'test_code': o.test_code,
        'status': o.status, 'ordered_at': o.ordered_at.isoformat()
    } for o in orders]}), 200

@lab_bp.route('/orders/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_status(id):
    order = LabOrder.query.get_or_404(id)
    order.status = request.json.get('status', order.status)
    db.session.commit()
    return jsonify({'success': True}), 200

@lab_bp.route('/results', methods=['POST'])
@jwt_required()
def add_result():
    data = request.get_json()
    result = LabResult(
        lab_order_id=data['order_id'],
        test_code=data.get('test_code'),
        value=data['value'],
        unit=data.get('unit', ''),
        normal_range=data.get('normal_range', ''),
        is_abnormal=data.get('is_abnormal', False),
        notes=data.get('notes', ''),
        recorded_by=get_jwt_identity()
    )
    db.session.add(result)
    db.session.commit()
    return jsonify({'success': True, 'result_id': result.id}), 201

@lab_bp.route('/results/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_results(patient_id):
    results = LabResult.query.join(LabOrder).filter(LabOrder.patient_id == patient_id).all()
    return jsonify({'success': True, 'results': [{
        'id': r.id, 'test_code': r.test_code, 'value': r.value,
        'unit': r.unit, 'is_abnormal': r.is_abnormal, 'notes': r.notes,
        'recorded_at': r.recorded_at.isoformat()
    } for r in results]}), 200