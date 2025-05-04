-- Create EHR tables for Shastho Healthcare System
-- Migration: ehr_system_tables

-- Main EHR record linked to a patient
CREATE TABLE IF NOT EXISTS "public"."EHR" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "patient_id" UUID NOT NULL REFERENCES "public"."patients"("id") ON DELETE CASCADE,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create index on patient_id for faster lookups
CREATE INDEX IF NOT EXISTS "idx_ehr_patient_id" ON "public"."EHR" ("patient_id");

-- EHR_Visits: Records of patient visits
CREATE TABLE IF NOT EXISTS "public"."EHR_Visits" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "ehr_id" UUID NOT NULL REFERENCES "public"."EHR"("id") ON DELETE CASCADE,
    "date" DATE NOT NULL,
    "time" TIME NOT NULL,
    "visit_type" VARCHAR NOT NULL,
    "provider_id" UUID REFERENCES "public"."doctors"("id") ON DELETE SET NULL,
    "chief_complaint" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes for EHR_Visits
CREATE INDEX IF NOT EXISTS "idx_ehr_visits_ehr_id" ON "public"."EHR_Visits" ("ehr_id");
CREATE INDEX IF NOT EXISTS "idx_ehr_visits_provider_id" ON "public"."EHR_Visits" ("provider_id");
CREATE INDEX IF NOT EXISTS "idx_ehr_visits_date" ON "public"."EHR_Visits" ("date");

-- EHR_Diagnoses: Medical diagnoses made during visits
CREATE TABLE IF NOT EXISTS "public"."EHR_Diagnoses" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "visit_id" UUID NOT NULL REFERENCES "public"."EHR_Visits"("id") ON DELETE CASCADE,
    "diagnosis_code" VARCHAR NOT NULL,
    "diagnosis_description" TEXT NOT NULL,
    "diagnosed_by" UUID REFERENCES "public"."doctors"("id") ON DELETE SET NULL,
    "diagnosed_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes for EHR_Diagnoses
CREATE INDEX IF NOT EXISTS "idx_ehr_diagnoses_visit_id" ON "public"."EHR_Diagnoses" ("visit_id");
CREATE INDEX IF NOT EXISTS "idx_ehr_diagnoses_diagnosed_by" ON "public"."EHR_Diagnoses" ("diagnosed_by");
CREATE INDEX IF NOT EXISTS "idx_ehr_diagnoses_diagnosis_code" ON "public"."EHR_Diagnoses" ("diagnosis_code");

-- EHR_Medications: Medications prescribed during visits
CREATE TABLE IF NOT EXISTS "public"."EHR_Medications" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "visit_id" UUID NOT NULL REFERENCES "public"."EHR_Visits"("id") ON DELETE CASCADE,
    "medication_name" VARCHAR NOT NULL,
    "dosage" VARCHAR NOT NULL,
    "frequency" VARCHAR NOT NULL,
    "start_date" DATE NOT NULL,
    "end_date" DATE,
    "prescribed_by" UUID REFERENCES "public"."doctors"("id") ON DELETE SET NULL,
    "prescribed_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes for EHR_Medications
CREATE INDEX IF NOT EXISTS "idx_ehr_medications_visit_id" ON "public"."EHR_Medications" ("visit_id");
CREATE INDEX IF NOT EXISTS "idx_ehr_medications_prescribed_by" ON "public"."EHR_Medications" ("prescribed_by");

-- EHR_Allergies: Patient allergies
CREATE TABLE IF NOT EXISTS "public"."EHR_Allergies" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "ehr_id" UUID NOT NULL REFERENCES "public"."EHR"("id") ON DELETE CASCADE,
    "allergen" VARCHAR NOT NULL,
    "reaction" TEXT NOT NULL,
    "severity" VARCHAR NOT NULL CHECK (severity IN ('Mild', 'Moderate', 'Severe', 'Life-threatening')),
    "noted_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "noted_by" UUID REFERENCES "public"."doctors"("id") ON DELETE SET NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes for EHR_Allergies
CREATE INDEX IF NOT EXISTS "idx_ehr_allergies_ehr_id" ON "public"."EHR_Allergies" ("ehr_id");
CREATE INDEX IF NOT EXISTS "idx_ehr_allergies_allergen" ON "public"."EHR_Allergies" ("allergen");

-- EHR_Procedures: Medical procedures performed
CREATE TABLE IF NOT EXISTS "public"."EHR_Procedures" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "visit_id" UUID NOT NULL REFERENCES "public"."EHR_Visits"("id") ON DELETE CASCADE,
    "procedure_code" VARCHAR NOT NULL,
    "procedure_description" TEXT NOT NULL,
    "performed_by" UUID REFERENCES "public"."doctors"("id") ON DELETE SET NULL,
    "performed_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes for EHR_Procedures
