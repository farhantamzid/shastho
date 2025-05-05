from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from app.routes.auth import role_required, login_required
from app.utils.db import Database
from app.models.database import Hospital, Department, HospitalAdmin, User, UserStatus, Doctor, DoctorNote, HospitalDepartment, parse_iso_datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Length, Optional
from uuid import UUID

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize database
db = Database()

class MultiCheckboxField(SelectMultipleField):
    """A multiple-select, except displays a list of checkboxes."""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

# Form definitions
class HospitalForm(FlaskForm):
    name = StringField('Hospital Name', validators=[DataRequired(), Length(min=2, max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(min=2, max=100)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=5, max=200)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    departments = MultiCheckboxField('Departments', coerce=str, validators=[Optional()])

class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired(), Length(min=2, max=100)])
    hospital_id = SelectField('Hospital', validators=[DataRequired()], coerce=str)

# Define a simple dummy form for CSRF token generation in modals
class DummyForm(FlaskForm):
    pass

@admin_bp.route('/')
@role_required(['admin'])
def dashboard():
    """Admin dashboard."""

    # Ensure common departments exist
    ensure_common_departments()

    # Count various entities for dashboard stats
    hospitals = db.get_all(Hospital)
    departments = db.get_all(Department)
    hospital_count = len(hospitals) if hospitals else 0
    department_count = len(departments) if departments else 0

    # Get pending admin applications
    from app.models.auth import find_users_by_role_and_status
    pending_admin_users = find_users_by_role_and_status('hospital_admin', UserStatus.INACTIVE)
    pending_admin_count = len(pending_admin_users) if pending_admin_users else 0

    # Get pending doctor applications
    pending_doctor_users = find_users_by_role_and_status('doctor', UserStatus.INACTIVE)
    pending_doctor_count = len(pending_doctor_users) if pending_doctor_users else 0

    # Prepare dashboard data
    stats = {
        'hospital_count': hospital_count,
        'department_count': department_count,
        'pending_admin_count': pending_admin_count,
        'pending_doctor_count': pending_doctor_count
    }

    # Get recent activity - for a real app, this could be audit logs or similar
    recent_activities = []

    return render_template('admin/dashboard.html', stats=stats, recent_activities=recent_activities)

def ensure_common_departments():
    """Ensure common department templates exist for hospital assignment."""
    common_departments = [
        {"name": "Emergency"},
        {"name": "Cardiology"},
        {"name": "Neurology"},
        {"name": "Orthopedics"},
        {"name": "Pediatrics"},
        {"name": "Oncology"},
        {"name": "Radiology"},
        {"name": "Obstetrics & Gynecology"},
        {"name": "Psychiatry"},
        {"name": "General Medicine"}
    ]

    # Get all departments
    all_departments = db.get_all(Department)
    existing_names = [d.name.lower() for d in all_departments]

    # Create any missing common departments
    for dept in common_departments:
        if dept["name"].lower() not in existing_names:
            new_dept = Department(
                name=dept["name"]
            )
            db.save(new_dept)

@admin_bp.route('/hospitals')
@role_required(['admin'])
def hospitals():
    """Hospital listing page."""
    # Get query parameters for searching and filtering
    search_query = request.args.get('search', '')

    # Get all hospitals
    hospitals = db.get_all(Hospital)

    # Filter hospitals if search query is provided
    if search_query:
        hospitals = [h for h in hospitals if search_query.lower() in h.name.lower() or
                     (h.location and search_query.lower() in h.location.lower())]

    return render_template('admin/hospitals.html', hospitals=hospitals, search_query=search_query)

