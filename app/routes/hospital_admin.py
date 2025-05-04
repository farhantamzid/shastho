from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length
from app.routes.auth import role_required, login_required
from app.utils.db import Database
from app.models.database import HospitalAdmin, Hospital, User, TestImageAdminRequest, AdminRequestStatus, UserRole, UserStatus
from uuid import UUID

hospital_admin_bp = Blueprint('hospital_admin', __name__, url_prefix='/hospital-admin')

# Initialize database
db = Database()

# Form for Test/Imaging Admin request
class TestImageAdminRequestForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    department = StringField('Department/Area', validators=[DataRequired(), Length(min=2, max=100)])
    qualification = StringField('Qualifications', validators=[DataRequired(), Length(min=2, max=200)])
    experience = TextAreaField('Experience', validators=[DataRequired(), Length(min=10, max=500)])
    reason = TextAreaField('Reason for Role Request', validators=[DataRequired(), Length(min=10, max=500)])

# Form for Hospital Admin profile updates
class HospitalAdminProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=5, max=200)])

@hospital_admin_bp.route('/')
@role_required(['hospital_admin'])
def dashboard():
    """Hospital Admin dashboard landing page."""
    # Get the current user's information
    user_id = session.get('user_id')

    # Get the hospital admin profile
    hospital_admin = db.get_by_field(HospitalAdmin, 'user_id', user_id)

    if not hospital_admin:
        flash('Hospital Administrator profile not found.', 'error')
        return redirect(url_for('main.index'))

    # Get the hospital information
    hospital = db.get_by_id(Hospital, hospital_admin.hospital_id)

    # Get all pending Test/Imaging Admin applications
    pending_requests = db.get_by_fields(
        TestImageAdminRequest,
        {
            'hospital_id': hospital_admin.hospital_id,
            'status': AdminRequestStatus.PENDING
        }
    )
    pending_requests_count = len(pending_requests)

    stats = {
        'hospital_name': hospital.name if hospital else "Unknown Hospital",
        'pending_requests_count': pending_requests_count,
    }

    return render_template(
        'hospital_admin/dashboard.html',
        stats=stats,
        hospital_admin=hospital_admin,
        pending_requests=pending_requests
    )

@hospital_admin_bp.route('/profile', methods=['GET', 'POST'])
@role_required(['hospital_admin'])
def profile():
    """View and update Hospital Admin profile."""
    # Get the current user's information
    user_id = session.get('user_id')

    # Get the hospital admin profile
    hospital_admin = db.get_by_field(HospitalAdmin, 'user_id', user_id)

    if not hospital_admin:
        flash('Hospital Administrator profile not found.', 'error')
        return redirect(url_for('main.index'))

    # Get the hospital information
    hospital = db.get_by_id(Hospital, hospital_admin.hospital_id)

    # Create form instance
    form = HospitalAdminProfileForm(obj=hospital_admin)

    if form.validate_on_submit():
        # Update the hospital admin profile
        hospital_admin.full_name = form.full_name.data
        hospital_admin.contact_number = form.contact_number.data
        hospital_admin.address = form.address.data
        hospital_admin.updated_at = db.get_current_time()

        # Save to database
        updated = db.update(hospital_admin)

        if updated:
            flash('Profile updated successfully!', 'success')
        else:
            flash('There was an error updating your profile. Please try again.', 'error')

    return render_template(
        'hospital_admin/profile.html',
        form=form,
        hospital_admin=hospital_admin,
        hospital=hospital
    )

