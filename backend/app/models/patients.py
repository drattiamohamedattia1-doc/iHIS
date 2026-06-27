"""
Patient model and related medical record models.
"""
from datetime import datetime, date
from app.extensions import db


class Patient(db.Model):
    """Patient model with comprehensive health information"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Medical Record Number
    patient_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Demographics
    blood_type = db.Column(db.String(5))
    marital_status = db.Column(db.String(20))
    occupation = db.Column(db.String(100))
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relationship = db.Column(db.String(50))
    
    # Insurance
    insurance_provider = db.Column(db.String(100))
    insurance_policy_number = db.Column(db.String(50))
    insurance_group_number = db.Column(db.String(50))
    
    # Medical History
    medical_history = db.Column(db.Text)
    surgical_history = db.Column(db.Text)
    family_history = db.Column(db.Text)
    social_history = db.Column(db.Text)
    
    # Allergies (JSON string)
    allergies = db.Column(db.Text, default='[]')
    
    # Chronic Conditions (JSON string)
    chronic_conditions = db.Column(db.Text, default='[]')
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, inactive, deceased
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref='patient_profile', lazy=True)
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic')
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy='dynamic')
    vital_signs = db.relationship('VitalSigns', backref='patient', lazy='dynamic')
    vaccinations = db.relationship('Vaccination', backref='patient', lazy='dynamic')
    
    def get_age(self):
        """Calculate patient age"""
        if self.user and self.user.date_of_birth:
            today = date.today()
            birth = self.user.date_of_birth
            return today.year - birth.year - (
                (today.month, today.day) < (birth.month, birth.day)
            )
        return None
    
    def to_dict(self):
        """Convert patient to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'user_id': self.user_id,
            'blood_type': self.blood_type,
            'marital_status': self.marital_status,
            'occupation': self.occupation,
            'emergency_contact': {
                'name': self.emergency_contact_name,
                'phone': self.emergency_contact_phone,
                'relationship': self.emergency_contact_relationship
            },
            'insurance': {
                'provider': self.insurance_provider,
                'policy_number': self.insurance_policy_number,
                'group_number': self.insurance_group_number
            },
            'age': self.get_age(),
            'status': self.status,
            'allergies': self.allergies,
            'chronic_conditions': self.chronic_conditions
        }
    
    def __repr__(self):
        return f'<Patient {self.patient_id}>'


class MedicalRecord(db.Model):
    """Electronic Medical Record (EMR)"""
    __tablename__ = 'medical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    # Visit Information
    visit_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    visit_type = db.Column(db.String(50))  # regular, emergency, follow-up
    chief_complaint = db.Column(db.Text)
    present_illness = db.Column(db.Text)
    
    # SOAP Notes
    subjective = db.Column(db.Text)
    objective = db.Column(db.Text)
    assessment = db.Column(db.Text)
    plan = db.Column(db.Text)
    
    # Clinical Notes
    clinical_notes = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, completed, signed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctor = db.relationship('Doctor', backref='medical_records')
    diagnoses = db.relationship('Diagnosis', backref='medical_record', lazy='dynamic')
    
    def __repr__(self):
        return f'<MedicalRecord {self.id}>'


class Diagnosis(db.Model):
    """Diagnosis with ICD-10 coding"""
    __tablename__ = 'diagnoses'
    
    id = db.Column(db.Integer, primary_key=True)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    icd10_code = db.Column(db.String(10), nullable=False)
    diagnosis_name = db.Column(db.String(200), nullable=False)
    diagnosis_type = db.Column(db.String(50))  # primary, secondary
    severity = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    diagnosed_date = db.Column(db.Date, nullable=False)
    resolution_date = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Diagnosis {self.icd10_code}>'


class Vaccination(db.Model):
    """Vaccination records"""
    __tablename__ = 'vaccinations'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    vaccine_name = db.Column(db.String(100), nullable=False)
    vaccine_code = db.Column(db.String(50))
    dose_number = db.Column(db.Integer)
    administration_date = db.Column(db.Date, nullable=False)
    administered_by = db.Column(db.String(100))
    facility = db.Column(db.String(100))
    lot_number = db.Column(db.String(50))
    next_due_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Vaccination {self.vaccine_name}>'


class VitalSigns(db.Model):
    """Patient vital signs records"""
    __tablename__ = 'vital_signs'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Vital Signs
    temperature = db.Column(db.Float)  # Celsius
    heart_rate = db.Column(db.Integer)  # BPM
    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    respiratory_rate = db.Column(db.Integer)
    oxygen_saturation = db.Column(db.Float)  # SpO2 %
    blood_sugar = db.Column(db.Float)  # mg/dL
    weight = db.Column(db.Float)  # kg
    height = db.Column(db.Float)  # cm
    bmi = db.Column(db.Float)
    pain_level = db.Column(db.Integer)  # 0-10 scale
    
    notes = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recorder = db.relationship('User', backref='recorded_vitals')
    
    def calculate_bmi(self):
        """Calculate BMI"""
        if self.weight and self.height:
            height_m = self.height / 100
            self.bmi = round(self.weight / (height_m ** 2), 1)
        return self.bmi
    
    def __repr__(self):
        return f'<VitalSigns Patient:{self.patient_id}>'