@admin_bp.route('/hospitals/create', methods=['GET', 'POST'])
@role_required(['admin'])
def create_hospital():
    """Create a new hospital."""
    print("\n=== CREATE HOSPITAL ROUTE ===")
    print(f"Request method: {request.method}")

    form = HospitalForm()

    # Get all departments for selection
    all_departments = db.get_all(Department)
    print(f"Total departments available: {len(all_departments)}")

    if not all_departments:
        # Ensure we have common departments
        print("No departments found, creating common departments")
        ensure_common_departments()
        # Try again after ensuring departments exist
        all_departments = db.get_all(Department)
        print(f"After creating common departments, found {len(all_departments)} departments")

    # Set the choices for the department selection
    form.departments.choices = [(str(dep.id), dep.name) for dep in all_departments]

    if form.validate_on_submit():
        print("Form validated successfully")

        try:
            # Create a new hospital object
            hospital = Hospital(
                name=form.name.data,
                location=form.location.data,
                address=form.address.data,
                contact_number=form.contact_number.data
            )

            # Save the new hospital to the database
            print(f"Creating hospital: {hospital.name}")
            new_hospital = db.create(hospital)
            print(f"Hospital created with ID: {new_hospital.id}")

            # Get selected department IDs from form
            selected_department_ids = request.form.getlist('departments')
            print(f"Selected department IDs from form: {selected_department_ids}")

            # Create hospital-department relationships
            for dept_id in selected_department_ids:
                hospital_dept = HospitalDepartment(
                    hospital_id=new_hospital.id,
                    department_id=UUID(dept_id)
                )
                print(f"Creating relationship with department ID: {dept_id}")
                created_relation = db.create(hospital_dept)
                print(f"Relationship created with ID: {created_relation.id if created_relation else 'Failed'}")

            flash('Hospital created successfully!', 'success')
            return redirect(url_for('admin.hospitals'))

        except Exception as e:
            print(f"Error creating hospital: {str(e)}")
            import traceback
            print(traceback.format_exc())
            flash(f'Error creating hospital: {str(e)}', 'error')

    # If there are form errors
    if form.errors:
        print(f"Form has errors: {form.errors}")

    return render_template('admin/hospital_form.html', form=form, is_edit=False)

@admin_bp.route('/hospitals/<hospital_id>/edit', methods=['GET', 'POST'])
@role_required(['admin'])
def edit_hospital(hospital_id):
    """Edit an existing hospital."""
    print("\n=== EDIT HOSPITAL ROUTE ===")
    print(f"Hospital ID: {hospital_id}")
    print(f"Request method: {request.method}")

    # Get the hospital from the database
    hospital = db.get_by_id(Hospital, hospital_id)

    if not hospital:
        flash('Hospital not found.', 'error')
        return redirect(url_for('admin.hospitals'))

    print(f"Hospital found: {hospital.name}")

    # Create form and populate with hospital data
    form = HospitalForm(obj=hospital)

    # Get all departments for selection
    all_departments = db.get_all(Department)
    print(f"Total departments available: {len(all_departments)}")

    # Set department choices
    form.departments.choices = [(str(dep.id), dep.name) for dep in all_departments]

    # Get current hospital-department relationships
    hospital_departments = db.query(HospitalDepartment, hospital_id=hospital_id)
    print(f"Found {len(hospital_departments)} existing department relationships")

    # If this is GET request, set the current department selections
    if request.method == 'GET':
        # Extract current department IDs
        current_department_ids = [str(hd.department_id) for hd in hospital_departments]
        print(f"Current department IDs: {current_department_ids}")

        # Set the selected departments in the form
        form.departments.data = current_department_ids

    # Handle form submission
    if form.validate_on_submit():
        print("Form validated successfully")

        try:
            # Update hospital data
            hospital.name = form.name.data
            hospital.location = form.location.data
            hospital.address = form.address.data
            hospital.contact_number = form.contact_number.data

            # Save updated hospital
            print(f"Saving hospital: {hospital.name}")
            updated_hospital = db.save(hospital)
            print(f"Hospital saved with ID: {updated_hospital.id}")

            # Get selected department IDs from form
            selected_department_ids = request.form.getlist('departments')
            print(f"Selected department IDs from form: {selected_department_ids}")

            # Convert to UUID objects
            selected_department_uuids = [UUID(dept_id) for dept_id in selected_department_ids]

            # Get current department IDs
            current_department_uuids = [hd.department_id for hd in hospital_departments]

            # Find departments to add and remove
            departments_to_add = [dept_id for dept_id in selected_department_uuids
                                  if dept_id not in current_department_uuids]

            departments_to_remove = [hd for hd in hospital_departments
                                     if hd.department_id not in selected_department_uuids]

            print(f"Departments to add: {len(departments_to_add)}")
            print(f"Departments to remove: {len(departments_to_remove)}")

            # Add new department relationships
            for dept_id in departments_to_add:
                new_relation = HospitalDepartment(
                    hospital_id=updated_hospital.id,
                    department_id=dept_id
                )
                print(f"Creating relationship with department ID: {dept_id}")
                db.create(new_relation)

            # Remove old department relationships
            for hd in departments_to_remove:
                print(f"Removing relationship ID: {hd.id}")
                db.delete(HospitalDepartment, hd.id)

            flash('Hospital updated successfully!', 'success')
            return redirect(url_for('admin.hospitals'))

        except Exception as e:
            print(f"Error updating hospital: {str(e)}")
            import traceback
            print(traceback.format_exc())
            flash(f'Error updating hospital: {str(e)}', 'error')

    # If there are form errors
    if form.errors:
        print(f"Form has errors: {form.errors}")

    return render_template('admin/hospital_form.html', form=form, hospital=hospital, is_edit=True)

