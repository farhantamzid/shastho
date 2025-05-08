from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.utils.auth import login_required, role_required
from app.models.database import UserRole, Patient, Hospital, Department, Doctor, Appointment, AppointmentStatus, HospitalDepartment
from app.utils.db import Database
# from app.utils.audit import audit_decorator, AuditResourceType, AuditActionType # Removed audit import
from app.utils.validation import patient_validation_rules, ValidationResult
from datetime import datetime, date, time, timedelta
import uuid
import secrets

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')
db = Database()

# Placeholder route - add actual patient routes here later
@patient_bp.route('/')
@login_required
@role_required(UserRole.DOCTOR, UserRole.HOSPITAL_ADMIN) # Adjust roles as needed
def patient_list():
    # Add logic to fetch and display patients
    patients = [] # Replace with actual db query
    return render_template('doctor/patient_list.html', patients=patients) # Assuming template exists

# Patient dashboard
@patient_bp.route('/dashboard')
@login_required
@role_required(UserRole.PATIENT)
def dashboard():
    # Get the user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash('Unable to identify user', 'error')
        return redirect(url_for('auth.login'))

    # Find the patient profile associated with this user
    try:
        # Query patient by user_id
        patients = db.query(Patient, user_id=str(user_id))
        if not patients or len(patients) == 0:
            flash('Patient profile not found', 'error')
            print(f"No patient profile found for user_id: {user_id}")
            return render_template('patient/dashboard.html', appointments=[])

        patient = patients[0]
        patient_id = patient.id
        print(f"Found patient: {patient.full_name} with ID: {patient_id}")
    except Exception as e:
        print(f"Error finding patient profile: {str(e)}")
        flash('Error accessing patient profile', 'error')
        return render_template('patient/dashboard.html', appointments=[])

    # Initialize an empty list for appointments
    formatted_appointments = []

    # Only try to fetch appointments if we have a valid patient_id
    try:
        # Use get_appointments_by_patient method
        all_appointments = db.get_appointments_by_patient(patient_id)

        # Filter appointments in Python for pending and future appointments
        today = date.today()
        appointments = [
            appt for appt in all_appointments
            if appt.date >= today and appt.status == AppointmentStatus.SCHEDULED.value
        ]

        # Sort appointments by date (ascending)
        appointments.sort(key=lambda x: x.date)

        # Format appointments for display with doctor and hospital info
        for appt in appointments:
            doctor = db.get_by_id(Doctor, appt.doctor_id)
            hospital = db.get_by_id(Hospital, appt.hospital_id)
            department = db.get_by_id(Department, appt.department_id)

            # Parse the time_slot which is stored as tstzrange in the database
            time_slot = appt.time_slot
            if isinstance(time_slot, str):
                # Parse the time slot string format like: ["2023-01-01 09:00:00+00","2023-01-01 09:30:00+00")
                start_time = time_slot.strip('["').split(',')[0].strip('"')
                start_time = datetime.fromisoformat(start_time.replace('+00', '+00:00')).strftime('%I:%M %p')
            else:
                start_time = "Time not available"

            formatted_appointments.append({
                'id': appt.id,
                'date': appt.date,
                'time': start_time,
                'doctor_name': doctor.full_name if doctor else 'Unknown',
                'hospital_name': hospital.name if hospital else 'Unknown',
                'department_name': department.name if department else 'Unknown',
                'status': appt.status
            })
    except Exception as e:
        # Log the error and show a flash message
        print(f"Error fetching appointments: {str(e)}")
        flash(f"Error loading appointments: {str(e)}", "error")

    return render_template('patient/dashboard.html', appointments=formatted_appointments)

# Start appointment booking flow
@patient_bp.route('/appointments/book', methods=['GET'])
@login_required
@role_required(UserRole.PATIENT)
def book_appointment():
    # Remove manual CSRF token generation as it conflicts with Flask-WTF's built-in csrf_token() function
    # which is already available in templates

    # Get all hospitals
    hospitals = db.get_all(Hospital)
    return render_template('patient/book_appointment.html', hospitals=hospitals, step=1)

# Get departments for a hospital (AJAX)
@patient_bp.route('/get_departments/<hospital_id>', methods=['GET'])
@login_required
@role_required(UserRole.PATIENT)
def get_departments(hospital_id):
    try:
        # Get departments for the hospital through the many-to-many relationship
        hospital_departments = []
        try:
            # First, get all hospital_department relationships for this hospital
            hospital_departments = db.get_hospital_departments(hospital_id)
        except Exception as e:
            print(f"Error getting hospital departments: {str(e)}")

        # Then, get each department
        departments = []
        for hd in hospital_departments:
            try:
                department = db.get_by_id(Department, hd.department_id)
                if department:
                    departments.append({
                        'id': department.id,
                        'name': department.name
                    })
            except Exception as e:
                print(f"Error processing department {hd.department_id}: {str(e)}")
                continue

        return jsonify({"departments": departments})
    except Exception as e:
        print(f"Error in get_departments: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get doctors for a department (AJAX)
@patient_bp.route('/get_doctors/<department_id>', methods=['GET'])
@login_required
@role_required(UserRole.PATIENT)
def get_doctors(department_id):
    try:
        print(f"\n=== FETCHING DOCTORS FOR DEPARTMENT ID: {department_id} ===")

        # Get doctors for the specified department
        doctors = []
        try:
            print(f"Calling db.get_doctors_by_department with department_id={department_id}")

            # Get all doctors with this department ID
            all_doctors = db.get_doctors_by_department(department_id)
            print(f"Found {len(all_doctors)} doctors for department {department_id}")

            # Log the doctor IDs for debugging
            doctor_ids = [str(doctor.id) for doctor in all_doctors]
            print(f"Doctor IDs: {doctor_ids}")

            # If no doctors were found, use a fallback direct query
            if not all_doctors:
                print("No doctors found in regular query. Attempting direct SQL query...")
                # Try a direct SQL query as a fallback
                try:
                    query = f"SELECT * FROM doctors WHERE department_id = '{department_id}'"
                    print(f"Executing direct query: {query}")
                    response = db.client.rpc('run_query', {"query": query}).execute()

                    if response.data:
                        print(f"Direct query found {len(response.data)} doctors")
                        all_doctors = [Doctor.from_dict(item) for item in response.data]
                        doctor_ids = [str(doctor.id) for doctor in all_doctors]
                        print(f"Doctor IDs from direct query: {doctor_ids}")
                except Exception as sql_error:
                    print(f"Error in direct SQL query: {str(sql_error)}")

            for doctor in all_doctors:
                # Check if doctor has the required fields before adding
                if not doctor.full_name:
                    print(f"Warning: Doctor {doctor.id} has no full_name, skipping")
                    continue

                doctor_data = {
                    'id': str(doctor.id),
                    'name': doctor.full_name,
                    'specialization': doctor.specialization or "General Practitioner",
                    'profile_picture': None  # Default to None since we handle it in the template
                }

                # Only add profile_picture URL if available (avoid errors)
                if hasattr(doctor, 'profile_picture') and doctor.profile_picture:
                    doctor_data['profile_picture'] = url_for('static', filename=f'images/profile_pictures/{doctor.profile_picture}')

                doctors.append(doctor_data)
                print(f"Added doctor: {doctor.full_name} ({doctor.id})")
        except Exception as e:
            print(f"Error fetching doctors by department: {str(e)}")
            import traceback
            print(traceback.format_exc())

        result = {"doctors": doctors}
        print(f"Returning result with {len(doctors)} doctors")
        return jsonify(result)
    except Exception as e:
        error_msg = f"Error in get_doctors: {str(e)}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": error_msg}), 500