@hospital_admin_bp.route('/admin-requests')
@role_required(['hospital_admin'])
def list_admin_requests():
    """List all Test/Imaging Admin requests with advanced filtering."""
    # Get the current user's information
    user_id = session.get('user_id')

    # Get the hospital admin profile
    hospital_admin = db.get_by_field(HospitalAdmin, 'user_id', user_id)

    if not hospital_admin:
        flash('Hospital Administrator profile not found.', 'error')
        return redirect(url_for('main.index'))

    # Get all admin requests for this hospital
    admin_requests = db.get_by_field(TestImageAdminRequest, 'hospital_id', hospital_admin.hospital_id)

    # Get filter parameters
    status_filter = request.args.get('status')
    search_query = request.args.get('search', '').strip().lower()
    sort_by = request.args.get('sort', 'created_at').lower()
    sort_dir = request.args.get('dir', 'desc').lower()
    department_filter = request.args.get('department')

    # Apply status filter
    if status_filter:
        try:
            status = AdminRequestStatus(status_filter)
            admin_requests = [req for req in admin_requests if req.status == status]
        except ValueError:
            # Invalid status, ignore filter
            pass

    # Apply department filter if provided
    if department_filter:
        admin_requests = [req for req in admin_requests if req.department.lower() == department_filter.lower()]

    # Apply search filter if provided
    if search_query:
        filtered_requests = []
        for req in admin_requests:
            # Search in multiple fields
            searchable_text = f"{req.full_name} {req.email} {req.department} {req.qualification}".lower()
            if search_query in searchable_text:
                filtered_requests.append(req)
        admin_requests = filtered_requests

    # Get unique departments for the filter dropdown
    all_departments = sorted(list(set(req.department for req in db.get_by_field(TestImageAdminRequest, 'hospital_id', hospital_admin.hospital_id))))

    # Sort the requests
    if sort_by == 'name':
        admin_requests = sorted(admin_requests, key=lambda r: r.full_name.lower(), reverse=(sort_dir == 'desc'))
    elif sort_by == 'department':
        admin_requests = sorted(admin_requests, key=lambda r: r.department.lower(), reverse=(sort_dir == 'desc'))
    elif sort_by == 'status':
        admin_requests = sorted(admin_requests, key=lambda r: r.status.value, reverse=(sort_dir == 'desc'))
    else:  # Default sort by created_at
        admin_requests = sorted(admin_requests, key=lambda r: r.created_at or db.get_current_time(), reverse=(sort_dir == 'desc'))

    # Count requests by status for statistics
    status_counts = {
        'total': len(db.get_by_field(TestImageAdminRequest, 'hospital_id', hospital_admin.hospital_id)),
        'pending': len([r for r in db.get_by_field(TestImageAdminRequest, 'hospital_id', hospital_admin.hospital_id)
                      if r.status == AdminRequestStatus.PENDING]),
        'approved': len([r for r in db.get_by_field(TestImageAdminRequest, 'hospital_id', hospital_admin.hospital_id)
                       if r.status == AdminRequestStatus.APPROVED]),
        'rejected': len([r for r in db.get_by_field(TestImageAdminRequest, 'hospital_id', hospital_admin.hospital_id)
                       if r.status == AdminRequestStatus.REJECTED])
    }

    return render_template(
        'hospital_admin/admin_requests.html',
        admin_requests=admin_requests,
        hospital_admin=hospital_admin,
        status_counts=status_counts,
        departments=all_departments,
        current_filters={
            'status': status_filter,
            'search': search_query,
            'sort': sort_by,
            'dir': sort_dir,
            'department': department_filter
        }
    )

@hospital_admin_bp.route('/new-admin-request', methods=['GET', 'POST'])
@role_required(['hospital_admin'])
def new_admin_request():
    """Create a new Test/Imaging Admin request."""
    # Get the current user's information
    user_id = session.get('user_id')

    # Get the hospital admin profile
    hospital_admin = db.get_by_field(HospitalAdmin, 'user_id', user_id)

    if not hospital_admin:
        flash('Hospital Administrator profile not found.', 'error')
        return redirect(url_for('main.index'))

    form = TestImageAdminRequestForm()

    if form.validate_on_submit():
        # Create a new request
        admin_request = TestImageAdminRequest(
            hospital_id=hospital_admin.hospital_id,
            full_name=form.full_name.data,
            email=form.email.data,
            contact_number=form.contact_number.data,
            department=form.department.data,
            qualification=form.qualification.data,
            experience=form.experience.data,
            reason=form.reason.data,
            submitted_by=UUID(user_id) if user_id else None,
            status=AdminRequestStatus.PENDING
        )

        # Save to database
        created_request = db.create(admin_request)

        if created_request:
            flash('Test/Imaging Admin request submitted successfully!', 'success')
            return redirect(url_for('hospital_admin.list_admin_requests'))
        else:
            flash('There was an error submitting the request. Please try again.', 'error')

    return render_template(
        'hospital_admin/new_admin_request.html',
        form=form,
        hospital_admin=hospital_admin
    )