@admin_bp.route('/hospitals/<hospital_id>/delete', methods=['POST'])
@role_required(['admin'])
def delete_hospital(hospital_id):
    """Delete a hospital."""
    print(f"\n=== DELETE HOSPITAL ROUTE ===")
    print(f"Hospital ID: {hospital_id}")
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    print(f"Is AJAX request: {is_ajax}")

    try:
        # Get the hospital
        hospital = db.get_by_id(Hospital, hospital_id)

        if not hospital:
            print("Hospital not found")
            if is_ajax:
                return jsonify({
                    'success': False,
                    'message': 'Hospital not found.'
                }), 404

            flash('Hospital not found.', 'error')
            return redirect(url_for('admin.hospitals'))

        hospital_name = hospital.name
        print(f"Found hospital: {hospital_name}")

        # Check if the hospital has department relationships
        hospital_departments = db.query(HospitalDepartment, hospital_id=hospital_id)
        print(f"Found {len(hospital_departments)} department relationships")

        # Delete all hospital-department relationships first
        for hd in hospital_departments:
            print(f"Deleting relationship ID: {hd.id}")
            db.delete(HospitalDepartment, hd.id)

        # Now delete the hospital
        delete_result = db.delete(Hospital, hospital_id)
        print(f"Hospital deletion result: {delete_result}")

        if is_ajax:
            return jsonify({
                'success': True,
                'message': f'Hospital "{hospital_name}" deleted successfully.'
            })

        flash(f'Hospital "{hospital_name}" deleted successfully.', 'success')
        return redirect(url_for('admin.hospitals'))

    except Exception as e:
        print(f"Error deleting hospital: {str(e)}")
        import traceback
        print(traceback.format_exc())

        if is_ajax:
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500

        flash(f'Error deleting hospital: {str(e)}', 'error')
        return redirect(url_for('admin.hospitals'))

