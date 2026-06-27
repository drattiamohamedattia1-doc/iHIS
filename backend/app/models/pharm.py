from datetime import datetime
from app.extensions import db

class PharmacyInventory(db.Model):
    __tablename__ = 'pharmacy_inventory'
    drug_code = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    drug_code = db.Column(db.String(20), db.ForeignKey('pharmacy_inventory.drug_code'))
    dosage = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')  # pending, verified, dispensed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='prescriptions')
    doctor = db.relationship('Doctor', backref='prescriptions')
    drug = db.relationship('PharmacyInventory', backref='prescriptions')