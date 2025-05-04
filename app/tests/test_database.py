import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, date, time
from uuid import UUID, uuid4

from app.models.database import (
    User, Hospital, Department, Patient, Doctor,
    DoctorAvailabilitySlot, Appointment,
    UserRole, UserStatus, Gender, AppointmentStatus
)
from app.utils.db import Database


class TestDatabaseModels(unittest.TestCase):
    """Test cases for database models."""

    def test_user_model(self):
        """Test the User model."""
        user_id = uuid4()
        user = User(
            id=user_id,
            username="test_user",
            password_hash="hashed_password",
            role=UserRole.DOCTOR,
            status=UserStatus.ACTIVE
        )

        # Test to_dict
        user_dict = user.to_dict()
        self.assertEqual(user_dict["id"], str(user_id))
        self.assertEqual(user_dict["username"], "test_user")
        self.assertEqual(user_dict["password_hash"], "hashed_password")
        self.assertEqual(user_dict["role"], "doctor")
        self.assertEqual(user_dict["status"], "active")

        # Test from_dict
        new_user = User.from_dict(user_dict)
        self.assertEqual(str(new_user.id), str(user_id))
        self.assertEqual(new_user.username, "test_user")
        self.assertEqual(new_user.password_hash, "hashed_password")
        self.assertEqual(new_user.role, UserRole.DOCTOR)
        self.assertEqual(new_user.status, UserStatus.ACTIVE)

    def test_hospital_model(self):
        """Test the Hospital model."""
        hospital_id = uuid4()
        hospital = Hospital(
            id=hospital_id,
            name="General Hospital",
            location="Downtown",
            address="123 Main St",
            contact_number="123-456-7890"
        )

        # Test to_dict
        hospital_dict = hospital.to_dict()
        self.assertEqual(hospital_dict["id"], str(hospital_id))
        self.assertEqual(hospital_dict["name"], "General Hospital")
        self.assertEqual(hospital_dict["location"], "Downtown")
        self.assertEqual(hospital_dict["address"], "123 Main St")
        self.assertEqual(hospital_dict["contact_number"], "123-456-7890")

        # Test from_dict
        new_hospital = Hospital.from_dict(hospital_dict)
        self.assertEqual(str(new_hospital.id), str(hospital_id))
        self.assertEqual(new_hospital.name, "General Hospital")
        self.assertEqual(new_hospital.location, "Downtown")
        self.assertEqual(new_hospital.address, "123 Main St")
        self.assertEqual(new_hospital.contact_number, "123-456-7890")

    def test_department_model(self):
        """Test the Department model."""
        department_id = uuid4()
        hospital_id = uuid4()
        department = Department(
            id=department_id,
            name="Cardiology",
            hospital_id=hospital_id
        )

        # Test to_dict
        department_dict = department.to_dict()
        self.assertEqual(department_dict["id"], str(department_id))
        self.assertEqual(department_dict["name"], "Cardiology")
        self.assertEqual(department_dict["hospital_id"], str(hospital_id))

        # Test from_dict
        new_department = Department.from_dict(department_dict)
        self.assertEqual(str(new_department.id), str(department_id))
        self.assertEqual(new_department.name, "Cardiology")
        self.assertEqual(str(new_department.hospital_id), str(hospital_id))

    def test_patient_model(self):
        """Test the Patient model."""
        patient_id = uuid4()
        user_id = uuid4()
        patient = Patient(
            id=patient_id,
            user_id=user_id,
            full_name="John Doe",
            date_of_birth=date(1990, 1, 1),
            gender=Gender.MALE,
            contact_number="987-654-3210",
            address="456 Elm St",
            emergency_contact_name="Jane Doe",
            emergency_contact_number="555-555-5555"
        )

        # Test to_dict
        patient_dict = patient.to_dict()
        self.assertEqual(patient_dict["id"], str(patient_id))
        self.assertEqual(patient_dict["user_id"], str(user_id))
        self.assertEqual(patient_dict["full_name"], "John Doe")
        self.assertEqual(patient_dict["date_of_birth"], "1990-01-01")
        self.assertEqual(patient_dict["gender"], "male")
        self.assertEqual(patient_dict["contact_number"], "987-654-3210")
        self.assertEqual(patient_dict["address"], "456 Elm St")
        self.assertEqual(patient_dict["emergency_contact_name"], "Jane Doe")
        self.assertEqual(patient_dict["emergency_contact_number"], "555-555-5555")

        # Test from_dict
        new_patient = Patient.from_dict(patient_dict)
        self.assertEqual(str(new_patient.id), str(patient_id))
        self.assertEqual(str(new_patient.user_id), str(user_id))
        self.assertEqual(new_patient.full_name, "John Doe")
        self.assertEqual(new_patient.gender, Gender.MALE)
        self.assertEqual(new_patient.contact_number, "987-654-3210")
        self.assertEqual(new_patient.address, "456 Elm St")
        self.assertEqual(new_patient.emergency_contact_name, "Jane Doe")
        self.assertEqual(new_patient.emergency_contact_number, "555-555-5555")

    def test_doctor_model(self):
        """Test the Doctor model."""
        doctor_id = uuid4()
        user_id = uuid4()
        hospital_id = uuid4()
        department_id = uuid4()
        doctor = Doctor(
            id=doctor_id,
            user_id=user_id,
            full_name="Dr. Smith",
            specialization="Cardiology",
            credentials="MD, PhD",
            hospital_id=hospital_id,
            department_id=department_id,
            contact_number="111-222-3333"
        )

        # Test to_dict
        doctor_dict = doctor.to_dict()
        self.assertEqual(doctor_dict["id"], str(doctor_id))
        self.assertEqual(doctor_dict["user_id"], str(user_id))
        self.assertEqual(doctor_dict["full_name"], "Dr. Smith")
        self.assertEqual(doctor_dict["specialization"], "Cardiology")
        self.assertEqual(doctor_dict["credentials"], "MD, PhD")
        self.assertEqual(doctor_dict["hospital_id"], str(hospital_id))
        self.assertEqual(doctor_dict["department_id"], str(department_id))
        self.assertEqual(doctor_dict["contact_number"], "111-222-3333")

        # Test from_dict
        new_doctor = Doctor.from_dict(doctor_dict)
        self.assertEqual(str(new_doctor.id), str(doctor_id))
        self.assertEqual(str(new_doctor.user_id), str(user_id))
        self.assertEqual(new_doctor.full_name, "Dr. Smith")
        self.assertEqual(new_doctor.specialization, "Cardiology")
        self.assertEqual(new_doctor.credentials, "MD, PhD")
        self.assertEqual(str(new_doctor.hospital_id), str(hospital_id))
        self.assertEqual(str(new_doctor.department_id), str(department_id))
        self.assertEqual(new_doctor.contact_number, "111-222-3333")

    def test_doctor_availability_slot_model(self):
        """Test the DoctorAvailabilitySlot model."""
        slot_id = uuid4()
        doctor_id = uuid4()
        slot = DoctorAvailabilitySlot(
            id=slot_id,
            doctor_id=doctor_id,
            day_of_week=1,  # Monday
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_available=True
        )

        # Test to_dict
        slot_dict = slot.to_dict()
        self.assertEqual(slot_dict["id"], str(slot_id))
        self.assertEqual(slot_dict["doctor_id"], str(doctor_id))
        self.assertEqual(slot_dict["day_of_week"], 1)
        self.assertEqual(slot_dict["start_time"], "09:00:00")
        self.assertEqual(slot_dict["end_time"], "17:00:00")
        self.assertEqual(slot_dict["is_available"], True)

        # Test from_dict
        new_slot = DoctorAvailabilitySlot.from_dict(slot_dict)
        self.assertEqual(str(new_slot.id), str(slot_id))
        self.assertEqual(str(new_slot.doctor_id), str(doctor_id))
        self.assertEqual(new_slot.day_of_week, 1)
        self.assertEqual(new_slot.is_available, True)

    def test_appointment_model(self):
        """Test the Appointment model."""
        appointment_id = uuid4()
        patient_id = uuid4()
        doctor_id = uuid4()
        hospital_id = uuid4()
        department_id = uuid4()

        # Create start and end time for the appointment
        start_time = datetime(2023, 7, 15, 10, 0)
        end_time = datetime(2023, 7, 15, 11, 0)

        appointment = Appointment(
            id=appointment_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            hospital_id=hospital_id,
            department_id=department_id,
            date=date(2023, 7, 15),
            time_slot=(start_time, end_time),
            status=AppointmentStatus.SCHEDULED
        )

        # Test to_dict
        appointment_dict = appointment.to_dict()
        self.assertEqual(appointment_dict["id"], str(appointment_id))
        self.assertEqual(appointment_dict["patient_id"], str(patient_id))
        self.assertEqual(appointment_dict["doctor_id"], str(doctor_id))
        self.assertEqual(appointment_dict["hospital_id"], str(hospital_id))
        self.assertEqual(appointment_dict["department_id"], str(department_id))
        self.assertEqual(appointment_dict["date"], "2023-07-15")
        self.assertEqual(appointment_dict["time_slot"]["start"], start_time.isoformat())
        self.assertEqual(appointment_dict["time_slot"]["end"], end_time.isoformat())
        self.assertEqual(appointment_dict["status"], "scheduled")

        # Test from_dict with time_slot as a string (simulating Postgres format)
        appointment_dict["time_slot"] = f"[{start_time.isoformat()},{end_time.isoformat()})"
        new_appointment = Appointment.from_dict(appointment_dict)
        self.assertEqual(str(new_appointment.id), str(appointment_id))
        self.assertEqual(str(new_appointment.patient_id), str(patient_id))
        self.assertEqual(str(new_appointment.doctor_id), str(doctor_id))
        self.assertEqual(str(new_appointment.hospital_id), str(hospital_id))
        self.assertEqual(str(new_appointment.department_id), str(department_id))
        self.assertEqual(new_appointment.status, AppointmentStatus.SCHEDULED)