@admin_bp.route('/departments')
@role_required(['admin'])
def departments():
    """Department listing page."""
    print("\n=== DEPARTMENTS ROUTE ===")

    # Get query parameters for searching and filtering
    search_query = request.args.get('search', '')
    hospital_id = request.args.get('hospital_id', '')

    print(f"Search query: '{search_query}'")
    print(f"Hospital filter: '{hospital_id}'")

    # Get all departments
    all_departments = db.get_all(Department)
    print(f"Total departments: {len(all_departments)}")

    # Filter departments if search query is provided
    if search_query:
        all_departments = [d for d in all_departments if search_query.lower() in d.name.lower()]
        print(f"After search filter, {len(all_departments)} departments remain")

    # Get all hospital-department relationships
    all_hospital_departments = db.get_all(HospitalDepartment)
    print(f"Total hospital-department relationships: {len(all_hospital_departments)}")

    # Get all hospitals for lookup
    hospitals = {str(h.id): h for h in db.get_all(Hospital)}
    print(f"Total hospitals: {len(hospitals)}")

    # For each department, find its hospitals
    departments_with_hospitals = []
    for dept in all_departments:
        dept_id = str(dept.id)

        # Find all relationships for this department
        dept_hospital_rels = [hd for hd in all_hospital_departments if str(hd.department_id) == dept_id]
        print(f"Department '{dept.name}' has {len(dept_hospital_rels)} hospital relationships")

        # Get hospital info for each relationship
        dept_hospitals = []
        for hd in dept_hospital_rels:
            h_id = str(hd.hospital_id)
            if h_id in hospitals:
                dept_hospitals.append({
                    'id': h_id,
                    'rel_id': str(hd.id),  # Include relationship ID for deletion
                    'name': hospitals[h_id].name
                })

        # Filter by hospital if specified
        if hospital_id and not any(h['id'] == hospital_id for h in dept_hospitals):
            continue

        # Add department with its hospitals to the result list
        departments_with_hospitals.append({
            'department': dept,
            'hospitals': dept_hospitals
        })

    print(f"Final departments to display: {len(departments_with_hospitals)}")
    return render_template('admin/departments.html', departments=departments_with_hospitals)

@admin_bp.route('/hospital-departments/<hospital_department_id>/delete', methods=['POST'])
@role_required(['admin'])
def delete_hospital_department(hospital_department_id):
    """Remove a department from a specific hospital."""
    print(f"\n=== DELETE HOSPITAL-DEPARTMENT ROUTE ===")
    print(f"Relationship ID: {hospital_department_id}")
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    print(f"Is AJAX request: {is_ajax}")

    try:
        # Get the hospital-department relationship
        hospital_dept = db.get_by_id(HospitalDepartment, hospital_department_id)

        if not hospital_dept:
            print(f"Hospital-Department relationship not found with ID: {hospital_department_id}")
            if is_ajax:
                return jsonify({
                    'success': False,
                    'message': 'Hospital-Department relationship not found.'
                }), 404

            flash('Hospital-Department relationship not found.', 'error')
            return redirect(url_for('admin.departments'))

        print(f"Found relationship: hospital_id={hospital_dept.hospital_id}, department_id={hospital_dept.department_id}")

        # Delete the relationship
        delete_result = db.delete(HospitalDepartment, hospital_department_id)
        print(f"Delete result: {delete_result}")

        if is_ajax:
            return jsonify({
                'success': True,
                'message': 'Department removed from hospital successfully.'
            })

        flash('Department removed from hospital successfully.', 'success')
        return redirect(url_for('admin.departments'))

    except Exception as e:
        print(f"Error deleting hospital-department relationship: {str(e)}")
        import traceback
        print(traceback.format_exc())

        if is_ajax:
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500

        flash(f'Error removing department from hospital: {str(e)}', 'error')
        return redirect(url_for('admin.departments'))

