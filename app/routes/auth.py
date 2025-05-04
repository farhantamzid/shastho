from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from app.models.database import UserRole, UserStatus, Gender
from app.models.auth import create_user, validate_credentials, find_user_by_id, find_user_by_username
from functools import wraps
from uuid import uuid4
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Form definitions
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Register as', choices=[
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Administrator'),
        ('staff', 'Staff')
    ], validators=[DataRequired()])

    # Patient-specific fields (shown conditionally when role='patient')
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[Optional()])
    contact_number = StringField('Contact Number', validators=[Optional(), Length(min=10, max=15)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=200)])
    emergency_contact_name = StringField('Emergency Contact Name', validators=[Optional(), Length(min=2, max=100)])
    emergency_contact_number = StringField('Emergency Contact Number', validators=[Optional(), Length(min=10, max=15)])

# Helper functions for role-based access control
def login_required(f):
    """Decorator for routes that require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    """Decorator for routes that require specific roles"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not session.get('user_role') or session.get('user_role') not in roles:
                flash('You do not have permission to access this page', 'error')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = validate_credentials(form.email.data, form.password.data)

        if user:
            # Set session
            session['user_id'] = str(user.id)
            session['user_role'] = user.role.value if user.role else None
            session['user_email'] = user.username  # Store email
            session['user_name'] = user.full_name if hasattr(user, 'full_name') and user.full_name else user.username

            # If remember me is checked, set session to be permanent
            if form.remember_me.data:
                session.permanent = True

            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Additional server-side validation for patient fields if the role is 'patient'
        validation_errors = []

        if form.role.data == 'patient':
            # Date of birth validation
            if not form.date_of_birth.data:
                validation_errors.append('Date of birth is required for patients.')
            elif form.date_of_birth.data > datetime.now().date():
                validation_errors.append('Date of birth cannot be in the future.')

            # Gender validation
            if not form.gender.data:
                validation_errors.append('Gender is required for patients.')

            # Contact number validation
            if not form.contact_number.data:
                validation_errors.append('Contact number is required for patients.')
            elif len(form.contact_number.data) < 10 or len(form.contact_number.data) > 15:
                validation_errors.append('Contact number must be between 10 and 15 characters.')

            # Address validation
            if not form.address.data:
                validation_errors.append('Address is required for patients.')
            elif len(form.address.data) < 5:
                validation_errors.append('Address must be at least 5 characters.')

            # Emergency contact name validation
            if not form.emergency_contact_name.data:
                validation_errors.append('Emergency contact name is required for patients.')

            # Emergency contact number validation
            if not form.emergency_contact_number.data:
                validation_errors.append('Emergency contact number is required for patients.')
            elif len(form.emergency_contact_number.data) < 10 or len(form.emergency_contact_number.data) > 15:
                validation_errors.append('Emergency contact number must be between 10 and 15 characters.')

        # Check for uniqueness of username/email
        existing_user = find_user_by_username(form.email.data)
        if existing_user:
            validation_errors.append('A user with that email already exists.')

        # If there are validation errors, show them
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return render_template('auth/register.html', form=form)

        # All validations passed, create the user
        user = create_user(
            username=form.email.data,
            password=form.password.data,
            role=form.role.data,
            full_name=form.full_name.data
        )

        if user:
            # If registering as a patient, create a patient record
            if form.role.data == 'patient':
                try:
                    from app.models.database import Patient, Gender

                    # Create patient record linked to user
                    patient = Patient(
                        user_id=user.id,
                        full_name=form.full_name.data,
                        date_of_birth=form.date_of_birth.data if form.date_of_birth.data else None,
                        gender=Gender(form.gender.data) if form.gender.data else None,
                        contact_number=form.contact_number.data,
                        address=form.address.data,
                        emergency_contact_name=form.emergency_contact_name.data,
                        emergency_contact_number=form.emergency_contact_number.data
                    )

                    # Save patient to database (using a mock database for now)
                    from app.models.patient import save_patient
                    saved_patient = save_patient(patient)

                    if saved_patient:
                        # Save user ID and role in session for redirection to success page
                        session['temp_user_id'] = str(user.id)
                        session['temp_user_role'] = user.role.value if user.role else 'patient'

                        # Redirect to registration success page
                        flash('Registration successful! Your patient account has been created.', 'success')
                        return redirect(url_for('auth.registration_success'))
                    else:
                        # Handle patient save failure
                        flash('There was an error creating your patient profile. Please try again.', 'error')
                        return render_template('auth/register.html', form=form)
                except Exception as e:
                    # Handle any exceptions during patient creation
                    flash(f'An error occurred: {str(e)}. Please try again.', 'error')
                    return render_template('auth/register.html', form=form)
            else:
                # For non-patient users, redirect to login
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('auth.login'))
        else:
            # Handle user creation failure
            flash('There was an error creating your account. Please try again.', 'error')
            return render_template('auth/register.html', form=form)

    return render_template('auth/register.html', form=form)

@auth_bp.route('/registration-success', methods=['GET'])
def registration_success():
    # Check if we have temporary user info in session
    user_id = session.pop('temp_user_id', None)
    user_role = session.pop('temp_user_role', None)

    if not user_id:
        # If no temp user ID, redirect to home
        return redirect(url_for('main.index'))

    return render_template('auth/registration_success.html', user_role=user_role)

@auth_bp.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')
    user = find_user_by_id(user_id)

    if not user:
        session.clear()  # Clear invalid session
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('auth.login'))

    return render_template('auth/profile.html', user=user)

@auth_bp.route('/admin')
@role_required(['admin'])
def admin():
    # Redirect to the new admin dashboard
    return redirect(url_for('admin.dashboard'))

@auth_bp.route('/restricted')
@role_required(['admin', 'staff'])
def restricted_area():
    return render_template('restricted.html')