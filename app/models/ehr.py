"""
EHR (Electronic Health Record) models for the Shastho Flask application.
-----------------------------------------------------------------------
This file defines all models related to EHR, such as allergies, diagnoses, medications, immunizations, and test results.
Each class represents a table or entity in the EHR system.
"""
from datetime import datetime, date, time
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from uuid import UUID, uuid4


class AllergySeverity(str, Enum):
    """Severity levels for allergies."""
    MILD = 'Mild'
    MODERATE = 'Moderate'
    SEVERE = 'Severe'
    LIFE_THREATENING = 'Life-threatening'


class EHR:
    """Model representing a patient's Electronic Health Record."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        patient_id: UUID = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.patient_id = patient_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EHR':
        """Create an EHR instance from a dictionary."""
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')

        # Convert string timestamps to datetime objects
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))

        return cls(
            id=data.get('id'),
            patient_id=data.get('patient_id'),
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'patient_id': str(self.patient_id) if self.patient_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EHR_Visit:
    """Model representing a patient visit in the EHR system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        ehr_id: UUID = None,
        date: date = None,
        time: time = None,
        visit_type: str = None,
        provider_id: UUID = None,
        chief_complaint: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.ehr_id = ehr_id
        self.date = date
        self.time = time
        self.visit_type = visit_type
        self.provider_id = provider_id
        self.chief_complaint = chief_complaint
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EHR_Visit':
        """Create an EHR_Visit instance from a dictionary."""
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        visit_date = data.get('date')
        visit_time = data.get('time')

        # Convert string timestamps to datetime objects
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        if isinstance(visit_date, str):
            visit_date = date.fromisoformat(visit_date)
        if isinstance(visit_time, str):
            # Handle time strings in format "HH:MM:SS"
            if len(visit_time.split(':')) == 3:
                hours, minutes, seconds = visit_time.split(':')
                visit_time = time(int(hours), int(minutes), int(float(seconds)))

        return cls(
            id=data.get('id'),
            ehr_id=data.get('ehr_id'),
            date=visit_date,
            time=visit_time,
            visit_type=data.get('visit_type'),
            provider_id=data.get('provider_id'),
            chief_complaint=data.get('chief_complaint'),
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'ehr_id': str(self.ehr_id) if self.ehr_id else None,
            'date': self.date.isoformat() if self.date else None,
            'time': str(self.time) if self.time else None,
            'visit_type': self.visit_type,
            'provider_id': str(self.provider_id) if self.provider_id else None,
            'chief_complaint': self.chief_complaint,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EHR_Diagnosis:
    """Model representing a medical diagnosis in the EHR system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        visit_id: UUID = None,
        diagnosis_code: str = None,
        diagnosis_description: str = None,
        diagnosed_by: UUID = None,
        diagnosed_at: datetime = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.visit_id = visit_id
        self.diagnosis_code = diagnosis_code
        self.diagnosis_description = diagnosis_description
        self.diagnosed_by = diagnosed_by
        self.diagnosed_at = diagnosed_at or datetime.now()
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EHR_Diagnosis':
        """Create an EHR_Diagnosis instance from a dictionary."""
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        diagnosed_at = data.get('diagnosed_at')

        # Convert string timestamps to datetime objects
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        if isinstance(diagnosed_at, str):
            diagnosed_at = datetime.fromisoformat(diagnosed_at.replace('Z', '+00:00'))

        return cls(
            id=data.get('id'),
            visit_id=data.get('visit_id'),
            diagnosis_code=data.get('diagnosis_code'),
            diagnosis_description=data.get('diagnosis_description'),
            diagnosed_by=data.get('diagnosed_by'),
            diagnosed_at=diagnosed_at,
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'visit_id': str(self.visit_id) if self.visit_id else None,
            'diagnosis_code': self.diagnosis_code,
            'diagnosis_description': self.diagnosis_description,
            'diagnosed_by': str(self.diagnosed_by) if self.diagnosed_by else None,
            'diagnosed_at': self.diagnosed_at.isoformat() if self.diagnosed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EHR_Medication:
    """Model representing a medication in the EHR system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        visit_id: UUID = None,
        medication_name: str = None,
        dosage: str = None,
        frequency: str = None,
        start_date: date = None,
        end_date: Optional[date] = None,
        prescribed_by: UUID = None,
        prescribed_at: datetime = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.visit_id = visit_id
        self.medication_name = medication_name
        self.dosage = dosage
        self.frequency = frequency
        self.start_date = start_date
        self.end_date = end_date
        self.prescribed_by = prescribed_by
        self.prescribed_at = prescribed_at or datetime.now()
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EHR_Medication':
        """Create an EHR_Medication instance from a dictionary."""
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        prescribed_at = data.get('prescribed_at')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Convert string timestamps to datetime objects
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        if isinstance(prescribed_at, str):
            prescribed_at = datetime.fromisoformat(prescribed_at.replace('Z', '+00:00'))
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)

        return cls(
            id=data.get('id'),
            visit_id=data.get('visit_id'),
            medication_name=data.get('medication_name'),
            dosage=data.get('dosage'),
            frequency=data.get('frequency'),
            start_date=start_date,
            end_date=end_date,
            prescribed_by=data.get('prescribed_by'),
            prescribed_at=prescribed_at,
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'visit_id': str(self.visit_id) if self.visit_id else None,
            'medication_name': self.medication_name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'prescribed_by': str(self.prescribed_by) if self.prescribed_by else None,
            'prescribed_at': self.prescribed_at.isoformat() if self.prescribed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EHR_Allergy:
    """Model representing a patient allergy in the EHR system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        ehr_id: UUID = None,
        allergen: str = None,
        reaction: str = None,
        severity: AllergySeverity = None,
        noted_at: datetime = None,
        noted_by: UUID = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.ehr_id = ehr_id
        self.allergen = allergen
        self.reaction = reaction
        self.severity = severity
        self.noted_at = noted_at or datetime.now()
        self.noted_by = noted_by
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EHR_Allergy':
        """Create an EHR_Allergy instance from a dictionary."""
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        noted_at = data.get('noted_at')

        # Convert string timestamps to datetime objects
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        if isinstance(noted_at, str):
            noted_at = datetime.fromisoformat(noted_at.replace('Z', '+00:00'))

        severity = data.get('severity')
        if severity and isinstance(severity, str):
            severity = AllergySeverity(severity)

        return cls(
            id=data.get('id'),
            ehr_id=data.get('ehr_id'),
            allergen=data.get('allergen'),
            reaction=data.get('reaction'),
            severity=severity,
            noted_at=noted_at,
            noted_by=data.get('noted_by'),
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'ehr_id': str(self.ehr_id) if self.ehr_id else None,
            'allergen': self.allergen,
            'reaction': self.reaction,
            'severity': self.severity.value if self.severity else None,
            'noted_at': self.noted_at.isoformat() if self.noted_at else None,
            'noted_by': str(self.noted_by) if self.noted_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EHR_Procedure:
    """Model representing a medical procedure in the EHR system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        visit_id: UUID = None,
        procedure_code: str = None,
        procedure_description: str = None,
        performed_by: UUID = None,
        performed_at: datetime = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.visit_id = visit_id
        self.procedure_code = procedure_code
        self.procedure_description = procedure_description
        self.performed_by = performed_by
        self.performed_at = performed_at or datetime.now()
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EHR_Procedure':
        """Create an EHR_Procedure instance from a dictionary."""
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        performed_at = data.get('performed_at')

        # Convert string timestamps to datetime objects
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        if isinstance(performed_at, str):
            performed_at = datetime.fromisoformat(performed_at.replace('Z', '+00:00'))

        return cls(
            id=data.get('id'),
            visit_id=data.get('visit_id'),
            procedure_code=data.get('procedure_code'),
            procedure_description=data.get('procedure_description'),
            performed_by=data.get('performed_by'),
            performed_at=performed_at,
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'visit_id': str(self.visit_id) if self.visit_id else None,
            'procedure_code': self.procedure_code,
            'procedure_description': self.procedure_description,
            'performed_by': str(self.performed_by) if self.performed_by else None,
            'performed_at': self.performed_at.isoformat() if self.performed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EHR_Vital:
    """Model representing patient vital signs in the EHR system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        visit_id: UUID = None,
        temperature: Optional[float] = None,
        pulse: Optional[int] = None,
        blood_pressure: Optional[str] = None,
        respiratory_rate: Optional[int] = None,
        recorded_at: datetime = None,
        recorded_by: UUID = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.visit_id = visit_id
        self.temperature = temperature
        self.pulse = pulse
        self.blood_pressure = blood_pressure
        self.respiratory_rate = respiratory_rate
        self.recorded_at = recorded_at or datetime.now()
        self.recorded_by = recorded_by
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EHR_Vital':
        """Create an EHR_Vital instance from a dictionary."""
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        recorded_at = data.get('recorded_at')

        # Convert string timestamps to datetime objects
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        if isinstance(recorded_at, str):
            recorded_at = datetime.fromisoformat(recorded_at.replace('Z', '+00:00'))

        return cls(
            id=data.get('id'),
            visit_id=data.get('visit_id'),
            temperature=data.get('temperature'),
            pulse=data.get('pulse'),
            blood_pressure=data.get('blood_pressure'),
            respiratory_rate=data.get('respiratory_rate'),
            recorded_at=recorded_at,
            recorded_by=data.get('recorded_by'),
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'visit_id': str(self.visit_id) if self.visit_id else None,
            'temperature': self.temperature,
            'pulse': self.pulse,
            'blood_pressure': self.blood_pressure,
            'respiratory_rate': self.respiratory_rate,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'recorded_by': str(self.recorded_by) if self.recorded_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EHR_Immunization:
    """Model representing a patient immunization in the EHR system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        ehr_id: UUID = None,
        vaccine: str = None,
        date_administered: date = None,
        administered_by: UUID = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.ehr_id = ehr_id
        self.vaccine = vaccine
        self.date_administered = date_administered
        self.administered_by = administered_by
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EHR_Immunization':
        """Create an EHR_Immunization instance from a dictionary."""
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        date_administered = data.get('date_administered')

        # Convert string timestamps to datetime objects
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        if isinstance(date_administered, str):
            date_administered = date.fromisoformat(date_administered)

        return cls(
            id=data.get('id'),
            ehr_id=data.get('ehr_id'),
            vaccine=data.get('vaccine'),
            date_administered=date_administered,
            administered_by=data.get('administered_by'),
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'ehr_id': str(self.ehr_id) if self.ehr_id else None,
            'vaccine': self.vaccine,
            'date_administered': self.date_administered.isoformat() if self.date_administered else None,
            'administered_by': str(self.administered_by) if self.administered_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EHR_TestResult:
    """Model representing a medical test result in the EHR system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        ehr_id: UUID = None,
        test_type: str = None,
        test_date: date = None,
        result_data: Dict[str, Any] = None,
        file_path: Optional[str] = None,
        uploaded_by: UUID = None,
        uploaded_at: datetime = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.ehr_id = ehr_id
        self.test_type = test_type
        self.test_date = test_date
        self.result_data = result_data or {}
        self.file_path = file_path
        self.uploaded_by = uploaded_by
        self.uploaded_at = uploaded_at or datetime.now()
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EHR_TestResult':
        """Create an EHR_TestResult instance from a dictionary."""
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        uploaded_at = data.get('uploaded_at')
        test_date = data.get('test_date')

        # Convert string timestamps to datetime objects
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        if isinstance(uploaded_at, str):
            uploaded_at = datetime.fromisoformat(uploaded_at.replace('Z', '+00:00'))
        if isinstance(test_date, str):
            test_date = date.fromisoformat(test_date)

        return cls(
            id=data.get('id'),
            ehr_id=data.get('ehr_id'),
            test_type=data.get('test_type'),
            test_date=test_date,
            result_data=data.get('result_data', {}),
            file_path=data.get('file_path'),
            uploaded_by=data.get('uploaded_by'),
            uploaded_at=uploaded_at,
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'ehr_id': str(self.ehr_id) if self.ehr_id else None,
            'test_type': self.test_type,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'result_data': self.result_data,
            'file_path': self.file_path,
            'uploaded_by': str(self.uploaded_by) if self.uploaded_by else None,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EHR_ProviderNote:
    """Model representing a provider's clinical note in the EHR system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        visit_id: UUID = None,
        note_text: str = None,
        created_by: UUID = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.visit_id = visit_id
        self.note_text = note_text
        self.created_by = created_by
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EHR_ProviderNote':
        """Create an EHR_ProviderNote instance from a dictionary."""
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')

        # Convert string timestamps to datetime objects
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))

        return cls(
            id=data.get('id'),
            visit_id=data.get('visit_id'),
            note_text=data.get('note_text'),
            created_by=data.get('created_by'),
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'visit_id': str(self.visit_id) if self.visit_id else None,
            'note_text': self.note_text,
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Prescription:
    """Model representing a medication prescription in the EHR system."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        visit_id: UUID = None,
        medication_name: str = None,
        dosage: str = None,
        frequency: str = None,
        instructions: str = None,
        prescribed_by: UUID = None,
        prescribed_at: datetime = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or uuid4()
        self.visit_id = visit_id
        self.medication_name = medication_name
        self.dosage = dosage
        self.frequency = frequency
        self.instructions = instructions
        self.prescribed_by = prescribed_by
        self.prescribed_at = prescribed_at or datetime.now()
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Prescription':
        """Create a Prescription instance from a dictionary."""
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        prescribed_at = data.get('prescribed_at')

        # Convert string timestamps to datetime objects
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        if isinstance(prescribed_at, str):
            prescribed_at = datetime.fromisoformat(prescribed_at.replace('Z', '+00:00'))

        return cls(
            id=data.get('id'),
            visit_id=data.get('visit_id'),
            medication_name=data.get('medication_name'),
            dosage=data.get('dosage'),
            frequency=data.get('frequency'),
            instructions=data.get('instructions'),
            prescribed_by=data.get('prescribed_by'),
            prescribed_at=prescribed_at,
            created_at=created_at,
            updated_at=updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary."""
        return {
            'id': str(self.id),
            'visit_id': str(self.visit_id) if self.visit_id else None,
            'medication_name': self.medication_name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'instructions': self.instructions,
            'prescribed_by': str(self.prescribed_by) if self.prescribed_by else None,
            'prescribed_at': self.prescribed_at.isoformat() if self.prescribed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }