from datetime import datetime
from app.extensions import db

class RadiologyOrder(db.Model):
    __tablename__ = 'radiology_orders'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    modality = db.Column(db.String(10))
    body_part = db.Column(db.String(100))
    clinical_indication = db.Column(db.Text)
    status = db.Column(db.String(20), default='ordered')  # ordered, scheduled, performed, reported
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='radiology_orders')
    doctor = db.relationship('Doctor', backref='radiology_orders')
    report = db.relationship('RadiologyReport', backref='order', uselist=False)

class RadiologyReport(db.Model):
    __tablename__ = 'radiology_reports'
    id = db.Column(db.Integer, primary_key=True)
    radiology_order_id = db.Column(db.Integer, db.ForeignKey('radiology_orders.id'), unique=True, nullable=False)
    radiologist_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    findings = db.Column(db.Text)
    impression = db.Column(db.Text)
    conclusion = db.Column(db.Text)
    is_critical = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)