@hospital_admin_bp.route('/admin-request/<request_id>/update-status', methods=['POST'])
@role_required(['hospital_admin'])
def update_admin_request_status(request_id):
    """Update the status of a Test/Imaging Admin request."""
    # Get the current user's information
    user_id = session.get('user_id')

    # Get the hospital admin profile
    hospital_admin = db.get_by_field(HospitalAdmin, 'user_id', user_id)

    if not hospital_admin:
        flash('Hospital Administrator profile not found.', 'error')
        return redirect(url_for('main.index'))

    # Get the request
    admin_request = db.get_by_id(TestImageAdminRequest, request_id)

    if not admin_request:
        flash('Admin request not found.', 'error')
        return redirect(url_for('hospital_admin.list_admin_requests'))

    # Verify the request belongs to this hospital admin's hospital
    if str(admin_request.hospital_id) != str(hospital_admin.hospital_id):
        flash('You do not have permission to update this request.', 'error')
        return redirect(url_for('hospital_admin.list_admin_requests'))

    # Get the new status from the form
    new_status = request.form.get('status')

    if not new_status or new_status not in [status.value for status in AdminRequestStatus]:
        flash('Invalid status value.', 'error')
        return redirect(url_for('hospital_admin.list_admin_requests'))

    # Update the request status
    admin_request.status = AdminRequestStatus(new_status)
    admin_request.updated_at = db.get_current_time()

    # Save the updated request
    updated = db.update(admin_request)

    if updated:
        if new_status == AdminRequestStatus.APPROVED.value:
            flash('Admin request has been approved. The user can now register with the approved email.', 'success')
            return redirect(url_for('hospital_admin.admin_approval_confirmation', request_id=request_id))
        else:
            flash('Admin request has been rejected.', 'success')
    else:
        flash('There was an error updating the request. Please try again.', 'error')

    return redirect(url_for('hospital_admin.list_admin_requests'))

@hospital_admin_bp.route('/admin-request/<request_id>/approval-confirmation')
@role_required(['hospital_admin'])
def admin_approval_confirmation(request_id):
    """Display confirmation page after approving an admin request."""
    # Get the current user's information
    user_id = session.get('user_id')

    # Get the hospital admin profile
    hospital_admin = db.get_by_field(HospitalAdmin, 'user_id', user_id)

    if not hospital_admin:
        flash('Hospital Administrator profile not found.', 'error')
        return redirect(url_for('main.index'))

    # Get the request
    admin_request = db.get_by_id(TestImageAdminRequest, request_id)

    if not admin_request:
        flash('Admin request not found.', 'error')
        return redirect(url_for('hospital_admin.list_admin_requests'))

    return render_template(
        'hospital_admin/approval_confirmation.html',
        admin_request=admin_request,
        hospital_admin=hospital_admin
    )

@hospital_admin_bp.route('/admin-request/<request_id>')
@role_required(['hospital_admin'])
def view_admin_request(request_id):
    """View details of a specific Test/Imaging Admin request."""
    # Get the current user's information
    user_id = session.get('user_id')

    # Get the hospital admin profile
    hospital_admin = db.get_by_field(HospitalAdmin, 'user_id', user_id)

    if not hospital_admin:
        flash('Hospital Administrator profile not found.', 'error')
        return redirect(url_for('main.index'))

    # Get the request
    admin_request = db.get_by_id(TestImageAdminRequest, request_id)

    if not admin_request:
        flash('Admin request not found.', 'error')
        return redirect(url_for('hospital_admin.list_admin_requests'))

    # Verify the request belongs to this hospital admin's hospital
    if str(admin_request.hospital_id) != str(hospital_admin.hospital_id):
        flash('You do not have permission to view this request.', 'error')
        return redirect(url_for('hospital_admin.list_admin_requests'))

    return render_template(
        'hospital_admin/view_admin_request.html',
        admin_request=admin_request,
        hospital_admin=hospital_admin
    )