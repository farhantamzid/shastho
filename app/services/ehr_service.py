from uuid import UUID
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import os
import requests
from urllib.parse import quote

from app.utils.db import db
from app.models.ehr import (
    EHR, EHR_Visit, EHR_Diagnosis, EHR_Medication,
    EHR_Allergy, EHR_Procedure, EHR_Vital,
    EHR_Immunization, EHR_TestResult, EHR_ProviderNote
)
from app.models.database import Patient

def get_patient_ehr(patient_id: UUID) -> Tuple[Optional[EHR], bool]:
    """
    Get a patient's EHR record

    Args:
        patient_id: UUID of the patient

    Returns:
        Tuple of (EHR object or None, boolean indicating if EHR exists)
    """
    try:
        # Query for EHR records for this patient
        ehr_records = db.query(EHR, patient_id=str(patient_id))

        # If patient has an EHR, return it
        if ehr_records and len(ehr_records) > 0:
            return ehr_records[0], True

        # If patient exists but no EHR, return (None, False)
        patient = db.get_by_id(Patient, patient_id)
        if patient:
            return None, False

        # If patient doesn't exist, return (None, False)
        return None, False
    except Exception as e:
        print(f"Error retrieving patient EHR: {str(e)}")
        return None, False

def create_patient_ehr(patient_id: UUID) -> Optional[EHR]:
    """
    Create a new EHR record for a patient

    Args:
        patient_id: UUID of the patient

    Returns:
        Newly created EHR object or None if failed
    """
    try:
        # Make sure patient exists
        patient = db.get_by_id(Patient, patient_id)
        if not patient:
            return None

        # Create new EHR record
        ehr = EHR(
            patient_id=patient_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Save to database
        db.insert(ehr)
        return ehr
    except Exception as e:
        print(f"Error creating patient EHR: {str(e)}")
        return None

def get_ehr_visits(ehr_id: UUID, limit: int = None, offset: int = None,
                  sort_by: str = 'date', sort_dir: str = 'desc') -> List[EHR_Visit]:
    """
    Get visits for an EHR, with optional pagination and sorting

    Args:
        ehr_id: UUID of the EHR record
        limit: Maximum number of records to return
        offset: Offset for pagination
        sort_by: Field to sort by (date, visit_type, etc)
        sort_dir: Sort direction ('asc' or 'desc')

    Returns:
        List of EHR_Visit objects
    """
    try:
        # Query for visits
        visits = db.query(EHR_Visit, ehr_id=str(ehr_id))

        if not visits:
            return []

        # Sort visits by date (newest first is default)
        if sort_by == 'date':
            reverse = sort_dir.lower() == 'desc'
            visits.sort(key=lambda v: (v.date or date.min, v.time or datetime.min.time()), reverse=reverse)

        # Apply pagination if specified
        if limit is not None:
            start_idx = offset if offset is not None else 0
            end_idx = start_idx + limit
            visits = visits[start_idx:end_idx]

        return visits
    except Exception as e:
        print(f"Error retrieving EHR visits: {str(e)}")
        return []

def get_visit_details(visit_id: UUID) -> Dict[str, Any]:
    """
    Get comprehensive details for a specific visit

    Args:
        visit_id: UUID of the visit

    Returns:
        Dictionary with visit details and related records
    """
    try:
        # Get the visit
        visit = db.get_by_id(EHR_Visit, visit_id)
        if not visit:
            return {}

        # Get diagnoses for this visit
        diagnoses = db.query(EHR_Diagnosis, visit_id=str(visit_id))

        # Get medications for this visit
        medications = db.query(EHR_Medication, visit_id=str(visit_id))

        # Get procedures for this visit
        procedures = db.query(EHR_Procedure, visit_id=str(visit_id))

        # Get vitals for this visit
        vitals = db.query(EHR_Vital, visit_id=str(visit_id))

        # Get provider notes for this visit
        notes = db.query(EHR_ProviderNote, visit_id=str(visit_id))

        # Compile all data
        visit_data = {
            'visit': visit,
            'diagnoses': diagnoses or [],
            'medications': medications or [],
            'procedures': procedures or [],
            'vitals': vitals or [],
            'notes': notes or []
        }

        return visit_data
    except Exception as e:
        print(f"Error retrieving visit details: {str(e)}")
        return {}

def get_ehr_allergies(ehr_id: UUID) -> List[EHR_Allergy]:
    """
    Get allergies for an EHR

    Args:
        ehr_id: UUID of the EHR record

    Returns:
        List of EHR_Allergy objects
    """
    try:
        allergies = db.query(EHR_Allergy, ehr_id=str(ehr_id))
        return allergies or []
    except Exception as e:
        print(f"Error retrieving EHR allergies: {str(e)}")
        return []

def get_ehr_immunizations(ehr_id: UUID) -> List[EHR_Immunization]:
    """
    Get immunizations for an EHR

    Args:
        ehr_id: UUID of the EHR record

    Returns:
        List of EHR_Immunization objects
    """
    try:
        immunizations = db.query(EHR_Immunization, ehr_id=str(ehr_id))
        return immunizations or []
    except Exception as e:
        print(f"Error retrieving EHR immunizations: {str(e)}")
        return []

def get_ehr_test_results(ehr_id: UUID) -> List[EHR_TestResult]:
    """
    Get test results for an EHR

    Args:
        ehr_id: UUID of the EHR record

    Returns:
        List of EHR_TestResult objects
    """
    try:
        test_results = db.query(EHR_TestResult, ehr_id=str(ehr_id))
        return test_results or []
    except Exception as e:
        print(f"Error retrieving EHR test results: {str(e)}")
        return []

def search_patients(search_term: str,
                   limit: int = 20, offset: int = 0,
                   search_by_name: bool = True,
                   search_by_email: bool = False,
                   search_by_id: bool = False) -> list:
    """
    Search for patients by ID, name, or email using Supabase as the primary source.
    Falls back to local DB if Supabase is unavailable.
    """
    SUPABASE_PROJECT_ID = os.environ.get('SUPABASE_PROJECT_ID', 'qdcrvgofelmqobkfonfi')
    SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ.get('SUPABASE_ANON_KEY')

    if not SUPABASE_KEY:
        print("Supabase key not found, falling back to local DB.")
        # Note: Local fallback might need updating to handle new filters
        return _search_patients_local(search_term, limit, offset)

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    from uuid import UUID
    import re
    from urllib.parse import quote
    filters = []
    or_conditions = []

    # Check if search term is empty - if so, return all patients (or based on default filters)
    if not search_term:
        base_url = f"https://{SUPABASE_PROJECT_ID}.supabase.co/rest/v1/patients?select=id,full_name,date_of_birth,gender,contact_number,email&limit={limit}&offset={offset}"
        try:
            response = requests.get(base_url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error querying Supabase: {e}")
            print("Falling back to local DB for empty search.")
            return _search_patients_local('', limit, offset)

    # Build filters based on selected checkboxes
    if search_by_id:
        try:
            patient_id = str(UUID(search_term))
            or_conditions.append(f"id.eq.{patient_id}")
        except ValueError:
            # If ID is checked but term is not UUID, don't add ID filter unless term is clearly not for name/email
            pass # Or maybe add a flash message? For now, skip.

    if search_by_name:
        # Use ilike for case-insensitive partial matching
        or_conditions.append(f"full_name.ilike.*{quote(search_term)}*")

    if search_by_email:
        # Assume email column exists
        or_conditions.append(f"email.ilike.*{quote(search_term)}*")

    # If no valid filters selected or generated, maybe return empty or all?
    # For now, if or_conditions is empty, it implies no boxes were checked or ID was checked with invalid input.
    # Let's default to searching name if nothing else is valid/selected.
    if not or_conditions and not search_by_name and not search_by_email and not search_by_id:
         or_conditions.append(f"full_name.ilike.*{quote(search_term)}*") # Default fallback
    elif not or_conditions:
        # If filters were checked but resulted in no valid condition (e.g., ID checked with non-UUID)
        # Return empty list as the specific search yielded no valid query part
        return []

    # Construct the Supabase query URL
    # Select email as well
    base_url = f"https://{SUPABASE_PROJECT_ID}.supabase.co/rest/v1/patients?select=id,full_name,date_of_birth,gender,contact_number,email&limit={limit}&offset={offset}"

    # Combine OR conditions
    filter_string = f"or=({','.join(or_conditions)})"
    url = f"{base_url}&{filter_string}"

    print(f"Supabase Query URL: {url}") # For debugging

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying Supabase: {e}")
        print("Falling back to local DB.")
        # Note: Local fallback might need updating to handle new filters
        return _search_patients_local(search_term, limit, offset)

def _search_patients_local(search_term: str,
                          limit: int = 20, offset: int = 0) -> list:
    """
    Fallback: Search for patients in the local database (if configured).
    NOTE: This local search needs to be updated to reflect the new filters (name, email, id).
          Currently, it only mimics the old behavior.
    """
    print("Executing local patient search (fallback).")
    try:
        all_patients = db.query(Patient) # Fetch all patients locally
        if not all_patients:
            return []

        results = []
        search_lower = search_term.lower()

        for patient in all_patients:
            match = False
            # Simple local search logic (needs improvement for filters)
            if search_lower in str(patient.id).lower():
                match = True
            elif search_lower in patient.full_name.lower():
                match = True
            # Add email search if patient model has email
            # elif hasattr(patient, 'email') and patient.email and search_lower in patient.email.lower():
            #     match = True
            elif search_lower == str(patient.date_of_birth):
                 match = True

            if match:
                results.append(patient)

        # Apply pagination
        total_items = len(results)
        return results[offset:offset + limit]

    except Exception as e:
        print(f"Error during local patient search: {e}")
        return []