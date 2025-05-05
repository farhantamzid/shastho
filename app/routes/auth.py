from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from app.models.database import UserRole, UserStatus, Gender, Language, Hospital, Department, HospitalDepartment
from app.models.auth import (
    create_user, validate_credentials, find_user_by_id, find_user_by_username,
    create_password_reset_token, verify_reset_token, reset_password_with_token,
    change_password, update_user_profile_picture, update_user_language_preference,
    update_user_status, create_user_session, get_user_sessions, get_active_sessions,
    terminate_session, terminate_all_sessions, update_session_activity
)
from functools import wraps
from uuid import uuid4, UUID
import os
import secrets
from datetime import datetime
from werkzeug.utils import secure_filename

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
        ('staff', 'Staff'),
        ('hospital_admin', 'Hospital Administrator')
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

    # Hospital Admin-specific fields (shown conditionally when role='hospital_admin')
    hospital_id = SelectField('Hospital', validators=[Optional()], coerce=str)

    # Doctor-specific fields (shown conditionally when role='doctor')
    specialization = StringField('Specialization', validators=[Optional(), Length(min=2, max=100)])
    credentials = TextAreaField('Credentials/Qualifications', validators=[Optional(), Length(max=500)])
    department_id = SelectField('Department', validators=[Optional()], coerce=str)

# Add new password reset request form
class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

# Add new password reset form
class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

# Add password change form
class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])

# Add profile picture upload form
class ProfilePictureForm(FlaskForm):
    picture = FileField('Profile Picture', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])

# Add language preference form
class LanguagePreferenceForm(FlaskForm):
    language = SelectField('Language', validators=[DataRequired()], choices=[
        (Language.ENGLISH.value, 'English'),
        (Language.BANGLA.value, 'Bangla')
    ])

# Add account deactivation form
class DeactivateAccountForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = BooleanField('I understand this action', validators=[DataRequired()])