CREATE INDEX IF NOT EXISTS "idx_ehr_procedures_visit_id" ON "public"."EHR_Procedures" ("visit_id");
CREATE INDEX IF NOT EXISTS "idx_ehr_procedures_performed_by" ON "public"."EHR_Procedures" ("performed_by");
CREATE INDEX IF NOT EXISTS "idx_ehr_procedures_procedure_code" ON "public"."EHR_Procedures" ("procedure_code");

-- EHR_Vitals: Patient vital signs
CREATE TABLE IF NOT EXISTS "public"."EHR_Vitals" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "visit_id" UUID NOT NULL REFERENCES "public"."EHR_Visits"("id") ON DELETE CASCADE,
    "temperature" DECIMAL(5,2),
    "pulse" INTEGER,
    "blood_pressure" VARCHAR,
    "respiratory_rate" INTEGER,
    "recorded_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "recorded_by" UUID REFERENCES "public"."doctors"("id") ON DELETE SET NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes for EHR_Vitals
CREATE INDEX IF NOT EXISTS "idx_ehr_vitals_visit_id" ON "public"."EHR_Vitals" ("visit_id");
CREATE INDEX IF NOT EXISTS "idx_ehr_vitals_recorded_at" ON "public"."EHR_Vitals" ("recorded_at");

-- EHR_Immunizations: Patient immunization records
CREATE TABLE IF NOT EXISTS "public"."EHR_Immunizations" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "ehr_id" UUID NOT NULL REFERENCES "public"."EHR"("id") ON DELETE CASCADE,
    "vaccine" VARCHAR NOT NULL,
    "date_administered" DATE NOT NULL,
    "administered_by" UUID REFERENCES "public"."doctors"("id") ON DELETE SET NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes for EHR_Immunizations
CREATE INDEX IF NOT EXISTS "idx_ehr_immunizations_ehr_id" ON "public"."EHR_Immunizations" ("ehr_id");
CREATE INDEX IF NOT EXISTS "idx_ehr_immunizations_vaccine" ON "public"."EHR_Immunizations" ("vaccine");
CREATE INDEX IF NOT EXISTS "idx_ehr_immunizations_date_administered" ON "public"."EHR_Immunizations" ("date_administered");

-- EHR_TestResults: Test results for patients
CREATE TABLE IF NOT EXISTS "public"."EHR_TestResults" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "ehr_id" UUID NOT NULL REFERENCES "public"."EHR"("id") ON DELETE CASCADE,
    "test_type" VARCHAR NOT NULL,
    "test_date" DATE NOT NULL,
    "result_data" JSONB NOT NULL,
    "file_path" TEXT,
    "uploaded_by" UUID REFERENCES "public"."doctors"("id") ON DELETE SET NULL,
    "uploaded_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes for EHR_TestResults
CREATE INDEX IF NOT EXISTS "idx_ehr_test_results_ehr_id" ON "public"."EHR_TestResults" ("ehr_id");
CREATE INDEX IF NOT EXISTS "idx_ehr_test_results_test_type" ON "public"."EHR_TestResults" ("test_type");
CREATE INDEX IF NOT EXISTS "idx_ehr_test_results_test_date" ON "public"."EHR_TestResults" ("test_date");

-- EHR_ProviderNotes: Clinical notes from providers
CREATE TABLE IF NOT EXISTS "public"."EHR_ProviderNotes" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "visit_id" UUID NOT NULL REFERENCES "public"."EHR_Visits"("id") ON DELETE CASCADE,
    "note_text" TEXT NOT NULL,
    "created_by" UUID REFERENCES "public"."doctors"("id") ON DELETE SET NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes for EHR_ProviderNotes
CREATE INDEX IF NOT EXISTS "idx_ehr_provider_notes_visit_id" ON "public"."EHR_ProviderNotes" ("visit_id");
CREATE INDEX IF NOT EXISTS "idx_ehr_provider_notes_created_by" ON "public"."EHR_ProviderNotes" ("created_by");

-- Prescriptions: Medication prescriptions
CREATE TABLE IF NOT EXISTS "public"."Prescriptions" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "visit_id" UUID NOT NULL REFERENCES "public"."EHR_Visits"("id") ON DELETE CASCADE,
    "medication_name" VARCHAR NOT NULL,
    "dosage" VARCHAR NOT NULL,
    "frequency" VARCHAR NOT NULL,
    "instructions" TEXT NOT NULL,
    "prescribed_by" UUID REFERENCES "public"."doctors"("id") ON DELETE SET NULL,
    "prescribed_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes for Prescriptions
CREATE INDEX IF NOT EXISTS "idx_prescriptions_visit_id" ON "public"."Prescriptions" ("visit_id");
CREATE INDEX IF NOT EXISTS "idx_prescriptions_prescribed_by" ON "public"."Prescriptions" ("prescribed_by");
CREATE INDEX IF NOT EXISTS "idx_prescriptions_medication_name" ON "public"."Prescriptions" ("medication_name");