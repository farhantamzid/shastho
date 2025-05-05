from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional
from app.routes.auth import role_required, login_required
from app.utils.db import Database
from app.models.database import HospitalAdmin, Hospital, User, TestImageAdminRequest, AdminRequestStatus, UserRole, UserStatus, TestAdmin
from uuid import UUID
from datetime import datetime

hospital_admin_bp = Blueprint('hospital_admin', __name__, url_prefix='/hospital-admin')

# Initialize database
db = Database()

# Dummy form for CSRF protection
class DummyForm(FlaskForm):
    pass

# Form for Hospital Admin profile updates
class HospitalAdminProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=200)])

@hospital_admin_bp.route('/')
@role_required(['hospital_admin'])
def dashboard():
    """Hospital Admin dashboard landing page."""
    # Get the current user's information
    user_id = session.get('user_id')

    # Get the hospital admin profile records
    hospital_admin_records = db.get_by_field(HospitalAdmin, 'user_id', user_id)

    if not hospital_admin_records:
        flash('Hospital Administrator profile not found.', 'error')
        return redirect(url_for('main.index'))

    # Get the first hospital admin record
    hospital_admin = hospital_admin_records[0]

    # Get the hospital information
    hospital = db.get_by_id(Hospital, hospital_admin.hospital_id)

    # Get all pending Test/Imaging Admin users for this hospital
    from app.models.auth import find_users_by_role_and_status
    pending_test_admins = find_users_by_role_and_status('test_admin', UserStatus.INACTIVE)

    # Filter test admin users by hospital
    test_admin_details = []
    for user in pending_test_admins:
        # Find the TestAdmin record(s) for this user
        test_admin_records = db.get_by_field(TestAdmin, 'user_id', user.id)

        # Check if any records were found and belong to this hospital
        if test_admin_records:
            test_admin = test_admin_records[0]

            # Only include admins for this hospital
            if str(test_admin.hospital_id) == str(hospital_admin.hospital_id):
                test_admin_details.append({
                    'user': user,
                    'admin': test_admin
                })

    pending_test_admins_count = len(test_admin_details)

    stats = {
        'hospital_name': hospital.name if hospital else "Unknown Hospital",
        'pending_test_admins_count': pending_test_admins_count,
    }

    return render_template(
        'hospital_admin/dashboard.html',
        stats=stats,
        hospital_admin=hospital_admin,
        test_admin_details=test_admin_details
    )

@hospital_admin_bp.route('/profile')
@role_required(['hospital_admin'])
def profile():
    """Hospital Admin profile page."""
    # Get the current user's information
    user_id = session.get('user_id')

    # Get the hospital admin profile records
    hospital_admin_records = db.get_by_field(HospitalAdmin, 'user_id', user_id)

    if not hospital_admin_records:
        flash('Hospital Administrator profile not found.', 'error')
        return redirect(url_for('main.index'))

    # Get the first hospital admin record
    hospital_admin = hospital_admin_records[0]

    # Get the hospital information
    hospital = db.get_by_id(Hospital, hospital_admin.hospital_id)

    return render_template(
        'hospital_admin/profile.html',
        hospital_admin=hospital_admin,
        hospital=hospital
    )

