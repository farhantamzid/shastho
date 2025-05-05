from datetime import datetime
from typing import Dict, Any, Optional, Union
from uuid import UUID
from flask import request, session, current_app, g
import json

from app.models.audit import AuditLog, AuditActionType, AuditResourceType
from app.utils.db import Database

db = Database()

def get_request_info() -> Dict[str, Any]:
    """Extract information from the current request"""
    info = {
        'ip_address': request.remote_addr if request else None,
        'user_agent': request.user_agent.string if request and request.user_agent else None,
    }
    return info

def log_action(
    action: AuditActionType,
    resource_type: AuditResourceType,
    resource_id: Optional[Union[UUID, str]] = None,
    user_id: Optional[Union[UUID, str]] = None,
    details: Optional[Dict[str, Any]] = None,
    changes: Optional[Dict[str, Any]] = None,
    success: bool = True
) -> AuditLog:
    """
    Log an action in the audit log.

    Args:
        action: The type of action being performed
        resource_type: The type of resource being acted upon
        resource_id: The ID of the resource (optional)
        user_id: The ID of the user performing the action (optional, defaults to current user)
        details: Additional details about the action (optional)
        changes: Record of what changed in the resource (optional)
        success: Whether the action was successful (default: True)

    Returns:
        The created AuditLog instance
    """
    # Get current user from session if not provided
    if user_id is None and session and 'user_id' in session:
        user_id = session.get('user_id')

    # Convert string IDs to UUID if necessary
    if isinstance(user_id, str):
        user_id = UUID(user_id)
    if isinstance(resource_id, str):
        try:
            resource_id = UUID(resource_id)
        except ValueError:
            # If not a valid UUID, keep as string (some resources might have non-UUID IDs)
            pass

    # Get request information
    request_info = get_request_info()

    # Create the audit log entry
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id if isinstance(resource_id, UUID) else None,
        ip_address=request_info['ip_address'],
        user_agent=request_info['user_agent'],
        details=details or {},
        changes=changes or {},
        success=success
    )

    # Store in database
    try:
        db.insert(audit_log)
        return audit_log
    except Exception as e:
        # Don't let audit logging failure affect the main application
        current_app.logger.error(f"Failed to log audit event: {str(e)}")
        return audit_log

def log_create(
    resource_type: AuditResourceType,
    resource_id: Union[UUID, str],
    details: Optional[Dict[str, Any]] = None,
    user_id: Optional[Union[UUID, str]] = None
) -> AuditLog:
    """Log a resource creation event"""
    return log_action(
        action=AuditActionType.CREATE,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        details=details
    )

def log_read(
    resource_type: AuditResourceType,
    resource_id: Union[UUID, str],
    details: Optional[Dict[str, Any]] = None,
    user_id: Optional[Union[UUID, str]] = None
) -> AuditLog:
    """Log a resource read/access event"""
    return log_action(
        action=AuditActionType.READ,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        details=details
    )

def log_update(
    resource_type: AuditResourceType,
    resource_id: Union[UUID, str],
    old_data: Dict[str, Any],
    new_data: Dict[str, Any],
    user_id: Optional[Union[UUID, str]] = None
) -> AuditLog:
    """Log a resource update event with change tracking"""
    # Calculate the changes
    changes = {
        'before': old_data,
        'after': new_data,
        'changed_fields': [k for k in new_data if k in old_data and new_data[k] != old_data[k]]
    }

    return log_action(
        action=AuditActionType.UPDATE,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        changes=changes
    )

def log_delete(
    resource_type: AuditResourceType,
    resource_id: Union[UUID, str],
    details: Optional[Dict[str, Any]] = None,
    user_id: Optional[Union[UUID, str]] = None
) -> AuditLog:
    """Log a resource deletion event"""
    return log_action(
        action=AuditActionType.DELETE,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        details=details
    )

def log_login(
    user_id: Union[UUID, str],
    success: bool = True,
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """Log a user login event"""
    action = AuditActionType.LOGIN if success else AuditActionType.FAILED_LOGIN
    return log_action(
        action=action,
        resource_type=AuditResourceType.USER,
        resource_id=user_id,
        user_id=user_id if success else None,  # Only include user_id if login successful
        details=details,
        success=success
    )

def log_logout(
    user_id: Union[UUID, str],
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """Log a user logout event"""
    return log_action(
        action=AuditActionType.LOGOUT,
        resource_type=AuditResourceType.USER,
        resource_id=user_id,
        user_id=user_id,
        details=details
    )

def audit_decorator(resource_type: AuditResourceType, action: AuditActionType):
    """
    Decorator for auditing function calls

    Usage:
        @audit_decorator(AuditResourceType.PATIENT, AuditActionType.READ)
        def view_patient(patient_id):
            # Function implementation
    """
    def decorator(func):
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract resource_id from args or kwargs
            resource_id = None
            for param in ['id', 'patient_id', 'visit_id', 'user_id', 'resource_id']:
                if param in kwargs:
                    resource_id = kwargs[param]
                    break

            # For update and delete operations, get the old state before the function executes
            old_data = None
            if action == AuditActionType.UPDATE or action == AuditActionType.DELETE:
                try:
                    # Attempt to get the resource from the database
                    # This is a simplified example, actual implementation would depend on your ORM
                    if resource_type == AuditResourceType.PATIENT and resource_id:
                        from app.models.database import Patient
                        old_resource = db.get_by_id(Patient, resource_id)
                        if old_resource:
                            old_data = old_resource.to_dict() if hasattr(old_resource, 'to_dict') else vars(old_resource)
                except Exception as e:
                    current_app.logger.error(f"Error fetching resource for audit: {str(e)}")

            # Execute the original function
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                success = False
                raise e
            finally:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                # Log the action
                details = {
                    'function': func.__name__,
                    'duration_seconds': duration,
                    'args': str(args) if args else None,
                    'kwargs': {k: v for k, v in kwargs.items() if k not in ['password', 'token']}  # Filter sensitive data
                }

                # For update operations, try to get the new state
                new_data = None
                if action == AuditActionType.UPDATE and resource_id and old_data:
                    try:
                        if resource_type == AuditResourceType.PATIENT:
                            from app.models.database import Patient
                            new_resource = db.get_by_id(Patient, resource_id)
                            if new_resource:
                                new_data = new_resource.to_dict() if hasattr(new_resource, 'to_dict') else vars(new_resource)

                        if old_data and new_data:
                            log_update(resource_type, resource_id, old_data, new_data)
                        else:
                            log_action(action, resource_type, resource_id, details=details, success=success)
                    except Exception as e:
                        current_app.logger.error(f"Error logging audit update: {str(e)}")
                        log_action(action, resource_type, resource_id, details=details, success=success)
                else:
                    log_action(action, resource_type, resource_id, details=details, success=success)

            return result
        return wrapper
    return decorator