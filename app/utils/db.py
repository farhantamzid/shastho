import os
from typing import List, Dict, Any, Optional, Union, Type, TypeVar
from uuid import UUID
from datetime import datetime

from supabase import create_client, Client
from dotenv import load_dotenv

from app.models.database import (
    User, Hospital, Department, Patient, Doctor,
    DoctorAvailabilitySlot, Appointment, PasswordResetToken,
    DoctorNote, UserSession, HospitalDepartment, HospitalAdmin
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
            Prescription, PasswordResetToken, DoctorNote, UserSession, HospitalDepartment, HospitalAdmin)

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
            HospitalAdmin: "hospital_admins"
        }

        if model_class not in table_map:
            raise ValueError(f"Unknown model class: {model_class.__name__}")

        return table_map[model_class]

    def create(self, model: T) -> T:
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
                return model  # Return original model on error

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

            print("No data in response, returning original model")
            return model

        except Exception as e:
            print(f"Exception in create: {str(e)}")
            print(f"Exception type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return model

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
        return self.query(Doctor, department_id=str(department_id))

    def get_doctors_by_hospital(self, hospital_id: Union[str, UUID]) -> List[Doctor]:
        """Get all doctors in a hospital."""
        return self.query(Doctor, hospital_id=str(hospital_id))

    # Appointment-specific operations

    def get_appointments_by_patient(self, patient_id: Union[str, UUID]) -> List[Appointment]:
        """Get all appointments for a patient."""
        return self.query(Appointment, patient_id=str(patient_id))

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

    # Availability-specific operations

    def get_availability_by_doctor(self, doctor_id: Union[str, UUID]) -> List[DoctorAvailabilitySlot]:
        """Get all availability slots for a doctor."""
        return self.query(DoctorAvailabilitySlot, doctor_id=str(doctor_id))

    def get_availability_by_day(self, doctor_id: Union[str, UUID], day_of_week: int) -> List[DoctorAvailabilitySlot]:
        """Get all availability slots for a doctor on a specific day."""
        table_name = self._get_table_name(DoctorAvailabilitySlot)

        response = self.client.table(table_name).select("*")\
            .eq("doctor_id", str(doctor_id))\
            .eq("day_of_week", day_of_week)\
            .execute()

        if response.data:
            return [DoctorAvailabilitySlot.from_dict(item) for item in response.data]

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

# Singleton instance for easy access
db = Database()