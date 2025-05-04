from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from app.routes.auth import role_required, login_required
from app.utils.db import Database
from app.models.database import Hospital, Department
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize database
db = Database()

# Form definitions
class HospitalForm(FlaskForm):
    name = StringField('Hospital Name', validators=[DataRequired(), Length(min=2, max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(min=2, max=100)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=5, max=200)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])

class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired(), Length(min=2, max=100)])
    hospital_id = SelectField('Hospital', validators=[DataRequired()], coerce=str)
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])

@admin_bp.route('/')
@role_required(['admin'])
def dashboard():
    """Admin dashboard landing page."""
    # Get count of hospitals and departments for dashboard overview
    hospitals = db.get_all(Hospital)
    departments = db.get_all(Department)

    hospital_count = len(hospitals)
    department_count = len(departments)

    stats = {
        'hospital_count': hospital_count,
        'department_count': department_count,
    }

    return render_template('admin/dashboard.html', stats=stats)

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
    form = HospitalForm()

    if form.validate_on_submit():
        # Create a new hospital object
        hospital = Hospital(
            name=form.name.data,
            location=form.location.data,
            address=form.address.data,
            contact_number=form.contact_number.data,
            description=form.description.data
        )

        # Save the hospital to the database
        saved_hospital = db.save(hospital)

        if saved_hospital:
            flash('Hospital created successfully!', 'success')
            return redirect(url_for('admin.hospitals'))
        else:
            flash('Failed to create hospital.', 'error')

    return render_template('admin/hospital_form.html', form=form, is_edit=False)

@admin_bp.route('/hospitals/<hospital_id>/edit', methods=['GET', 'POST'])
@role_required(['admin'])
def edit_hospital(hospital_id):
    """Edit an existing hospital."""
    # Get the hospital from the database
    hospital = db.get_by_id(Hospital, hospital_id)

    if not hospital:
        flash('Hospital not found.', 'error')
        return redirect(url_for('admin.hospitals'))

    form = HospitalForm(obj=hospital)

    if form.validate_on_submit():
        # Update hospital with form data
        hospital.name = form.name.data
        hospital.location = form.location.data
        hospital.address = form.address.data
        hospital.contact_number = form.contact_number.data
        hospital.description = form.description.data

        # Save the updated hospital
        updated_hospital = db.save(hospital)

        if updated_hospital:
            flash('Hospital updated successfully!', 'success')
            return redirect(url_for('admin.hospitals'))
        else:
            flash('Failed to update hospital.', 'error')

    return render_template('admin/hospital_form.html', form=form, hospital=hospital, is_edit=True)

@admin_bp.route('/hospitals/<hospital_id>/delete', methods=['POST'])
@role_required(['admin'])
def delete_hospital(hospital_id):
    """Delete a hospital."""
    # Check if the hospital has departments
    departments = db.get_by_field(Department, 'hospital_id', hospital_id)

    if departments:
        # Return a JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': f'Cannot delete this hospital because it has {len(departments)} department(s) associated with it. Please delete or reassign the departments first.'
            }), 400

        # Regular form submission
        flash(f'Cannot delete this hospital because it has {len(departments)} department(s) associated with it. Please delete or reassign the departments first.', 'error')
        return redirect(url_for('admin.hospitals'))

    # Get the hospital
    hospital = db.get_by_id(Hospital, hospital_id)

    if not hospital:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Hospital not found.'}), 404

        flash('Hospital not found.', 'error')
        return redirect(url_for('admin.hospitals'))

    # Delete the hospital
    deleted = db.delete(hospital)

    if deleted:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Hospital deleted successfully.'})

        flash('Hospital deleted successfully.', 'success')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Failed to delete hospital.'}), 500

        flash('Failed to delete hospital.', 'error')

    return redirect(url_for('admin.hospitals'))

@admin_bp.route('/departments')
@role_required(['admin'])
def departments():
    """Department listing page."""
    # Get query parameters for searching and filtering
    search_query = request.args.get('search', '')
    hospital_id = request.args.get('hospital_id', '')

    # Get all departments
    departments = db.get_all(Department)

    # Filter departments if search query is provided
    if search_query:
        departments = [d for d in departments if search_query.lower() in d.name.lower()]

    # Filter by hospital if specified
    if hospital_id:
        departments = [d for d in departments if str(d.hospital_id) == hospital_id]

    # Get all hospitals for filtering
    hospitals = db.get_all(Hospital)

    # Create a mapping of hospital IDs to names for display
    hospital_names = {str(h.id): h.name for h in hospitals}

    return render_template('admin/departments.html',
                          departments=departments,
                          search_query=search_query,
                          hospital_id=hospital_id,
                          hospitals=hospitals,
                          hospital_names=hospital_names)

@admin_bp.route('/departments/create', methods=['GET', 'POST'])
@role_required(['admin'])
def create_department():
    """Create a new department."""
    form = DepartmentForm()

    # Get hospitals for dropdown
    hospitals = db.get_all(Hospital)
    form.hospital_id.choices = [(str(h.id), h.name) for h in hospitals]

    if form.validate_on_submit():
        # Create a new department object
        department = Department(
            name=form.name.data,
            hospital_id=form.hospital_id.data,
            description=form.description.data if hasattr(form, 'description') else None
        )

        # Save the department to the database
        saved_department = db.save(department)

        if saved_department:
            flash('Department created successfully!', 'success')
            return redirect(url_for('admin.departments'))
        else:
            flash('Failed to create department.', 'error')

    return render_template('admin/department_form.html', form=form, is_edit=False)

@admin_bp.route('/departments/<department_id>/edit', methods=['GET', 'POST'])
@role_required(['admin'])
def edit_department(department_id):
    """Edit an existing department."""
    # Get the department from the database
    department = db.get_by_id(Department, department_id)

    if not department:
        flash('Department not found.', 'error')
        return redirect(url_for('admin.departments'))

    form = DepartmentForm(obj=department)

    # Get hospitals for dropdown
    hospitals = db.get_all(Hospital)
    form.hospital_id.choices = [(str(h.id), h.name) for h in hospitals]

    if form.validate_on_submit():
        # Update department with form data
        department.name = form.name.data
        department.hospital_id = form.hospital_id.data
        if hasattr(form, 'description'):
            department.description = form.description.data

        # Save the updated department
        updated_department = db.save(department)

        if updated_department:
            flash('Department updated successfully!', 'success')
            return redirect(url_for('admin.departments'))
        else:
            flash('Failed to update department.', 'error')

    return render_template('admin/department_form.html', form=form, department=department, is_edit=True)

@admin_bp.route('/departments/<department_id>/delete', methods=['POST'])
@role_required(['admin'])
def delete_department(department_id):
    """Delete a department."""
    # Get the department
    department = db.get_by_id(Department, department_id)

    if not department:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Department not found.'}), 404

        flash('Department not found.', 'error')
        return redirect(url_for('admin.departments'))

    # Delete the department
    deleted = db.delete(department)

    if deleted:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Department deleted successfully.'})

        flash('Department deleted successfully.', 'success')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Failed to delete department.'}), 500

        flash('Failed to delete department.', 'error')

    return redirect(url_for('admin.departments'))