@patch('app.utils.db.create_client')
class TestDatabaseUtility(unittest.TestCase):
    """Test cases for Database utility."""

    def setUp(self):
        # Reset the singleton instance before each test
        Database._instance = None

    def test_init_supabase(self, mock_create_client):
        """Test database initialization."""
        # Setup
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        # Test with env vars
        with patch.dict('os.environ', {'SUPABASE_URL': 'https://test.supabase.co', 'SUPABASE_KEY': 'test_key'}):
            db = Database()

            # Verify
            mock_create_client.assert_called_with('https://test.supabase.co', 'test_key')
            self.assertEqual(db.client, mock_client)

    def test_create(self, mock_create_client):
        """Test create operation."""
        # Setup
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        with patch.dict('os.environ', {'SUPABASE_URL': 'https://test.supabase.co', 'SUPABASE_KEY': 'test_key'}):
            db = Database()

            # Setup mock response
            user_id = uuid4()
            user = User(
                id=user_id,
                username="test_user",
                password_hash="hashed_password",
                role=UserRole.PATIENT
            )

            user_dict = user.to_dict()
            table_mock = mock_client.table.return_value
            insert_mock = table_mock.insert.return_value
            execute_mock = insert_mock.execute.return_value
            execute_mock.data = [user_dict]

            # Call method
            result = db.create(user)

            # Verify
            mock_client.table.assert_called_with("users")
            table_mock.insert.assert_called_once()
            self.assertEqual(str(result.id), str(user_id))
            self.assertEqual(result.username, "test_user")

    def test_get_by_id(self, mock_create_client):
        """Test get_by_id operation."""
        # Setup
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        with patch.dict('os.environ', {'SUPABASE_URL': 'https://test.supabase.co', 'SUPABASE_KEY': 'test_key'}):
            db = Database()

            # Setup mock response
            user_id = uuid4()
            user_dict = {
                "id": str(user_id),
                "username": "test_user",
                "password_hash": "hashed_password",
                "role": "patient",
                "status": "active"
            }

            table_mock = mock_client.table.return_value
            select_mock = table_mock.select.return_value
            eq_mock = select_mock.eq.return_value
            execute_mock = eq_mock.execute.return_value
            execute_mock.data = [user_dict]

            # Call method
            result = db.get_by_id(User, user_id)

            # Verify
            mock_client.table.assert_called_with("users")
            table_mock.select.assert_called_with("*")
            select_mock.eq.assert_called_with("id", str(user_id))
            self.assertEqual(str(result.id), str(user_id))
            self.assertEqual(result.username, "test_user")
            self.assertEqual(result.role, UserRole.PATIENT)

    def test_query(self, mock_create_client):
        """Test query operation."""
        # Setup
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        with patch.dict('os.environ', {'SUPABASE_URL': 'https://test.supabase.co', 'SUPABASE_KEY': 'test_key'}):
            db = Database()

            # Setup mock response
            doctor_id = uuid4()
            hospital_id = uuid4()
            department_id = uuid4()

            doctor_dict = {
                "id": str(doctor_id),
                "full_name": "Dr. Smith",
                "specialization": "Cardiology",
                "hospital_id": str(hospital_id),
                "department_id": str(department_id)
            }

            table_mock = mock_client.table.return_value
            select_mock = table_mock.select.return_value
            eq_mock = select_mock.eq.return_value
            execute_mock = eq_mock.execute.return_value
            execute_mock.data = [doctor_dict]

            # Call method
            result = db.query(Doctor, department_id=str(department_id))

            # Verify
            mock_client.table.assert_called_with("doctors")
            table_mock.select.assert_called_with("*")
            select_mock.eq.assert_called_with("department_id", str(department_id))
            self.assertEqual(len(result), 1)
            self.assertEqual(str(result[0].id), str(doctor_id))
            self.assertEqual(result[0].full_name, "Dr. Smith")


if __name__ == '__main__':
    unittest.main()