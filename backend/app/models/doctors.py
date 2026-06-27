"""
Doctor model with specialties and schedules.
"""
from datetime import datetime
from app.extensions import db


class Doctor(db.Model):
    """Doctor model with professional information"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=False)
    
    # Professional Information
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    qualification = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    university = db.Column(db.String(200))
    graduation_year = db.Column(db.Integer)
    
    # Contact & Availability
    consultation_fee = db.Column(db.Float, default=0.0)
    is_available = db.Column(db.Boolean, default=True)
    max_patients_per_day = db.Column(db.Integer, default=20)
    
    # Bio
    bio = db.Column(db.Text)
    languages_spoken = db.Column(db.String(200))  # Comma-separated
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, on_leave, inactive
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref='doctor_profile', lazy=True)
    specialty = db.relationship('Specialty', backref='doctors', lazy=True)
    schedules = db.relationship('DoctorSchedule', backref='doctor', lazy='dynamic')
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic')
    
    def to_dict(self):
        """Convert doctor to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.get_full_name() if self.user else None,
            'specialty': self.specialty.name if self.specialty else None,
            'license_number': self.license_number,
            'qualification': self.qualification,
            'experience_years': self.experience_years,
            'consultation_fee': self.consultation_fee,
            'is_available': self.is_available,
            'languages_spoken': self.languages_spoken.split(',') if self.languages_spoken else [],
            'bio': self.bio,
            'status': self.status
        }
    
    def __repr__(self):
        return f'<Doctor {self.license_number}>'


class Specialty(db.Model):
    """Medical specialties"""
    __tablename__ = 'specialties'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # medical, surgical, diagnostic
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Specialty {self.name}>'


class DoctorSchedule(db.Model):
    """Doctor's working schedule"""
    __tablename__ = 'doctor_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    slot_duration = db.Column(db.Integer, default=30)  # minutes
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DoctorSchedule Day:{self.day_of_week}>'