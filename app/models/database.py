from datetime import datetime, date, time
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from uuid import UUID, uuid4


class UserRole(str, Enum):
    ADMIN = 'admin'
    PATIENT = 'patient'
    DOCTOR = 'doctor'
    STAFF = 'staff'


class UserStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'


class Gender(str, Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'


class AppointmentStatus(str, Enum):
    SCHEDULED = 'scheduled'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    NO_SHOW = 'no-show'


class User:
    """Model representing a user in the system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        username: str = None,
        password_hash: str = None,
        role: UserRole = None,
        status: UserStatus = UserStatus.ACTIVE,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User instance from a dictionary."""
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            password_hash=data.get('password_hash'),
            role=UserRole(data.get('role')) if data.get('role') else None,
            status=UserStatus(data.get('status')) if data.get('status') else UserStatus.ACTIVE,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role.value if self.role else None,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Hospital:
    """Model representing a hospital in the system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        name: str = None,
        location: str = None,
        address: str = None,
        contact_number: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.name = name
        self.location = location
        self.address = address
        self.contact_number = contact_number
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hospital':
        """Create a Hospital instance from a dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            location=data.get('location'),
            address=data.get('address'),
            contact_number=data.get('contact_number'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'name': self.name,
            'location': self.location,
            'address': self.address,
            'contact_number': self.contact_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Department:
    """Model representing a department in a hospital."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        name: str = None,
        hospital_id: UUID = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.name = name
        self.hospital_id = hospital_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Department':
        """Create a Department instance from a dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            hospital_id=data.get('hospital_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'name': self.name,
            'hospital_id': str(self.hospital_id) if self.hospital_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Patient:
    """Model representing a patient in the system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        user_id: UUID = None,
        full_name: str = None,
        date_of_birth: date = None,
        gender: Gender = None,
        contact_number: str = None,
        address: str = None,
        emergency_contact_name: str = None,
        emergency_contact_number: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.user_id = user_id
        self.full_name = full_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.contact_number = contact_number
        self.address = address
        self.emergency_contact_name = emergency_contact_name
        self.emergency_contact_number = emergency_contact_number
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Patient':
        """Create a Patient instance from a dictionary."""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            full_name=data.get('full_name'),
            date_of_birth=data.get('date_of_birth'),
            gender=Gender(data.get('gender')) if data.get('gender') else None,
            contact_number=data.get('contact_number'),
            address=data.get('address'),
            emergency_contact_name=data.get('emergency_contact_name'),
            emergency_contact_number=data.get('emergency_contact_number'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender.value if self.gender else None,
            'contact_number': self.contact_number,
            'address': self.address,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_number': self.emergency_contact_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Doctor:
    """Model representing a doctor in the system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        user_id: UUID = None,
        full_name: str = None,
        specialization: str = None,
        credentials: str = None,
        hospital_id: UUID = None,
        department_id: UUID = None,
        contact_number: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.user_id = user_id
        self.full_name = full_name
        self.specialization = specialization
        self.credentials = credentials
        self.hospital_id = hospital_id
        self.department_id = department_id
        self.contact_number = contact_number
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Doctor':
        """Create a Doctor instance from a dictionary."""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            full_name=data.get('full_name'),
            specialization=data.get('specialization'),
            credentials=data.get('credentials'),
            hospital_id=data.get('hospital_id'),
            department_id=data.get('department_id'),
            contact_number=data.get('contact_number'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'full_name': self.full_name,
            'specialization': self.specialization,
            'credentials': self.credentials,
            'hospital_id': str(self.hospital_id) if self.hospital_id else None,
            'department_id': str(self.department_id) if self.department_id else None,
            'contact_number': self.contact_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DoctorAvailabilitySlot:
    """Model representing a doctor's availability slot."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        doctor_id: UUID = None,
        day_of_week: int = None,  # 0-6 representing Monday-Sunday
        start_time: time = None,
        end_time: time = None,
        is_available: bool = True,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.doctor_id = doctor_id
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.is_available = is_available
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DoctorAvailabilitySlot':
        """Create a DoctorAvailabilitySlot instance from a dictionary."""
        return cls(
            id=data.get('id'),
            doctor_id=data.get('doctor_id'),
            day_of_week=data.get('day_of_week'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            is_available=data.get('is_available', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'doctor_id': str(self.doctor_id) if self.doctor_id else None,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Appointment:
    """Model representing an appointment in the system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        patient_id: UUID = None,
        doctor_id: UUID = None,
        hospital_id: UUID = None,
        department_id: UUID = None,
        date: date = None,
        time_slot: tuple = None,  # (start_time, end_time) as datetime objects
        status: AppointmentStatus = AppointmentStatus.SCHEDULED,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.hospital_id = hospital_id
        self.department_id = department_id
        self.date = date
        self.time_slot = time_slot
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Appointment':
        """Create an Appointment instance from a dictionary."""
        time_slot = None
        if 'time_slot' in data and data['time_slot']:
            # Parse the time_slot range from Postgres
            # Expected format: "[2023-01-01 10:00:00+00,2023-01-01 11:00:00+00)"
            # Convert to a tuple of datetime objects
            time_slot_str = data['time_slot'].strip('[]()').split(',')
            if len(time_slot_str) == 2:
                start_str, end_str = time_slot_str
                try:
                    # This is a simplification - actual parsing would be more complex
                    time_slot = (datetime.fromisoformat(start_str), datetime.fromisoformat(end_str))
                except ValueError:
                    pass

        return cls(
            id=data.get('id'),
            patient_id=data.get('patient_id'),
            doctor_id=data.get('doctor_id'),
            hospital_id=data.get('hospital_id'),
            department_id=data.get('department_id'),
            date=data.get('date'),
            time_slot=time_slot,
            status=AppointmentStatus(data.get('status')) if data.get('status') else AppointmentStatus.SCHEDULED,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        time_slot_dict = None
        if self.time_slot and len(self.time_slot) == 2:
            start_time, end_time = self.time_slot
            if isinstance(start_time, datetime) and isinstance(end_time, datetime):
                time_slot_dict = {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                }

        return {
            'id': str(self.id),
            'patient_id': str(self.patient_id) if self.patient_id else None,
            'doctor_id': str(self.doctor_id) if self.doctor_id else None,
            'hospital_id': str(self.hospital_id) if self.hospital_id else None,
            'department_id': str(self.department_id) if self.department_id else None,
            'date': self.date.isoformat() if self.date else None,
            'time_slot': time_slot_dict,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }