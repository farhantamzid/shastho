from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SearchField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from app.models.database import UserRole, Doctor, Hospital, Department, DoctorAvailabilitySlot, Patient
from app.models.auth import find_user_by_id
from app.utils.auth import login_required, role_required
from app.utils.db import Database
from app.models.ehr import EHR_Visit, EHR_Diagnosis, EHR_Medication, EHR_ProviderNote
from app.services.ehr_service import search_patients, get_patient_ehr, get_visit_details, get_ehr_visits, get_ehr_allergies, get_ehr_immunizations, get_ehr_test_results
from app.forms.ehr_forms import DiagnosisForm, MedicationForm, PrescriptionForm, AllergyForm, VitalSignsForm, ProviderNoteForm
from datetime import datetime, date
from uuid import UUID
import os
from werkzeug.utils import secure_filename
import math

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
    from app.services.doctor_service import get_doctor_by_user_id, get_doctor_hospital_info

    doctor = get_doctor_by_user_id(user_id)
    if not doctor:
        flash('Doctor profile not found. Please contact support.', 'error')
        return redirect(url_for('auth.profile'))

    # Get hospital and department info
    hospital_name, department_name = get_doctor_hospital_info(doctor.hospital_id, doctor.department_id)

    # Get doctor availability slots
    # In a real app, this would be retrieved from your database
    from app.services.doctor_service import get_doctor_availability_slots

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
        from app.services.doctor_service import update_doctor_profile

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
            from app.services.doctor_service import update_doctor_profile_picture

            relative_path = f"/static/images/profile_pictures/{filename}"
            success = update_doctor_profile_picture(user_id, relative_path)

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

@doctor_bp.route('/patient/<uuid:patient_id>/visit/<uuid:visit_id>/diagnosis/<uuid:diagnosis_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.DOCTOR)
def edit_diagnosis(patient_id, visit_id, diagnosis_id):
    """
    Edit an existing diagnosis
    """
    # Get patient, visit, and diagnosis information
    db = Database()
    patient = db.get_by_id(Patient, patient_id)
    visit = db.get_by_id(EHR_Visit, visit_id)
    diagnosis = db.get_by_id(EHR_Diagnosis, diagnosis_id)

    if not patient or not visit or not diagnosis:
        flash('Patient, visit, or diagnosis not found.', 'error')
        return redirect(url_for('doctor.patient_search'))

    # Initialize form
    form = DiagnosisForm(obj=diagnosis)
    form.visit_id.data = str(visit_id)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Update diagnosis
            diagnosis.diagnosis_code = form.diagnosis_code.data
            diagnosis.diagnosis_description = form.diagnosis_description.data
            diagnosis.diagnosed_at = form.diagnosed_at.data
            diagnosis.updated_at = datetime.now()

            # Save to database
            db.update(diagnosis)

            flash('Diagnosis updated successfully.', 'success')
            return redirect(url_for('doctor.view_visit_details', patient_id=patient_id, visit_id=visit_id))
        except Exception as e:
            flash(f'Error updating diagnosis: {str(e)}', 'error')

    # Format the visit date for display
    visit_date = visit.date.strftime('%Y-%m-%d') if visit.date else 'N/A'

    return render_template('doctor/ehr/add_diagnosis.html',
                           form=form,
                           patient=patient,
                           visit_id=visit_id,
                           visit_date=visit_date,
                           is_edit=True)

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

@doctor_bp.route('/patient/<uuid:patient_id>/visit/<uuid:visit_id>/medication/<uuid:medication_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.DOCTOR)
def edit_medication(patient_id, visit_id, medication_id):
    """
    Edit an existing medication
    """
    # Get patient, visit, and medication information
    db = Database()
    patient = db.get_by_id(Patient, patient_id)
    visit = db.get_by_id(EHR_Visit, visit_id)
    medication = db.get_by_id(EHR_Medication, medication_id)

    if not patient or not visit or not medication:
        flash('Patient, visit, or medication not found.', 'error')
        return redirect(url_for('doctor.patient_search'))

    # Initialize form
    form = MedicationForm(obj=medication)
    form.visit_id.data = str(visit_id)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Update medication
            medication.medication_name = form.medication_name.data
            medication.dosage = form.dosage.data
            medication.frequency = form.frequency.data
            medication.start_date = form.start_date.data
            medication.end_date = form.end_date.data
            medication.updated_at = datetime.now()

            # Save to database
            db.update(medication)

            flash('Medication updated successfully.', 'success')
            return redirect(url_for('doctor.view_visit_details', patient_id=patient_id, visit_id=visit_id))
        except Exception as e:
            flash(f'Error updating medication: {str(e)}', 'error')

    # Format the visit date for display
    visit_date = visit.date.strftime('%Y-%m-%d') if visit.date else 'N/A'

    return render_template('doctor/ehr/add_medication.html',
                           form=form,
                           patient=patient,
                           visit_id=visit_id,
                           visit_date=visit_date,
                           is_edit=True)

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