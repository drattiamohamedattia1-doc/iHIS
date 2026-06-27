"""
Dental API Routes
Dental Charting, Procedures, Imaging
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

dental_bp = Blueprint('dental', __name__)

# Tooth numbering: FDI, Universal, Palmer
TOOTH_SYSTEMS = ['FDI', 'Universal', 'Palmer']

# Mock dental records
dental_records = [
    {'id': 1, 'patient_id': 1, 'tooth': 11, 'system': 'FDI', 'condition': 'caries', 'treatment': 'filling', 'date': '2026-06-15'},
    {'id': 2, 'patient_id': 1, 'tooth': 36, 'system': 'FDI', 'condition': 'missing', 'treatment': 'implant', 'date': '2026-06-20'}
]

dental_procedures = [
    {'id': 1, 'name': 'Dental Filling', 'code': 'DF001', 'cost': 500},
    {'id': 2, 'name': 'Root Canal Treatment', 'code': 'RCT001', 'cost': 3000},
    {'id': 3, 'name': 'Tooth Extraction', 'code': 'EX001', 'cost': 800},
    {'id': 4, 'name': 'Dental Implant', 'code': 'IMP001', 'cost': 10000},
    {'id': 5, 'name': 'Scaling & Polishing', 'code': 'SP001', 'cost': 600},
    {'id': 6, 'name': 'Crown Placement', 'code': 'CR001', 'cost': 4000},
    {'id': 7, 'name': 'Orthodontic Braces', 'code': 'ORTH001', 'cost': 15000}
]

# Dental chart (mocked for 32 teeth)
dental_chart = {}


@dental_bp.route('/systems', methods=['GET'])
@jwt_required()
def get_numbering_systems():
    """Get supported tooth numbering systems"""
    return jsonify({
        'success': True,
        'systems': TOOTH_SYSTEMS,
        'recommended': 'FDI'
    }), 200


@dental_bp.route('/chart/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_dental_chart(patient_id):
    """Get dental chart for a patient"""
    patient_records = [r for r in dental_records if r['patient_id'] == patient_id]
    return jsonify({
        'success': True,
        'patient_id': patient_id,
        'records': patient_records,
        'chart': dental_chart.get(patient_id, {})
    }), 200


@dental_bp.route('/chart', methods=['POST'])
@jwt_required()
def update_dental_chart():
    """Add or update tooth condition"""
    data = request.get_json()
    record = {
        'id': len(dental_records) + 1,
        'patient_id': data['patient_id'],
        'tooth': data['tooth'],
        'system': data.get('system', 'FDI'),
        'condition': data['condition'],
        'treatment': data.get('treatment', ''),
        'date': data.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    }
    dental_records.append(record)
    # Update chart
    patient_id = data['patient_id']
    tooth = data['tooth']
    if patient_id not in dental_chart:
        dental_chart[patient_id] = {}
    dental_chart[patient_id][tooth] = {'condition': data['condition'], 'treatment': data.get('treatment', '')}
    
    return jsonify({'success': True, 'record': record}), 201


@dental_bp.route('/procedures', methods=['GET'])
@jwt_required()
def get_procedures():
    """Get list of dental procedures"""
    return jsonify({'success': True, 'procedures': dental_procedures}), 200


@dental_bp.route('/imaging', methods=['POST'])
@jwt_required()
def add_imaging():
    """Add dental imaging record (mock)"""
    data = request.get_json()
    image = {
        'id': 1,
        'patient_id': data['patient_id'],
        'type': data.get('type', 'Panoramic'),
        'url': data.get('url', '/uploads/dental/sample.jpg'),
        'date': datetime.utcnow().isoformat()
    }
    return jsonify({'success': True, 'image': image}), 201


@dental_bp.route('/imaging/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_imaging(patient_id):
    """Get dental imaging for a patient"""
    images = [
        {'id': 1, 'type': 'Panoramic', 'url': '/uploads/dental/pano.jpg', 'date': '2026-06-20'},
        {'id': 2, 'type': 'Bitewing', 'url': '/uploads/dental/bw.jpg', 'date': '2026-06-21'}
    ]
    return jsonify({'success': True, 'images': images}), 200