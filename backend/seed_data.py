"""
Seed Data Script - Creates initial roles, permissions, specialties and admin user.
Run this once to populate the database with default data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.users import User, Role, Permission
from app.models.doctors import Specialty
from datetime import datetime


def seed_data():
    """Seed the database with initial data"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("  Seeding iHIS Database...")
        print("=" * 60)
        
        # 1. Create Permissions
        print("\n📋 Creating Permissions...")
        permissions = [
            {'name': 'create_user', 'description': 'Create new users', 'module': 'users'},
            {'name': 'edit_user', 'description': 'Edit user details', 'module': 'users'},
            {'name': 'delete_user', 'description': 'Delete users', 'module': 'users'},
            {'name': 'view_user', 'description': 'View user details', 'module': 'users'},
            {'name': 'manage_roles', 'description': 'Manage roles and permissions', 'module': 'admin'},
            {'name': 'view_patient', 'description': 'View patient records', 'module': 'patients'},
            {'name': 'edit_patient', 'description': 'Edit patient records', 'module': 'patients'},
            {'name': 'create_appointment', 'description': 'Create appointments', 'module': 'appointments'},
            {'name': 'manage_appointment', 'description': 'Manage appointments', 'module': 'appointments'},
            {'name': 'write_prescription', 'description': 'Write prescriptions', 'module': 'pharmacy'},
            {'name': 'view_lab_results', 'description': 'View laboratory results', 'module': 'laboratory'},
            {'name': 'manage_lab', 'description': 'Manage laboratory orders', 'module': 'laboratory'},
            {'name': 'view_radiology', 'description': 'View radiology reports', 'module': 'radiology'},
            {'name': 'manage_pharmacy', 'description': 'Manage pharmacy inventory', 'module': 'pharmacy'},
            {'name': 'manage_nursing', 'description': 'Nursing management', 'module': 'nursing'},
            {'name': 'system_admin', 'description': 'Full system administration', 'module': 'admin'},
        ]
        
        created_permissions = []
        for perm in permissions:
            existing = Permission.query.filter_by(name=perm['name']).first()
            if not existing:
                p = Permission(**perm)
                db.session.add(p)
                created_permissions.append(perm['name'])
        
        db.session.commit()
        print(f"   ✓ Created {len(created_permissions)} permissions")
        
        # 2. Create Roles
        print("\n👥 Creating Roles...")
        all_permissions = Permission.query.all()
        
        roles = [
            {
                'name': 'super_admin',
                'description': 'Full system access and control',
                'permissions': all_permissions
            },
            {
                'name': 'admin',
                'description': 'Hospital administrator',
                'permissions': [p for p in all_permissions if p.module in ['users', 'admin', 'appointments']]
            },
            {
                'name': 'doctor',
                'description': 'Medical doctor',
                'permissions': [p for p in all_permissions if p.module in ['patients', 'appointments', 'pharmacy', 'laboratory', 'radiology']]
            },
            {
                'name': 'patient',
                'description': 'Patient',
                'permissions': [p for p in all_permissions if p.name in ['view_patient', 'create_appointment', 'view_lab_results', 'view_radiology']]
            },
            {
                'name': 'nurse',
                'description': 'Nurse',
                'permissions': [p for p in all_permissions if p.module in ['patients', 'nursing', 'appointments']]
            },
            {
                'name': 'lab_technician',
                'description': 'Laboratory technician',
                'permissions': [p for p in all_permissions if p.module == 'laboratory']
            },
            {
                'name': 'radiologist',
                'description': 'Radiology specialist',
                'permissions': [p for p in all_permissions if p.module == 'radiology']
            },
            {
                'name': 'pharmacist',
                'description': 'Pharmacist',
                'permissions': [p for p in all_permissions if p.module == 'pharmacy']
            },
            {
                'name': 'receptionist',
                'description': 'Front desk receptionist',
                'permissions': [p for p in all_permissions if p.module in ['patients', 'appointments']]
            }
        ]
        
        for role_data in roles:
            existing = Role.query.filter_by(name=role_data['name']).first()
            if not existing:
                role = Role(name=role_data['name'], description=role_data['description'])
                role.permissions = role_data['permissions']
                db.session.add(role)
                print(f"   ✓ Created role: {role_data['name']}")
        
        db.session.commit()
        
        # 3. Create Specialties
        print("\n🏥 Creating Medical Specialties...")
        specialties = [
            'Internal Medicine', 'Cardiology', 'Neurology', 'Pediatrics',
            'Orthopedics', 'Surgery', 'ENT', 'Dermatology', 'Psychiatry',
            'Ophthalmology', 'Oncology', 'Gynecology', 'Urology',
            'Endocrinology', 'Gastroenterology', 'Pulmonology', 'Nephrology',
            'Family Medicine', 'Emergency Medicine', 'Radiology',
            'Anesthesiology', 'Pathology', 'General Dentistry',
            'Orthodontics', 'Physical Therapy', 'Sports Rehabilitation'
        ]
        
        for spec_name in specialties:
            existing = Specialty.query.filter_by(name=spec_name).first()
            if not existing:
                specialty = Specialty(name=spec_name, category='medical')
                db.session.add(specialty)
                print(f"   ✓ Created specialty: {spec_name}")
        
        db.session.commit()
        
        # 4. Create Super Admin User
        print("\n👑 Creating Super Admin User...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@ihis.com',
                first_name='System',
                last_name='Administrator',
                phone='+1234567890',
                is_active=True,
                is_verified=True,
                email_verified=True
            )
            admin.set_password('Admin@123')
            admin_role = Role.query.filter_by(name='super_admin').first()
            admin.roles.append(admin_role)
            db.session.add(admin)
            print("   ✓ Created Super Admin (username: admin, password: Admin@123)")
        else:
            print("   → Super Admin already exists")
        
        # 5. Create Demo Doctor
        print("\n👨‍⚕️ Creating Demo Doctor...")
        doctor_user = User.query.filter_by(username='dr.smith').first()
        if not doctor_user:
            doctor_user = User(
                username='dr.smith',
                email='dr.smith@ihis.com',
                first_name='John',
                last_name='Smith',
                phone='+1234567891',
                is_active=True,
                is_verified=True
            )
            doctor_user.set_password('Doctor@123')
            doctor_role = Role.query.filter_by(name='doctor').first()
            doctor_user.roles.append(doctor_role)
            
            # Create doctor profile
            specialty = Specialty.query.filter_by(name='Cardiology').first()
            if not specialty:
                specialty = Specialty.query.first()
            
            import random
            from app.models.doctors import Doctor
            doctor = Doctor(
                user_id=None,  # Will be set after flush
                specialty_id=specialty.id,
                license_number=f"LIC-{random.randint(10000, 99999)}",
                qualification='MD, FACC',
                experience_years=15,
                university='Harvard Medical School',
                bio='Experienced cardiologist with 15 years of practice.',
                languages_spoken='English, Spanish'
            )
            
            db.session.add(doctor_user)
            db.session.flush()
            
            doctor.user_id = doctor_user.id
            db.session.add(doctor)
            
            print("   ✓ Created Demo Doctor (username: dr.smith, password: Doctor@123)")
        
        # 6. Create Demo Patient
        print("\n🏥 Creating Demo Patient...")
        patient_user = User.query.filter_by(username='patient1').first()
        if not patient_user:
            patient_user = User(
                username='patient1',
                email='patient1@ihis.com',
                first_name='Sarah',
                last_name='Johnson',
                phone='+1234567892',
                date_of_birth=datetime(1990, 5, 15).date(),
                is_active=True,
                is_verified=True
            )
            patient_user.set_password('Patient@123')
            patient_role = Role.query.filter_by(name='patient').first()
            patient_user.roles.append(patient_role)
            
            # Create patient profile
            import random
            from app.models.patients import Patient
            patient = Patient(
                user_id=None,
                patient_id=f"PT-{random.randint(10000, 99999)}",
                blood_type='A+',
                emergency_contact_name='Michael Johnson',
                emergency_contact_phone='+1234567899',
                emergency_contact_relationship='Spouse',
                insurance_provider='Blue Cross',
                insurance_policy_number='BCBS123456',
                allergies='["Penicillin", "Peanuts"]',
                chronic_conditions='["Asthma"]'
            )
            
            db.session.add(patient_user)
            db.session.flush()
            
            patient.user_id = patient_user.id
            db.session.add(patient)
            
            print("   ✓ Created Demo Patient (username: patient1, password: Patient@123)")
        
        db.session.commit()
        
        # Summary
        print("\n" + "=" * 60)
        print("  ✅ Database Seeded Successfully!")
        print("=" * 60)
        print(f"  📋 Permissions: {Permission.query.count()}")
        print(f"  👥 Roles: {Role.query.count()}")
        print(f"  🏥 Specialties: {Specialty.query.count()}")
        print(f"  👤 Users: {User.query.count()}")
        print("=" * 60)
        print("\n  Login Credentials:")
        print("  ┌─────────────┬──────────────────┬─────────────┐")
        print("  │ Username    │ Role             │ Password    │")
        print("  ├─────────────┼──────────────────┼─────────────┤")
        print("  │ admin       │ Super Admin      │ Admin@123   │")
        print("  │ dr.smith    │ Doctor           │ Doctor@123  │")
        print("  │ patient1    │ Patient          │ Patient@123 │")
        print("  └─────────────┴──────────────────┴─────────────┘")
        print()

if __name__ == '__main__':
    seed_data()