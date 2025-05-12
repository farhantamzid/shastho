"""
Patient-specific models for the Shastho Flask application.
---------------------------------------------------------
This file defines models related to patient-specific data and logic.
"""
from app.models.database import Patient
from uuid import UUID
from app.utils.db import db

def find_patient_by_id(patient_id: UUID) -> Patient:
    """Find a patient by their ID."""
    return db.get_by_id(Patient, patient_id)

def find_patient_by_user_id(user_id: UUID) -> Patient:
    """Find a patient by the associated user ID."""
    patients = db.query(Patient, user_id=str(user_id))
    return patients[0] if patients else None

def save_patient(patient: Patient) -> Patient:
    """Save a patient to the database."""
    # Ensure patient has an ID
    if not patient.id:
        from uuid import uuid4
        patient.id = uuid4()

    # Save to database
    return db.create(patient)

def update_patient(patient: Patient) -> Patient:
    """Update an existing patient record."""
    # Update the patient in the database
    return db.update(patient)

def delete_patient(patient_id: UUID) -> bool:
    """Delete a patient from the database."""
    return db.delete(Patient, patient_id)

def get_all_patients() -> list:
    """Get all patients."""
    return db.get_all(Patient)