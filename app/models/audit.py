"""
Audit logging models for the Shastho Flask application.
------------------------------------------------------
This file defines models for audit logging, tracking changes and actions in the system for security and compliance.
"""
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any, List
from enum import Enum
from app.models.database import User, Patient, Doctor, HospitalAdmin

class AuditActionType(str, Enum):
    """Types of actions that can be audited"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    FAILED_LOGIN = "failed_login"
    ACCESS = "access"

class AuditResourceType(str, Enum):
    """Types of resources that can be audited"""
    PATIENT = "patient"
    DOCTOR = "doctor"
    HOSPITAL_ADMIN = "hospital_admin"
    USER = "user"
    EHR = "ehr"
    VISIT = "visit"
    DIAGNOSIS = "diagnosis"
    MEDICATION = "medication"
    PRESCRIPTION = "prescription"
    PROVIDER_NOTE = "provider_note"
    PROCEDURE = "procedure"
    ALLERGY = "allergy"
    IMMUNIZATION = "immunization"
    TEST_RESULT = "test_result"
    VITALS = "vitals"

class AuditLog:
    """Model for audit logs"""

    def __init__(
        self,
        id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        action: AuditActionType = None,
        resource_type: AuditResourceType = None,
        resource_id: Optional[UUID] = None,
        timestamp: datetime = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        changes: Optional[Dict[str, Any]] = None,
        success: bool = True
    ):
        self.id = id or uuid4()
        self.user_id = user_id
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.timestamp = timestamp or datetime.now()
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.details = details or {}
        self.changes = changes or {}
        self.success = success

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditLog':
        """Create an AuditLog instance from a dictionary"""
        action = AuditActionType(data.get('action')) if data.get('action') else None
        resource_type = AuditResourceType(data.get('resource_type')) if data.get('resource_type') else None

        return cls(
            id=UUID(data.get('id')) if data.get('id') else None,
            user_id=UUID(data.get('user_id')) if data.get('user_id') else None,
            action=action,
            resource_type=resource_type,
            resource_id=UUID(data.get('resource_id')) if data.get('resource_id') else None,
            timestamp=datetime.fromisoformat(data.get('timestamp')) if data.get('timestamp') else None,
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent'),
            details=data.get('details', {}),
            changes=data.get('changes', {}),
            success=data.get('success', True)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to a dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'action': self.action.value if self.action else None,
            'resource_type': self.resource_type.value if self.resource_type else None,
            'resource_id': str(self.resource_id) if self.resource_id else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'details': self.details,
            'changes': self.changes,
            'success': self.success
        }