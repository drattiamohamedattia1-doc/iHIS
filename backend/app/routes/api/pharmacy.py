from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.pharm import PharmacyInventory, Prescription

pharmacy_bp = Blueprint('pharmacy', __name__)

# للعمليات التي لم تنقل لقاعدة البيانات بالكامل
DRUG_INTERACTIONS = [('AMOX250','LEVO500'), ('PARA500','OMEP20')]

@pharmacy_bp.route('/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    items = PharmacyInventory.query.all()
    return jsonify({'success': True, 'inventory': [{
        'drug_code': i.drug_code, 'name': i.name, 'category': i.category,
        'price': i.price, 'stock': i.stock
    } for i in items]}), 200

@pharmacy_bp.route('/prescriptions', methods=['POST'])
@jwt_required()
def create_prescription():
    data = request.get_json()
    rx = Prescription(
        patient_id=data['patient_id'],
        doctor_id=data.get('doctor_id'),
        drug_code=data['drug_code'],
        dosage=data.get('dosage',''),
        frequency=data.get('frequency',''),
        duration=data.get('duration','')
    )
    db.session.add(rx)
    db.session.commit()
    return jsonify({'success': True, 'prescription_id': rx.id}), 201

@pharmacy_bp.route('/prescriptions', methods=['GET'])
@jwt_required()
def get_prescriptions():
    patient_id = request.args.get('patient_id')
    status = request.args.get('status')
    query = Prescription.query
    if patient_id:
        query = query.filter_by(patient_id=int(patient_id))
    if status:
        query = query.filter_by(status=status)
    rx_list = query.all()
    return jsonify({'success': True, 'prescriptions': [{
        'id': r.id, 'patient_id': r.patient_id, 'drug_code': r.drug_code,
        'dosage': r.dosage, 'frequency': r.frequency, 'duration': r.duration,
        'status': r.status, 'created_at': r.created_at.isoformat()
    } for r in rx_list]}), 200

@pharmacy_bp.route('/prescriptions/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_status(id):
    rx = Prescription.query.get_or_404(id)
    rx.status = request.json.get('status', rx.status)
    db.session.commit()
    return jsonify({'success': True}), 200

@pharmacy_bp.route('/check-interaction', methods=['POST'])
@jwt_required()
def check_interaction():
    drugs = request.json.get('drugs', [])
    interactions = []
    for i in range(len(drugs)):
        for j in range(i+1, len(drugs)):
            pair = (drugs[i], drugs[j])
            if pair in DRUG_INTERACTIONS or (pair[1], pair[0]) in DRUG_INTERACTIONS:
                interactions.append({'drugs': pair, 'severity': 'moderate',
                                     'description': f'Interaction between {drugs[i]} and {drugs[j]}'})
    return jsonify({'success': True, 'has_interactions': len(interactions)>0,
                    'interactions': interactions}), 200

@pharmacy_bp.route('/dispense', methods=['POST'])
@jwt_required()
def dispense():
    data = request.get_json()
    drug_code = data['drug_code']
    quantity = data.get('quantity', 1)
    drug = PharmacyInventory.query.get(drug_code)
    if not drug:
        return jsonify({'success': False, 'message': 'Drug not found'}), 404
    if drug.stock < quantity:
        return jsonify({'success': False, 'message': 'Insufficient stock'}), 400
    drug.stock -= quantity
    db.session.commit()
    return jsonify({'success': True, 'message': f'Dispensed {quantity} of {drug.name}',
                    'remaining': drug.stock}), 200

@pharmacy_bp.route('/inventory/low-stock', methods=['GET'])
@jwt_required()
def low_stock():
    items = PharmacyInventory.query.filter(PharmacyInventory.stock < 50).all()
    return jsonify({'success': True, 'low_stock': [{'drug_code': i.drug_code, 'name': i.name, 'stock': i.stock} for i in items]}), 200