@hospital_admin_bp.route('/pending-test-admins')
@role_required(['hospital_admin'])
def pending_test_admins():
    """View pending Test/Imaging Admin applications."""
    # Get the current user's information
    user_id = session.get('user_id')
    print(f"\n=== PENDING TEST ADMINS DEBUG ===")
    print(f"Current user ID: {user_id}")

    # Get all test admin users regardless of hospital first for debugging
    from app.models.auth import find_users_by_role_and_status
    from app.models.database import UserRole, UserStatus
    all_test_admins = find_users_by_role_and_status('test_admin', UserStatus.INACTIVE)
    print(f"Found total {len(all_test_admins)} test admin users with status INACTIVE")

    # Debug output all test admins
    for user in all_test_admins:
        print(f"Test Admin User: ID={user.id}, Username={user.username}, Role={user.role.value}, Status={user.status.value}")

        # Get the TestAdmin record for this user
        test_admin_records = db.get_by_field(TestAdmin, 'user_id', user.id)
        if test_admin_records:
            print(f"  Found {len(test_admin_records)} test admin records")
            for admin in test_admin_records:
                print(f"  Admin Record: ID={admin.id}, Hospital ID={admin.hospital_id}, Full name={admin.full_name}")
        else:
            print(f"  No TestAdmin records found for this user")

    hospital_admin_records = db.get_by_field(HospitalAdmin, 'user_id', user_id)
    print(f"Found {len(hospital_admin_records)} hospital admin records")

    if not hospital_admin_records:
        flash('Hospital Administrator profile not found.', 'error')
        return redirect(url_for('main.index'))

    # Get the first hospital admin record
    hospital_admin = hospital_admin_records[0]
    print(f"Hospital admin ID: {hospital_admin.id}")
    print(f"Hospital admin's hospital ID: {hospital_admin.hospital_id}")
    print(f"Type of hospital ID: {type(hospital_admin.hospital_id)}")

    # Helper function to normalize IDs for comparison
    def normalize_id(id_value):
        if id_value is None:
            return None
        # Convert UUID to string for comparison
        if isinstance(id_value, UUID):
            return str(id_value)
        # If already a string, return as is
        if isinstance(id_value, str):
            return id_value
        # Otherwise, convert to string
        return str(id_value)

    # Normalize hospital admin's hospital ID for comparison
    hospital_admin_hospital_id = normalize_id(hospital_admin.hospital_id)
    print(f"Normalized hospital admin's hospital ID: {hospital_admin_hospital_id}")

    # Get all inactive users with Test Admin role
    from app.models.auth import find_users_by_role_and_status
    pending_users = find_users_by_role_and_status('test_admin', UserStatus.INACTIVE)
    print(f"Found {len(pending_users)} pending test admin users")

    if len(pending_users) > 0:
        for idx, user in enumerate(pending_users):
            print(f"Pending User {idx+1}: ID={user.id}, Username={user.username}")

    # Get additional test admin info for each user
    admin_details = []
    for user in pending_users:
        print(f"Processing user: {user.id}, {user.username}")

        # Find the TestAdmin record(s) for this user
        test_admin_records = db.get_by_field(TestAdmin, 'user_id', user.id)
        print(f"  Found {len(test_admin_records)} test admin records for this user")

        # Debug each test admin record
        for idx, record in enumerate(test_admin_records):
            print(f"  Record {idx+1}: ID={record.id}, Hospital ID={record.hospital_id}, Type of hospital ID={type(record.hospital_id)}")

        # Check if any records were found
        if test_admin_records:
            test_admin = test_admin_records[0]
            test_admin_hospital_id = normalize_id(test_admin.hospital_id)
            print(f"  Test admin hospital ID: {test_admin.hospital_id}")
            print(f"  Normalized test admin hospital ID: {test_admin_hospital_id}")
            print(f"  Hospital admin hospital ID: {hospital_admin.hospital_id}")
            print(f"  Normalized hospital admin hospital ID: {hospital_admin_hospital_id}")
            print(f"  IDs match: {test_admin_hospital_id == hospital_admin_hospital_id}")

            # IMPORTANT: Add to admin_details regardless of hospital ID match for debugging
            # This way we'll see all pending test admins in the UI even if there's a matching issue
            print(f"  Adding to admin_details for debugging")

            # Ensure created_at is a datetime object
            if isinstance(test_admin.created_at, str):
                test_admin.created_at = datetime.fromisoformat(test_admin.created_at.replace('Z', '+00:00'))

            admin_details.append({
                'user': user,
                'admin': test_admin,
                'hospital_match': test_admin_hospital_id == hospital_admin_hospital_id
            })
        else:
            print(f"  No test admin records found for this user")

    print(f"Final admin_details count: {len(admin_details)}")
    for idx, detail in enumerate(admin_details):
        print(f"Detail {idx+1}: User={detail['user'].username}, Admin={detail['admin'].full_name}, Hospital Match={detail['hospital_match']}")

    # Create a dummy form instance for CSRF token
    form = DummyForm()

    return render_template('hospital_admin/pending_test_admins.html', admin_details=admin_details, hospital_admin=hospital_admin, form=form)

