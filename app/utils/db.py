"""
Database utility functions for the Shastho Flask application.
-----------------------------------------------------------
This file contains helper functions for database operations, such as connecting, querying, and managing transactions.
Used throughout the app for low-level DB access.
"""
import os
from typing import List, Dict, Any, Optional, Union, Type, TypeVar
from uuid import UUID
from datetime import datetime

from supabase import create_client, Client
from dotenv import load_dotenv

from app.models.database import (
    User, Hospital, Department, Patient, Doctor,
    DoctorAvailabilitySlot, Appointment, PasswordResetToken,
    DoctorNote, UserSession, HospitalDepartment, HospitalAdmin,
    TestImageAdminRequest, AdminRequestStatus, TestAdmin
)
from app.models.ehr import (
    EHR, EHR_Visit, EHR_Diagnosis, EHR_Medication,
    EHR_Allergy, EHR_Procedure, EHR_Vital, EHR_Immunization,
    EHR_TestResult, EHR_ProviderNote, Prescription
)

# Load environment variables
load_dotenv()

T = TypeVar('T', User, Hospital, Department, Patient, Doctor,
            DoctorAvailabilitySlot, Appointment, EHR, EHR_Visit,
            EHR_Diagnosis, EHR_Medication, EHR_Allergy, EHR_Procedure,
            EHR_Vital, EHR_Immunization, EHR_TestResult, EHR_ProviderNote,
            Prescription, PasswordResetToken, DoctorNote, UserSession, HospitalDepartment, HospitalAdmin, TestAdmin, TestImageAdminRequest)

