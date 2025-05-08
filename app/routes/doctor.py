from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SearchField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from app.models.database import UserRole, Doctor, Hospital, Department, DoctorAvailabilitySlot, Patient
from app.models.auth import find_user_by_id
from app.utils.auth import login_required, role_required
from app.utils.db import Database
from app.models.ehr import EHR, EHR_Visit, EHR_Diagnosis, EHR_Medication, EHR_Allergy, EHR_Procedure, EHR_Vital, EHR_Immunization, EHR_TestResult, EHR_ProviderNote, Prescription
from app.services.ehr_service import search_patients, get_patient_ehr, get_visit_details, get_ehr_visits, get_ehr_allergies, get_ehr_immunizations, get_ehr_test_results
from app.services.doctor_service import (
    get_doctor_by_user_id, get_doctor_availability_slots,
    update_doctor_profile, update_doctor_profile_picture,
    get_doctor_hospital_info, add_availability_slot,
    delete_availability_slot, update_availability_slot, # Corrected names
    bulk_update_availability
)
from app.forms.ehr_forms import DiagnosisForm, MedicationForm, PrescriptionForm, AllergyForm, VitalSignsForm, ProviderNoteForm, TestResultForm, ProcedureForm, ImmunizationForm
from datetime import datetime, date
from uuid import UUID
import os
from werkzeug.utils import secure_filename
import math

# Assuming current_user is available globally or passed appropriately
# If using Flask-Login, it's usually available after login
from flask_login import current_user

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

class DoctorProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    specialization = StringField('Specialization', validators=[DataRequired(), Length(min=3, max=100)])
    credentials = TextAreaField('Credentials', validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=20)])

class ProfilePictureForm(FlaskForm):
    picture = FileField('Profile Picture', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])

class PatientSearchForm(FlaskForm):
    """Enhanced form for searching patients by various criteria"""
    search_term = SearchField('Search by ID, Name or Date of Birth', validators=[DataRequired()])
    page = IntegerField('Page', validators=[Optional(), NumberRange(min=1)], default=1)
    per_page = SelectField('Results per page',
                          choices=[(10, '10'), (20, '20'), (50, '50'), (100, '100')],
                          validators=[Optional()],
                          default=20,
                          coerce=int)
    filter_name = BooleanField('Search by Name', default=True)
    filter_email = BooleanField('Search by Email')
    filter_id = BooleanField('Search by ID')

@doctor_bp.route('/dashboard')
@login_required
@role_required(UserRole.DOCTOR)
def dashboard():
    """
    Doctor dashboard showing overview of appointments, patients, and records
    """
    user_id = session.get('user_id')

    # Placeholder for stats data (in a real app, this would be queried from DB)
    stats = {
        'today_appointments': 0,
        'patient_count': 0,
        'pending_records': 0
    }

    # Placeholder for upcoming appointments (in a real app, this would be queried from DB)
    upcoming_appointments = []

    return render_template('doctor/dashboard.html',
                           stats=stats,
                           upcoming_appointments=upcoming_appointments)

@doctor_bp.route('/profile')
@login_required
@role_required(UserRole.DOCTOR)
def profile():
    """
    Doctor profile page where the doctor can view and update their information
    """
    user_id = session.get('user_id')
    user = find_user_by_id(user_id)

    if not user:
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('auth.login'))

    # Get doctor information
    # In a real app, this would be retrieved from your database
    doctor = get_doctor_by_user_id(user_id)
    if not doctor:
        flash('Doctor profile not found. Please contact support.', 'error')
        return redirect(url_for('auth.profile'))

    # Get hospital and department info
    hospital_name, department_name = get_doctor_hospital_info(doctor.hospital_id, doctor.department_id)

    # Get doctor availability slots
    # In a real app, this would be retrieved from your database
    availability_slots = get_doctor_availability_slots(doctor.id)

    return render_template('doctor/profile.html',
                          user_email=user.username,
                          doctor=doctor,
                          hospital_name=hospital_name,
                          department_name=department_name,
                          availability_slots=availability_slots)

@doctor_bp.route('/update-profile', methods=['POST'])
@login_required
@role_required(UserRole.DOCTOR)
def update_profile():
    """
    Update doctor profile information
    """
    user_id = session.get('user_id')
    form = DoctorProfileForm()

    if form.validate_on_submit():
        # Update doctor information in the database
        # In a real app, this would be a call to your database service
        success = update_doctor_profile(
            user_id=user_id,
            full_name=form.full_name.data,
            specialization=form.specialization.data,
            credentials=form.credentials.data,
            contact_number=form.contact_number.data
        )

        if success:
            flash('Profile updated successfully!', 'success')
        else:
            flash('Failed to update profile. Please try again.', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'error')

    return redirect(url_for('doctor.profile'))

