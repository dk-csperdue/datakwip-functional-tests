-- ============================================================================
-- Create Functional Test User in DataKwip Database
-- ============================================================================
--
-- This script creates the functional-test-user in the core.user table
-- and links them to org_id=1 with admin permissions for testing.
--
-- Usage:
--   1. Get Railway database connection:
--      railway variables --service datakwip-timescaledb | grep DATABASE_URL
--
--   2. Connect with psql (if available):
--      psql "postgresql://..."
--
--   3. Run this script:
--      \i setup_test_user.sql
--
-- OR use the Python script:
--   python create_test_user_in_db.py
--
-- ============================================================================

BEGIN;

-- ============================================================================
-- Step 1: Verify org_id=1 exists
-- ============================================================================

DO $$
DECLARE
    org_exists boolean;
    org_key_val varchar;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM core.org WHERE id = 1
    ) INTO org_exists;

    IF NOT org_exists THEN
        RAISE EXCEPTION 'Organization with id=1 does not exist! Run the simulator first to create organizations.';
    END IF;

    SELECT org_key INTO org_key_val FROM core.org WHERE id = 1;
    RAISE NOTICE '✓ Organization found: id=1, key=%', org_key_val;
END $$;


-- ============================================================================
-- Step 2: Create or update user in core.user
-- ============================================================================

DO $$
DECLARE
    test_user_id integer;
    test_user_email varchar := 'functional-test-user@datakwip.local';
    -- Replace this with actual Keycloak UUID if you have it
    -- Get it from: SELECT id FROM keycloak.user_entity WHERE email = 'functional-test-user@datakwip.local'
    -- Or leave as NULL and link later
    keycloak_uuid varchar := NULL;
BEGIN
    -- Check if user exists
    SELECT id INTO test_user_id FROM core.user WHERE email = test_user_email;

    IF test_user_id IS NULL THEN
        -- Create new user
        INSERT INTO core.user (email, keycloak_user_id)
        VALUES (test_user_email, keycloak_uuid)
        RETURNING id INTO test_user_id;

        RAISE NOTICE '✓ User created: id=%, email=%', test_user_id, test_user_email;
    ELSE
        -- Update keycloak_user_id if we have it and it's not set
        IF keycloak_uuid IS NOT NULL THEN
            UPDATE core.user
            SET keycloak_user_id = keycloak_uuid
            WHERE id = test_user_id
            AND keycloak_user_id IS NULL;

            RAISE NOTICE '✓ User already exists: id=%, email=% (keycloak_user_id updated)', test_user_id, test_user_email;
        ELSE
            RAISE NOTICE '✓ User already exists: id=%, email=%', test_user_id, test_user_email;
        END IF;
    END IF;

    -- Store user_id for next steps
    PERFORM set_config('app.test_user_id', test_user_id::text, false);
END $$;


-- ============================================================================
-- Step 3: Link user to org_id=1 (org_user table)
-- ============================================================================

DO $$
DECLARE
    test_user_id integer;
    test_org_id integer := 1;
    link_exists boolean;
BEGIN
    -- Get user_id from previous step
    test_user_id := current_setting('app.test_user_id')::integer;

    -- Check if org_user link exists
    SELECT EXISTS (
        SELECT 1 FROM core.org_user
        WHERE user_id = test_user_id AND org_id = test_org_id
    ) INTO link_exists;

    IF NOT link_exists THEN
        -- Create org_user link
        INSERT INTO core.org_user (user_id, org_id)
        VALUES (test_user_id, test_org_id);

        RAISE NOTICE '✓ User (id=%) linked to organization (id=%)', test_user_id, test_org_id;
    ELSE
        RAISE NOTICE '✓ User (id=%) already linked to organization (id=%)', test_user_id, test_org_id;
    END IF;
END $$;


-- ============================================================================
-- Step 4: Grant org_admin permissions (recommended for testing)
-- ============================================================================

DO $$
DECLARE
    test_user_id integer;
    test_org_id integer := 1;
    admin_exists boolean;
BEGIN
    -- Get user_id from previous step
    test_user_id := current_setting('app.test_user_id')::integer;

    -- Check if user is already org_admin
    SELECT EXISTS (
        SELECT 1 FROM core.org_admin
        WHERE user_id = test_user_id AND org_id = test_org_id
    ) INTO admin_exists;

    IF NOT admin_exists THEN
        -- Grant org_admin permissions
        INSERT INTO core.org_admin (user_id, org_id)
        VALUES (test_user_id, test_org_id);

        RAISE NOTICE '✓ User (id=%) granted org_admin permissions for org (id=%)', test_user_id, test_org_id;
    ELSE
        RAISE NOTICE '✓ User (id=%) already has org_admin permissions for org (id=%)', test_user_id, test_org_id;
    END IF;
END $$;


-- ============================================================================
-- Step 5: Verify setup
-- ============================================================================

DO $$
DECLARE
    test_user_id integer;
    test_user_email varchar;
    test_org_id integer;
    test_org_key varchar;
    is_org_user boolean;
    is_org_admin boolean;
BEGIN
    test_user_id := current_setting('app.test_user_id')::integer;

    -- Get user details
    SELECT email INTO test_user_email FROM core.user WHERE id = test_user_id;

    -- Get org details
    SELECT id, org_key INTO test_org_id, test_org_key FROM core.org WHERE id = 1;

    -- Check org_user membership
    SELECT EXISTS (
        SELECT 1 FROM core.org_user WHERE user_id = test_user_id AND org_id = test_org_id
    ) INTO is_org_user;

    -- Check org_admin permissions
    SELECT EXISTS (
        SELECT 1 FROM core.org_admin WHERE user_id = test_user_id AND org_id = test_org_id
    ) INTO is_org_admin;

    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'SUCCESS! Test user configured for functional tests';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'User details:';
    RAISE NOTICE '  Database ID: %', test_user_id;
    RAISE NOTICE '  Email: %', test_user_email;
    RAISE NOTICE '  Organization: % (%)', test_org_id, test_org_key;
    RAISE NOTICE '  Is org_user: %', is_org_user;
    RAISE NOTICE '  Is org_admin: %', is_org_admin;
    RAISE NOTICE '';
    RAISE NOTICE 'You can now run the functional tests:';
    RAISE NOTICE '  pytest tests/test_api.py -v';
    RAISE NOTICE '============================================================';
END $$;

COMMIT;


-- ============================================================================
-- Optional: Get Keycloak UUID for user
-- ============================================================================
-- If you need to link the Keycloak UUID later, run this in the Keycloak DB:
--
-- SELECT id, username, email
-- FROM keycloak.user_entity
-- WHERE email = 'functional-test-user@datakwip.local';
--
-- Then update the core.user table:
--
-- UPDATE core.user
-- SET keycloak_user_id = '<keycloak-uuid-here>'
-- WHERE email = 'functional-test-user@datakwip.local';
--
-- ============================================================================


-- ============================================================================
-- Rollback (if needed)
-- ============================================================================
-- To remove the test user setup:
--
-- DELETE FROM core.org_admin WHERE user_id IN (SELECT id FROM core.user WHERE email = 'functional-test-user@datakwip.local');
-- DELETE FROM core.org_user WHERE user_id IN (SELECT id FROM core.user WHERE email = 'functional-test-user@datakwip.local');
-- DELETE FROM core.user WHERE email = 'functional-test-user@datakwip.local';
--
-- ============================================================================