class Database:
    """Database utility for Supabase interactions."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._init_supabase()
        return cls._instance

    def _init_supabase(self) -> None:
        """Initialize the Supabase client."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        print(f"\n=== INITIALIZING SUPABASE CONNECTION ===")

        # Validate environment variables
        if not supabase_url:
            print("ERROR: SUPABASE_URL is not set in environment variables")
            raise ValueError("SUPABASE_URL environment variable must be set")

        if not supabase_key:
            print("ERROR: SUPABASE_KEY is not set in environment variables")
            raise ValueError("SUPABASE_KEY environment variable must be set")

        print(f"URL: {supabase_url[:30]}...") # Only print part of the URL for security
        print(f"Key: {supabase_key[:15]}...") # Only print part of the key for security

        # Try to connect with retry logic
        max_retries = 3
        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                print(f"Connecting to Supabase (attempt {retry_count + 1}/{max_retries})...")
                self.client = create_client(supabase_url, supabase_key)

                # Test the connection with a simple query
                print("Testing connection...")
                test_result = self.client.table("hospitals").select("id").limit(1).execute()

                if hasattr(test_result, 'error') and test_result.error:
                    print(f"Connection test error: {test_result.error}")
                    raise Exception(f"Connection test failed: {test_result.error}")

                record_count = len(test_result.data) if hasattr(test_result, 'data') else 0
                print(f"Connection successful! Found {record_count} hospital records in the test query.")
                return

            except Exception as e:
                retry_count += 1
                last_error = e
                print(f"Connection attempt {retry_count} failed: {str(e)}")
                if retry_count < max_retries:
                    print(f"Retrying in 1 second...")
                    import time
                    time.sleep(1)

        # If we get here, all retries failed
        print(f"Failed to connect to Supabase after {max_retries} attempts")
        import traceback
        print(f"Last error: {str(last_error)}")
        print(traceback.format_exc())
        raise last_error

    # Generic CRUD operations

    def _get_table_name(self, model_class: Type[T]) -> str:
        """Get the table name for a model class."""
        table_map = {
            User: "users",
            Hospital: "hospitals",
            Department: "departments",
            Patient: "patients",
            Doctor: "doctors",
            DoctorAvailabilitySlot: "doctor_availability_slots",
            Appointment: "appointments",
            # EHR models
            EHR: "EHR",
            EHR_Visit: "EHR_Visits",
            EHR_Diagnosis: "EHR_Diagnoses",
            EHR_Medication: "EHR_Medications",
            EHR_Allergy: "EHR_Allergies",
            EHR_Procedure: "EHR_Procedures",
            EHR_Vital: "EHR_Vitals",
            EHR_Immunization: "EHR_Immunizations",
            EHR_TestResult: "EHR_TestResults",
            EHR_ProviderNote: "EHR_ProviderNotes",
            Prescription: "Prescriptions",
            # Password reset token
            PasswordResetToken: "password_reset_tokens",
            # Doctor notes
            DoctorNote: "doctor_notes",
            # User sessions
            UserSession: "user_sessions",
            # Hospital-Department relationship
            HospitalDepartment: "hospital_departments",
            # Hospital Admin
            HospitalAdmin: "hospital_admins",
            # Test Admin
            TestAdmin: "test_admins",
            # Test/Imaging Admin Requests
            TestImageAdminRequest: "test_image_admin_requests"
        }

        if model_class not in table_map:
            raise ValueError(f"Unknown model class: {model_class.__name__}")

        return table_map[model_class]

    def create(self, model: T) -> Optional[T]:
        """Create a new record in the database."""
        try:
            table_name = self._get_table_name(model.__class__)
            data = model.to_dict()

            # Print debug information
            print(f"\n=== CREATE OPERATION ===")
            print(f"Table: {table_name}")
            print(f"Data being sent: {data}")

            # Remove None values and ensure ID is a string
            clean_data = {}
            for k, v in data.items():
                if v is not None:
                    # Convert UUID objects to strings
                    if isinstance(v, UUID):
                        clean_data[k] = str(v)
                    else:
                        clean_data[k] = v

            print(f"Data after cleaning: {clean_data}")

            # Execute the insert operation
            response = self.client.table(table_name).insert(clean_data).execute()

            # Log response details
            print(f"Response status: {getattr(response, 'status_code', 'Unknown')}")
            if hasattr(response, 'data'):
                print(f"Response data: {response.data}")
            else:
                print("No response.data attribute")

            if hasattr(response, 'error') and response.error:
                print(f"Response error: {response.error}")
                if hasattr(response.error, 'details'):
                    print(f"Error details: {response.error.details}")
                return None

            # Process response data
            if hasattr(response, 'data') and response.data and len(response.data) > 0:
                try:
                    # Create a new model instance from the response data
                    new_model = model.__class__.from_dict(response.data[0])
                    print(f"Successfully created record with ID: {new_model.id}")
                    print(f"Returning: {new_model.to_dict()}")
                    return new_model
                except Exception as parse_error:
                    print(f"Error parsing response data: {str(parse_error)}")
                    import traceback
                    print(traceback.format_exc())
                    # If we failed to parse the response, but have confirmation it was created,
                    # return the original model with the ID from the response
                    if 'id' in response.data[0]:
                        model.id = response.data[0]['id']
                        print(f"Setting ID on original model: {model.id}")
                        return model

            print("No data in response, returning None to indicate potential failure")
            return None

        except Exception as e:
            print(f"Exception in create: {str(e)}")
            print(f"Exception type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

    def get_by_id(self, model_class: Type[T], id: Union[str, UUID]) -> Optional[T]:
        """Get a record by ID."""
        table_name = self._get_table_name(model_class)

        response = self.client.table(table_name).select("*").eq("id", str(id)).execute()

        if response.data and len(response.data) > 0:
            return model_class.from_dict(response.data[0])

        return None

    def get_all(self, model_class: Type[T], limit: int = 100, offset: int = 0) -> List[T]:
        """Get all records of a type."""
        table_name = self._get_table_name(model_class)

        response = self.client.table(table_name).select("*").range(offset, offset + limit - 1).execute()

        if response.data:
            return [model_class.from_dict(item) for item in response.data]

        return []

    def query(self, model_class: Type[T], **filters) -> List[T]:
        """Query records with filters."""
        table_name = self._get_table_name(model_class)

        query = self.client.table(table_name).select("*")

        for field, value in filters.items():
            query = query.eq(field, value)

        response = query.execute()

        if response.data:
            return [model_class.from_dict(item) for item in response.data]

        return []

    def get_by_field(self, model_class: Type[T], field: str, value: Any) -> List[T]:
        """Get records by a specific field value."""
        table_name = self._get_table_name(model_class)

        response = self.client.table(table_name).select("*").eq(field, value).execute()

        if response.data:
            return [model_class.from_dict(item) for item in response.data]

        return []

    def update(self, model: T) -> T:
        """Update a record in the database."""
        try:
            table_name = self._get_table_name(model.__class__)
            data = model.to_dict()

            # Print debug information
            print(f"\n=== UPDATE OPERATION ===")
            print(f"Table: {table_name}")
            print(f"ID being updated: {data.get('id')}")
            print(f"Data being sent: {data}")

            # Extract ID for the WHERE clause
            id_str = str(data.pop('id', None))
            if not id_str:
                print("ERROR: Cannot update without an ID")
                return model

            # Clean the data
            clean_data = {}
            for k, v in data.items():
                if v is not None:
                    # Convert UUID objects to strings
                    if isinstance(v, UUID):
                        clean_data[k] = str(v)
                    else:
                        clean_data[k] = v

            print(f"Data after cleaning: {clean_data}")
            print(f"ID for WHERE clause: {id_str}")

            # Execute the update operation
            response = self.client.table(table_name).update(clean_data).eq("id", id_str).execute()

            # Log response details
            print(f"Response status: {getattr(response, 'status_code', 'Unknown')}")
            if hasattr(response, 'data'):
                print(f"Response data: {response.data}")
            else:
                print("No response.data attribute")

            if hasattr(response, 'error') and response.error:
                print(f"Response error: {response.error}")
                if hasattr(response.error, 'details'):
                    print(f"Error details: {response.error.details}")
                return model  # Return original model on error

            # Process response data
            if hasattr(response, 'data') and response.data and len(response.data) > 0:
                try:
                    # Create a new model instance from the response data
                    updated_model = model.__class__.from_dict(response.data[0])
                    print(f"Successfully updated record with ID: {updated_model.id}")
                    print(f"Returning: {updated_model.to_dict()}")
                    return updated_model
                except Exception as parse_error:
                    print(f"Error parsing response data: {str(parse_error)}")
                    import traceback
                    print(traceback.format_exc())
                    # If we failed to parse but have confirmation, return original with ID
                    if 'id' in response.data[0]:
                        model.id = response.data[0]['id']
                        print(f"Preserving ID on original model: {model.id}")
                        return model

            # Add the ID back to the model before returning
            model.id = UUID(id_str) if not isinstance(model.id, UUID) else model.id
            print("No data in response or update may have failed, returning original model")
            return model

        except Exception as e:
            print(f"Exception in update: {str(e)}")
            print(f"Exception type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return model

    def save(self, model: T) -> T:
        """Save a record to the database.
        This method determines whether to create or update based on whether the ID exists.
        """
        try:
            print(f"\n=== SAVE OPERATION ===")
            print(f"Model type: {model.__class__.__name__}")
            print(f"Model ID: {model.id}")

            if not model.id:
                print("No ID found - calling create()")
                return self.create(model)
            else:
                print("ID found - calling update()")
                return self.update(model)
        except Exception as e:
            print(f"Exception in save: {str(e)}")
            print(f"Exception type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return model

    def delete(self, model_class: Type[T], id: Union[str, UUID]) -> bool:
        """Delete a record by ID."""
        try:
            table_name = self._get_table_name(model_class)

            print(f"\n=== DELETE OPERATION ===")
            print(f"Table: {table_name}")
            print(f"ID being deleted: {id}")

            response = self.client.table(table_name).delete().eq("id", str(id)).execute()
            print(f"Response status: {getattr(response, 'status_code', 'Unknown')}")
            print(f"Response data: {response.data}")

            if hasattr(response, 'error') and response.error:
                print(f"Response error: {response.error}")
                if hasattr(response.error, 'details'):
                    print(f"Error details: {response.error.details}")

            result = response.data is not None and len(response.data) > 0
            print(f"Delete successful: {result}")
            return result
        except Exception as e:
            print(f"Exception in delete: {str(e)}")
            print(f"Exception type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False

    # User-specific operations

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        response = self.client.table("users").select("*").eq("username", username).execute()

        if response.data and len(response.data) > 0:
            return User.from_dict(response.data[0])

        return None

    # Doctor-specific operations

    def get_doctors_by_department(self, department_id: Union[str, UUID]) -> List[Doctor]:
        """Get all doctors in a department."""
        try:
            print(f"=== FETCHING DOCTORS BY DEPARTMENT ===")
            print(f"Department ID: {department_id}")

            # Convert UUID to string if needed
            if isinstance(department_id, UUID):
                department_id = str(department_id)

            # Make sure department_id is valid
            if not department_id or not isinstance(department_id, str):
                print(f"Invalid department_id: {department_id}")
                return []

            # Try the direct query approach
            table_name = self._get_table_name(Doctor)
            print(f"Using table: {table_name}")

            # Log the query we're about to execute
            print(f"Executing query: SELECT * FROM {table_name} WHERE department_id = '{department_id}'")

            # Execute the query
            response = self.client.table(table_name).select("*").eq("department_id", department_id).execute()

            # Log query result
            if hasattr(response, 'error') and response.error:
                print(f"Query error: {response.error}")
                return []

            result_count = len(response.data) if hasattr(response, 'data') and response.data else 0
            print(f"Query returned {result_count} doctors")

            # Convert the results to Doctor objects
            if result_count > 0:
                doctors = [Doctor.from_dict(item) for item in response.data]
                doctor_ids = [str(doc.id) for doc in doctors]
                print(f"Doctor IDs: {doctor_ids}")
                return doctors

            return []
        except Exception as e:
            print(f"Error in get_doctors_by_department: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []  # Return empty list instead of raising exception

    def get_doctors_by_hospital(self, hospital_id: Union[str, UUID]) -> List[Doctor]:
        """Get all doctors in a hospital."""
        return self.query(Doctor, hospital_id=str(hospital_id))

    def get_doctors_by_hospital_department(self, hospital_id: Union[str, UUID], department_id: Union[str, UUID]) -> List[Doctor]:
        """Get all doctors in a specific department of a hospital."""
        try:
            return self.query(Doctor, hospital_id=str(hospital_id), department_id=str(department_id))
        except Exception as e:
            print(f"Error fetching doctors by hospital and department: {str(e)}")
            return []

    def get_hospital_departments(self, hospital_id: Union[str, UUID]) -> List[HospitalDepartment]:
        """Get departments for a hospital from the many-to-many relationship table."""
        try:
            # Use the existing query method instead of trying to use raw SQL
            result = self.query(HospitalDepartment, hospital_id=str(hospital_id))
            return result
        except Exception as e:
            print(f"Error in get_hospital_departments: {str(e)}")
            return []  # Return empty list instead of raising exception

    # Appointment-specific operations

    def get_appointments_by_patient(self, patient_id: Union[str, UUID]) -> List[Appointment]:
        """Get all appointments for a patient."""
        try:
            # Use the query method instead of raw SQL
            return self.query(Appointment, patient_id=str(patient_id))
        except Exception as e:
            print(f"Error in get_appointments_by_patient: {str(e)}")
            return []

    def get_appointments_by_doctor(self, doctor_id: Union[str, UUID]) -> List[Appointment]:
        """Get all appointments for a doctor."""
        return self.query(Appointment, doctor_id=str(doctor_id))

    def get_appointments_by_date_range(self,
                                      doctor_id: Union[str, UUID],
                                      start_date: str,
                                      end_date: str) -> List[Appointment]:
        """Get all appointments for a doctor in a date range."""
        table_name = self._get_table_name(Appointment)

        response = self.client.table(table_name).select("*")\
            .eq("doctor_id", str(doctor_id))\
            .gte("date", start_date)\
            .lte("date", end_date)\
            .execute()

        if response.data:
            return [Appointment.from_dict(item) for item in response.data]

        return []

    def get_appointments_by_doctor_date(self, doctor_id, appointment_date):
        """Get all appointments for a doctor on a specific date."""
        try:
            table_name = self._get_table_name(Appointment)

            # Use the Supabase client directly with proper filters
            response = self.client.table(table_name).select("*")\
                .eq("doctor_id", str(doctor_id))\
                .eq("date", str(appointment_date))\
                .execute()

            if response.data:
                return [Appointment.from_dict(item) for item in response.data]
            return []
        except Exception as e:
            print(f"Error in get_appointments_by_doctor_date: {str(e)}")
            return []

    # Availability-specific operations

    def get_availability_by_doctor(self, doctor_id: Union[str, UUID]) -> List[DoctorAvailabilitySlot]:
        """Get all availability slots for a doctor."""
        try:
            # Use the query method instead of raw SQL
            return self.query(DoctorAvailabilitySlot, doctor_id=str(doctor_id))
        except Exception as e:
            print(f"Error in get_availability_by_doctor: {str(e)}")
            return []

    def get_availability_by_day(self, doctor_id: Union[str, UUID], day_of_week: int) -> List[DoctorAvailabilitySlot]:
        """Get availability slots for a doctor on a specific day."""
        table_name = self._get_table_name(DoctorAvailabilitySlot)

        try:
            response = self.client.table(table_name).select("*")\
                .eq("doctor_id", str(doctor_id))\
                .eq("day_of_week", day_of_week)\
                .execute()

            if response.data:
                return [DoctorAvailabilitySlot.from_dict(item) for item in response.data]
            return []
        except Exception as e:
            print(f"Error fetching availability by day: {str(e)}")
            return []

    def add_doctor_availability_slot(self, slot: DoctorAvailabilitySlot) -> Optional[DoctorAvailabilitySlot]:
        """Add a new availability slot for a doctor."""
        try:
            print(f"Adding availability slot: day={slot.day_of_week}, start={slot.start_time}, end={slot.end_time}")

            # First validate the data
            if not slot.doctor_id:
                print("Error: doctor_id is required for availability slot")
                return None

            if not isinstance(slot.doctor_id, UUID):
                try:
                    slot.doctor_id = UUID(slot.doctor_id)
                except (ValueError, TypeError) as e:
                    print(f"Error converting doctor_id to UUID: {e}")
                    return None

            # Create the slot using our general create method
            created_slot = self.create(slot)

            if created_slot:
                print(f"Successfully created availability slot with ID: {created_slot.id}")
            else:
                print("Failed to create availability slot")

            return created_slot
        except Exception as e:
            print(f"Error in add_doctor_availability_slot: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None

    def update_doctor_availability_slot(self, slot: DoctorAvailabilitySlot) -> bool:
        """Update an existing availability slot."""
        try:
            print(f"Updating availability slot ID: {slot.id}, day={slot.day_of_week}, start={slot.start_time}, end={slot.end_time}")

            # Validate that the slot has an ID
            if not slot.id:
                print("Error: Cannot update slot without ID")
                return False

            # Ensure doctor_id is a UUID
            if not isinstance(slot.doctor_id, UUID):
                try:
                    slot.doctor_id = UUID(slot.doctor_id)
                except (ValueError, TypeError) as e:
                    print(f"Error converting doctor_id to UUID: {e}")
                    return False

            # Update the slot using our general update method
            updated_slot = self.update(slot)

            if updated_slot:
                print(f"Successfully updated availability slot ID: {updated_slot.id}")
                return True
            else:
                print(f"Failed to update availability slot ID: {slot.id}")
                return False
        except Exception as e:
            print(f"Error in update_doctor_availability_slot: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

    def delete_doctor_availability_slot(self, slot_id: Union[str, UUID]) -> bool:
        """Delete an availability slot by ID."""
        try:
            return self.delete(DoctorAvailabilitySlot, slot_id)
        except Exception as e:
            print(f"Error deleting availability slot: {str(e)}")
            return False

    def bulk_update_doctor_availability(self, slots: List[DoctorAvailabilitySlot]) -> bool:
        """Update multiple availability slots in a transaction.

        Args:
            slots: List of DoctorAvailabilitySlot objects to update

        Returns:
            bool: True if all updates were successful, False otherwise
        """
        all_successful = True

        for slot in slots:
            result = self.update_doctor_availability_slot(slot)
            if not result:
                all_successful = False
                print(f"Failed to update slot: {slot.id}")

        return all_successful

    def get_available_slots_for_booking(self, doctor_id: Union[str, UUID], date_str: str) -> List[Dict[str, Any]]:
        """Get available time slots for booking on a specific date.

        Args:
            doctor_id: ID of the doctor
            date_str: Date string in ISO format (YYYY-MM-DD)

        Returns:
            List of available time slots with start and end times
        """
        from datetime import datetime, timedelta

        # Parse the date string to get the day of week (0=Monday, 6=Sunday)
        date_obj = datetime.fromisoformat(date_str)
        day_of_week = date_obj.weekday()  # Monday is 0

        # Get availability for this day
        slots = self.get_availability_by_day(doctor_id, day_of_week)

        # Get any existing appointments for this date to check for conflicts
        appointments = self.get_appointments_by_date(doctor_id, date_str)

        available_slots = []

        for slot in slots:
            if slot.is_available:
                # Check slot duration, default to 30 min if not specified
                duration_minutes = slot.slot_duration_minutes or 30

                # Create time slots within the available period
                slot_time = datetime.combine(date_obj.date(), slot.start_time)
                end_time = datetime.combine(date_obj.date(), slot.end_time)

                while slot_time + timedelta(minutes=duration_minutes) <= end_time:
                    # Check if this slot conflicts with any appointments
                    slot_end = slot_time + timedelta(minutes=duration_minutes)
                    is_available = True

                    for appt in appointments:
                        # Check if appointment overlaps with this slot
                        # Assuming appointment time_slot is stored as a range like [start, end)
                        appt_start = appt.get('start_time')
                        appt_end = appt.get('end_time')

                        if (appt_start and appt_end and
                            ((slot_time >= appt_start and slot_time < appt_end) or
                             (slot_end > appt_start and slot_end <= appt_end) or
                             (slot_time <= appt_start and slot_end >= appt_end))):
                            is_available = False
                            break

                    if is_available:
                        available_slots.append({
                            'start_time': slot_time.strftime('%H:%M'),
                            'end_time': slot_end.strftime('%H:%M'),
                            'duration_minutes': duration_minutes
                        })

                    # Move to next slot
                    slot_time += timedelta(minutes=duration_minutes)

        return available_slots

    def get_appointments_by_date(self, doctor_id: Union[str, UUID], date_str: str) -> List[Dict[str, Any]]:
        """Get all appointments for a doctor on a specific date."""
        table_name = self._get_table_name(Appointment)

        try:
            response = self.client.table(table_name).select("*")\
                .eq("doctor_id", str(doctor_id))\
                .eq("date", date_str)\
                .execute()

            if response.data:
                return response.data
            return []
        except Exception as e:
            print(f"Error fetching appointments by date: {str(e)}")
            return []

    # EHR-specific operations

    def get_ehr_by_patient_id(self, patient_id: Union[str, UUID]) -> Optional[EHR]:
        """Get the EHR record for a patient."""
        ehrs = self.query(EHR, patient_id=str(patient_id))
        return ehrs[0] if ehrs else None

    def get_visits_by_ehr_id(self, ehr_id: Union[str, UUID]) -> List[EHR_Visit]:
        """Get all visits for an EHR."""
        return self.query(EHR_Visit, ehr_id=str(ehr_id))

    def get_diagnoses_by_visit_id(self, visit_id: Union[str, UUID]) -> List[EHR_Diagnosis]:
        """Get all diagnoses for a visit."""
        return self.query(EHR_Diagnosis, visit_id=str(visit_id))

    def get_medications_by_visit_id(self, visit_id: Union[str, UUID]) -> List[EHR_Medication]:
        """Get all medications for a visit."""
        return self.query(EHR_Medication, visit_id=str(visit_id))

    def get_allergies_by_ehr_id(self, ehr_id: Union[str, UUID]) -> List[EHR_Allergy]:
        """Get all allergies for an EHR."""
        return self.query(EHR_Allergy, ehr_id=str(ehr_id))

    def get_procedures_by_visit_id(self, visit_id: Union[str, UUID]) -> List[EHR_Procedure]:
        """Get all procedures for a visit."""
        return self.query(EHR_Procedure, visit_id=str(visit_id))

    def get_vitals_by_visit_id(self, visit_id: Union[str, UUID]) -> List[EHR_Vital]:
        """Get all vitals for a visit."""
        return self.query(EHR_Vital, visit_id=str(visit_id))

    def get_immunizations_by_ehr_id(self, ehr_id: Union[str, UUID]) -> List[EHR_Immunization]:
        """Get all immunizations for an EHR."""
        return self.query(EHR_Immunization, ehr_id=str(ehr_id))

    def get_test_results_by_ehr_id(self, ehr_id: Union[str, UUID]) -> List[EHR_TestResult]:
        """Get all test results for an EHR."""
        return self.query(EHR_TestResult, ehr_id=str(ehr_id))

    def get_provider_notes_by_visit_id(self, visit_id: Union[str, UUID]) -> List[EHR_ProviderNote]:
        """Get all provider notes for a visit."""
        return self.query(EHR_ProviderNote, visit_id=str(visit_id))

    def get_prescriptions_by_visit_id(self, visit_id: Union[str, UUID]) -> List[Prescription]:
        """Get all prescriptions for a visit."""
        return self.query(Prescription, visit_id=str(visit_id))

    def get_recent_visits(self, ehr_id: Union[str, UUID], limit: int = 5) -> List[EHR_Visit]:
        """Get recent visits for an EHR."""
        table_name = self._get_table_name(EHR_Visit)

        response = self.client.table(table_name).select("*")\
            .eq("ehr_id", str(ehr_id))\
            .order("date", desc=True)\
            .order("time", desc=True)\
            .limit(limit)\
            .execute()

        if response.data:
            return [EHR_Visit.from_dict(item) for item in response.data]

        return []

    def get_patient_medical_summary(self, patient_id: Union[str, UUID]) -> Dict[str, Any]:
        """
        Get a comprehensive medical summary for a patient.

        Returns a dictionary containing:
        - EHR record
        - Recent visits
        - Active medications
        - Allergies
        - Immunizations
        - Recent test results
        """
        # Get the EHR record
        ehr = self.get_ehr_by_patient_id(patient_id)

        if not ehr:
            return {
                "error": "No EHR found for this patient"
            }

        ehr_id = ehr.id

        # Get recent visits
        recent_visits = self.get_recent_visits(ehr_id, 3)

        # Get active medications (from recent visits)
        active_medications = []
        if recent_visits:
            for visit in recent_visits:
                visit_meds = self.get_medications_by_visit_id(visit.id)
                active_medications.extend(visit_meds)

        # Get allergies
        allergies = self.get_allergies_by_ehr_id(ehr_id)

        # Get immunizations
        immunizations = self.get_immunizations_by_ehr_id(ehr_id)

        # Get recent test results
        test_results = self.get_test_results_by_ehr_id(ehr_id)

        return {
            "ehr": ehr.to_dict(),
            "recent_visits": [visit.to_dict() for visit in recent_visits],
            "active_medications": [med.to_dict() for med in active_medications],
            "allergies": [allergy.to_dict() for allergy in allergies],
            "immunizations": [immunization.to_dict() for immunization in immunizations],
            "test_results": [result.to_dict() for result in test_results]
        }

    def get_reset_token_by_token(self, token: str) -> Optional[PasswordResetToken]:
        """Get a password reset token by its token value."""
        response = self.client.table("password_reset_tokens").select("*").eq("token", token).execute()

        if response.data and len(response.data) > 0:
            return PasswordResetToken.from_dict(response.data[0])

        return None

    def get_valid_reset_token_by_user_id(self, user_id: Union[str, UUID]) -> Optional[PasswordResetToken]:
        """Get the most recent valid (not used, not expired) reset token for a user."""
        response = self.client.table("password_reset_tokens") \
            .select("*") \
            .eq("user_id", str(user_id)) \
            .eq("used", False) \
            .gt("expires_at", datetime.now().isoformat()) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

        if response.data and len(response.data) > 0:
            return PasswordResetToken.from_dict(response.data[0])

        return None

    def mark_token_as_used(self, token_id: Union[str, UUID]) -> bool:
        """Mark a password reset token as used."""
        response = self.client.table("password_reset_tokens") \
            .update({"used": True}) \
            .eq("id", str(token_id)) \
            .execute()

        return response.data is not None and len(response.data) > 0

    def get_doctor_notes(self, doctor_id: Union[str, UUID]) -> List[DoctorNote]:
        """Get all notes for a doctor."""
        return self.query(DoctorNote, doctor_id=str(doctor_id))

    # Add missing fetch_all method after the query method
    def fetch_all(self, query: str, params: tuple = None) -> List[Any]:
        """Execute a raw SQL query and return all results.

        Args:
            query: SQL query string with %s placeholders
            params: Tuple of parameter values

        Returns:
            List of model objects from the results
        """
        try:
            print(f"Executing SQL query: {query} with params: {params}")

            # Extract table name from the query
            import re
            table_match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
            if not table_match:
                raise ValueError(f"Cannot extract table name from query: {query}")

            table_name = table_match.group(1).strip()
            print(f"Extracted table name: {table_name}")

            # Map table name to model class
            table_to_model = {
                "users": User,
                "hospitals": Hospital,
                "departments": Department,
                "patients": Patient,
                "doctors": Doctor,
                "doctor_availability": DoctorAvailabilitySlot,
                "doctor_availability_slots": DoctorAvailabilitySlot,
                "appointments": Appointment,
                "hospital_departments": HospitalDepartment
                # Add other mappings as needed
            }

            if table_name not in table_to_model:
                raise ValueError(f"Unknown table name: {table_name}")

            model_class = table_to_model[table_name]

            # Build RPC call
            # Note: This is a simplified approach and might need adjustments for complex queries
            if params:
                # Replace SQL placeholders with named parameters
                param_dict = {}
                modified_query = query
                for i, param in enumerate(params):
                    param_name = f"p{i}"
                    param_dict[param_name] = param
                    modified_query = modified_query.replace("%s", f":{param_name}", 1)

                response = self.client.rpc('run_query', {"query": modified_query, "params": param_dict}).execute()
            else:
                response = self.client.rpc('run_query', {"query": query}).execute()

            if response.error:
                print(f"Error executing query: {response.error}")
                return []

            # Convert results to model objects
            if response.data:
                return [model_class.from_dict(item) for item in response.data]

            return []

        except Exception as e:
            print(f"Error in fetch_all: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []

# Singleton instance for easy access
db = Database()