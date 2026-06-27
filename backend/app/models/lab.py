from datetime import datetime
from app.extensions import db

class LabOrder(db.Model):
    __tablename__ = 'lab_orders'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    test_code = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='ordered')  # ordered, collected, processing, completed
    ordered_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='lab_orders')
    doctor = db.relationship('Doctor', backref='lab_orders')
    result = db.relationship('LabResult', backref='order', uselist=False)

class LabResult(db.Model):
    __tablename__ = 'lab_results'
    id = db.Column(db.Integer, primary_key=True)
    lab_order_id = db.Column(db.Integer, db.ForeignKey('lab_orders.id'), unique=True, nullable=False)
    test_code = db.Column(db.String(50))
    value = db.Column(db.String(50))
    unit = db.Column(db.String(20))
    normal_range = db.Column(db.String(50))
    is_abnormal = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'))