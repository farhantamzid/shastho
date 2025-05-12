"""
Main routes for the Shastho Flask application.
---------------------------------------------
This file defines general routes that are not specific to any user role.
Includes home, landing, and other public-facing pages.
Each route is registered as part of the 'main_bp' blueprint in app/__init__.py.
"""

from flask import Blueprint, render_template, session, redirect, url_for
from app.routes.auth import login_required

# Create a Blueprint for main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route.

    This route handles the application's landing page.
    If a user is already logged in, they'll be redirected to
    their role-specific dashboard. Otherwise, the index page
    will be displayed.

    Returns:
        Rendered template or redirect response depending on login status
    """
    # Check if user is logged in
    if session.get('user_id'):
        user_role = session.get('user_role')

        # Redirect to appropriate dashboard based on role
        if user_role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user_role == 'hospital_admin':
            return redirect(url_for('hospital_admin.dashboard'))
        elif user_role == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        elif user_role == 'patient':
            return redirect(url_for('patient.dashboard'))
        elif user_role == 'staff':
            return render_template('staff_dashboard.html')
        else:
            # Default dashboard for other roles
            return redirect(url_for('main.dashboard'))

    # If not logged in, show the home page
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard route.

    This is a general dashboard that redirects to the appropriate
    role-specific dashboard based on the user's role. It requires
    the user to be logged in (enforced by the @login_required decorator).

    Returns:
        Rendered template specific to the user's role
    """
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