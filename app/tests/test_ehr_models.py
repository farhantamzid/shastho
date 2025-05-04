import unittest
from datetime import datetime, date, time
from uuid import uuid4

from app.models.ehr import (
    EHR, EHR_Visit, EHR_Diagnosis, EHR_Medication,
    EHR_Allergy, EHR_Procedure, EHR_Vital, EHR_Immunization,
    EHR_TestResult, EHR_ProviderNote, Prescription, AllergySeverity
)
from app.utils.db import db
from app.models.database import Patient, Doctor


class TestEHRModels(unittest.TestCase):
    """Test case for EHR models and operations."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        # Get an existing patient
        patients = db.get_all(Patient, limit=1)
        cls.patient = patients[0] if patients else None

        # Get an existing doctor
        doctors = db.get_all(Doctor, limit=1)
        cls.doctor = doctors[0] if doctors else None

        # Skip tests if no patient or doctor exists
        if not cls.patient or not cls.doctor:
            raise unittest.SkipTest("No patient or doctor data available for tests")

        # Create test EHR
        cls.ehr = EHR(patient_id=cls.patient.id)
        cls.ehr = db.create(cls.ehr)

        # Create test visit
        cls.visit = EHR_Visit(
            ehr_id=cls.ehr.id,
            date=date.today(),
            time=datetime.now().time(),
            visit_type="Regular Checkup",
            provider_id=cls.doctor.id,
            chief_complaint="Routine physical examination"
        )
        cls.visit = db.create(cls.visit)

    @classmethod
    def tearDownClass(cls):
        """Clean up test data."""
        # Delete test data in reverse order of creation to handle foreign key constraints
        if hasattr(cls, 'visit'):
            db.delete(EHR_Visit, cls.visit.id)

        if hasattr(cls, 'ehr'):
            db.delete(EHR, cls.ehr.id)

    def test_ehr_creation(self):
        """Test EHR creation and retrieval."""
        # Verify EHR was created
        retrieved_ehr = db.get_by_id(EHR, self.ehr.id)
        self.assertIsNotNone(retrieved_ehr)
        self.assertEqual(str(retrieved_ehr.patient_id), str(self.patient.id))

        # Test get_ehr_by_patient_id method
        patient_ehr = db.get_ehr_by_patient_id(self.patient.id)
        self.assertIsNotNone(patient_ehr)
        self.assertEqual(str(patient_ehr.id), str(self.ehr.id))

    def test_visit_creation(self):
        """Test EHR Visit creation and retrieval."""
        # Verify visit was created
        retrieved_visit = db.get_by_id(EHR_Visit, self.visit.id)
        self.assertIsNotNone(retrieved_visit)
        self.assertEqual(str(retrieved_visit.ehr_id), str(self.ehr.id))

        # Test get_visits_by_ehr_id method
        visits = db.get_visits_by_ehr_id(self.ehr.id)
        self.assertGreaterEqual(len(visits), 1)
        self.assertEqual(str(visits[0].id), str(self.visit.id))

    def test_diagnosis(self):
        """Test diagnosis creation and retrieval."""
        # Create a diagnosis
        diagnosis = EHR_Diagnosis(
            visit_id=self.visit.id,
            diagnosis_code="E11.9",
            diagnosis_description="Type 2 diabetes mellitus without complications",
            diagnosed_by=self.doctor.id
        )
        diagnosis = db.create(diagnosis)

        try:
            # Verify diagnosis was created
            retrieved_diagnosis = db.get_by_id(EHR_Diagnosis, diagnosis.id)
            self.assertIsNotNone(retrieved_diagnosis)
            self.assertEqual(retrieved_diagnosis.diagnosis_code, "E11.9")

            # Test get_diagnoses_by_visit_id method
            diagnoses = db.get_diagnoses_by_visit_id(self.visit.id)
            self.assertGreaterEqual(len(diagnoses), 1)
            self.assertEqual(diagnoses[0].diagnosis_code, "E11.9")
        finally:
            # Clean up
            db.delete(EHR_Diagnosis, diagnosis.id)

    def test_medication(self):
        """Test medication creation and retrieval."""
        # Create a medication
        medication = EHR_Medication(
            visit_id=self.visit.id,
            medication_name="Metformin",
            dosage="500mg",
            frequency="Twice daily",
            start_date=date.today(),
            prescribed_by=self.doctor.id
        )
        medication = db.create(medication)

        try:
            # Verify medication was created
            retrieved_medication = db.get_by_id(EHR_Medication, medication.id)
            self.assertIsNotNone(retrieved_medication)
            self.assertEqual(retrieved_medication.medication_name, "Metformin")

            # Test get_medications_by_visit_id method
            medications = db.get_medications_by_visit_id(self.visit.id)
            self.assertGreaterEqual(len(medications), 1)
            self.assertEqual(medications[0].medication_name, "Metformin")
        finally:
            # Clean up
            db.delete(EHR_Medication, medication.id)

    def test_allergy(self):
        """Test allergy creation and retrieval."""
        # Create an allergy
        allergy = EHR_Allergy(
            ehr_id=self.ehr.id,
            allergen="Penicillin",
            reaction="Rash, hives",
            severity=AllergySeverity.MODERATE,
            noted_by=self.doctor.id
        )
        allergy = db.create(allergy)

        try:
            # Verify allergy was created
            retrieved_allergy = db.get_by_id(EHR_Allergy, allergy.id)
            self.assertIsNotNone(retrieved_allergy)
            self.assertEqual(retrieved_allergy.allergen, "Penicillin")
            self.assertEqual(retrieved_allergy.severity, AllergySeverity.MODERATE)

            # Test get_allergies_by_ehr_id method
            allergies = db.get_allergies_by_ehr_id(self.ehr.id)
            self.assertGreaterEqual(len(allergies), 1)
            self.assertEqual(allergies[0].allergen, "Penicillin")
        finally:
            # Clean up
            db.delete(EHR_Allergy, allergy.id)

    def test_procedure(self):
        """Test procedure creation and retrieval."""
        # Create a procedure
        procedure = EHR_Procedure(
            visit_id=self.visit.id,
            procedure_code="99213",
            procedure_description="Office visit, established patient, level 3",
            performed_by=self.doctor.id
        )
        procedure = db.create(procedure)

        try:
            # Verify procedure was created
            retrieved_procedure = db.get_by_id(EHR_Procedure, procedure.id)
            self.assertIsNotNone(retrieved_procedure)
            self.assertEqual(retrieved_procedure.procedure_code, "99213")

            # Test get_procedures_by_visit_id method
            procedures = db.get_procedures_by_visit_id(self.visit.id)
            self.assertGreaterEqual(len(procedures), 1)
            self.assertEqual(procedures[0].procedure_code, "99213")
        finally:
            # Clean up
            db.delete(EHR_Procedure, procedure.id)

    def test_vital(self):
        """Test vital signs creation and retrieval."""
        # Create vital signs
        vitals = EHR_Vital(
            visit_id=self.visit.id,
            temperature=98.6,
            pulse=72,
            blood_pressure="120/80",
            respiratory_rate=16,
            recorded_by=self.doctor.id
        )
        vitals = db.create(vitals)

        try:
            # Verify vitals were created
            retrieved_vitals = db.get_by_id(EHR_Vital, vitals.id)
            self.assertIsNotNone(retrieved_vitals)
            self.assertEqual(retrieved_vitals.temperature, 98.6)
            self.assertEqual(retrieved_vitals.pulse, 72)

            # Test get_vitals_by_visit_id method
            all_vitals = db.get_vitals_by_visit_id(self.visit.id)
            self.assertGreaterEqual(len(all_vitals), 1)
            self.assertEqual(all_vitals[0].temperature, 98.6)
        finally:
            # Clean up
            db.delete(EHR_Vital, vitals.id)

    def test_immunization(self):
        """Test immunization creation and retrieval."""
        # Create an immunization
        immunization = EHR_Immunization(
            ehr_id=self.ehr.id,
            vaccine="Influenza",
            date_administered=date.today(),
            administered_by=self.doctor.id
        )
        immunization = db.create(immunization)

        try:
            # Verify immunization was created
            retrieved_immunization = db.get_by_id(EHR_Immunization, immunization.id)
            self.assertIsNotNone(retrieved_immunization)
            self.assertEqual(retrieved_immunization.vaccine, "Influenza")

            # Test get_immunizations_by_ehr_id method
            immunizations = db.get_immunizations_by_ehr_id(self.ehr.id)
            self.assertGreaterEqual(len(immunizations), 1)
            self.assertEqual(immunizations[0].vaccine, "Influenza")
        finally:
            # Clean up
            db.delete(EHR_Immunization, immunization.id)

    def test_test_result(self):
        """Test test result creation and retrieval."""
        # Create a test result
        test_result = EHR_TestResult(
            ehr_id=self.ehr.id,
            test_type="Blood Glucose",
            test_date=date.today(),
            result_data={"value": 110, "unit": "mg/dL", "normal_range": "70-99"},
            uploaded_by=self.doctor.id
        )
        test_result = db.create(test_result)

        try:
            # Verify test result was created
            retrieved_test_result = db.get_by_id(EHR_TestResult, test_result.id)
            self.assertIsNotNone(retrieved_test_result)
            self.assertEqual(retrieved_test_result.test_type, "Blood Glucose")
            self.assertEqual(retrieved_test_result.result_data["value"], 110)

            # Test get_test_results_by_ehr_id method
            test_results = db.get_test_results_by_ehr_id(self.ehr.id)
            self.assertGreaterEqual(len(test_results), 1)
            self.assertEqual(test_results[0].test_type, "Blood Glucose")
        finally:
            # Clean up
            db.delete(EHR_TestResult, test_result.id)

    def test_provider_note(self):
        """Test provider note creation and retrieval."""
        # Create a provider note
        note = EHR_ProviderNote(
            visit_id=self.visit.id,
            note_text="Patient appears healthy. Advised on diet and exercise.",
            created_by=self.doctor.id
        )
        note = db.create(note)

        try:
            # Verify provider note was created
            retrieved_note = db.get_by_id(EHR_ProviderNote, note.id)
            self.assertIsNotNone(retrieved_note)
            self.assertIn("diet and exercise", retrieved_note.note_text)

            # Test get_provider_notes_by_visit_id method
            notes = db.get_provider_notes_by_visit_id(self.visit.id)
            self.assertGreaterEqual(len(notes), 1)
            self.assertIn("diet and exercise", notes[0].note_text)
        finally:
            # Clean up
            db.delete(EHR_ProviderNote, note.id)

    def test_prescription(self):
        """Test prescription creation and retrieval."""
        # Create a prescription
        prescription = Prescription(
            visit_id=self.visit.id,
            medication_name="Lisinopril",
            dosage="10mg",
            frequency="Once daily",
            instructions="Take in the morning with water",
            prescribed_by=self.doctor.id
        )
        prescription = db.create(prescription)

        try:
            # Verify prescription was created
            retrieved_prescription = db.get_by_id(Prescription, prescription.id)
            self.assertIsNotNone(retrieved_prescription)
            self.assertEqual(retrieved_prescription.medication_name, "Lisinopril")

            # Test get_prescriptions_by_visit_id method
            prescriptions = db.get_prescriptions_by_visit_id(self.visit.id)
            self.assertGreaterEqual(len(prescriptions), 1)
            self.assertEqual(prescriptions[0].medication_name, "Lisinopril")
        finally:
            # Clean up
            db.delete(Prescription, prescription.id)

    def test_patient_medical_summary(self):
        """Test retrieving a patient's medical summary."""
        # Create test data for the summary
        allergy = EHR_Allergy(
            ehr_id=self.ehr.id,
            allergen="Peanuts",
            reaction="Anaphylaxis",
            severity=AllergySeverity.SEVERE,
            noted_by=self.doctor.id
        )
        db.create(allergy)

        immunization = EHR_Immunization(
            ehr_id=self.ehr.id,
            vaccine="COVID-19",
            date_administered=date.today(),
            administered_by=self.doctor.id
        )
        db.create(immunization)

        medication = EHR_Medication(
            visit_id=self.visit.id,
            medication_name="Atorvastatin",
            dosage="20mg",
            frequency="Once daily",
            start_date=date.today(),
            prescribed_by=self.doctor.id
        )
        db.create(medication)

        try:
            # Get the medical summary
            summary = db.get_patient_medical_summary(self.patient.id)

            # Verify the summary structure
            self.assertIn("ehr", summary)
            self.assertIn("recent_visits", summary)
            self.assertIn("active_medications", summary)
            self.assertIn("allergies", summary)
            self.assertIn("immunizations", summary)

            # Verify summary content
            self.assertEqual(summary["ehr"]["id"], str(self.ehr.id))
            self.assertGreaterEqual(len(summary["recent_visits"]), 1)
            self.assertGreaterEqual(len(summary["allergies"]), 1)
            self.assertGreaterEqual(len(summary["immunizations"]), 1)

            # Check for specific test data
            allergy_names = [a["allergen"] for a in summary["allergies"]]
            self.assertIn("Peanuts", allergy_names)

            vaccine_names = [i["vaccine"] for i in summary["immunizations"]]
            self.assertIn("COVID-19", vaccine_names)

            med_names = [m["medication_name"] for m in summary["active_medications"]]
            self.assertIn("Atorvastatin", med_names)
        finally:
            # Clean up
            db.delete(EHR_Allergy, allergy.id)
            db.delete(EHR_Immunization, immunization.id)
            db.delete(EHR_Medication, medication.id)

    def test_foreign_key_constraints(self):
        """Test foreign key constraints."""
        # Attempt to create a record with non-existent foreign key
        invalid_visit = EHR_Visit(
            ehr_id=uuid4(),  # Non-existent EHR ID
            date=date.today(),
            time=datetime.now().time(),
            visit_type="Test Visit",
            chief_complaint="Test complaint"
        )

        # This should fail due to FK constraint
        with self.assertRaises(Exception):
            db.create(invalid_visit)


if __name__ == '__main__':
    unittest.main()