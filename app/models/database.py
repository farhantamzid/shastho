from datetime import datetime, date, time
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from uuid import UUID, uuid4
from dateutil.parser import isoparse

# Helper function to parse ISO dates safely
def parse_iso_datetime(date_string: Optional[str]) -> Optional[datetime]:
    if date_string:
        try:
            return isoparse(date_string)
        except (ValueError, TypeError):
            return None
    return None


class UserRole(str, Enum):
    ADMIN = 'admin'
    PATIENT = 'patient'
    DOCTOR = 'doctor'
    STAFF = 'staff'
    HOSPITAL_ADMIN = 'hospital_admin'
    TEST_ADMIN = 'test_admin'


class UserStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'


class Gender(str, Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'


class Language(str, Enum):
    ENGLISH = 'english'
    BANGLA = 'bangla'


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
        updated_at: datetime = None,
        profile_picture_url: str = None,
        language_preference: Language = Language.ENGLISH
    ):
        self.id = id or uuid4()
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.profile_picture_url = profile_picture_url
        self.language_preference = language_preference

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User instance from a dictionary."""
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            password_hash=data.get('password_hash'),
            role=UserRole(data.get('role')) if data.get('role') else None,
            status=UserStatus(data.get('status')) if data.get('status') else UserStatus.ACTIVE,
            created_at=parse_iso_datetime(data.get('created_at')),
            updated_at=parse_iso_datetime(data.get('updated_at')),
            profile_picture_url=data.get('profile_picture_url'),
            language_preference=Language(data.get('language_preference')) if data.get('language_preference') else Language.ENGLISH
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
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'profile_picture_url': self.profile_picture_url,
            'language_preference': self.language_preference.value if self.language_preference else None
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
            created_at=parse_iso_datetime(data.get('created_at')),
            updated_at=parse_iso_datetime(data.get('updated_at'))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        # Ensure created_at and updated_at are properly formatted
        created_at_iso = None
        if self.created_at:
            if isinstance(self.created_at, str):
                created_at_iso = self.created_at
            else:
                created_at_iso = self.created_at.isoformat()

        updated_at_iso = None
        if self.updated_at:
            if isinstance(self.updated_at, str):
                updated_at_iso = self.updated_at
            else:
                updated_at_iso = self.updated_at.isoformat()

        return {
            'id': str(self.id),
            'name': self.name,
            'location': self.location,
            'address': self.address,
            'contact_number': self.contact_number,
            'created_at': created_at_iso,
            'updated_at': updated_at_iso
        }


class Department:
    """Model representing a department in the system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        name: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.name = name
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Department':
        """Create a Department instance from a dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            created_at=parse_iso_datetime(data.get('created_at')),
            updated_at=parse_iso_datetime(data.get('updated_at'))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        # Ensure created_at and updated_at are properly formatted
        created_at_iso = None
        if self.created_at:
            if isinstance(self.created_at, str):
                created_at_iso = self.created_at
            else:
                created_at_iso = self.created_at.isoformat()

        updated_at_iso = None
        if self.updated_at:
            if isinstance(self.updated_at, str):
                updated_at_iso = self.updated_at
            else:
                updated_at_iso = self.updated_at.isoformat()

        return {
            'id': str(self.id),
            'name': self.name,
            'created_at': created_at_iso,
            'updated_at': updated_at_iso
        }


class HospitalDepartment:
    """Model representing the many-to-many relationship between hospitals and departments."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        hospital_id: UUID = None,
        department_id: UUID = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.hospital_id = hospital_id
        self.department_id = department_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HospitalDepartment':
        """Create a HospitalDepartment instance from a dictionary."""
        try:
            # Convert string IDs to UUID objects safely
            id_val = data.get('id')
            hospital_id_val = data.get('hospital_id')
            department_id_val = data.get('department_id')

            # ID conversion
            if id_val:
                if isinstance(id_val, str):
                    id_val = UUID(id_val)
                elif isinstance(id_val, UUID):
                    pass  # Already a UUID
                else:
                    print(f"Warning: Unexpected ID type: {type(id_val)}")
                    id_val = None  # Will generate a new UUID in __init__

            # Hospital ID conversion
            if hospital_id_val:
                if isinstance(hospital_id_val, str):
                    hospital_id_val = UUID(hospital_id_val)
                elif isinstance(hospital_id_val, UUID):
                    pass  # Already a UUID
                else:
                    print(f"Warning: Unexpected hospital_id type: {type(hospital_id_val)}")
                    hospital_id_val = None

            # Department ID conversion
            if department_id_val:
                if isinstance(department_id_val, str):
                    department_id_val = UUID(department_id_val)
                elif isinstance(department_id_val, UUID):
                    pass  # Already a UUID
                else:
                    print(f"Warning: Unexpected department_id type: {type(department_id_val)}")
                    department_id_val = None

            # Parse dates
            created_at = parse_iso_datetime(data.get('created_at'))
            updated_at = parse_iso_datetime(data.get('updated_at'))

            return cls(
                id=id_val,
                hospital_id=hospital_id_val,
                department_id=department_id_val,
                created_at=created_at,
                updated_at=updated_at
            )
        except Exception as e:
            print(f"Error in HospitalDepartment.from_dict: {str(e)}")
            import traceback
            print(traceback.format_exc())
            print(f"Raw data: {data}")
            # Return a new instance with only the ID if possible
            return cls(id=UUID(data.get('id')) if data.get('id') and isinstance(data.get('id'), str) else None)

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        # Ensure created_at and updated_at are properly formatted
        created_at_iso = None
        if self.created_at:
            if isinstance(self.created_at, str):
                created_at_iso = self.created_at
            else:
                created_at_iso = self.created_at.isoformat()

        updated_at_iso = None
        if self.updated_at:
            if isinstance(self.updated_at, str):
                updated_at_iso = self.updated_at
            else:
                updated_at_iso = self.updated_at.isoformat()

        return {
            'id': str(self.id),
            'hospital_id': str(self.hospital_id) if self.hospital_id else None,
            'department_id': str(self.department_id) if self.department_id else None,
            'created_at': created_at_iso,
            'updated_at': updated_at_iso
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
        contact_number: str = None,
        hospital_id: UUID = None,
        department_id: UUID = None,
        first_login_complete: bool = False,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.user_id = user_id
        self.full_name = full_name
        self.specialization = specialization
        self.credentials = credentials
        self.contact_number = contact_number
        self.hospital_id = hospital_id
        self.department_id = department_id
        self.first_login_complete = first_login_complete
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
            contact_number=data.get('contact_number'),
            hospital_id=data.get('hospital_id'),
            department_id=data.get('department_id'),
            first_login_complete=data.get('first_login_complete', False),
            created_at=parse_iso_datetime(data.get('created_at')),
            updated_at=parse_iso_datetime(data.get('updated_at'))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'full_name': self.full_name,
            'specialization': self.specialization,
            'credentials': self.credentials,
            'contact_number': self.contact_number,
            'hospital_id': str(self.hospital_id) if self.hospital_id else None,
            'department_id': str(self.department_id) if self.department_id else None,
            'first_login_complete': self.first_login_complete,
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


class HospitalAdmin:
    """Model representing a hospital administrator in the system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        user_id: UUID = None,
        full_name: str = None,
        hospital_id: UUID = None,
        contact_number: str = None,
        address: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.user_id = user_id
        self.full_name = full_name
        self.hospital_id = hospital_id
        self.contact_number = contact_number
        self.address = address
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HospitalAdmin':
        """Create a HospitalAdmin instance from a dictionary."""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            full_name=data.get('full_name'),
            hospital_id=data.get('hospital_id'),
            contact_number=data.get('contact_number'),
            address=data.get('address'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'full_name': self.full_name,
            'hospital_id': str(self.hospital_id) if self.hospital_id else None,
            'contact_number': self.contact_number,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AdminRequestStatus(str, Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'


class TestImageAdminRequest:
    """Model representing a request for a Test/Imaging Admin role."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        hospital_id: UUID = None,
        full_name: str = None,
        email: str = None,
        contact_number: str = None,
        department: str = None,
        qualification: str = None,
        experience: str = None,
        reason: str = None,
        submitted_by: UUID = None,  # HospitalAdmin user_id who submitted the request
        status: AdminRequestStatus = AdminRequestStatus.PENDING,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.hospital_id = hospital_id
        self.full_name = full_name
        self.email = email
        self.contact_number = contact_number
        self.department = department
        self.qualification = qualification
        self.experience = experience
        self.reason = reason
        self.submitted_by = submitted_by
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestImageAdminRequest':
        """Create a TestImageAdminRequest instance from a dictionary."""
        return cls(
            id=data.get('id'),
            hospital_id=data.get('hospital_id'),
            full_name=data.get('full_name'),
            email=data.get('email'),
            contact_number=data.get('contact_number'),
            department=data.get('department'),
            qualification=data.get('qualification'),
            experience=data.get('experience'),
            reason=data.get('reason'),
            submitted_by=data.get('submitted_by'),
            status=AdminRequestStatus(data.get('status')) if data.get('status') else AdminRequestStatus.PENDING,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'hospital_id': str(self.hospital_id) if self.hospital_id else None,
            'full_name': self.full_name,
            'email': self.email,
            'contact_number': self.contact_number,
            'department': self.department,
            'qualification': self.qualification,
            'experience': self.experience,
            'reason': self.reason,
            'submitted_by': str(self.submitted_by) if self.submitted_by else None,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PasswordResetToken:
    """Model representing a password reset token."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        user_id: UUID = None,
        token: str = None,
        expires_at: datetime = None,
        created_at: datetime = None,
        used: bool = False
    ):
        self.id = id or uuid4()
        self.user_id = user_id
        self.token = token
        self.expires_at = expires_at
        self.created_at = created_at or datetime.now()
        self.used = used

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PasswordResetToken':
        """Create a PasswordResetToken instance from a dictionary."""
        return cls(
            id=UUID(data.get('id')) if data.get('id') else None,
            user_id=UUID(data.get('user_id')) if data.get('user_id') else None,
            token=data.get('token'),
            expires_at=data.get('expires_at'),
            created_at=data.get('created_at'),
            used=data.get('used', False)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'token': self.token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'used': self.used
        }

    def is_valid(self) -> bool:
        """Check if the token is valid (not used and not expired)."""
        if self.used:
            return False

        if self.expires_at and datetime.now() > self.expires_at:
            return False

        return True


class UserSession:
    """Model for user sessions."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        user_id: UUID = None,
        session_id: str = None,
        user_agent: str = None,
        ip_address: str = None,
        last_activity: datetime = None,
        created_at: datetime = None,
        is_active: bool = True
    ):
        self.id = id or uuid4()
        self.user_id = user_id
        self.session_id = session_id
        self.user_agent = user_agent
        self.ip_address = ip_address
        self.last_activity = last_activity or datetime.now()
        self.created_at = created_at or datetime.now()
        self.is_active = is_active

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSession':
        """Create a UserSession instance from a dictionary."""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            session_id=data.get('session_id'),
            user_agent=data.get('user_agent'),
            ip_address=data.get('ip_address'),
            last_activity=data.get('last_activity'),
            created_at=data.get('created_at'),
            is_active=data.get('is_active', True)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'session_id': self.session_id,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }


class DoctorNote:
    """Model for storing notes about doctor approval/rejection."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        doctor_id: UUID = None,
        note_type: str = None,  # 'approval', 'rejection'
        content: str = None,
        created_by: UUID = None,
        created_at: datetime = None
    ):
        self.id = id or uuid4()
        self.doctor_id = doctor_id
        self.note_type = note_type
        self.content = content
        self.created_by = created_by
        self.created_at = created_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DoctorNote':
        """Create a DoctorNote instance from a dictionary."""
        return cls(
            id=data.get('id'),
            doctor_id=data.get('doctor_id'),
            note_type=data.get('note_type'),
            content=data.get('content'),
            created_by=data.get('created_by'),
            created_at=data.get('created_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'doctor_id': str(self.doctor_id) if self.doctor_id else None,
            'note_type': self.note_type,
            'content': self.content,
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }