from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.rad import RadiologyOrder, RadiologyReport

radiology_bp = Blueprint('radiology', __name__)

IMAGING_MODALITIES = {
    'XRAY': 'X-Ray', 'CT': 'CT Scan', 'MRI': 'MRI',
    'US': 'Ultrasound', 'MAMMO': 'Mammography', 'PET': 'PET Scan',
    'ECHO': 'Echocardiography', 'DEXA': 'Bone Densitometry'
}

@radiology_bp.route('/modalities', methods=['GET'])
@jwt_required()
def get_modalities():
    return jsonify({'success': True, 'modalities': [{'code': c, 'name': n} for c, n in IMAGING_MODALITIES.items()]}), 200

@radiology_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    data = request.get_json()
    order = RadiologyOrder(
        patient_id=data['patient_id'],
        doctor_id=data.get('doctor_id'),
        modality=data['modality'],
        body_part=data.get('body_part'),
        clinical_indication=data.get('clinical_indication')
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'success': True, 'order_id': order.id}), 201

@radiology_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    patient_id = request.args.get('patient_id')
    query = RadiologyOrder.query
    if patient_id:
        query = query.filter_by(patient_id=int(patient_id))
    orders = query.all()
    return jsonify({'success': True, 'orders': [{
        'id': o.id, 'patient_id': o.patient_id, 'modality': o.modality,
        'body_part': o.body_part, 'status': o.status,
        'created_at': o.created_at.isoformat()
    } for o in orders]}), 200

@radiology_bp.route('/orders/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_status(id):
    order = RadiologyOrder.query.get_or_404(id)
    order.status = request.json.get('status', order.status)
    db.session.commit()
    return jsonify({'success': True}), 200

@radiology_bp.route('/reports', methods=['POST'])
@jwt_required()
def add_report():
    data = request.get_json()
    report = RadiologyReport(
        radiology_order_id=data['order_id'],
        radiologist_id=get_jwt_identity(),
        findings=data.get('findings'),
        impression=data.get('impression'),
        conclusion=data.get('conclusion'),
        is_critical=data.get('is_critical', False)
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'success': True, 'report_id': report.id}), 201

@radiology_bp.route('/reports/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_reports(patient_id):
    reports = RadiologyReport.query.join(RadiologyOrder).filter(
        RadiologyOrder.patient_id == patient_id
    ).all()
    return jsonify({'success': True, 'reports': [{
        'id': r.id, 'order_id': r.radiology_order_id, 'findings': r.findings,
        'impression': r.impression, 'conclusion': r.conclusion,
        'created_at': r.created_at.isoformat()
    } for r in reports]}), 200