"""
Pharmacy API Routes
Prescriptions, Inventory, Dispensing, Drug Interactions
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from datetime import datetime

pharmacy_bp = Blueprint('pharmacy', __name__)

# Mock drug database
DRUG_DB = {
    'PARA500': {'name': 'Paracetamol 500mg', 'category': 'Analgesic', 'price': 5.00, 'stock': 100},
    'AMOX250': {'name': 'Amoxicillin 250mg', 'category': 'Antibiotic', 'price': 12.00, 'stock': 50},
    'OMEP20': {'name': 'Omeprazole 20mg', 'category': 'GI', 'price': 15.00, 'stock': 75},
    'MET500': {'name': 'Metformin 500mg', 'category': 'Diabetes', 'price': 8.00, 'stock': 60},
    'ATOR10': {'name': 'Atorvastatin 10mg', 'category': 'Lipid', 'price': 20.00, 'stock': 40},
    'LEVO500': {'name': 'Levofloxacin 500mg', 'category': 'Antibiotic', 'price': 18.00, 'stock': 30}
}

# Drug interactions (pairs that shouldn't be combined)
DRUG_INTERACTIONS = [
    ('AMOX250', 'LEVO500'),  # Both antibiotics
    ('PARA500', 'OMEP20'),   # Mild interaction
]

# Mock prescriptions
prescriptions = [
    {'id': 1, 'patient_id': 1, 'doctor_id': 1, 'drug_code': 'PARA500', 'dosage': '1 tablet', 'frequency': '3x daily', 'duration': '5 days', 'status': 'pending'},
    {'id': 2, 'patient_id': 1, 'doctor_id': 1, 'drug_code': 'OMEP20', 'dosage': '1 capsule', 'frequency': '1x daily', 'duration': '30 days', 'status': 'dispensed'}
]


# ----- Prescriptions -----
@pharmacy_bp.route('/prescriptions', methods=['GET'])
@jwt_required()
def get_prescriptions():
    """Get prescriptions with optional filters"""
    patient_id = request.args.get('patient_id')
    status = request.args.get('status')
    result = prescriptions
    if patient_id:
        result = [p for p in result if p['patient_id'] == int(patient_id)]
    if status:
        result = [p for p in result if p['status'] == status]
    return jsonify({'success': True, 'prescriptions': result}), 200

@pharmacy_bp.route('/prescriptions', methods=['POST'])
@jwt_required()
def create_prescription():
    """Create new prescription"""
    data = request.get_json()
    new_rx = {
        'id': len(prescriptions) + 1,
        'patient_id': data['patient_id'],
        'doctor_id': data.get('doctor_id'),
        'drug_code': data['drug_code'],
        'dosage': data.get('dosage', ''),
        'frequency': data.get('frequency', ''),
        'duration': data.get('duration', ''),
        'status': 'pending'
    }
    prescriptions.append(new_rx)
    return jsonify({'success': True, 'message': 'Prescription created', 'prescription': new_rx}), 201

@pharmacy_bp.route('/prescriptions/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_prescription_status(id):
    """Update prescription status (pending, verified, dispensed)"""
    data = request.get_json()
    for p in prescriptions:
        if p['id'] == id:
            p['status'] = data['status']
            return jsonify({'success': True, 'message': f'Prescription {id} status updated to {data["status"]}'}), 200
    return jsonify({'success': False, 'message': 'Prescription not found'}), 404


# ----- Inventory -----
@pharmacy_bp.route('/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    """Get drug inventory"""
    inventory = [{'code': code, **info} for code, info in DRUG_DB.items()]
    return jsonify({'success': True, 'inventory': inventory}), 200

@pharmacy_bp.route('/inventory/<drug_code>', methods=['PUT'])
@jwt_required()
def update_inventory(drug_code):
    """Update drug stock"""
    data = request.get_json()
    if drug_code in DRUG_DB:
        DRUG_DB[drug_code]['stock'] = data.get('stock', DRUG_DB[drug_code]['stock'])
        return jsonify({'success': True, 'message': f'Stock updated for {drug_code}'}), 200
    return jsonify({'success': False, 'message': 'Drug not found'}), 404

@pharmacy_bp.route('/inventory/low-stock', methods=['GET'])
@jwt_required()
def low_stock_alerts():
    """Get drugs with low stock (below 50)"""
    low_stock = [{'code': code, **info} for code, info in DRUG_DB.items() if info['stock'] < 50]
    return jsonify({'success': True, 'low_stock': low_stock, 'count': len(low_stock)}), 200


# ----- Drug Interactions -----
@pharmacy_bp.route('/check-interaction', methods=['POST'])
@jwt_required()
def check_interaction():
    """Check for drug interactions"""
    data = request.get_json()
    drugs = data.get('drugs', [])
    interactions = []
    for i in range(len(drugs)):
        for j in range(i+1, len(drugs)):
            pair = (drugs[i], drugs[j])
            if pair in DRUG_INTERACTIONS or (pair[1], pair[0]) in DRUG_INTERACTIONS:
                interactions.append({
                    'drugs': pair,
                    'severity': 'moderate',
                    'description': f'Potential interaction between {drugs[i]} and {drugs[j]}'
                })
    return jsonify({
        'success': True,
        'has_interactions': len(interactions) > 0,
        'interactions': interactions
    }), 200


# ----- Dispensing -----
@pharmacy_bp.route('/dispense', methods=['POST'])
@jwt_required()
def dispense_medication():
    """Dispense medication and update stock"""
    data = request.get_json()
    drug_code = data['drug_code']
    quantity = data.get('quantity', 1)
    
    if drug_code not in DRUG_DB:
        return jsonify({'success': False, 'message': 'Drug not found'}), 404
    
    if DRUG_DB[drug_code]['stock'] < quantity:
        return jsonify({'success': False, 'message': 'Insufficient stock'}), 400
    
    DRUG_DB[drug_code]['stock'] -= quantity
    
    return jsonify({
        'success': True,
        'message': f'Dispensed {quantity} x {DRUG_DB[drug_code]["name"]}',
        'remaining_stock': DRUG_DB[drug_code]['stock']
    }), 200