# Helper functions for role-based access control
def login_required(f):
    """Decorator for routes that require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))

        # Update session activity if session_id is present
        if 'session_id' in session:
            update_session_activity(session['session_id'])

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
            # Check if the user is active
            if user.status != UserStatus.ACTIVE:
                flash('Your account is not active. If you are a Hospital Admin, your account requires approval.', 'error')
                return render_template('auth/login.html', form=form)

            # Generate a unique session ID
            session_id = secrets.token_hex(16)

            # Set session
            session['user_id'] = str(user.id)
            session['user_role'] = user.role.value if user.role else None
            session['user_email'] = user.username  # Store email
            session['user_name'] = user.full_name if hasattr(user, 'full_name') and user.full_name else user.username
            session['session_id'] = session_id

            # Store profile picture URL in session if available
            if user.profile_picture_url:
                session['profile_picture_url'] = user.profile_picture_url

            # Store language preference in session
            if user.language_preference:
                session['language'] = user.language_preference.value

            # If remember me is checked, set session to be permanent
            if form.remember_me.data:
                session.permanent = True

            # Create session record in database
            create_user_session(
                user_id=user.id,
                session_id=session_id,
                user_agent=request.user_agent.string,
                ip_address=request.remote_addr
            )

            flash('Login successful!', 'success')

            # Redirect based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            # Role-specific redirects
            if user.role == UserRole.ADMIN:
                return redirect(url_for('admin.dashboard'))
            elif user.role == UserRole.HOSPITAL_ADMIN:
                return redirect(url_for('hospital_admin.dashboard'))
            elif user.role == UserRole.DOCTOR:
                return redirect(url_for('doctor.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET'])
def register():
    """Registration landing page with options for different user types"""
    return render_template('auth/register_landing.html')

@auth_bp.route('/register/patient', methods=['GET', 'POST'])
def register_patient():
    """Patient registration page"""
    form = RegistrationForm()

    # Set the role field to patient by default
    form.role.data = 'patient'

    # Always populate choices for SelectFields to avoid "Choices cannot be None" error
    try:
        from app.models.database import Gender

        # Set gender choices
        form.gender.choices = [('', 'Select Gender')] + [(g.value, g.name.title()) for g in Gender]

        # Explicitly set choices for fields not used by patients to prevent validation errors
        form.hospital_id.choices = []
        form.department_id.choices = []

    except Exception as e:
        # Handle any exceptions gracefully
        form.gender.choices = [('', 'Error loading gender options')]
        print(f"Error loading gender options: {str(e)}")

    if form.validate_on_submit():
        # Additional server-side validation for patient fields
        validation_errors = []

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
            return render_template('auth/register_patient.html', form=form)

        # All validations passed, create the user
        user = create_user(
            username=form.email.data,
            password=form.password.data,
            role='patient',
            full_name=form.full_name.data
        )

        if user:
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
                    return render_template('auth/register_patient.html', form=form)
            except Exception as e:
                # Handle any exceptions during patient creation
                flash(f'An error occurred: {str(e)}. Please try again.', 'error')
                return render_template('auth/register_patient.html', form=form)
        else:
            # Handle user creation failure
            flash('There was an error creating your account. Please try again.', 'error')
            return render_template('auth/register_patient.html', form=form)

    return render_template('auth/register_patient.html', form=form)

@auth_bp.route('/register/doctor', methods=['GET', 'POST'])
def register_doctor():
    """Doctor registration page"""
    form = RegistrationForm()

    # Set the role field to doctor by default
    form.role.data = 'doctor'

    # Always populate choices for SelectFields to avoid "Choices cannot be None" error
    try:
        from app.models.database import Hospital, Department
        from app.utils.db import db

        # Initialize hospital choices
        hospitals = db.get_all(Hospital)
        form.hospital_id.choices = [('', 'Select Hospital')] + [(str(h.id), h.name) for h in hospitals]

        # Initialize department choices with a default empty choice
        form.department_id.choices = [('', 'Select Hospital First')]

        # Handle AJAX request to get departments for a hospital
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.args.get('hospital_id'):
            hospital_id_str = request.args.get('hospital_id')
            print(f"AJAX request received for hospital_id: {hospital_id_str}")
            try:
                # Convert hospital_id string to UUID
                hospital_id = UUID(hospital_id_str)

                # 1. Find relationships for this hospital
                hospital_department_rels = db.query(HospitalDepartment, hospital_id=hospital_id)
                department_ids = [rel.department_id for rel in hospital_department_rels]

                print(f"Found {len(department_ids)} department relationships for hospital {hospital_id}")

                # 2. Fetch actual departments based on found IDs using get_by_id
                departments = []
                if department_ids:
                    for dept_id in department_ids:
                        dept = db.get_by_id(Department, dept_id)
                        if dept:
                            departments.append(dept)


                # Debug information
                print(f"Found {len(departments)} departments for hospital {hospital_id}")
                for dept in departments:
                    print(f"  - Department: {dept.id}, {dept.name}")

                # Format departments for JSON response
                result = [{'id': str(dept.id), 'name': dept.name} for dept in departments]
                return jsonify(result)
            except ValueError:
                print(f"Invalid hospital_id format received: {hospital_id_str}")
                return jsonify({"error": "Invalid hospital ID format"}), 400
            except Exception as e:
                print(f"Error fetching departments for hospital {hospital_id_str}: {str(e)}")
                return jsonify({"error": str(e)}), 500

        # If this is a POST request and hospital_id is provided, load departments for form validation
        if request.method == 'POST' and form.hospital_id.data:
            try:
                hospital_id = UUID(form.hospital_id.data)
                hospital_department_rels = db.query(HospitalDepartment, hospital_id=hospital_id)
                department_ids = [rel.department_id for rel in hospital_department_rels]

                # Fetch departments individually for POST validation choices
                departments = []
                if department_ids:
                    for dept_id in department_ids:
                        dept = db.get_by_id(Department, dept_id)
                        if dept:
                            departments.append(dept)

                form.department_id.choices = [('', 'Select Department')] + [(str(d.id), d.name) for d in departments]
            except ValueError:
                 print(f"Invalid hospital_id in POST data: {form.hospital_id.data}")
                 # Keep default choices or set to error state
                 form.department_id.choices = [('', 'Select Hospital First')]
            except Exception as e:
                 print(f"Error loading departments during POST for hospital {form.hospital_id.data}: {str(e)}")
                 form.department_id.choices = [('', 'Error loading departments')]

    except Exception as e:
        # Handle any exceptions gracefully
        form.hospital_id.choices = [('', 'Error loading hospitals')]
        form.department_id.choices = [('', 'Error loading departments')]
        print(f"Error loading hospitals or departments: {str(e)}")

    if form.validate_on_submit():
        # Additional server-side validation for doctor fields
        validation_errors = []

        # Specialization validation
        if not form.specialization.data:
            validation_errors.append('Specialization is required for doctors.')

        # Credentials validation
        if not form.credentials.data:
            validation_errors.append('Credentials/Qualifications are required for doctors.')

        # Hospital selection validation
        if not form.hospital_id.data:
            validation_errors.append('Hospital selection is required for doctors.')

        # Department selection validation
        if not form.department_id.data:
            validation_errors.append('Department selection is required for doctors.')

        # Contact number validation
        if not form.contact_number.data:
            validation_errors.append('Contact number is required for doctors.')
        elif len(form.contact_number.data) < 10 or len(form.contact_number.data) > 15:
            validation_errors.append('Contact number must be between 10 and 15 characters.')

        # Check for uniqueness of username/email
        existing_user = find_user_by_username(form.email.data)
        if existing_user:
            validation_errors.append('A user with that email already exists.')

        # If there are validation errors, show them
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return render_template('auth/register_doctor.html', form=form)

        # All validations passed, create the user
        user = create_user(
            username=form.email.data,
            password=form.password.data,
            role='doctor',
            full_name=form.full_name.data
        )

        if user:
            try:
                from app.models.database import Doctor, UserStatus
                from app.utils.db import db

                # Update user status to pending
                update_user_status(user.id, UserStatus.INACTIVE)

                # Create doctor record linked to user
                doctor = Doctor(
                    user_id=user.id,
                    full_name=form.full_name.data,
                    specialization=form.specialization.data,
                    credentials=form.credentials.data,
                    hospital_id=form.hospital_id.data,
                    department_id=form.department_id.data,
                    contact_number=form.contact_number.data
                )

                # Save doctor to database
                saved_doctor = db.create(doctor)

                if saved_doctor:
                    flash('Registration successful! Your doctor account requires administrative approval. You will be notified when your account is activated.', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    # Handle doctor save failure
                    flash('There was an error creating your doctor profile. Please try again.', 'error')
                    return render_template('auth/register_doctor.html', form=form)
            except Exception as e:
                # Handle any exceptions during doctor creation
                flash(f'An error occurred: {str(e)}. Please try again.', 'error')
                return render_template('auth/register_doctor.html', form=form)
        else:
            # Handle user creation failure
            flash('There was an error creating your account. Please try again.', 'error')
            return render_template('auth/register_doctor.html', form=form)

    return render_template('auth/register_doctor.html', form=form)

@auth_bp.route('/register/hospital-admin', methods=['GET', 'POST'])
def register_hospital_admin():
    """Hospital Admin registration page"""
    form = RegistrationForm()

    # Set the role field to hospital_admin by default
    form.role.data = 'hospital_admin'

    # Always populate choices for SelectFields to avoid "Choices cannot be None" error
    try:
        from app.models.database import Hospital
        from app.utils.db import db

        # Initialize hospital choices
        hospitals = db.get_all(Hospital)
        form.hospital_id.choices = [('', 'Select Hospital')] + [(str(h.id), h.name) for h in hospitals]

        # Initialize department_id choices with a default empty list
        # Even though it's not used for hospital admins, it needs valid choices to prevent errors
        form.department_id.choices = [('', 'Not Required for Hospital Admin')]
    except Exception as e:
        # Handle any exceptions gracefully
        form.hospital_id.choices = [('', 'Error loading hospitals')]
        form.department_id.choices = [('', 'Not Required for Hospital Admin')]
        print(f"Error loading hospitals: {str(e)}")

    if form.validate_on_submit():
        # Additional server-side validation for hospital admin fields
        validation_errors = []

        # Hospital selection validation
        if not form.hospital_id.data:
            validation_errors.append('Hospital selection is required for Hospital Administrators.')

        # Contact number validation
        if not form.contact_number.data:
            validation_errors.append('Contact number is required for Hospital Administrators.')
        elif len(form.contact_number.data) < 10 or len(form.contact_number.data) > 15:
            validation_errors.append('Contact number must be between 10 and 15 characters.')

        # Address validation
        if not form.address.data:
            validation_errors.append('Address is required for Hospital Administrators.')

        # Check for uniqueness of username/email
        existing_user = find_user_by_username(form.email.data)
        if existing_user:
            validation_errors.append('A user with that email already exists.')

        # If there are validation errors, show them
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return render_template('auth/register_hospital_admin.html', form=form)

        # All validations passed, create the user
        user = create_user(
            username=form.email.data,
            password=form.password.data,
            role='hospital_admin',
            full_name=form.full_name.data
        )

        if user:
            try:
                from app.models.database import HospitalAdmin
                from app.utils.db import db

                # Create hospital admin record linked to user
                hospital_admin = HospitalAdmin(
                    user_id=user.id,
                    full_name=form.full_name.data,
                    hospital_id=form.hospital_id.data,
                    contact_number=form.contact_number.data,
                    address=form.address.data
                )

                # Save hospital admin to database
                saved_admin = db.create(hospital_admin)

                # Check if the save operation returned a model with an ID
                if saved_admin and saved_admin.id:
                    # We don't immediately log in hospital admins - they require approval
                    flash('Registration successful! Your Hospital Administrator account requires approval. You will be notified when your account is activated.', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    # Handle admin save failure
                    flash('There was an error creating your Hospital Administrator profile. Please try again.', 'error')
                    return render_template('auth/register_hospital_admin.html', form=form)
            except Exception as e:
                # Handle any exceptions during hospital admin creation
                flash(f'An error occurred: {str(e)}. Please try again.', 'error')
                return render_template('auth/register_hospital_admin.html', form=form)
        else:
            # Handle user creation failure
            flash('There was an error creating your account. Please try again.', 'error')
            return render_template('auth/register_hospital_admin.html', form=form)

    return render_template('auth/register_hospital_admin.html', form=form)

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
    # If logged in, terminate the current session
    if 'user_id' in session and 'session_id' in session:
        terminate_session(session['session_id'])

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

    password_form = PasswordChangeForm()
    profile_picture_form = ProfilePictureForm()
    language_form = LanguagePreferenceForm()
    deactivate_form = DeactivateAccountForm()

    # Set default language in form
    if user.language_preference:
        language_form.language.data = user.language_preference.value

    # Get active sessions
    active_sessions = get_active_sessions(user_id)

    # Get current session
    current_session_id = session.get('session_id')

    return render_template('auth/profile.html',
                          user=user,
                          password_form=password_form,
                          profile_picture_form=profile_picture_form,
                          language_form=language_form,
                          deactivate_form=deactivate_form,
                          active_sessions=active_sessions,
                          current_session_id=current_session_id)

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password_route():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        user_id = session.get('user_id')

        if change_password(user_id, form.current_password.data, form.new_password.data):
            flash('Your password has been updated successfully.', 'success')
        else:
            flash('Current password is incorrect.', 'error')

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'error')

    return redirect(url_for('auth.profile'))

@auth_bp.route('/upload-profile-picture', methods=['POST'])
@login_required
def upload_profile_picture():
    form = ProfilePictureForm()
    if form.validate_on_submit():
        user_id = session.get('user_id')
        user = find_user_by_id(user_id)

        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.profile'))

        try:
            # Get the uploaded file
            file = form.picture.data

            # Create a secure filename
            filename = secure_filename(f"{user_id}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}")

            # Ensure directory exists
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'images', 'profile_pictures')
            os.makedirs(upload_folder, exist_ok=True)

            # Save the file
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            # Update user profile picture URL in database
            relative_path = f"/static/images/profile_pictures/{filename}"
            update_user_profile_picture(user_id, relative_path)

            # Update the session with the new profile picture URL
            session['profile_picture_url'] = relative_path

            flash('Profile picture updated successfully', 'success')
        except Exception as e:
            flash(f'Error uploading profile picture: {str(e)}', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'error')

    return redirect(url_for('auth.profile'))

# Add password reset request route
@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    # If user is already logged in, redirect to profile
    if 'user_id' in session:
        return redirect(url_for('auth.profile'))

    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        email = form.email.data
        user = find_user_by_username(email)

        # Always show the same message whether the user exists or not
        # This prevents enumeration attacks
        flash('If your email is registered, you will receive a password reset link shortly.', 'success')

        # If the user exists, generate a token
        if user:
            token = create_password_reset_token(user.id)

            # In a real application, you would send an email here
            # For testing/development, we'll just display the link
            if token:
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                print(f"Password reset link: {reset_url}")  # For testing only
                # In production, you would do something like: send_password_reset_email(user.email, reset_url)

        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password_request.html', form=form)

@auth_bp.route('/admin')
@role_required(['admin'])
def admin():
    # Redirect to the new admin dashboard
    return redirect(url_for('admin.dashboard'))

@auth_bp.route('/hospital-admin')
@role_required(['hospital_admin'])
def hospital_admin():
    # Redirect to the hospital admin dashboard
    return redirect(url_for('hospital_admin.dashboard'))

@auth_bp.route('/restricted')
@role_required(['admin', 'staff'])
def restricted_area():
    return render_template('restricted.html')

# Add password reset route
@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # If user is already logged in, redirect to profile
    if 'user_id' in session and 'first_time_login' not in session:
        return redirect(url_for('auth.profile'))

    # Verify token is valid
    user = verify_reset_token(token)
    if not user:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.reset_password_request'))

    first_login = request.args.get('first_login', False)

    form = ResetPasswordForm()
    if form.validate_on_submit():
        if reset_password_with_token(token, form.password.data):
            # If this is a first-time login for a doctor, show different message
            if 'first_time_login' in session:
                flash('Your password has been set successfully. You can now start using your account.', 'success')
                session.pop('first_time_login', None)  # Remove first-time login flag
                return redirect(url_for('doctor.dashboard'))
            else:
                flash('Your password has been reset successfully. You can now log in with your new password.', 'success')
                return redirect(url_for('auth.login'))
        else:
            flash('There was an error resetting your password. Please try again.', 'error')

    # Pass whether this is a first login to the template
    return render_template('auth/reset_password.html', form=form, token=token, first_login=first_login)

@auth_bp.route('/change-language', methods=['POST'])
@login_required
def change_language():
    form = LanguagePreferenceForm()
    if form.validate_on_submit():
        user_id = session.get('user_id')

        # Update language preference
        if update_user_language_preference(user_id, form.language.data):
            # Update session
            session['language'] = form.language.data
            flash('Language preference updated successfully', 'success')
        else:
            flash('Failed to update language preference', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'error')

    return redirect(url_for('auth.profile'))

@auth_bp.route('/deactivate-account', methods=['POST'])
@login_required
def deactivate_account():
    form = DeactivateAccountForm()
    if form.validate_on_submit():
        user_id = session.get('user_id')
        user = find_user_by_id(user_id)

        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.profile'))

        # Verify password
        if not validate_credentials(user.username, form.password.data):
            flash('Password is incorrect', 'error')
            return redirect(url_for('auth.profile'))

        # Deactivate account
        if update_user_status(user_id, UserStatus.INACTIVE):
            # Clear session
            session.clear()
            flash('Your account has been deactivated. Contact support to reactivate it.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Failed to deactivate account', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'error')

    return redirect(url_for('auth.profile'))

@auth_bp.route('/terminate-session/<session_id>')
@login_required
def terminate_user_session(session_id):
    user_id = session.get('user_id')
    current_session_id = session.get('session_id')

    # Prevent terminating current session through this route
    if session_id == current_session_id:
        flash('Cannot terminate current session. Use logout instead.', 'error')
        return redirect(url_for('auth.profile'))

    # Get user sessions
    user_sessions = get_user_sessions(user_id)

    # Check if session belongs to the user
    if not any(s.session_id == session_id for s in user_sessions):
        flash('Session not found or not owned by you.', 'error')
        return redirect(url_for('auth.profile'))

    # Terminate the session
    if terminate_session(session_id):
        flash('Session terminated successfully.', 'success')
    else:
        flash('Failed to terminate session.', 'error')

    return redirect(url_for('auth.profile'))

@auth_bp.route('/terminate-all-sessions')
@login_required
def terminate_all_user_sessions():
    user_id = session.get('user_id')
    current_session_id = session.get('session_id')

    # Terminate all sessions except current one
    if terminate_all_sessions(user_id, current_session_id):
        flash('All other sessions terminated successfully.', 'success')
    else:
        flash('Failed to terminate some sessions.', 'error')

    return redirect(url_for('auth.profile'))