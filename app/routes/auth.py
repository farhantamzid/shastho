from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from app.models.database import UserRole, UserStatus
from app.models.auth import create_user, validate_credentials, find_user_by_id
from functools import wraps
from uuid import uuid4

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
        user = create_user(
            username=form.email.data,
            password=form.password.data,
            role=form.role.data,
            full_name=form.full_name.data
        )

        if user:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('A user with that email already exists', 'error')

    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.index'))

# Example of a protected route that requires authentication
@auth_bp.route('/profile')
@login_required
def profile():
    user = find_user_by_id(session['user_id'])
    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect(url_for('auth.login'))

    return render_template('auth/profile.html', user=user)

# Example of a route that requires specific role(s)
@auth_bp.route('/admin')
@role_required(['admin'])
def admin():
    return "Admin area - only admins can see this page"

# Example of a route that allows multiple roles
@auth_bp.route('/restricted')
@role_required(['admin', 'staff'])
def restricted_area():
    return "Restricted area - only admins and staff can see this page"