# Get time slots for a doctor on a specific date (AJAX)
@patient_bp.route('/get_time_slots/<doctor_id>/<date_str>', methods=['GET'])
@login_required
@role_required(UserRole.PATIENT)
def get_time_slots(doctor_id, date_str):
    try:
        # Parse the date
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

        day_of_week = selected_date.weekday()  # 0-6 for Monday-Sunday

        # Get the doctor's regular availability for this day of week
        availability_slots = []
        try:
            all_slots = db.get_availability_by_doctor(doctor_id)
            availability_slots = [slot for slot in all_slots if slot.day_of_week == day_of_week and slot.is_available]
        except Exception as e:
            print(f"Error getting doctor availability: {str(e)}")

        # Get existing appointments for this doctor on this date
        booked_time_slots = []
        try:
            appointments = db.get_appointments_by_doctor_date(doctor_id, selected_date)
            for appt in appointments:
                # Handle both string and enum status
                status_is_cancelled = False
                if isinstance(appt.status, str):
                    status_is_cancelled = appt.status == AppointmentStatus.CANCELLED.value
                else:
                    status_is_cancelled = appt.status == AppointmentStatus.CANCELLED

                # Skip cancelled appointments
                if status_is_cancelled:
                    continue

                # Process time slot
                if isinstance(appt.time_slot, str):
                    # Parse time slot from string
                    try:
                        if ' - ' in appt.time_slot:
                            start_time = appt.time_slot.split(' - ')[0]
                            end_time = appt.time_slot.split(' - ')[1]
                            booked_time_slots.append((start_time, end_time))
                    except:
                        # Handle malformed time slot string
                        continue
                else:
                    # Handle non-string time slot data
                    continue
        except Exception as e:
            print(f"Error getting appointments: {str(e)}")

        # Generate available time slots based on availability and booked slots
        available_time_slots = []

        # If no availability slots, generate some default time slots for testing
        if not availability_slots:
            # Generate dummy slots from 9 AM to 5 PM in 30-minute increments
            start_hour = 9
            end_hour = 17
            for hour in range(start_hour, end_hour):
                for minute in [0, 30]:
                    start_time = f"{hour:02d}:{minute:02d}"
                    end_time = f"{hour:02d}:{minute+30:02d}" if minute == 0 else f"{hour+1:02d}:00"

                    # Format for display
                    start_display = datetime.strptime(start_time, '%H:%M').strftime('%I:%M %p')
                    end_display = datetime.strptime(end_time, '%H:%M').strftime('%I:%M %p')

                    time_slot = f"{start_display} - {end_display}"

                    # Check if slot is already booked
                    is_booked = False
                    for booked_start, booked_end in booked_time_slots:
                        if start_display == booked_start and end_display == booked_end:
                            is_booked = True
                            break

                    if not is_booked:
                        available_time_slots.append(time_slot)
        else:
            # Process actual availability slots
            for slot in availability_slots:
                # Format start and end times
                start_time = datetime.combine(selected_date, slot.start_time).strftime('%I:%M %p')
                end_time = datetime.combine(selected_date, slot.end_time).strftime('%I:%M %p')

                time_slot = f"{start_time} - {end_time}"

                # Check if slot is already booked
                is_booked = False
                for booked_start, booked_end in booked_time_slots:
                    if start_time == booked_start and end_time == booked_end:
                        is_booked = True
                        break

                if not is_booked:
                    available_time_slots.append(time_slot)

        return jsonify({"time_slots": available_time_slots})
    except Exception as e:
        print(f"Error in get_time_slots: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Book appointment submission
@patient_bp.route('/appointments/book', methods=['POST'])
@login_required
@role_required(UserRole.PATIENT)
def submit_appointment():
    # Update CSRF token validation to use Flask-WTF's built-in validation
    # The form validation will be handled automatically by Flask-WTF

    try:
        # Get form data
        hospital_id = request.form.get('hospital_id')
        department_id = request.form.get('department_id')
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')

        # Validate form data
        if not all([hospital_id, department_id, doctor_id, appointment_date, appointment_time]):
            flash('Please fill out all required fields', 'error')
            return redirect(url_for('patient.book_appointment'))

        # Parse date and time
        try:
            booking_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()

            # Handle the time format from the form (which might be like "9:00 AM - 9:30 AM")
            time_slot = appointment_time
            if ' - ' in time_slot:
                start_time_str, end_time_str = time_slot.split(' - ')
                try:
                    start_time = datetime.strptime(start_time_str, '%I:%M %p').time()
                    end_time = datetime.strptime(end_time_str, '%I:%M %p').time()
                except ValueError:
                    flash('Invalid time format', 'error')
                    return redirect(url_for('patient.book_appointment'))
            else:
                flash('Invalid time slot format', 'error')
                return redirect(url_for('patient.book_appointment'))

        except ValueError as e:
            flash(f'Invalid date or time format: {str(e)}', 'error')
            return redirect(url_for('patient.book_appointment'))

        # Create datetime objects for start and end time
        start_datetime = datetime.combine(booking_date, start_time).replace(tzinfo=None)
        end_datetime = datetime.combine(booking_date, end_time).replace(tzinfo=None)

        # Format for PostgreSQL tstzrange - using the proper range format
        # Format: ["2023-08-07 10:00:00+00","2023-08-07 10:30:00+00")
        formatted_start = start_datetime.strftime('%Y-%m-%d %H:%M:%S+00')
        formatted_end = end_datetime.strftime('%Y-%m-%d %H:%M:%S+00')
        postgres_time_slot = f'["{formatted_start}","{formatted_end}")'

        # Get user ID from session
        user_id = session.get('user_id')
        if not user_id:
            flash('Unable to identify user', 'error')
            return redirect(url_for('patient.book_appointment'))

        # Find the patient profile associated with this user
        try:
            # Query patient by user_id to get the patient's unique ID
            patients = db.query(Patient, user_id=str(user_id))
            if not patients or len(patients) == 0:
                flash('Patient profile not found', 'error')
                print(f"No patient profile found for user_id: {user_id}")
                return redirect(url_for('patient.book_appointment'))

            patient = patients[0]
            patient_id = patient.id
            print(f"Found patient: {patient.full_name} with ID: {patient_id}")
        except Exception as e:
            print(f"Error finding patient profile: {str(e)}")
            flash('Error accessing patient profile', 'error')
            return redirect(url_for('patient.book_appointment'))

        # Check if the slot is still available (to prevent double booking)
        try:
            # Get appointments for this doctor, on this date, that are scheduled
            existing_appointments = db.get_appointments_by_doctor_date(doctor_id, booking_date)

            # Filter to just scheduled appointments
            conflicting_appointments = []
            for appt in existing_appointments:
                # Handle both string and enum status
                is_scheduled = False
                if isinstance(appt.status, str):
                    is_scheduled = appt.status == AppointmentStatus.SCHEDULED.value
                else:
                    is_scheduled = appt.status == AppointmentStatus.SCHEDULED

                if is_scheduled:
                    conflicting_appointments.append(appt)

            # Check for time conflicts
            for appt in conflicting_appointments:
                if appt.time_slot == time_slot:
                    flash('This time slot is no longer available. Please select another time.', 'error')
                    return redirect(url_for('patient.book_appointment'))
        except Exception as e:
            print(f"Error checking for appointment conflicts: {str(e)}")
            # If we can't check for conflicts, we'll assume the slot is still available

        # Create new appointment
        try:
            new_appointment = Appointment(
                id=str(uuid.uuid4()),
                patient_id=str(patient_id),  # Use the patient's profile ID, not the user_id
                doctor_id=str(doctor_id),
                hospital_id=str(hospital_id),
                department_id=str(department_id),
                date=booking_date,
                time_slot=postgres_time_slot,  # Use the PostgreSQL formatted time slot
                status=AppointmentStatus.SCHEDULED,  # Use enum directly, not .value
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            flash(f'Error creating appointment object: {str(e)}', 'error')
            return redirect(url_for('patient.book_appointment'))

        try:
            saved_appointment = db.create(new_appointment)
            if saved_appointment:
                flash('Appointment booked successfully!', 'success')
                return redirect(url_for('patient.appointment_success', appointment_id=saved_appointment.id))
            else:
                flash('Error booking appointment: Database operation failed', 'error')
                return redirect(url_for('patient.book_appointment'))
        except Exception as e:
            flash(f'Error booking appointment: {str(e)}', 'error')
            return redirect(url_for('patient.book_appointment'))
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(url_for('patient.book_appointment'))

# Appointment success page
@patient_bp.route('/appointments/<appointment_id>/success')
@login_required
@role_required(UserRole.PATIENT)
def appointment_success(appointment_id):
    try:
        # Get the appointment details
        appointment = db.get_by_id(Appointment, appointment_id)
        if not appointment:
            flash('Appointment not found', 'error')
            return redirect(url_for('patient.dashboard'))

        # Get related entities
        doctor = db.get_by_id(Doctor, appointment.doctor_id)
        hospital = db.get_by_id(Hospital, appointment.hospital_id)
        department = db.get_by_id(Department, appointment.department_id)

        # Format date - handle both date objects and strings
        appointment_date = appointment.date
        if isinstance(appointment_date, date):
            # Format as string if it's a date object
            formatted_date = appointment_date.strftime('%A, %B %d, %Y')
        else:
            # Try to parse the date if it's a string
            try:
                formatted_date = datetime.strptime(appointment_date, '%Y-%m-%d').strftime('%A, %B %d, %Y')
            except (ValueError, TypeError):
                formatted_date = appointment_date  # Keep as is if parsing fails

        # Parse time_slot
        time_slot = appointment.time_slot
        if isinstance(time_slot, str):
            # Parse the time slot string format from PostgreSQL
            if '["' in time_slot and '","' in time_slot:
                start_time = time_slot.strip('["').split('","')[0]
                try:
                    start_time = datetime.fromisoformat(start_time.replace('+00', '+00:00')).strftime('%I:%M %p')
                except (ValueError, TypeError):
                    start_time = "Time information not available"
            elif ' - ' in time_slot:
                # Already in display format like "9:00 AM - 9:30 AM"
                start_time = time_slot.split(' - ')[0]
            else:
                start_time = time_slot  # Keep as is if format is unknown
        else:
            start_time = "Time information not available"

        # Format the status for display
        status_display = appointment.status
        if isinstance(status_display, AppointmentStatus):
            status_display = status_display.value.capitalize()
        elif isinstance(status_display, str):
            status_display = status_display.capitalize()

        appointment_details = {
            'id': appointment.id,
            'date': formatted_date,
            'time': start_time,
            'doctor_name': doctor.full_name if doctor else 'Unknown',
            'hospital_name': hospital.name if hospital else 'Unknown',
            'department_name': department.name if department else 'Unknown',
            'status': status_display
        }

        return render_template('patient/appointment_success.html', appointment=appointment_details)
    except Exception as e:
        print(f"Error in appointment_success: {str(e)}")
        import traceback
        print(traceback.format_exc())
        flash(f"Error loading appointment details: {str(e)}", "error")
        return redirect(url_for('patient.dashboard'))

# View my appointments
@patient_bp.route('/appointments')
@login_required
@role_required(UserRole.PATIENT)
def my_appointments():
    # Get the user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash('Unable to identify user', 'error')
        return redirect(url_for('auth.login'))

    # Find the patient profile associated with this user
    try:
        # Query patient by user_id
        patients = db.query(Patient, user_id=str(user_id))
        if not patients or len(patients) == 0:
            flash('Patient profile not found', 'error')
            print(f"No patient profile found for user_id: {user_id}")
            return render_template('patient/my_appointments.html', appointments=[])

        patient = patients[0]
        patient_id = patient.id
        print(f"Found patient: {patient.full_name} with ID: {patient_id}")
    except Exception as e:
        print(f"Error finding patient profile: {str(e)}")
        flash('Error accessing patient profile', 'error')
        return render_template('patient/my_appointments.html', appointments=[])

    # Initialize an empty list for appointments
    formatted_appointments = []

    # Only try to fetch appointments if we have a valid patient_id
    try:
        # Get all appointments for this patient
        appointments = db.get_appointments_by_patient(patient_id)

        # Sort in descending date order
        appointments.sort(key=lambda x: x.date, reverse=True)

        # Format appointments for display with doctor and hospital info
        for appt in appointments:
            doctor = db.get_by_id(Doctor, appt.doctor_id)
            hospital = db.get_by_id(Hospital, appt.hospital_id)
            department = db.get_by_id(Department, appt.department_id)

            # Parse the time_slot which is stored as tstzrange in the database
            time_slot = appt.time_slot
            if isinstance(time_slot, str):
                # Parse the time slot string format like: ["2023-01-01 09:00:00+00","2023-01-01 09:30:00+00")
                start_time = time_slot.strip('["').split(',')[0].strip('"')
                start_time = datetime.fromisoformat(start_time.replace('+00', '+00:00')).strftime('%I:%M %p')
            else:
                start_time = "Time not available"

            formatted_appointments.append({
                'id': appt.id,
                'date': appt.date,
                'time': start_time,
                'doctor_name': doctor.full_name if doctor else 'Unknown',
                'hospital_name': hospital.name if hospital else 'Unknown',
                'department_name': department.name if department else 'Unknown',
                'status': appt.status,
                'is_past': appt.date < date.today() or
                          (appt.date == date.today() and start_time < datetime.now().strftime('%I:%M %p'))
            })
    except Exception as e:
        # Log the error and show a flash message
        print(f"Error fetching appointments: {str(e)}")
        flash(f"Error loading appointments: {str(e)}", "error")

    return render_template('patient/my_appointments.html', appointments=formatted_appointments)

# Cancel appointment
@patient_bp.route('/appointments/<appointment_id>/cancel', methods=['POST'])
@login_required
@role_required(UserRole.PATIENT)
def cancel_appointment(appointment_id):
    # Get the user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash('Unable to identify user', 'error')
        return redirect(url_for('auth.login'))

    # Find the patient profile associated with this user
    try:
        # Query patient by user_id
        patients = db.query(Patient, user_id=str(user_id))
        if not patients or len(patients) == 0:
            flash('Patient profile not found', 'error')
            print(f"No patient profile found for user_id: {user_id}")
            return redirect(url_for('patient.dashboard'))

        patient = patients[0]
        patient_id = patient.id
        print(f"Found patient: {patient.full_name} with ID: {patient_id}")
    except Exception as e:
        print(f"Error finding patient profile: {str(e)}")
        flash('Error accessing patient profile', 'error')
        return redirect(url_for('patient.dashboard'))

    # Get the appointment by ID
    appointment = db.get_by_id(Appointment, appointment_id)

    # Check if it belongs to this patient
    if not appointment or str(appointment.patient_id) != str(patient_id):
        flash('Appointment not found or you do not have permission to cancel it', 'error')
        return redirect(url_for('patient.my_appointments'))

    # Check if the appointment is already completed or cancelled
    # Convert status to enum for comparison if it's a string
    appointment_status = appointment.status
    if isinstance(appointment_status, str):
        try:
            appointment_status = AppointmentStatus(appointment_status)
        except ValueError:
            # If we can't convert to enum, use string comparison as fallback
            if appointment_status in [AppointmentStatus.COMPLETED.value, AppointmentStatus.CANCELLED.value]:
                flash('Cannot cancel an appointment that is already completed or cancelled', 'error')
                return redirect(url_for('patient.my_appointments'))
    else:
        # It's already an enum, compare directly
        if appointment_status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
            flash('Cannot cancel an appointment that is already completed or cancelled', 'error')
            return redirect(url_for('patient.my_appointments'))

    # Check if the appointment is in the past
    if appointment.date < date.today():
        flash('Cannot cancel an appointment that is in the past', 'error')
        return redirect(url_for('patient.my_appointments'))

    # Update the appointment status
    try:
        db.update(Appointment, appointment.id, {
            "status": AppointmentStatus.CANCELLED,  # Use enum directly, not .value
            "updated_at": datetime.now()
        })
        flash('Appointment cancelled successfully', 'success')
    except Exception as e:
        flash(f'Error cancelling appointment: {str(e)}', 'error')

    return redirect(url_for('patient.my_appointments'))

# Doctor list (for browsing)
@patient_bp.route('/doctors')
@login_required
@role_required(UserRole.PATIENT)
def doctor_list():
    try:
        # Get all doctors
        all_doctors = db.get_all(Doctor)

        # Format with hospital and department info
        doctors = []
        for doctor in all_doctors:
            try:
                hospital = db.get_by_id(Hospital, doctor.hospital_id) if doctor.hospital_id else None
                department = db.get_by_id(Department, doctor.department_id) if doctor.department_id else None

                doctors.append({
                    'id': doctor.id,
                    'full_name': doctor.full_name,
                    'specialization': doctor.specialization,
                    'credentials': doctor.credentials,
                    'hospital_id': hospital.id if hospital else None,
                    'hospital_name': hospital.name if hospital else 'Unknown',
                    'department_id': department.id if department else None,
                    'department_name': department.name if department else 'Unknown'
                })
            except Exception as e:
                print(f"Error processing doctor {doctor.id}: {str(e)}")
                # Continue with next doctor if one fails
                continue

        # Sort by name
        doctors.sort(key=lambda x: x['full_name'])
    except Exception as e:
        print(f"Error fetching doctors: {str(e)}")
        flash(f"Error loading doctors: {str(e)}", "error")
        doctors = []

    return render_template('patient/doctor_list.html', doctors=doctors)

# Doctor details page
@patient_bp.route('/doctors/<doctor_id>')
@login_required
@role_required(UserRole.PATIENT)
def doctor_details(doctor_id):
    try:
        # Get doctor details
        doctor = db.get_by_id(Doctor, doctor_id)

        if not doctor:
            flash('Doctor not found', 'error')
            return redirect(url_for('patient.doctor_list'))

        # Get hospital and department
        hospital = db.get_by_id(Hospital, doctor.hospital_id) if doctor.hospital_id else None
        department = db.get_by_id(Department, doctor.department_id) if doctor.department_id else None

        # Create a dict with all doctor details
        doctor_info = {
            'id': doctor.id,
            'full_name': doctor.full_name,
            'specialization': doctor.specialization,
            'credentials': doctor.credentials,
            'contact_number': doctor.contact_number if hasattr(doctor, 'contact_number') else None,
            'hospital_id': hospital.id if hospital else None,
            'hospital_name': hospital.name if hospital else 'Unknown',
            'department_id': department.id if department else None,
            'department_name': department.name if department else 'Unknown'
        }

        # Get doctor's availability
        try:
            availability_slots = db.get_availability_by_doctor(doctor_id)

            # Filter for only available slots
            availability_slots = [slot for slot in availability_slots if slot.is_available]
        except Exception as e:
            print(f"Error fetching doctor availability: {str(e)}")
            availability_slots = []
            flash("Could not retrieve doctor's availability schedule", "warning")

        # Format availability for display
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        formatted_availability = []

        for slot in availability_slots:
            try:
                day = days_of_week[slot.day_of_week]
                start = slot.start_time.strftime('%I:%M %p')
                end = slot.end_time.strftime('%I:%M %p')
                formatted_availability.append({
                    'day': day,
                    'hours': f'{start} - {end}'
                })
            except (AttributeError, IndexError) as e:
                print(f"Error formatting availability slot: {str(e)}")
                # Skip this slot if there's an error
                continue

        return render_template(
            'patient/doctor_details.html',
            doctor=doctor_info,
            availability=formatted_availability
        )
    except Exception as e:
        print(f"Error in doctor_details route: {str(e)}")
        flash(f"Error loading doctor details: {str(e)}", "error")
        return redirect(url_for('patient.doctor_list'))

@patient_bp.route('/my-ehr')
@login_required
@role_required(UserRole.PATIENT)
def my_ehr():
    """
    Allow patients to view their own Electronic Health Record (EHR)
    with dummy data since this is frontend-only implementation.
    """
    # Get the user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash('Unable to identify user', 'error')
        return redirect(url_for('auth.login'))

    # Find the patient profile associated with this user
    try:
        # Query patient by user_id
        patients = db.query(Patient, user_id=str(user_id))
        if not patients or len(patients) == 0:
            flash('Patient profile not found', 'error')
            return render_template('patient/my_ehr.html', patient=None, has_ehr=False)

        patient = patients[0]
    except Exception as e:
        print(f"Error finding patient profile: {str(e)}")
        flash('Error accessing patient profile', 'error')
        return render_template('patient/my_ehr.html', patient=None, has_ehr=False)

    # Since this is a frontend-only implementation with dummy data,
    # we'll always set has_ehr to True and provide dummy data

    # Create dummy data for the EHR view
    today = date.today()

    # Dummy allergies
    allergies = [
        {"name": "Penicillin", "severity": "Severe", "reaction": "Hives, Difficulty breathing"},
        {"name": "Peanuts", "severity": "Moderate", "reaction": "Skin rash, Swelling"}
    ]

    # Dummy diagnoses grouped by visit
    visits = [
        {
            "id": str(uuid.uuid4()),
            "date": today - timedelta(days=5),
            "doctor": "Dr. Sarah Johnson",
            "department": "General Medicine",
            "diagnoses": [
                {"name": "Hypertension", "icd_code": "I10", "notes": "Prescribe daily medication and monitor blood pressure"}
            ],
            "medications": [
                {"name": "Lisinopril", "dosage": "10mg", "frequency": "Daily", "start_date": today - timedelta(days=5), "end_date": today + timedelta(days=25)}
            ],
            "notes": "Patient reports occasional headaches. Advised to reduce sodium intake and increase physical activity."
        },
        {
            "id": str(uuid.uuid4()),
            "date": today - timedelta(days=60),
            "doctor": "Dr. Michael Chen",
            "department": "ENT",
            "diagnoses": [
                {"name": "Acute Sinusitis", "icd_code": "J01.90", "notes": "Prescribe antibiotics and decongestants"}
            ],
            "medications": [
                {"name": "Amoxicillin", "dosage": "500mg", "frequency": "Every 8 hours", "start_date": today - timedelta(days=60), "end_date": today - timedelta(days=50)},
                {"name": "Sudafed", "dosage": "30mg", "frequency": "Every 6 hours as needed", "start_date": today - timedelta(days=60), "end_date": today - timedelta(days=54)}
            ],
            "notes": "Follow up in 10 days if symptoms persist."
        }
    ]

    # Dummy immunizations
    immunizations = [
        {"name": "Influenza vaccine", "date": today - timedelta(days=180), "administered_by": "Dr. Emily Wilson"},
        {"name": "Tetanus booster", "date": today - timedelta(days=365), "administered_by": "Dr. James Miller"},
        {"name": "COVID-19 vaccine", "date": today - timedelta(days=90), "administered_by": "Dr. Sarah Johnson"}
    ]

    # Dummy test results
    test_results = [
        {"name": "Complete Blood Count", "date": today - timedelta(days=5), "result": "Normal", "notes": "All values within normal range"},
        {"name": "Lipid Panel", "date": today - timedelta(days=5), "result": "Abnormal", "notes": "LDL cholesterol slightly elevated (130 mg/dL)"},
        {"name": "Blood Pressure", "date": today - timedelta(days=5), "result": "140/90 mmHg", "notes": "Slightly elevated, continue monitoring"}
    ]

    # Dummy vitals for the summary section
    vitals = {
        "height": "5'10\" (178 cm)",
        "weight": "160 lbs (72.5 kg)",
        "bmi": "23.0",
        "blood_pressure": "140/90 mmHg",
        "heart_rate": "72 bpm",
        "temperature": "98.6°F (37°C)",
        "last_updated": today - timedelta(days=5)
    }

    return render_template('patient/my_ehr.html',
                          patient=patient,
                          has_ehr=True,
                          allergies=allergies,
                          visits=visits,
                          immunizations=immunizations,
                          test_results=test_results,
                          vitals=vitals)

# Add other routes like view_patient, add_patient, edit_patient etc.