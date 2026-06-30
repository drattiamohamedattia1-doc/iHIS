from datetime import datetime
from app.extensions import db

class Admission(db.Model):
    __tablename__ = 'admissions'
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    mrn = db.Column(db.String(20), nullable=False)
    diagnosis = db.Column(db.Text)
    department = db.Column(db.String(100), nullable=False)
    admission_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='admitted')
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_name': self.patient_name,
            'age': self.age,
            'mrn': self.mrn,
            'diagnosis': self.diagnosis,
            'department': self.department,
            'admission_date': self.admission_date.isoformat() if self.admission_date else None,
            'status': self.status,
            'notes': self.notes
        }