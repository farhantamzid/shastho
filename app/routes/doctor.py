from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from app.routes.auth import role_required, login_required
from app.models.database import Doctor, Hospital, Department, UserRole
from app.utils.db import db

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard')
@role_required(['doctor'])
def dashboard():
    """Doctor dashboard."""
    # Get current user info
    user_id = session.get('user_id')

    # Get doctor info
    doctor_records = db.query(Doctor, user_id=user_id)

    if not doctor_records:
        flash('Doctor profile not found.', 'error')
        return redirect(url_for('main.index'))

    doctor = doctor_records[0]

    # Get hospital and department info
    hospital = db.get_by_id(Hospital, doctor.hospital_id) if doctor.hospital_id else None
    department = db.get_by_id(Department, doctor.department_id) if doctor.department_id else None

    # Compile context data
    context = {
        'doctor': {
            'full_name': doctor.full_name,
            'specialization': doctor.specialization,
            'credentials': doctor.credentials,
            'contact_number': doctor.contact_number,
            'hospital_name': hospital.name if hospital else "No Hospital Assigned",
            'department_name': department.name if department else "No Department Assigned"
        }
    }

    return render_template('doctor/dashboard.html', **context)