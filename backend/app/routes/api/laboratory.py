"""
Laboratory API Routes
Lab Orders, Results, Test Catalog
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from datetime import datetime

lab_bp = Blueprint('laboratory', __name__)

# Supported lab tests catalog
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


# ----- Test Catalog -----
@lab_bp.route('/tests', methods=['GET'])
@jwt_required()
def get_tests():
    """Get list of available lab tests"""
    return jsonify({
        'success': True,
        'tests': [{'code': code, **info} for code, info in LAB_TESTS.items()]
    }), 200


# ----- Lab Orders -----
@lab_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new lab order"""
    data = request.get_json()
    # Simplified order creation (in production, use LabOrder model)
    order = {
        'id': 1,
        'patient_id': data['patient_id'],
        'doctor_id': data.get('doctor_id'),
        'test_code': data['test_code'],
        'status': 'ordered',
        'created_at': datetime.utcnow().isoformat(),
        'test_info': LAB_TESTS.get(data['test_code'], {})
    }
    return jsonify({
        'success': True,
        'message': 'Lab order created',
        'order': order
    }), 201


@lab_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """Get lab orders (filter by patient or status)"""
    patient_id = request.args.get('patient_id')
    status = request.args.get('status')
    # Placeholder - return mock data
    orders = [
        {'id': 1, 'patient_id': 1, 'test_code': 'CBC', 'status': 'completed', 'ordered_at': '2026-06-27T10:00:00'},
        {'id': 2, 'patient_id': 1, 'test_code': 'HbA1c', 'status': 'pending', 'ordered_at': '2026-06-27T11:00:00'}
    ]
    if patient_id:
        orders = [o for o in orders if o['patient_id'] == int(patient_id)]
    if status:
        orders = [o for o in orders if o['status'] == status]
    return jsonify({'success': True, 'orders': orders}), 200


@lab_bp.route('/orders/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(id):
    """Update order status (collected, processing, completed)"""
    data = request.get_json()
    return jsonify({
        'success': True,
        'message': f'Order {id} status updated to {data["status"]}'
    }), 200


# ----- Lab Results -----
@lab_bp.route('/results', methods=['POST'])
@jwt_required()
def add_result():
    """Add lab test result"""
    data = request.get_json()
    result = {
        'id': 1,
        'order_id': data['order_id'],
        'test_code': data['test_code'],
        'value': data['value'],
        'unit': data.get('unit', ''),
        'normal_range': LAB_TESTS.get(data['test_code'], {}).get('normal_range', ''),
        'is_abnormal': data.get('is_abnormal', False),
        'notes': data.get('notes', ''),
        'recorded_at': datetime.utcnow().isoformat(),
        'recorded_by': get_jwt_identity()
    }
    return jsonify({
        'success': True,
        'message': 'Result recorded',
        'result': result
    }), 201


@lab_bp.route('/results/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_results(patient_id):
    """Get lab results for a patient"""
    # Mock data
    results = [
        {'id': 1, 'test_code': 'CBC', 'value': '7.2', 'unit': 'x10³/µL', 'normal_range': '4.5-11.0', 'is_abnormal': False, 'date': '2026-06-20'},
        {'id': 2, 'test_code': 'HbA1c', 'value': '6.2', 'unit': '%', 'normal_range': '< 5.7', 'is_abnormal': True, 'date': '2026-06-20'}
    ]
    return jsonify({'success': True, 'results': results}), 200