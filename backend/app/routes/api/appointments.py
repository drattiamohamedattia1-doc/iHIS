from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.appointments import Appointment
from app.models.doctors import Doctor, DoctorSchedule
from datetime import datetime, date, time

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('', methods=['POST'])
@jwt_required()
def create_appointment():
    data = request.get_json()
    try:
        appointment = Appointment(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            appointment_date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            appointment_time=datetime.strptime(data['time'], '%H:%M').time(),
            appointment_type=data.get('type', 'regular'),
            reason=data.get('reason', ''),
            symptoms=data.get('symptoms', '')
        )
        db.session.add(appointment)
        db.session.commit()
        return jsonify({'success': True, 'appointment': appointment.to_dict()}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@appointments_bp.route('', methods=['GET'])
@jwt_required()
def get_appointments():
    patient_id = request.args.get('patient_id')
    doctor_id = request.args.get('doctor_id')
    query = Appointment.query.filter_by(is_deleted=False)
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    appointments = query.order_by(Appointment.appointment_date.desc()).all()
    return jsonify({
        'success': True,
        'appointments': [a.to_dict() for a in appointments]
    }), 200

@appointments_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    data = request.get_json()
    if 'status' in data:
        appointment.status = data['status']
    db.session.commit()
    return jsonify({'success': True, 'appointment': appointment.to_dict()}), 200