from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.dental_m import DentalRecord, DentalProcedure
from datetime import date

dental_bp = Blueprint('dental', __name__)

TOOTH_SYSTEMS = ['FDI', 'Universal', 'Palmer']

@dental_bp.route('/systems', methods=['GET'])
@jwt_required()
def get_systems():
    return jsonify({'success': True, 'systems': TOOTH_SYSTEMS}), 200

@dental_bp.route('/chart', methods=['POST'])
@jwt_required()
def add_chart_entry():
    data = request.get_json()
    record = DentalRecord(
        patient_id=data['patient_id'],
        tooth_number=data['tooth'],
        numbering_system=data.get('system', 'FDI'),
        condition=data['condition'],
        treatment=data.get('treatment', ''),
        procedure_date=date.today() if not data.get('date') else date.fromisoformat(data['date'])
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'success': True, 'record_id': record.id}), 201

@dental_bp.route('/chart/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_chart(patient_id):
    records = DentalRecord.query.filter_by(patient_id=patient_id).all()
    return jsonify({'success': True, 'records': [{
        'id': r.id, 'tooth': r.tooth_number, 'system': r.numbering_system,
        'condition': r.condition, 'treatment': r.treatment,
        'date': r.procedure_date.isoformat() if r.procedure_date else None
    } for r in records]}), 200

@dental_bp.route('/procedures', methods=['GET'])
@jwt_required()
def get_procedures():
    procs = DentalProcedure.query.all()
    return jsonify({'success': True, 'procedures': [{
        'id': p.id, 'name': p.name, 'code': p.code, 'cost': p.cost
    } for p in procs]}), 200

@dental_bp.route('/imaging', methods=['POST'])
@jwt_required()
def add_imaging():
    # لم ننشئ نموذجاً للصور بعد، يمكن استخدام نموذج بسيط أو الإبقاء على وهمي
    data = request.get_json()
    return jsonify({'success': True, 'image': {'id':1, 'patient_id':data['patient_id'],
                     'type':data.get('type','Panoramic'), 'url':'/uploads/dental/sample.jpg'}}), 201

@dental_bp.route('/imaging/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_imaging(patient_id):
    return jsonify({'success': True, 'images': [
        {'id':1, 'type':'Panoramic', 'url':'/uploads/dental/pano.jpg', 'date':'2026-06-20'},
        {'id':2, 'type':'Bitewing', 'url':'/uploads/dental/bw.jpg', 'date':'2026-06-21'}
    ]}), 200