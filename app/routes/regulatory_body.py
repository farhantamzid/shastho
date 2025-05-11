from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth import login_required, role_required
from app.models.database import UserRole
from app.utils.db import Database

# Create Blueprint for regulatory body routes
regulatory_body_bp = Blueprint('regulatory_body', __name__, url_prefix='/regulatory')
db = Database()

# Regulatory Body Dashboard route
@regulatory_body_bp.route('/dashboard')
# Temporarily disable role checks for testing
# @login_required
# @role_required(UserRole.REGULATORY_BODY)
def dashboard():
    """
    Regulatory Body Dashboard - Entry point for government regulatory users
    """
    # Get the user ID from session
    user_id = session.get('user_id')

    # Dummy data for the dashboard
    stats = {
        'total_hospitals': 142,
        'hospitals_inspected': 98,
        'compliance_rate': '92%',
        'pending_approvals': 17,
        'alerts': 3,
        'recent_reports': 12
    }

    # Dummy data for recent activities
    recent_activities = [
        {
            'action': 'Hospital Inspection',
            'target': 'Metro General Hospital',
            'status': 'Completed',
            'details': 'Regular annual inspection',
            'date': '2023-07-15'
        },
        {
            'action': 'License Approval',
            'target': 'Dr. Sarah Johnson',
            'status': 'Approved',
            'details': 'New medical license',
            'date': '2023-07-12'
        },
        {
            'action': 'Compliance Warning',
            'target': 'Riverside Clinic',
            'status': 'Pending',
            'details': 'Safety protocol violations',
            'date': '2023-07-10'
        },
        {
            'action': 'Policy Update',
            'target': 'All registered facilities',
            'status': 'In Progress',
            'details': 'New patient data security guidelines',
            'date': '2023-07-08'
        }
    ]

    user_name = session.get('user_name', 'Regulatory Official')

    return render_template('regulatory_body/dashboard.html',
                          user_name=user_name,
                          stats=stats,
                          recent_activities=recent_activities)

# Regulatory Body Profile route
@regulatory_body_bp.route('/profile')
# Temporarily disable role checks for testing
# @login_required
# @role_required(UserRole.REGULATORY_BODY)
def profile():
    """
    Regulatory Body Profile - View and edit profile information
    """
    # Get the user ID from session
    user_id = session.get('user_id')

    # Dummy profile data
    profile = {
        'name': 'John Doe',
        'email': 'john.doe@health.gov',
        'agency': 'Department of Health Services',
        'role': 'Senior Health Inspector',
        'jurisdiction': 'Central District',
        'badge_number': 'R-7845',
        'contact': '+1 (555) 123-4567'
    }

    return render_template('regulatory_body/profile.html', profile=profile)