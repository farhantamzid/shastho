from flask import Blueprint, render_template, session, redirect, url_for
from app.routes.auth import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard route."""
    user_role = session.get('user_role')

    # Redirect to appropriate dashboard based on role
    if user_role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif user_role == 'hospital_admin':
        return redirect(url_for('hospital_admin.dashboard'))
    elif user_role == 'doctor':
        return render_template('doctor_dashboard.html')
    elif user_role == 'patient':
        return render_template('patient_dashboard.html')
    elif user_role == 'staff':
        return render_template('staff_dashboard.html')

    # Default dashboard for other roles
    return render_template('dashboard.html')