@admin_bp.route('/pending-admins')
@role_required(['admin'])
def pending_admins():
    """View pending Hospital Admin applications."""
    # Get all users with Hospital Admin role and pending status
    from app.models.auth import find_users_by_role_and_status
    pending_admins = find_users_by_role_and_status('hospital_admin', UserStatus.INACTIVE)

    # Get additional hospital admin info for each user
    admin_details = []
    for user in pending_admins:
        # Find the HospitalAdmin record(s) for this user
        hospital_admin_records = db.get_by_field(HospitalAdmin, 'user_id', user.id)

        # Check if any records were found
        if hospital_admin_records:
            # Use the first record found (assuming one user maps to one hospital admin role for now)
            hospital_admin = hospital_admin_records[0]

            # Ensure created_at is a datetime object
            if isinstance(hospital_admin.created_at, str):
                hospital_admin.created_at = parse_iso_datetime(hospital_admin.created_at)

            # Get the hospital name
            hospital = db.get_by_id(Hospital, hospital_admin.hospital_id) if hospital_admin.hospital_id else None
            hospital_name = hospital.name if hospital else "Unknown Hospital"

            admin_details.append({
                'user': user,
                'admin': hospital_admin, # Use the single hospital_admin object
                'hospital_name': hospital_name
            })
        # Optional: Add an else block here to handle cases where a user has the role but no HospitalAdmin record exists, if necessary.
        # else:
        #     # Handle case where HospitalAdmin record is missing for a pending user
        #     print(f"Warning: User {user.id} has pending hospital_admin role but no HospitalAdmin record.")
        #     # Optionally append with default/error values or skip

    # Create a dummy form instance for CSRF token
    form = DummyForm()

    return render_template('admin/pending_admins.html', admin_details=admin_details, form=form)

@admin_bp.route('/pending-admins/<user_id>/approve', methods=['POST'])
@role_required(['admin'])
def approve_admin(user_id):
    """Approve a Hospital Admin application."""
    # Find the user
    from app.models.auth import find_user_by_id, update_user_status
    user = find_user_by_id(user_id)

    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.pending_admins'))

    # Update user status to ACTIVE
    success = update_user_status(user_id, UserStatus.ACTIVE)

    if success:
        # TODO: In a real application, send an email notification to the user
        flash('Hospital Admin approved successfully. They can now log in.', 'success')
    else:
        flash('Failed to approve Hospital Admin.', 'error')

    return redirect(url_for('admin.pending_admins'))

@admin_bp.route('/pending-admins/<user_id>/reject', methods=['POST'])
@role_required(['admin'])
def reject_admin(user_id):
    """Reject a Hospital Admin application."""
    # Find the user
    from app.models.auth import find_user_by_id, update_user_status
    user = find_user_by_id(user_id)

    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.pending_admins'))

    # Update user status to SUSPENDED (rejected)
    success = update_user_status(user_id, UserStatus.SUSPENDED)

    if success:
        # TODO: In a real application, send an email notification to the user
        flash('Hospital Admin application rejected.', 'success')
    else:
        flash('Failed to reject Hospital Admin application.', 'error')

    return redirect(url_for('admin.pending_admins'))

# Doctor application management routes
@admin_bp.route('/pending-doctors')
@role_required(['admin'])
def pending_doctors():
    """List of pending doctor applications."""
    # Get query parameters for searching and filtering
    search_query = request.args.get('search', '')

    # Find users with doctor role and inactive status
    from app.models.auth import find_users_by_role_and_status
    from app.models.database import UserStatus

    pending_doctor_users = find_users_by_role_and_status('doctor', UserStatus.INACTIVE)

    # --- DEBUGGING --- #
    print(f"\nDEBUG: Found {len(pending_doctor_users)} users with role='doctor' and status='inactive'")
    for u in pending_doctor_users:
        print(f"  - User ID: {u.id}, Username: {u.username}, Status: {u.status}")
    # --- END DEBUGGING --- #

    # Get the complete doctor info for each user
    from app.models.database import Doctor
    from app.utils.db import db

    pending_doctors = []
    for user in pending_doctor_users:
        # Query the doctor record using the user_id
        doctor_records = db.query(Doctor, user_id=user.id)
        if doctor_records:
            doctor = doctor_records[0]

            # Get hospital and department info
            hospital = db.get_by_id(Hospital, doctor.hospital_id) if doctor.hospital_id else None
            department = db.get_by_id(Department, doctor.department_id) if doctor.department_id else None

            # Create a combined record
            doctor_info = {
                'user_id': str(user.id),
                'username': user.username,
                'full_name': doctor.full_name,
                'specialization': doctor.specialization,
                'credentials': doctor.credentials,
                'contact_number': doctor.contact_number,
                'hospital_id': str(doctor.hospital_id) if doctor.hospital_id else None,
                'hospital_name': hospital.name if hospital else "Unknown Hospital",
                'department_id': str(doctor.department_id) if doctor.department_id else None,
                'department_name': department.name if department else "Unknown Department",
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else "Unknown"
            }

            # Filter by search query if provided
            if search_query:
                if (search_query.lower() in doctor_info['full_name'].lower() or
                    search_query.lower() in doctor_info['specialization'].lower() or
                    search_query.lower() in doctor_info['username'].lower() or
                    search_query.lower() in doctor_info['hospital_name'].lower() or
                    search_query.lower() in doctor_info['department_name'].lower()):
                    pending_doctors.append(doctor_info)
            else:
                pending_doctors.append(doctor_info)

    # Create an instance of the dummy form
    dummy_form = DummyForm()

    return render_template('admin/pending_doctors.html',
                           pending_doctors=pending_doctors,
                           search_query=search_query,
                           count=len(pending_doctors),
                           dummy_form=dummy_form)

