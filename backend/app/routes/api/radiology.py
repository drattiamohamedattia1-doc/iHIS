"""
Radiology API Routes
Imaging requests, reports, DICOM-ready structure
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from datetime import datetime

radiology_bp = Blueprint('radiology', __name__)

# Supported imaging modalities
IMAGING_MODALITIES = {
    'XRAY': 'X-Ray',
    'CT': 'CT Scan',
    'MRI': 'MRI',
    'US': 'Ultrasound',
    'MAMMO': 'Mammography',
    'PET': 'PET Scan',
    'ECHO': 'Echocardiography',
    'DEXA': 'Bone Densitometry'
}


# ----- Modality Catalog -----
@radiology_bp.route('/modalities', methods=['GET'])
@jwt_required()
def get_modalities():
    """Get list of available imaging modalities"""
    return jsonify({
        'success': True,
        'modalities': [{'code': code, 'name': name} for code, name in IMAGING_MODALITIES.items()]
    }), 200


# ----- Imaging Requests -----
@radiology_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new radiology imaging request"""
    data = request.get_json()
    # In production, save to RadiologyOrder model
    order = {
        'id': 1,
        'patient_id': data['patient_id'],
        'doctor_id': data.get('doctor_id'),
        'modality': data['modality'],
        'body_part': data.get('body_part', ''),
        'clinical_indication': data.get('clinical_indication', ''),
        'status': 'ordered',
        'created_at': datetime.utcnow().isoformat()
    }
    return jsonify({
        'success': True,
        'message': 'Imaging request created',
        'order': order
    }), 201


@radiology_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """Get radiology orders with optional filters"""
    patient_id = request.args.get('patient_id')
    modality = request.args.get('modality')
    status = request.args.get('status')
    
    # Mock data
    orders = [
        {'id': 1, 'patient_id': 1, 'modality': 'XRAY', 'body_part': 'Chest', 'status': 'completed', 'created_at': '2026-06-20T10:00:00'},
        {'id': 2, 'patient_id': 1, 'modality': 'MRI', 'body_part': 'Brain', 'status': 'pending', 'created_at': '2026-06-27T11:00:00'}
    ]
    if patient_id:
        orders = [o for o in orders if o['patient_id'] == int(patient_id)]
    if modality:
        orders = [o for o in orders if o['modality'] == modality]
    if status:
        orders = [o for o in orders if o['status'] == status]
    
    return jsonify({'success': True, 'orders': orders}), 200


@radiology_bp.route('/orders/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(id):
    """Update imaging order status (scheduled, performed, reported)"""
    data = request.get_json()
    return jsonify({
        'success': True,
        'message': f'Order {id} status updated to {data["status"]}'
    }), 200


# ----- Radiology Reports -----
@radiology_bp.route('/reports', methods=['POST'])
@jwt_required()
def add_report():
    """Add radiology report for an imaging order"""
    data = request.get_json()
    report = {
        'id': 1,
        'order_id': data['order_id'],
        'radiologist_id': get_jwt_identity(),
        'findings': data.get('findings', ''),
        'impression': data.get('impression', ''),
        'conclusion': data.get('conclusion', ''),
        'is_critical': data.get('is_critical', False),
        'image_url': data.get('image_url', ''),
        'created_at': datetime.utcnow().isoformat()
    }
    return jsonify({
        'success': True,
        'message': 'Report created',
        'report': report
    }), 201


@radiology_bp.route('/reports/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_reports(patient_id):
    """Get radiology reports for a patient"""
    # Mock data
    reports = [
        {'id': 1, 'order_id': 1, 'modality': 'XRAY', 'body_part': 'Chest', 'findings': 'Clear lungs', 'impression': 'Normal', 'date': '2026-06-20'},
        {'id': 2, 'order_id': 2, 'modality': 'MRI', 'body_part': 'Brain', 'findings': 'No abnormalities', 'impression': 'Normal', 'date': '2026-06-27'}
    ]
    return jsonify({'success': True, 'reports': reports}), 200