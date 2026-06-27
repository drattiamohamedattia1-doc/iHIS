from datetime import datetime
from app.extensions import db

class DentalRecord(db.Model):
    __tablename__ = 'dental_records'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    tooth_number = db.Column(db.Integer, nullable=False)
    numbering_system = db.Column(db.String(10), default='FDI')
    condition = db.Column(db.String(50))
    treatment = db.Column(db.String(100))
    procedure_date = db.Column(db.Date)

    patient = db.relationship('Patient', backref='dental_records')

class DentalProcedure(db.Model):
    __tablename__ = 'dental_procedures'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(20), unique=True)
    cost = db.Column(db.Float, default=0.0)