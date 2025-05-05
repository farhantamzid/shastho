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
        slots = db.query(DoctorAvailabilitySlot, doctor_id=doctor_id)
        return slots if slots else []
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
                          start_time: time, end_time: time) -> bool:
    """
    Add a new availability slot for a doctor

    Args:
        doctor_id: The doctor's ID
        day_of_week: Integer (0-6) representing day of week (Monday=0)
        start_time: Start time for the slot
        end_time: End time for the slot

    Returns:
        True if successful, False otherwise
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
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Save to database
        db.insert(slot)
        return True
    except Exception as e:
        print(f"Error adding availability slot: {str(e)}")
        return False

def update_availability_slot(slot_id: UUID, day_of_week: int,
                            start_time: time, end_time: time,
                            is_available: bool) -> bool:
    """
    Update an existing availability slot

    Args:
        slot_id: The slot ID to update
        day_of_week: Integer (0-6) representing day of week (Monday=0)
        start_time: Start time for the slot
        end_time: End time for the slot
        is_available: Whether the slot is available

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

        # Save to database
        db.update(slot)
        return True
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
        db.delete(DoctorAvailabilitySlot, slot_id)
        return True
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