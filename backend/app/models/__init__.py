"""
iHIS Database Models Package
Import all models here for easy access
"""
from app.models.base import BaseModel, TimestampMixin
from app.models.users import User, Role, Permission, UserSession
from app.models.patients import Patient, MedicalRecord, Diagnosis, Vaccination
from app.models.doctors import Doctor, Specialty, DoctorSchedule
from app.models.appointments import Appointment

__all__ = [
    'BaseModel',
    'TimestampMixin',
    'User',
    'Role',
    'Permission',
    'UserSession',
    'Patient',
    'MedicalRecord',
    'Diagnosis',
    'Vaccination',
    'Doctor',
    'Specialty',
    'DoctorSchedule',
    'Appointment',
]