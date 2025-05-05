-- Migration for Test/Imaging Admin Requests table
-- This creates the table needed for managing Test/Imaging Admin role requests

CREATE TABLE IF NOT EXISTS "public"."test_image_admin_requests" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "hospital_id" UUID NOT NULL,
    "full_name" VARCHAR NOT NULL,
    "email" VARCHAR NOT NULL,
    "contact_number" VARCHAR NOT NULL,
    "department" VARCHAR NOT NULL,
    "qualification" VARCHAR NOT NULL,
    "experience" TEXT NOT NULL,
    "reason" TEXT NOT NULL,
    "submitted_by" UUID,  -- HospitalAdmin user_id who submitted the request
    "status" VARCHAR NOT NULL DEFAULT 'pending',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes for test_image_admin_requests
CREATE INDEX IF NOT EXISTS "idx_test_image_admin_requests_hospital_id" ON "public"."test_image_admin_requests" ("hospital_id");
CREATE INDEX IF NOT EXISTS "idx_test_image_admin_requests_status" ON "public"."test_image_admin_requests" ("status");
CREATE INDEX IF NOT EXISTS "idx_test_image_admin_requests_submitted_by" ON "public"."test_image_admin_requests" ("submitted_by");