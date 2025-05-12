"""
Authentication utility functions for the Shastho Flask application.
---------------------------------------------------------------
This file contains helper functions for authentication, such as login-required and role-required decorators.
Used throughout the app to protect routes.
"""
from functools import wraps
from flask import session, redirect, url_for, flash, current_app

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))

            user_role = session.get('user_role')
            if user_role not in roles:
                flash(f'You do not have permission to access this page. Required roles: {", ".join(roles)}', 'danger')
                if user_role == 'patient':
                    return redirect(url_for('patient.dashboard'))
                elif user_role == 'doctor':
                    return redirect(url_for('doctor.dashboard'))
                elif user_role == 'hospital_admin':
                    return redirect(url_for('hospital_admin.dashboard'))
                elif user_role == 'admin' or user_role == 'system_admin':
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('main.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator