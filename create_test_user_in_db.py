"""
Create functional test user in DataKwip database and link to org_id=1

This script:
1. Gets the Keycloak UUID for the test user
2. Creates the user in core.user table (if not exists)
3. Links the user to org_id=1 in org_user table

Usage:
    python create_test_user_in_db.py
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Get database URL from Railway environment variables
# You'll need to get this from: railway variables --service datakwip-timescaledb
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    print("Get it with: railway variables --service datakwip-timescaledb | grep DATABASE_URL")
    sys.exit(1)

# Test user details
TEST_USER_EMAIL = "functional-test-user@datakwip.local"
TEST_ORG_ID = 1

# Keycloak user ID - we'll fetch this from Keycloak
# For now, we'll create the user WITHOUT keycloak_user_id and link it later
KEYCLOAK_USER_ID = None  # Will be fetched from Keycloak or left NULL

def get_keycloak_user_uuid():
    """Get the Keycloak UUID for the test user"""
    from python_keycloak import KeycloakAdmin

    keycloak_base_url = os.getenv('KEYCLOAK_BASE_URL')
    keycloak_realm = os.getenv('KEYCLOAK_REALM')
    admin_user = os.getenv('KEYCLOAK_ADMIN')
    admin_password = os.getenv('KEYCLOAK_ADMIN_PASSWORD')

    if not all([keycloak_base_url, keycloak_realm, admin_user, admin_password]):
        print("WARNING: Keycloak credentials not found in .env")
        print("User will be created without keycloak_user_id (can be linked later)")
        return None

    try:
        # Connect to Keycloak admin
        keycloak_admin = KeycloakAdmin(
            server_url=keycloak_base_url,
            username=admin_user,
            password=admin_password,
            realm_name="master",  # Login to master realm
            user_realm_name=keycloak_realm,  # Target realm
            verify=True
        )

        # Search for user by email
        users = keycloak_admin.get_users({"email": TEST_USER_EMAIL})

        if not users:
            print(f"WARNING: User {TEST_USER_EMAIL} not found in Keycloak")
            print("User will be created in DB without keycloak_user_id")
            return None

        keycloak_uuid = users[0]['id']
        print(f"✓ Found Keycloak user: {TEST_USER_EMAIL}")
        print(f"  Keycloak UUID: {keycloak_uuid}")
        return keycloak_uuid

    except Exception as e:
        print(f"WARNING: Could not connect to Keycloak: {e}")
        print("User will be created without keycloak_user_id (can be linked later)")
        return None


def create_test_user_in_database():
    """Create test user in database and link to org"""

    print("\n" + "="*70)
    print("Creating Functional Test User in DataKwip Database")
    print("="*70 + "\n")

    # Get Keycloak UUID
    keycloak_uuid = get_keycloak_user_uuid()

    # Connect to database
    print(f"Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Check if org_id=1 exists
        cur.execute("SELECT id, org_key FROM core.org WHERE id = %s", (TEST_ORG_ID,))
        org = cur.fetchone()

        if not org:
            print(f"ERROR: Organization with id={TEST_ORG_ID} does not exist!")
            print("\nAvailable organizations:")
            cur.execute("SELECT id, org_key FROM core.org ORDER BY id")
            orgs = cur.fetchall()
            for o in orgs:
                print(f"  org_id={o['id']}, key={o['org_key']}")

            print("\nPlease run the simulator first to create organizations:")
            print("  cd ../datakwip-simulator")
            print("  python src/service_main.py")
            conn.close()
            sys.exit(1)

        print(f"✓ Organization found: id={org['id']}, key={org['org_key']}")

        # Check if user already exists
        cur.execute("SELECT id, email, keycloak_user_id FROM core.user WHERE email = %s", (TEST_USER_EMAIL,))
        existing_user = cur.fetchone()

        if existing_user:
            user_id = existing_user['id']
            print(f"✓ User already exists: id={user_id}, email={existing_user['email']}")

            # Update keycloak_user_id if we have it and it's not set
            if keycloak_uuid and not existing_user['keycloak_user_id']:
                cur.execute("""
                    UPDATE core.user
                    SET keycloak_user_id = %s
                    WHERE id = %s
                """, (keycloak_uuid, user_id))
                conn.commit()
                print(f"  ✓ Updated keycloak_user_id: {keycloak_uuid}")
        else:
            # Create new user
            cur.execute("""
                INSERT INTO core.user (email, keycloak_user_id)
                VALUES (%s, %s)
                RETURNING id
            """, (TEST_USER_EMAIL, keycloak_uuid))

            user_id = cur.fetchone()['id']
            conn.commit()
            print(f"✓ User created: id={user_id}, email={TEST_USER_EMAIL}")
            if keycloak_uuid:
                print(f"  keycloak_user_id: {keycloak_uuid}")

        # Check if org_user relationship exists
        cur.execute("""
            SELECT 1 FROM core.org_user
            WHERE user_id = %s AND org_id = %s
        """, (user_id, TEST_ORG_ID))

        if cur.fetchone():
            print(f"✓ User already linked to organization {TEST_ORG_ID}")
        else:
            # Link user to organization
            cur.execute("""
                INSERT INTO core.org_user (user_id, org_id)
                VALUES (%s, %s)
            """, (user_id, TEST_ORG_ID))
            conn.commit()
            print(f"✓ User linked to organization {TEST_ORG_ID}")

        # Grant org_admin permissions (optional but recommended for testing)
        cur.execute("""
            SELECT 1 FROM core.org_admin
            WHERE user_id = %s AND org_id = %s
        """, (user_id, TEST_ORG_ID))

        if cur.fetchone():
            print(f"✓ User already has org_admin permissions")
        else:
            cur.execute("""
                INSERT INTO core.org_admin (user_id, org_id)
                VALUES (%s, %s)
            """, (user_id, TEST_ORG_ID))
            conn.commit()
            print(f"✓ User granted org_admin permissions for org {TEST_ORG_ID}")

        print("\n" + "="*70)
        print("SUCCESS! Test user configured for functional tests")
        print("="*70)
        print(f"\nUser details:")
        print(f"  Database ID: {user_id}")
        print(f"  Email: {TEST_USER_EMAIL}")
        print(f"  Organization: {TEST_ORG_ID} ({org['org_key']})")
        print(f"  Keycloak UUID: {keycloak_uuid or 'Not linked (NULL)'}")
        print(f"  Permissions: org_admin")
        print("\nYou can now run the functional tests:")
        print("  pytest tests/test_api.py -v")

    except Exception as e:
        print(f"\nERROR: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    create_test_user_in_database()
