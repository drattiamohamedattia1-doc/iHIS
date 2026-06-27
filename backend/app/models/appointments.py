"""
Appointment scheduling model.
"""
from datetime import datetime
from app.extensions import db


class Appointment(db.Model):
    """Patient appointment with doctor"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    # Appointment Details
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time)
    appointment_type = db.Column(db.String(50))  # regular, emergency, follow-up, consultation
    reason = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='scheduled')
    # scheduled, confirmed, in_progress, completed, cancelled, no_show
    
    # Notes
    notes = db.Column(db.Text)
    cancellation_reason = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert appointment to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'date': self.appointment_date.isoformat() if self.appointment_date else None,
            'time': self.appointment_time.isoformat() if self.appointment_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'type': self.appointment_type,
            'reason': self.reason,
            'status': self.status,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.status}>'