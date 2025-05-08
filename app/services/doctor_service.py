from app.models.database import Doctor, Hospital, Department, DoctorAvailabilitySlot
from app.utils.db import db
from uuid import UUID, uuid4
from datetime import datetime, time
from typing import List, Tuple, Optional, Dict, Any

def get_doctor_by_user_id(user_id: str) -> Optional[Doctor]:
    """
    Retrieve a doctor record by user ID

    Args:
        user_id: The user ID linked to the doctor

    Returns:
        Doctor object or None if not found
    """
    try:
        doctor_records = db.query(Doctor, user_id=user_id)
        if doctor_records and len(doctor_records) > 0:
            return doctor_records[0]
        return None
    except Exception as e:
        print(f"Error retrieving doctor: {str(e)}")
        return None

def get_doctor_hospital_info(hospital_id: Optional[UUID], department_id: Optional[UUID]) -> Tuple[str, str]:
    """
    Get the hospital and department names for a doctor

    Args:
        hospital_id: The hospital ID
        department_id: The department ID

    Returns:
        Tuple of (hospital_name, department_name)
    """
    hospital_name = "No Hospital Assigned"
    department_name = "No Department Assigned"

    try:
        if hospital_id:
            hospital = db.get_by_id(Hospital, hospital_id)
            if hospital:
                hospital_name = hospital.name

        if department_id:
            department = db.get_by_id(Department, department_id)
            if department:
                department_name = department.name
    except Exception as e:
        print(f"Error retrieving hospital/department info: {str(e)}")

    return hospital_name, department_name

def get_doctor_availability_slots(doctor_id: UUID) -> List[DoctorAvailabilitySlot]:
    """
    Get all availability slots for a doctor

    Args:
        doctor_id: The doctor's ID

    Returns:
        List of availability slot objects
    """
    try:
        return db.get_availability_by_doctor(doctor_id)
    except Exception as e:
        print(f"Error retrieving availability slots: {str(e)}")
        return []

def update_doctor_profile(user_id: str, full_name: str, specialization: str,
                         credentials: str, contact_number: str) -> bool:
    """
    Update doctor profile information

    Args:
        user_id: The user ID
        full_name: The doctor's full name
        specialization: The doctor's specialization
        credentials: The doctor's credentials
        contact_number: The doctor's contact number

    Returns:
        True if successful, False otherwise
    """
    try:
        doctor = get_doctor_by_user_id(user_id)
        if not doctor:
            return False

        # Update doctor record
        doctor.full_name = full_name
        doctor.specialization = specialization
        doctor.credentials = credentials
        doctor.contact_number = contact_number
        doctor.updated_at = datetime.now()

        # Save to database
        db.update(doctor)
        return True
    except Exception as e:
        print(f"Error updating doctor profile: {str(e)}")
        return False

def update_doctor_profile_picture(user_id: str, picture_url: str) -> bool:
    """
    Update doctor's profile picture URL

    Args:
        user_id: The user ID
        picture_url: The URL to the profile picture

    Returns:
        True if successful, False otherwise
    """
    try:
        doctor = get_doctor_by_user_id(user_id)
        if not doctor:
            return False

        # Set the profile picture URL - assuming this is stored in a user table
        # connected to the doctor record. In a real app, this might be in a different
        # location based on your data model.
        from app.models.auth import update_user_profile_picture
        update_user_profile_picture(user_id, picture_url)

        return True
    except Exception as e:
        print(f"Error updating profile picture: {str(e)}")
        return False