@hospital_admin_bp.route('/approve-test-admin/<user_id>', methods=['POST'])
@role_required(['hospital_admin'])
def approve_test_admin(user_id):
    """Approve a pending Test/Imaging Admin account"""
    try:
        # Verify the hospital admin has permission (belongs to same hospital)
        current_user_id = session.get('user_id')
        hospital_admin = db.get_by_field(HospitalAdmin, 'user_id', current_user_id)[0]

        # Get the test admin user
        user = db.get_by_id(User, user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('hospital_admin.pending_test_admins'))

        # Get the test admin record
        test_admin_records = db.get_by_field(TestAdmin, 'user_id', user_id)
        if not test_admin_records:
            flash('Test Admin record not found.', 'error')
            return redirect(url_for('hospital_admin.pending_test_admins'))

        test_admin = test_admin_records[0]

        # Helper function to normalize IDs for comparison
        def normalize_id(id_value):
            if id_value is None:
                return None
            # Convert UUID to string for comparison
            if isinstance(id_value, UUID):
                return str(id_value)
            # If already a string, return as is
            if isinstance(id_value, str):
                return id_value
            # Otherwise, convert to string
            return str(id_value)

        # Check if the test admin belongs to the same hospital as the hospital admin
        if normalize_id(test_admin.hospital_id) != normalize_id(hospital_admin.hospital_id):
            flash('You do not have permission to approve this Test Admin.', 'error')
            return redirect(url_for('hospital_admin.pending_test_admins'))

        # Update the user status to active
        user.status = UserStatus.ACTIVE
        db.update(user)

        flash(f'Test Admin {test_admin.full_name} has been approved successfully.', 'success')

    except Exception as e:
        flash(f'Error approving Test Admin: {str(e)}', 'error')

    return redirect(url_for('hospital_admin.pending_test_admins'))

@hospital_admin_bp.route('/reject-test-admin/<user_id>', methods=['POST'])
@role_required(['hospital_admin'])
def reject_test_admin(user_id):
    """Reject a pending Test/Imaging Admin account"""
    try:
        # Verify the hospital admin has permission (belongs to same hospital)
        current_user_id = session.get('user_id')
        hospital_admin = db.get_by_field(HospitalAdmin, 'user_id', current_user_id)[0]

        # Get the test admin user
        user = db.get_by_id(User, user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('hospital_admin.pending_test_admins'))

        # Get the test admin record
        test_admin_records = db.get_by_field(TestAdmin, 'user_id', user_id)
        if not test_admin_records:
            flash('Test Admin record not found.', 'error')
            return redirect(url_for('hospital_admin.pending_test_admins'))

        test_admin = test_admin_records[0]

        # Helper function to normalize IDs for comparison
        def normalize_id(id_value):
            if id_value is None:
                return None
            # Convert UUID to string for comparison
            if isinstance(id_value, UUID):
                return str(id_value)
            # If already a string, return as is
            if isinstance(id_value, str):
                return id_value
            # Otherwise, convert to string
            return str(id_value)

        # Check if the test admin belongs to the same hospital as the hospital admin
        if normalize_id(test_admin.hospital_id) != normalize_id(hospital_admin.hospital_id):
            flash('You do not have permission to reject this Test Admin.', 'error')
            return redirect(url_for('hospital_admin.pending_test_admins'))

        # Update the user status to suspended (effectively rejecting them)
        user.status = UserStatus.SUSPENDED
        db.update(user)

        flash(f'Test Admin {test_admin.full_name} has been rejected.', 'success')

    except Exception as e:
        flash(f'Error rejecting Test Admin: {str(e)}', 'error')

    return redirect(url_for('hospital_admin.pending_test_admins'))