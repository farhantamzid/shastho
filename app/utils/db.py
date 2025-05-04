import os
from typing import List, Dict, Any, Optional, Union, Type, TypeVar
from uuid import UUID

from supabase import create_client, Client
from dotenv import load_dotenv

from app.models.database import (
    User, Hospital, Department, Patient, Doctor,
    DoctorAvailabilitySlot, Appointment
)

# Load environment variables
load_dotenv()

T = TypeVar('T', User, Hospital, Department, Patient, Doctor, DoctorAvailabilitySlot, Appointment)

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

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

        self.client: Client = create_client(supabase_url, supabase_key)

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
            Appointment: "appointments"
        }

        if model_class not in table_map:
            raise ValueError(f"Unknown model class: {model_class.__name__}")

        return table_map[model_class]

    def create(self, model: T) -> T:
        """Create a new record in the database."""
        table_name = self._get_table_name(model.__class__)
        data = model.to_dict()

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        response = self.client.table(table_name).insert(data).execute()

        if response.data and len(response.data) > 0:
            return model.__class__.from_dict(response.data[0])

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

    def update(self, model: T) -> T:
        """Update a record in the database."""
        table_name = self._get_table_name(model.__class__)
        data = model.to_dict()

        # Remove None values and id (for update)
        id_str = data.pop('id', None)
        data = {k: v for k, v in data.items() if v is not None}

        response = self.client.table(table_name).update(data).eq("id", id_str).execute()

        if response.data and len(response.data) > 0:
            return model.__class__.from_dict(response.data[0])

        return model

    def delete(self, model_class: Type[T], id: Union[str, UUID]) -> bool:
        """Delete a record by ID."""
        table_name = self._get_table_name(model_class)

        response = self.client.table(table_name).delete().eq("id", str(id)).execute()

        return response.data is not None and len(response.data) > 0

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


# Singleton instance for easy access
db = Database()