@admin_bp.route('/pending-doctors/<user_id>/approve', methods=['POST'])
@role_required(['admin'])
def approve_doctor(user_id):
    """Approve a doctor application."""
    # Get the user
    from app.models.auth import find_user_by_id, update_user_status
    from app.models.database import UserStatus, Doctor, DoctorNote
    from app.utils.db import db
    from flask import session as flask_session

    user = find_user_by_id(user_id)

    if not user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'User not found.'}), 404

        flash('User not found.', 'error')
        return redirect(url_for('admin.pending_doctors'))

    # Update the user status to active
    updated = update_user_status(user.id, UserStatus.ACTIVE)

    if updated:
        # Get notes if provided
        notes = request.form.get('notes', '')
        if notes:
            # Get doctor record
            doctor_records = db.query(Doctor, user_id=user.id)
            if doctor_records:
                doctor = doctor_records[0]
                # Create note record
                doctor_note = DoctorNote(
                    doctor_id=doctor.id,
                    note_type='approval',
                    content=notes,
                    created_by=flask_session.get('user_id')
                )
                db.create(doctor_note)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Doctor application approved.'})

        flash('Doctor application approved.', 'success')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Failed to approve doctor application.'}), 500

        flash('Failed to approve doctor application.', 'error')

    return redirect(url_for('admin.pending_doctors'))

@admin_bp.route('/pending-doctors/<user_id>/reject', methods=['POST'])
@role_required(['admin'])
def reject_doctor(user_id):
    """Reject a doctor application."""
    # Get the user
    from app.models.auth import find_user_by_id, update_user_status
    from app.models.database import UserStatus, Doctor, DoctorNote
    from app.utils.db import db
    from flask import session as flask_session

    user = find_user_by_id(user_id)

    if not user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'User not found.'}), 404

        flash('User not found.', 'error')
        return redirect(url_for('admin.pending_doctors'))

    # Update the user status to suspended (rejected)
    updated = update_user_status(user.id, UserStatus.SUSPENDED)

    if updated:
        # Get rejection reason if provided
        reason = request.form.get('reason', '')
        if reason:
            # Get doctor record
            doctor_records = db.query(Doctor, user_id=user.id)
            if doctor_records:
                doctor = doctor_records[0]
                # Create note record
                doctor_note = DoctorNote(
                    doctor_id=doctor.id,
                    note_type='rejection',
                    content=reason,
                    created_by=flask_session.get('user_id')
                )
                db.create(doctor_note)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Doctor application rejected.'})

        flash('Doctor application rejected.', 'success')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Failed to reject doctor application.'}), 500

        flash('Failed to reject doctor application.', 'error')

    return redirect(url_for('admin.pending_doctors'))