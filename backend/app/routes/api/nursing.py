"""
Nursing API Routes
Vital Signs, Medication Administration, Care Plans
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

nursing_bp = Blueprint('nursing', __name__)

# Mock nursing tasks and care plans
nursing_tasks = [
    {'id': 1, 'patient_id': 1, 'task': 'Check vital signs', 'scheduled': '2026-06-28T08:00', 'status': 'pending'},
    {'id': 2, 'patient_id': 1, 'task': 'Administer medication', 'scheduled': '2026-06-28T12:00', 'status': 'pending'}
]

care_plans = [
    {'id': 1, 'patient_id': 1, 'diagnosis': 'Hypertension', 'goals': 'Maintain BP < 140/90', 'interventions': ['Monitor BP daily', 'Low sodium diet']}
]


@nursing_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get nursing tasks with optional filters"""
    patient_id = request.args.get('patient_id')
    status = request.args.get('status')
    result = nursing_tasks
    if patient_id:
        result = [t for t in result if t['patient_id'] == int(patient_id)]
    if status:
        result = [t for t in result if t['status'] == status]
    return jsonify({'success': True, 'tasks': result}), 200

@nursing_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    """Create new nursing task"""
    data = request.get_json()
    task = {
        'id': len(nursing_tasks) + 1,
        'patient_id': data['patient_id'],
        'task': data['task'],
        'scheduled': data.get('scheduled', datetime.utcnow().isoformat()),
        'status': 'pending'
    }
    nursing_tasks.append(task)
    return jsonify({'success': True, 'task': task}), 201

@nursing_bp.route('/tasks/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_task_status(id):
    """Update task status"""
    data = request.get_json()
    for t in nursing_tasks:
        if t['id'] == id:
            t['status'] = data['status']
            return jsonify({'success': True, 'message': f'Task {id} marked as {data["status"]}'}), 200
    return jsonify({'success': False, 'message': 'Task not found'}), 404


@nursing_bp.route('/vitals', methods=['POST'])
@jwt_required()
def record_vitals():
    """Record patient vital signs"""
    data = request.get_json()
    vital = {
        'id': 1,
        'patient_id': data['patient_id'],
        'nurse_id': get_jwt_identity(),
        'temperature': data.get('temperature'),
        'heart_rate': data.get('heart_rate'),
        'blood_pressure': f"{data.get('bp_systolic')}/{data.get('bp_diastolic')}",
        'spo2': data.get('spo2'),
        'recorded_at': datetime.utcnow().isoformat()
    }
    return jsonify({'success': True, 'message': 'Vitals recorded', 'vital': vital}), 201


@nursing_bp.route('/care-plans', methods=['GET'])
@jwt_required()
def get_care_plans():
    """Get care plans for a patient"""
    patient_id = request.args.get('patient_id')
    result = care_plans
    if patient_id:
        result = [c for c in result if c['patient_id'] == int(patient_id)]
    return jsonify({'success': True, 'care_plans': result}), 200

@nursing_bp.route('/care-plans', methods=['POST'])
@jwt_required()
def create_care_plan():
    """Create new care plan"""
    data = request.get_json()
    plan = {
        'id': len(care_plans) + 1,
        'patient_id': data['patient_id'],
        'diagnosis': data['diagnosis'],
        'goals': data.get('goals', ''),
        'interventions': data.get('interventions', [])
    }
    care_plans.append(plan)
    return jsonify({'success': True, 'care_plan': plan}), 201


@nursing_bp.route('/medication-schedule', methods=['GET'])
@jwt_required()
def medication_schedule():
    """Get medication administration schedule"""
    patient_id = request.args.get('patient_id')
    schedule = [
        {'patient_id': 1, 'drug': 'Paracetamol', 'time': '08:00', 'dose': '500mg'},
        {'patient_id': 1, 'drug': 'Omeprazole', 'time': '20:00', 'dose': '20mg'}
    ]
    if patient_id:
        schedule = [s for s in schedule if s['patient_id'] == int(patient_id)]
    return jsonify({'success': True, 'schedule': schedule}), 200