@doctor_bp.route('/upload-profile-picture', methods=['POST'])
@login_required
@role_required(UserRole.DOCTOR)
def upload_profile_picture():
    """
    Upload doctor profile picture
    """
    form = ProfilePictureForm()
    if form.validate_on_submit():
        user_id = session.get('user_id')

        try:
            # Get the uploaded file
            file = form.picture.data

            # Create a secure filename
            filename = secure_filename(f"doctor_{user_id}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}")

            # Ensure directory exists
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'images', 'profile_pictures')
            os.makedirs(upload_folder, exist_ok=True)

            # Save the file
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            # Update doctor profile picture URL in database
            # In a real app, this would be a call to your database service
            success = update_doctor_profile_picture(user_id, f"/static/images/profile_pictures/{filename}")

            if success:
                flash('Profile picture updated successfully!', 'success')
            else:
                flash('Failed to update profile picture. Please try again.', 'error')

        except Exception as e:
            flash(f'Error uploading profile picture: {str(e)}', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'error')

    return redirect(url_for('doctor.profile'))

@doctor_bp.route('/patient-search', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.DOCTOR)
def patient_search():
    """
    Enhanced search for patients by ID, name, or date of birth with pagination and fuzzy matching
    """
    form = PatientSearchForm()
    patients = []
    search_performed = False
    search_term = ""
    pagination = {
        'page': 1,
        'per_page': 20,
        'total_pages': 1,
        'total_items': 0
    }

    if request.method == 'POST' and form.validate_on_submit():
        search_term = form.search_term.data
        page = form.page.data
        per_page = form.per_page.data
        search_performed = True

        # Get filter states
        search_by_name = form.filter_name.data
        search_by_email = form.filter_email.data
        search_by_id = form.filter_id.data

        # Calculate offset for pagination
        offset = (page - 1) * per_page

        # Use our new enhanced search function from ehr_service
        patients = search_patients(
            search_term=search_term,
            search_by_name=search_by_name,
            search_by_email=search_by_email,
            search_by_id=search_by_id,
            limit=per_page,
            offset=offset
        )

        # For pagination, we need to know the total number of matches
        # This is a simplified approach - in production, you'd want to optimize this
        all_matching_patients = search_patients(
            search_term=search_term,
            search_by_name=search_by_name,
            search_by_email=search_by_email,
            search_by_id=search_by_id
            # No limit/offset for count
        )

        total_items = len(all_matching_patients)
        total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1

        pagination = {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_items': total_items
        }

    # Handle GET requests with query parameters for pagination links
    elif request.method == 'GET' and 'search_term' in request.args:
        search_term = request.args.get('search_term', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search_performed = True

        # Get filter states from query args
        search_by_name = request.args.get('filter_name', 'true').lower() == 'true'
        search_by_email = request.args.get('filter_email', 'false').lower() == 'true'
        search_by_id = request.args.get('filter_id', 'false').lower() == 'true'

        # Fill the form with values from query parameters for consistent UI
        form.search_term.data = search_term
        form.filter_name.data = search_by_name
        form.filter_email.data = search_by_email
        form.filter_id.data = search_by_id
        form.page.data = page
        form.per_page.data = per_page

        # Calculate offset for pagination
        offset = (page - 1) * per_page

        # Use our new enhanced search function from ehr_service
        patients = search_patients(
            search_term=search_term,
            search_by_name=search_by_name,
            search_by_email=search_by_email,
            search_by_id=search_by_id,
            limit=per_page,
            offset=offset
        )

        # For pagination count
        all_matching_patients = search_patients(
            search_term=search_term,
            search_by_name=search_by_name,
            search_by_email=search_by_email,
            search_by_id=search_by_id
        )

        total_items = len(all_matching_patients)
        total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1

        pagination = {
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_items': total_items
        }

    return render_template('doctor/ehr/patient_search.html',
                          form=form,
                          patients=patients,
                          search_performed=search_performed,
                          search_term=search_term,
                          pagination=pagination)

@doctor_bp.route('/patient/<uuid:patient_id>/ehr')
@login_required
@role_required(UserRole.DOCTOR)
def view_ehr(patient_id):
    """
    View a patient's EHR
    Enhanced to use the new ehr_service
    """
    # Get patient information
    db = Database()
    patient = db.get_by_id(Patient, patient_id)

    if not patient:
        flash('Patient not found.', 'error')
        return redirect(url_for('doctor.patient_search'))

    # Get the patient's EHR using our service function
    ehr, has_ehr = get_patient_ehr(patient_id)

    # If patient doesn't have an EHR, we still show the patient info
    # but indicate no EHR data is available
    if not has_ehr:
        return render_template('doctor/ehr/view_ehr.html',
                              patient=patient,
                              has_ehr=False)

    # If EHR exists, get related data
    from app.services.ehr_service import (
        get_ehr_visits,
        get_ehr_allergies,
        get_ehr_immunizations,
        get_ehr_test_results
    )

    # Get visits (most recent first)
    visits = get_ehr_visits(ehr.id)

    # Get other EHR sections
    allergies = get_ehr_allergies(ehr.id)
    immunizations = get_ehr_immunizations(ehr.id)
    test_results = get_ehr_test_results(ehr.id)

    # Process visit data for display
    visits_with_details = []
    for visit in visits:
        # Get visit details
        visit_details = get_visit_details(visit.id)
        visits_with_details.append({
            'visit': visit,
            'diagnoses': visit_details.get('diagnoses', []),
            'medications': visit_details.get('medications', []),
            'procedures': visit_details.get('procedures', []),
            'vitals': visit_details.get('vitals', []),
            'notes': visit_details.get('notes', [])
        })

    return render_template('doctor/ehr/view_ehr.html',
                          patient=patient,
                          has_ehr=True,
                          ehr=ehr,
                          visits=visits_with_details,
                          allergies=allergies,
                          immunizations=immunizations,
                          test_results=test_results)

@doctor_bp.route('/patient/<uuid:patient_id>/ehr/visit/<uuid:visit_id>')
@login_required
@role_required(UserRole.DOCTOR)
def view_visit_details(patient_id, visit_id):
    """
    View details for a specific EHR visit
    Enhanced to use the new ehr_service
    """
    # Get patient information
    db = Database()
    patient = db.get_by_id(Patient, patient_id)

    if not patient:
        flash('Patient not found.', 'error')
        return redirect(url_for('doctor.patient_search'))

    # Get visit details using our service function
    from app.services.ehr_service import get_visit_details

    visit_data = get_visit_details(visit_id)
    if not visit_data or 'visit' not in visit_data:
        flash('Visit not found.', 'error')
        return redirect(url_for('doctor.view_ehr', patient_id=patient_id))

    return render_template('doctor/ehr/visit_details.html',
                          patient=patient,
                          visit=visit_data['visit'],
                          diagnoses=visit_data.get('diagnoses', []),
                          medications=visit_data.get('medications', []),
                          procedures=visit_data.get('procedures', []),
                          vitals=visit_data.get('vitals', []),
                          notes=visit_data.get('notes', []))

@doctor_bp.route('/patient/<uuid:patient_id>/visit/<uuid:visit_id>/diagnosis/add', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.DOCTOR)
def add_diagnosis(patient_id, visit_id):
    """
    Add a new diagnosis to a visit
    """
    # Get patient and visit information
    db = Database()
    patient = db.get_by_id(Patient, patient_id)
    visit = db.get_by_id(EHR_Visit, visit_id)

    if not patient or not visit:
        flash('Patient or visit not found.', 'error')
        return redirect(url_for('doctor.patient_search'))

    # Initialize form
    form = DiagnosisForm()
    form.visit_id.data = str(visit_id)

    # Default date to visit date or today
    if not form.diagnosed_at.data:
        form.diagnosed_at.data = visit.date or date.today()

    if request.method == 'POST' and form.validate_on_submit():
        try:
            user_id = session.get('user_id')
            if not user_id:
                flash('User session not found. Please log in again.', 'error')
                return redirect(url_for('auth.login'))

            # Fetch the doctor ID corresponding to the user ID
            doctor = db.get_by_field(Doctor, 'user_id', user_id)
            if not doctor:
                flash('Associated doctor profile not found.', 'error')
                # Redirect somewhere appropriate, maybe profile or dashboard
                return redirect(url_for('doctor.profile'))
            doctor_id = doctor[0].id # Assuming get_by_field returns a list

            # Create new diagnosis using the doctor_id
            diagnosis = EHR_Diagnosis(
                visit_id=visit_id,
                diagnosis_code=form.diagnosis_code.data,
                diagnosis_description=form.diagnosis_description.data,
                diagnosed_by=doctor_id,
                diagnosed_at=form.diagnosed_at.data,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            # Save to database
            created_diagnosis = db.create(diagnosis)

            if created_diagnosis:
                flash('Diagnosis added successfully.', 'success')
                return redirect(url_for('doctor.view_visit_details', patient_id=patient_id, visit_id=visit_id))
            else:
                flash('Failed to add diagnosis to the database.', 'error')

        except Exception as e:
            flash(f'Error adding diagnosis: {str(e)}', 'error')

    # Format the visit date for display
    visit_date = visit.date.strftime('%Y-%m-%d') if visit.date else 'N/A'

    return render_template('doctor/ehr/add_diagnosis.html',
                           form=form,
                           patient=patient,
                           visit_id=visit_id,
                           visit_date=visit_date)

@doctor_bp.route('/ehr/patient/<uuid:patient_id>/diagnosis/<uuid:diagnosis_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.DOCTOR)
def edit_diagnosis(patient_id, diagnosis_id):
    """Route to edit an existing diagnosis for a patient."""
    db = Database()
    patient = db.get_by_id(Patient, patient_id)
    diagnosis = db.get_by_id(EHR_Diagnosis, diagnosis_id)

    if not patient or not diagnosis:
        flash('Patient or Diagnosis record not found.', 'danger')
        # Redirect to a sensible place, maybe patient search or dashboard
        return redirect(url_for('doctor.patient_search'))

    # Corrected Ownership Check for Diagnosis (via Visit)
    visit = db.get_by_id(EHR_Visit, diagnosis.visit_id)
    ehr, _ = get_patient_ehr(patient_id)
    if not visit or not ehr or visit.ehr_id != ehr.id:
        flash('Invalid diagnosis record for this patient.', 'danger')
        return redirect(url_for('doctor.view_ehr', patient_id=patient_id))

    form = DiagnosisForm(obj=diagnosis) # Populate form with existing data on GET

    if form.validate_on_submit():
        try:
            # Update model object attributes
            diagnosis.diagnosis_code = form.diagnosis_code.data
            diagnosis.diagnosis_description = form.diagnosis_description.data
            diagnosis.diagnosed_at = form.diagnosed_at.data
            diagnosis.additional_notes = form.additional_notes.data
            diagnosis.updated_at = datetime.now() # Update timestamp

            # Use the custom DB utility to update
            db.update(diagnosis)

            flash('Diagnosis updated successfully!', 'success')
            return redirect(url_for('doctor.view_ehr', patient_id=patient_id) + '#summary') # Redirect back to EHR summary
        except Exception as e:
            # db.update likely handles rollback, but log/flash error
            flash(f'Error updating diagnosis: {str(e)}', 'danger')
    elif request.method == 'POST':
        flash('Please correct the errors below.', 'warning')

    return render_template('doctor/ehr/edit_diagnosis.html',
                           form=form,
                           patient=patient,
                           diagnosis=diagnosis)

@doctor_bp.route('/patient/<uuid:patient_id>/visit/<uuid:visit_id>/medication/add', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.DOCTOR)
def add_medication(patient_id, visit_id):
    """
    Add a new medication to a visit
    """
    # Get patient and visit information
    db = Database()
    patient = db.get_by_id(Patient, patient_id)
    visit = db.get_by_id(EHR_Visit, visit_id)

    if not patient or not visit:
        flash('Patient or visit not found.', 'error')
        return redirect(url_for('doctor.patient_search'))

    # Initialize form
    form = MedicationForm()
    form.visit_id.data = str(visit_id)

    # Default date to visit date or today
    if not form.start_date.data:
        form.start_date.data = visit.date or date.today()

    if request.method == 'POST' and form.validate_on_submit():
        try:
            user_id = session.get('user_id')
            if not user_id:
                flash('User session not found. Please log in again.', 'error')
                return redirect(url_for('auth.login'))

            # Fetch the doctor ID corresponding to the user ID
            doctor = db.get_by_field(Doctor, 'user_id', user_id)
            if not doctor:
                flash('Associated doctor profile not found.', 'error')
                return redirect(url_for('doctor.profile'))
            doctor_id = doctor[0].id

            # Create new medication using the doctor_id
            medication = EHR_Medication(
                visit_id=visit_id,
                medication_name=form.medication_name.data,
                dosage=form.dosage.data,
                frequency=form.frequency.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                prescribed_by=doctor_id,
                prescribed_at=datetime.now(),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            # Save to database
            created_medication = db.create(medication)

            if created_medication:
                flash('Medication added successfully.', 'success')
                return redirect(url_for('doctor.view_visit_details', patient_id=patient_id, visit_id=visit_id))
            else:
                flash('Failed to add medication to the database.', 'error')

        except Exception as e:
            flash(f'Error adding medication: {str(e)}', 'error')

    # Format the visit date for display
    visit_date = visit.date.strftime('%Y-%m-%d') if visit.date else 'N/A'

    return render_template('doctor/ehr/add_medication.html',
                           form=form,
                           patient=patient,
                           visit_id=visit_id,
                           visit_date=visit_date)

@doctor_bp.route('/ehr/patient/<uuid:patient_id>/medication/<uuid:medication_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.DOCTOR)
def edit_medication(patient_id, medication_id):
    """Route to edit an existing medication for a patient."""
    db = Database()
    patient = db.get_by_id(Patient, patient_id)
    medication = db.get_by_id(EHR_Medication, medication_id)

    if not patient or not medication:
        flash('Patient or Medication record not found.', 'danger')
        return redirect(url_for('doctor.patient_search'))

    # Corrected Ownership Check for Medication (via Visit)
    visit = db.get_by_id(EHR_Visit, medication.visit_id)
    ehr, _ = get_patient_ehr(patient_id)
    if not visit or not ehr or visit.ehr_id != ehr.id:
         flash('Invalid medication record for this patient.', 'danger')
         return redirect(url_for('doctor.view_ehr', patient_id=patient_id))

    form = MedicationForm(obj=medication)

    if form.validate_on_submit():
        try:
            medication.medication_name = form.medication_name.data
            medication.dosage = form.dosage.data
            medication.frequency = form.frequency.data
            medication.start_date = form.start_date.data
            medication.end_date = form.end_date.data
            medication.instructions = form.instructions.data
            medication.updated_at = datetime.now()

            db.update(medication)

            flash('Medication updated successfully!', 'success')
            return redirect(url_for('doctor.view_ehr', patient_id=patient_id) + '#summary')
        except Exception as e:
            flash(f'Error updating medication: {str(e)}', 'danger')
    elif request.method == 'POST':
        flash('Please correct the errors below.', 'warning')

    return render_template('doctor/ehr/edit_medication.html',
                           form=form,
                           patient=patient,
                           medication=medication)

@doctor_bp.route('/patient/<uuid:patient_id>/visit/<uuid:visit_id>/diagnosis/<uuid:diagnosis_id>/delete', methods=['POST'])
@login_required
@role_required(UserRole.DOCTOR)
def delete_diagnosis(patient_id, visit_id, diagnosis_id):
    """
    Delete a diagnosis
    """
    db = Database()
    diagnosis = db.get_by_id(EHR_Diagnosis, diagnosis_id)

    if not diagnosis or str(diagnosis.visit_id) != str(visit_id):
        flash('Diagnosis not found or does not belong to this visit.', 'error')
    else:
        try:
            db.delete(diagnosis)
            flash('Diagnosis deleted successfully.', 'success')
        except Exception as e:
            flash(f'Error deleting diagnosis: {str(e)}', 'error')

    return redirect(url_for('doctor.view_visit_details', patient_id=patient_id, visit_id=visit_id))

@doctor_bp.route('/patient/<uuid:patient_id>/visit/<uuid:visit_id>/medication/<uuid:medication_id>/delete', methods=['POST'])
@login_required
@role_required(UserRole.DOCTOR)
def delete_medication(patient_id, visit_id, medication_id):
    """Delete a medication record from a visit"""
    try:
        # Check if the medication exists and belongs to this visit
        medication = db.get_by_id(EHR_Medication, medication_id)
        if not medication or str(medication.visit_id) != str(visit_id):
            flash('Medication not found or does not belong to this visit.', 'error')
            return redirect(url_for('doctor.view_visit_details', patient_id=patient_id, visit_id=visit_id))

        # Delete the medication record
        db.delete(EHR_Medication, medication_id)
        flash('Medication record deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting medication record: {str(e)}', 'error')

    return redirect(url_for('doctor.view_visit_details', patient_id=patient_id, visit_id=visit_id))

@doctor_bp.route('/patient/<uuid:patient_id>/visit/<uuid:visit_id>/note/add', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.DOCTOR)
def add_note(patient_id, visit_id):
    """Add a new provider note to a visit"""
    # Create the form
    form = ProviderNoteForm()
    form.visit_id.data = str(visit_id)
    form.note_date.data = date.today()

    # Get visit data for context
    visit_data = get_visit_details(visit_id)
    visit = visit_data.get('visit')

    if not visit:
        flash('Visit not found.', 'error')
        return redirect(url_for('doctor.view_ehr', patient_id=patient_id))

    if form.validate_on_submit():
        try:
            # Determine what fields to use based on note type
            note_text = form.note_text.data

            # For SOAP notes, compile the structured data
            if form.note_type.data == 'soap':
                soap_note = f"SUBJECTIVE:\n{form.subjective.data or 'None documented'}\n\n"
                soap_note += f"OBJECTIVE:\n{form.objective.data or 'None documented'}\n\n"
                soap_note += f"ASSESSMENT:\n{form.assessment.data or 'None documented'}\n\n"
                soap_note += f"PLAN:\n{form.plan.data or 'None documented'}"
                note_text = soap_note

            user_id = session.get('user_id')
            if not user_id:
                flash('User session not found. Please log in again.', 'error')
                return redirect(url_for('auth.login'))

            # Fetch the doctor ID corresponding to the user ID
            doctor = db.get_by_field(Doctor, 'user_id', user_id)
            if not doctor:
                flash('Associated doctor profile not found.', 'error')
                return redirect(url_for('doctor.profile'))
            doctor_id = doctor[0].id

            # Create the note using the doctor_id
            note = EHR_ProviderNote(
                visit_id=visit_id,
                note_text=note_text,
                created_by=doctor_id
            )

            # Save to database
            created_note = db.create(note)

            if created_note:
                flash('Provider note added successfully.', 'success')
                return redirect(url_for('doctor.view_visit_details', patient_id=patient_id, visit_id=visit_id))
            else:
                flash('Failed to add provider note to the database.', 'error')

        except Exception as e:
            flash(f'Error adding provider note: {str(e)}', 'error')

    return render_template('doctor/ehr/add_note.html',
                          form=form,
                          patient_id=patient_id,
                          visit=visit,
                          action='Add')

@doctor_bp.route('/patient/<uuid:patient_id>/visit/<uuid:visit_id>/note/<uuid:note_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.DOCTOR)
def edit_note(patient_id, visit_id, note_id):
    """Edit an existing provider note"""
    # Get the note
    note = db.get_by_id(EHR_ProviderNote, note_id)

    if not note or str(note.visit_id) != str(visit_id):
        flash('Note not found or does not belong to this visit.', 'error')
        return redirect(url_for('doctor.view_visit_details', patient_id=patient_id, visit_id=visit_id))

    # Get visit data for context
    visit_data = get_visit_details(visit_id)
    visit = visit_data.get('visit')

    if not visit:
        flash('Visit not found.', 'error')
        return redirect(url_for('doctor.view_ehr', patient_id=patient_id))

    # Create and populate the form
    form = ProviderNoteForm()
    form.visit_id.data = str(visit_id)

    if request.method == 'GET':
        # Check if this is a SOAP note by looking for the structure
        if 'SUBJECTIVE:' in note.note_text and 'OBJECTIVE:' in note.note_text and 'ASSESSMENT:' in note.note_text and 'PLAN:' in note.note_text:
            form.note_type.data = 'soap'

            # Extract SOAP components
            try:
                sections = note.note_text.split('\n\n')
                form.subjective.data = sections[0].replace('SUBJECTIVE:', '').strip()
                form.objective.data = sections[1].replace('OBJECTIVE:', '').strip()
                form.assessment.data = sections[2].replace('ASSESSMENT:', '').strip()
                form.plan.data = sections[3].replace('PLAN:', '').strip()
            except:
                # If extraction fails, just use the whole note
                form.note_text.data = note.note_text
        else:
            # For other note types
            form.note_type.data = 'other'  # Default to 'other' if we can't determine type
            form.note_text.data = note.note_text

        form.note_date.data = note.created_at.date()

    if form.validate_on_submit():
        try:
            # Determine what fields to use based on note type
            note_text = form.note_text.data

            # For SOAP notes, compile the structured data
            if form.note_type.data == 'soap':
                soap_note = f"SUBJECTIVE:\n{form.subjective.data or 'None documented'}\n\n"
                soap_note += f"OBJECTIVE:\n{form.objective.data or 'None documented'}\n\n"
                soap_note += f"ASSESSMENT:\n{form.assessment.data or 'None documented'}\n\n"
                soap_note += f"PLAN:\n{form.plan.data or 'None documented'}"
                note_text = soap_note

            # Update the note
            note.note_text = note_text
            note.updated_at = datetime.now()

            # Save to database
            db.update(note)
            flash('Provider note updated successfully.', 'success')
            return redirect(url_for('doctor.view_visit_details', patient_id=patient_id, visit_id=visit_id))
        except Exception as e:
            flash(f'Error updating provider note: {str(e)}', 'error')

    return render_template('doctor/ehr/add_note.html',
                          form=form,
                          patient_id=patient_id,
                          visit=visit,
                          note_id=note_id,
                          action='Edit')

@doctor_bp.route('/patient/<uuid:patient_id>/visit/<uuid:visit_id>/note/<uuid:note_id>/delete', methods=['POST'])
@login_required
@role_required(UserRole.DOCTOR)
def delete_note(patient_id, visit_id, note_id):
    """Delete a provider note from a visit"""
    try:
        # Check if the note exists and belongs to this visit
        note = db.get_by_id(EHR_ProviderNote, note_id)
        if not note or str(note.visit_id) != str(visit_id):
            flash('Note not found or does not belong to this visit.', 'error')
            return redirect(url_for('doctor.view_visit_details', patient_id=patient_id, visit_id=visit_id))

        # Delete the note
        db.delete(EHR_ProviderNote, note_id)
        flash('Provider note deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting provider note: {str(e)}', 'error')

    return redirect(url_for('doctor.view_visit_details', patient_id=patient_id, visit_id=visit_id))

@doctor_bp.route('/ehr/patient/<uuid:patient_id>/allergy/<uuid:allergy_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.DOCTOR)
def edit_allergy(patient_id, allergy_id):
    """Route to edit an existing allergy for a patient."""
    db = Database()
    patient = db.get_by_id(Patient, patient_id)
    allergy = db.get_by_id(EHR_Allergy, allergy_id)

    if not patient or not allergy:
        flash('Patient or Allergy record not found.', 'danger')
        return redirect(url_for('doctor.patient_search'))

    ehr, _ = get_patient_ehr(patient_id)
    if not ehr or allergy.ehr_id != ehr.id:
        flash('Invalid allergy record for this patient.', 'danger')
        return redirect(url_for('doctor.view_ehr', patient_id=patient_id))

    form = AllergyForm(obj=allergy)

    if form.validate_on_submit():
        try:
            allergy.allergen = form.allergen.data
            allergy.reaction = form.reaction.data
            allergy.severity = form.severity.data # Assuming severity maps correctly
            allergy.onset_date = form.onset_date.data
            allergy.updated_at = datetime.now()

            db.update(allergy)

            flash('Allergy updated successfully!', 'success')
            return redirect(url_for('doctor.view_ehr', patient_id=patient_id) + '#allergies')
        except Exception as e:
            flash(f'Error updating allergy: {str(e)}', 'danger')
    elif request.method == 'POST':
        flash('Please correct the errors below.', 'warning')

    return render_template('doctor/ehr/edit_allergy.html',
                           form=form,
                           patient=patient,
                           allergy=allergy)

@doctor_bp.route('/ehr/patient/<uuid:patient_id>/immunization/<uuid:immunization_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.DOCTOR)
def edit_immunization(patient_id, immunization_id):
    """Route to edit an existing immunization for a patient."""
    db = Database()
    patient = db.get_by_id(Patient, patient_id)
    immunization = db.get_by_id(EHR_Immunization, immunization_id)

    if not patient or not immunization:
        flash('Patient or Immunization record not found.', 'danger')
        return redirect(url_for('doctor.patient_search'))

    ehr, _ = get_patient_ehr(patient_id)
    if not ehr or immunization.ehr_id != ehr.id:
         flash('Invalid immunization record for this patient.', 'danger')
         return redirect(url_for('doctor.view_ehr', patient_id=patient_id))

    form = ImmunizationForm(obj=immunization)

    if form.validate_on_submit():
        try:
            immunization.vaccine = form.vaccine.data
            immunization.date_administered = form.date_administered.data
            immunization.administered_by = form.administered_by.data
            immunization.updated_at = datetime.now()

            db.update(immunization)

            flash('Immunization updated successfully!', 'success')
            return redirect(url_for('doctor.view_ehr', patient_id=patient_id) + '#immunizations')
        except Exception as e:
            flash(f'Error updating immunization: {str(e)}', 'danger')
    elif request.method == 'POST':
        flash('Please correct the errors below.', 'warning')

    return render_template('doctor/ehr/edit_immunization.html',
                           form=form,
                           patient=patient,
                           immunization=immunization)

@doctor_bp.route('/ehr/patient/<uuid:patient_id>/test_result/<uuid:test_result_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.DOCTOR)
def edit_test_result(patient_id, test_result_id):
    """Route to edit an existing test result for a patient."""
    db = Database()
    patient = db.get_by_id(Patient, patient_id)
    test_result = db.get_by_id(EHR_TestResult, test_result_id)

    if not patient or not test_result:
        flash('Patient or Test Result record not found.', 'danger')
        return redirect(url_for('doctor.patient_search'))

    ehr, _ = get_patient_ehr(patient_id)
    if not ehr or test_result.ehr_id != ehr.id:
        flash('Invalid test result record for this patient.', 'danger')
        return redirect(url_for('doctor.view_ehr', patient_id=patient_id))

    form = TestResultForm(obj=test_result)

    if form.validate_on_submit():
        try:
            test_result.test_name = form.test_name.data # Check model field name (TestResult model uses test_type)
            test_result.test_date = form.test_date.data
            test_result.result_data = form.test_result.data # Model uses result_data (dict), form uses test_result (TextArea)? Might need adjustment.
            test_result.updated_at = datetime.now()

            # Handle file upload logic separately if needed (see comments in original route)

            db.update(test_result)

            flash('Test Result updated successfully!', 'success')
            return redirect(url_for('doctor.view_ehr', patient_id=patient_id) + '#test-results')
        except Exception as e:
            flash(f'Error updating test result: {str(e)}', 'danger')
    elif request.method == 'POST':
        flash('Please correct the errors below.', 'warning')

    return render_template('doctor/ehr/edit_test_result.html',
                           form=form,
                           patient=patient,
                           test_result=test_result)

@doctor_bp.route('/availability')
@login_required
@role_required(UserRole.DOCTOR)
def availability():
    """Doctor availability management page"""
    user_id = session.get('user_id')
    doctor = get_doctor_by_user_id(user_id)
    if not doctor:
        flash("Doctor profile not found.", "error")
        return redirect(url_for('doctor.profile'))

    # Fetch existing slots to pass to the template
    slots = get_doctor_availability_slots(doctor.id)

    # Prepare data for the form if needed (e.g., for editing)
    # This part depends on how you want to handle editing in the template
    # For now, just passing existing slots.

    return render_template('doctor/availability.html', doctor=doctor, slots=slots)

@doctor_bp.route('/availability/slots', methods=['GET'])
@login_required
@role_required(UserRole.DOCTOR)
def get_availability_slots():
    """Get all availability slots for current doctor"""
    user_id = session.get('user_id')
    doctor = get_doctor_by_user_id(user_id)

    if not doctor:
        return jsonify({"success": False, "message": "Doctor not found"}), 404

    slots = get_doctor_availability_slots(doctor.id)
    print(f"Found {len(slots)} availability slots for doctor")

    # Format slots for frontend
    formatted_slots = []
    for slot in slots:
        # Format the time object to string (HH:MM format)
        try:
            start_time_str = slot.start_time.strftime('%H:%M') if slot.start_time else None
            end_time_str = slot.end_time.strftime('%H:%M') if slot.end_time else None

            formatted_slot = {
                'id': str(slot.id),
                'day_of_week': slot.day_of_week,
                'start_time': start_time_str,
                'end_time': end_time_str,
                'is_available': slot.is_available,
                'slot_duration_minutes': slot.slot_duration_minutes
            }
            formatted_slots.append(formatted_slot)
        except Exception as e:
            print(f"Error formatting slot {slot.id}: {str(e)}")

    return jsonify({"success": True, "slots": formatted_slots})

@doctor_bp.route('/availability/add', methods=['POST'])
@login_required
@role_required(UserRole.DOCTOR)
def add_availability_slot_route():
    """Add a new availability slot for the current doctor"""
    data = request.get_json()
    user_id = session.get('user_id')
    doctor = get_doctor_by_user_id(user_id)

    if not doctor:
        return jsonify({"success": False, "message": "Doctor not found"}), 404

    day_of_week = data.get('day_of_week')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')
    is_available = data.get('is_available', True) # Default to True
    slot_duration_minutes = data.get('slot_duration_minutes', 30) # Default to 30 minutes

    if not all([day_of_week is not None, start_time_str, end_time_str]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
    except ValueError:
        return jsonify({"success": False, "message": "Invalid time format. Use HH:MM"}), 400

    # Call the enhanced service function that now returns the created slot
    created_slot = add_availability_slot(
        doctor.id, int(day_of_week), start_time, end_time, slot_duration_minutes
    )

    if created_slot:
        # Return the created slot data for the frontend
        return jsonify({
            "success": True,
            "message": "Slot added successfully",
            "slot": {
                "id": str(created_slot.id),
                "day_of_week": created_slot.day_of_week,
                "start_time": start_time_str,
                "end_time": end_time_str,
                "is_available": created_slot.is_available,
                "slot_duration_minutes": created_slot.slot_duration_minutes
            }
        }), 201
    else:
        return jsonify({"success": False, "message": "Failed to add availability slot"}), 500

@doctor_bp.route('/availability/save', methods=['POST'])
@login_required
@role_required(UserRole.DOCTOR)
def save_availability():
    """Save/Update multiple availability slots for the current doctor"""
    try:
        data = request.get_json()
        slots_data = data.get('slots', [])
        user_id = session.get('user_id')

        print(f"Processing availability save request for user_id: {user_id}")
        print(f"Received {len(slots_data)} slots to save")

        doctor = get_doctor_by_user_id(user_id)
        if not doctor:
            print(f"Doctor not found for user_id: {user_id}")
            return jsonify({"success": False, "message": "Doctor not found"}), 404

        if not isinstance(slots_data, list):
            print(f"Invalid slots data format: {type(slots_data)}")
            return jsonify({"success": False, "message": "Invalid slots data format"}), 400

        if len(slots_data) == 0:
            return jsonify({"success": False, "message": "No slots provided"}), 400

        # Validate each slot before processing
        for i, slot in enumerate(slots_data):
            # Check for required fields
            if 'day_of_week' not in slot:
                return jsonify({"success": False, "message": f"Slot #{i+1} missing day_of_week"}), 400
            if 'start_time' not in slot:
                return jsonify({"success": False, "message": f"Slot #{i+1} missing start_time"}), 400
            if 'end_time' not in slot:
                return jsonify({"success": False, "message": f"Slot #{i+1} missing end_time"}), 400

            # Validate day_of_week is in range
            if not (0 <= int(slot['day_of_week']) <= 6):
                return jsonify({"success": False, "message": f"Slot #{i+1} has invalid day_of_week: must be 0-6"}), 400

            # Validate time format
            try:
                datetime.strptime(slot['start_time'], '%H:%M')
                datetime.strptime(slot['end_time'], '%H:%M')
            except ValueError:
                return jsonify({"success": False, "message": f"Slot #{i+1} has invalid time format. Use HH:MM"}), 400

            # Validate end time is after start time
            if slot['start_time'] >= slot['end_time']:
                return jsonify({
                    "success": False,
                    "message": f"Slot #{i+1} has end time before or equal to start time"
                }), 400

        # Add doctor_id to each slot to ensure it's associated with correct doctor
        for slot in slots_data:
            slot['doctor_id'] = str(doctor.id)

        print(f"Sending {len(slots_data)} slots to bulk_update_availability")
        # Print sample slot for debugging
        if slots_data:
            print(f"Sample slot: {slots_data[0]}")

        # Use the enhanced bulk update function from service
        success = bulk_update_availability(slots_data)

        if success:
            print("Availability update successful")
            return jsonify({"success": True, "message": "Availability updated successfully."}), 200
        else:
            print("Availability update failed")
            return jsonify({"success": False, "message": "Failed to update availability. Please try again."}), 500
    except Exception as e:
        print(f"Exception in save_availability: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@doctor_bp.route('/availability/delete/<slot_id>', methods=['DELETE'])
@login_required
@role_required(UserRole.DOCTOR)
def delete_availability_slot_route(slot_id):
    """Delete an availability slot"""
    user_id = session.get('user_id')
    doctor = get_doctor_by_user_id(user_id)
    if not doctor:
        return jsonify({"success": False, "message": "Doctor not found"}), 404

    try:
        slot_uuid = UUID(slot_id)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid slot ID format"}), 400

    # Verify the slot belongs to the doctor before deleting
    # This is a security check to prevent deleting other doctors' slots
    slots = get_doctor_availability_slots(doctor.id)
    slot_belongs_to_doctor = any(str(slot.id) == slot_id for slot in slots)

    if not slot_belongs_to_doctor:
        return jsonify({"success": False, "message": "Access denied: Slot does not belong to this doctor"}), 403

    # Call the service function
    success = delete_availability_slot(slot_uuid)

    if success:
        return jsonify({"success": True, "message": "Availability slot deleted successfully"}), 200
    else:
        return jsonify({"success": False, "message": "Error: Failed to delete availability slot"}), 500

@doctor_bp.route('/availability/booking-slots', methods=['GET'])
@login_required
def get_doctor_booking_slots():
    """Get available booking slots for a specific doctor and date"""
    doctor_id = request.args.get('doctor_id')
    date = request.args.get('date')

    if not doctor_id or not date:
        return jsonify({"success": False, "message": "Missing required parameters: doctor_id and date"}), 400

    try:
        doctor_uuid = UUID(doctor_id)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid doctor ID format"}), 400

    # Validate date format (should be YYYY-MM-DD)
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"success": False, "message": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Get available booking slots using the new service function
    slots = get_available_booking_slots(doctor_uuid, date)

    return jsonify({
        "success": True,
        "slots": slots
    })