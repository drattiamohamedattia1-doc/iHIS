from datetime import datetime
from app.extensions import db

class NursingTask(db.Model):
    __tablename__ = 'nursing_tasks'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    nurse_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    task = db.Column(db.String(200))
    scheduled_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed

    patient = db.relationship('Patient', backref='nursing_tasks')
    nurse = db.relationship('User', backref='nursing_tasks')

class CarePlan(db.Model):
    __tablename__ = 'care_plans'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    nurse_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    diagnosis = db.Column(db.String(200))
    goals = db.Column(db.Text)
    interventions = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='care_plans')
    nurse = db.relationship('User', backref='care_plans')