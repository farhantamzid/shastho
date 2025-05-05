-- Migration for Test/Imaging Admins table
-- This creates the table needed for managing Test/Imaging Admin accounts

CREATE TABLE IF NOT EXISTS "public"."test_admins" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL UNIQUE,
    "full_name" VARCHAR NOT NULL,
    "hospital_id" UUID NOT NULL,
    "contact_number" VARCHAR NOT NULL,
    "department" VARCHAR,
    "qualification" VARCHAR,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes for test_admins
CREATE INDEX IF NOT EXISTS "idx_test_admins_user_id" ON "public"."test_admins" ("user_id");
CREATE INDEX IF NOT EXISTS "idx_test_admins_hospital_id" ON "public"."test_admins" ("hospital_id");