def add_availability_slot(doctor_id: UUID, day_of_week: int,
                        start_time: time, end_time: time,
                        slot_duration_minutes: int = 30) -> Optional[DoctorAvailabilitySlot]:
    """
    Add a new availability slot for a doctor

    Args:
        doctor_id: The doctor's ID
        day_of_week: Integer (0-6) representing day of week (Monday=0)
        start_time: Start time for the slot
        end_time: End time for the slot
        slot_duration_minutes: Duration of each appointment slot in minutes (default: 30)

    Returns:
        Created slot object if successful, None otherwise
    """
    try:
        # Create new slot
        slot = DoctorAvailabilitySlot(
            id=uuid4(),
            doctor_id=doctor_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            is_available=True,
            slot_duration_minutes=slot_duration_minutes,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Save to database using enhanced method
        return db.add_doctor_availability_slot(slot)
    except Exception as e:
        print(f"Error adding availability slot: {str(e)}")
        return None

def update_availability_slot(slot_id: UUID, day_of_week: int,
                            start_time: time, end_time: time,
                            is_available: bool,
                            slot_duration_minutes: int = None) -> bool:
    """
    Update an existing availability slot

    Args:
        slot_id: The slot ID to update
        day_of_week: Integer (0-6) representing day of week (Monday=0)
        start_time: Start time for the slot
        end_time: End time for the slot
        is_available: Whether the slot is available
        slot_duration_minutes: Optional duration in minutes for appointment slots

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the slot
        slot = db.get_by_id(DoctorAvailabilitySlot, slot_id)
        if not slot:
            return False

        # Update slot
        slot.day_of_week = day_of_week
        slot.start_time = start_time
        slot.end_time = end_time
        slot.is_available = is_available
        slot.updated_at = datetime.now()

        # Only update slot_duration_minutes if provided
        if slot_duration_minutes is not None:
            slot.slot_duration_minutes = slot_duration_minutes

        # Save to database using enhanced method
        return db.update_doctor_availability_slot(slot)
    except Exception as e:
        print(f"Error updating availability slot: {str(e)}")
        return False

def delete_availability_slot(slot_id: UUID) -> bool:
    """
    Delete an availability slot

    Args:
        slot_id: The slot ID to delete

    Returns:
        True if successful, False otherwise
    """
    try:
        return db.delete_doctor_availability_slot(slot_id)
    except Exception as e:
        print(f"Error deleting availability slot: {str(e)}")
        return False

def get_doctor_stats(doctor_id: UUID) -> Dict[str, int]:
    """
    Get statistics for a doctor's dashboard

    Args:
        doctor_id: The doctor's ID

    Returns:
        Dictionary with stats (appointments, patients, etc.)
    """
    try:
        # In a real app, this would query your database for actual statistics
        # This is just a placeholder
        today_appointments = db.count_today_appointments(doctor_id)
        patient_count = db.count_doctor_patients(doctor_id)
        pending_records = db.count_pending_records(doctor_id)

        return {
            'today_appointments': today_appointments,
            'patient_count': patient_count,
            'pending_records': pending_records
        }
    except Exception as e:
        print(f"Error retrieving doctor stats: {str(e)}")
        return {
            'today_appointments': 0,
            'patient_count': 0,
            'pending_records': 0
        }

def get_upcoming_appointments(doctor_id: UUID, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get upcoming appointments for a doctor

    Args:
        doctor_id: The doctor's ID
        limit: Maximum number of appointments to return

    Returns:
        List of appointment dictionaries with patient details
    """
    try:
        # In a real app, this would query your database for actual appointments
        # This is just a placeholder
        appointments = db.get_upcoming_appointments(doctor_id, limit)

        # Process and format appointments with patient info
        formatted_appointments = []
        for appt in appointments:
            patient = db.get_by_id("Patient", appt.patient_id)
            formatted_appointments.append({
                'id': str(appt.id),
                'patient_name': patient.full_name if patient else "Unknown",
                'patient_age': calculate_age(patient.date_of_birth) if patient and patient.date_of_birth else "N/A",
                'date': appt.date,
                'time_slot': appt.time_slot,
                'appointment_type': "Follow-up" if appt.is_followup else "Initial Consultation",
                'reason_for_visit': appt.reason_for_visit
            })

        return formatted_appointments
    except Exception as e:
        print(f"Error retrieving upcoming appointments: {str(e)}")
        return []

def calculate_age(birth_date):
    """Helper function to calculate age from birth date"""
    today = datetime.now().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def bulk_update_availability(slots_data: List[Dict[str, Any]]) -> bool:
    """
    Update multiple availability slots at once

    Args:
        slots_data: List of slot data dictionaries

    Returns:
        True if all updates were successful, False otherwise
    """
    try:
        # First, check if we have any slots to process
        if not slots_data or len(slots_data) == 0:
            print("No slots data provided to bulk_update_availability")
            return False

        # For doctor ID, we need to extract it from at least one slot
        doctor_id = None
        for slot in slots_data:
            if 'doctor_id' in slot and slot['doctor_id']:
                doctor_id = slot['doctor_id']
                if isinstance(doctor_id, str):
                    try:
                        doctor_id = UUID(doctor_id)
                    except (ValueError, TypeError):
                        print(f"Invalid doctor_id: {doctor_id}")
                        return False
                break

        if not doctor_id:
            print("Missing doctor_id in slots data")
            return False

        print(f"Processing bulk update for doctor_id: {doctor_id}")
        print(f"Received {len(slots_data)} slots to process")

        # Get all existing slots for this doctor (to know what needs to be deleted)
        existing_slots = db.get_availability_by_doctor(doctor_id)
        existing_slot_ids = {str(slot.id): slot for slot in existing_slots}
        print(f"Found {len(existing_slots)} existing slots")

        # Keep track of processed slot IDs to determine which ones to delete
        processed_slot_ids = set()

        # Check for duplicate slots (same day and overlapping times)
        # This provides backend validation in addition to frontend validation
        day_time_slots = {}  # Format: {day: [(start_time, end_time, slot_index)]}
        for i, slot_data in enumerate(slots_data):
            day = int(slot_data['day_of_week'])
            if day not in day_time_slots:
                day_time_slots[day] = []

            start_time_str = slot_data['start_time']
            end_time_str = slot_data['end_time']

            # Add seconds if missing for consistent comparison
            if start_time_str.count(':') == 1:
                start_time_str += ":00"
            if end_time_str.count(':') == 1:
                end_time_str += ":00"

            # Convert to datetime.time objects for comparison
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()

            # Check for overlap with existing slots for this day
            for st, et, idx in day_time_slots[day]:
                if (start_time >= st and start_time < et) or \
                   (end_time > st and end_time <= et) or \
                   (start_time <= st and end_time >= et):
                    print(f"Overlapping slots detected on day {day}: slot #{i+1} with slot #{idx+1}")
                    # We don't fail immediately - just log the issue.
                    # The frontend should prevent this from happening.

            day_time_slots[day].append((start_time, end_time, i))

        # Process each slot: update existing or create new
        for slot_data in slots_data:
            try:
                day_of_week = int(slot_data['day_of_week'])

                # Parse start and end times
                start_time_str = slot_data['start_time']
                end_time_str = slot_data['end_time']

                # Handle time format with or without seconds
                if ':' not in start_time_str or ':' not in end_time_str:
                    print(f"Invalid time format: start={start_time_str}, end={end_time_str}")
                    continue

                try:
                    # Parse time as HH:MM or HH:MM:SS
                    if start_time_str.count(':') == 1:
                        start_time_str += ":00"  # Add seconds if missing
                    if end_time_str.count(':') == 1:
                        end_time_str += ":00"  # Add seconds if missing

                    start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
                    end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
                except ValueError:
                    print(f"Error parsing time: start={start_time_str}, end={end_time_str}")
                    continue

                # Set default duration and availability
                slot_duration = slot_data.get('slot_duration_minutes', 60)  # Default to 1 hour
                is_available = slot_data.get('is_available', True)  # Default to available

                # Check if this is an existing slot that needs updating
                if 'id' in slot_data and slot_data['id']:
                    slot_id = slot_data['id']
                    if isinstance(slot_id, str):
                        try:
                            slot_id = UUID(slot_id)
                        except ValueError:
                            print(f"Invalid slot_id: {slot_id}")
                            continue

                    # Verify the slot actually exists in the database
                    if str(slot_id) not in existing_slot_ids:
                        print(f"Slot ID {slot_id} doesn't exist in the database - creating new instead")
                        new_slot = add_availability_slot(
                            doctor_id=doctor_id,
                            day_of_week=day_of_week,
                            start_time=start_time,
                            end_time=end_time,
                            slot_duration_minutes=slot_duration
                        )
                        if new_slot:
                            processed_slot_ids.add(str(new_slot.id))
                        continue

                    # Mark as processed
                    processed_slot_ids.add(str(slot_id))

                    # Update existing slot
                    print(f"Updating existing slot: ID={slot_id}, day={day_of_week}, start={start_time}, end={end_time}")
                    success = update_availability_slot(
                        slot_id=slot_id,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        end_time=end_time,
                        is_available=is_available,
                        slot_duration_minutes=slot_duration
                    )

                    if not success:
                        print(f"Failed to update slot: {slot_id}")
                else:
                    # Create new slot
                    print(f"Creating new slot: day={day_of_week}, start={start_time}, end={end_time}")
                    new_slot = add_availability_slot(
                        doctor_id=doctor_id,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        end_time=end_time,
                        slot_duration_minutes=slot_duration
                    )

                    if not new_slot:
                        print("Failed to create new slot")
                    else:
                        print(f"Created new slot with ID: {new_slot.id}")
                        # Add to processed list
                        processed_slot_ids.add(str(new_slot.id))
            except Exception as e:
                print(f"Error processing slot: {str(e)}")
                import traceback
                print(traceback.format_exc())
                # Continue with next slot

        # Delete any existing slots that weren't in the new data
        # (i.e., they were removed by the user)
        for slot_id, slot in existing_slot_ids.items():
            if slot_id not in processed_slot_ids:
                print(f"Deleting removed slot: {slot_id}")
                delete_availability_slot(slot.id)

        return True

    except Exception as e:
        print(f"Error in bulk_update_availability: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def get_available_booking_slots(doctor_id: UUID, date_str: str) -> List[Dict[str, Any]]:
    """
    Get available time slots for a specific date that can be booked

    Args:
        doctor_id: The doctor's ID
        date_str: Date string in ISO format (YYYY-MM-DD)

    Returns:
        List of available time slots with start and end times
    """
    try:
        return db.get_available_slots_for_booking(doctor_id, date_str)
    except Exception as e:
        print(f"Error getting available booking slots: {str(e)}")
        return []