"""Keycloak authentication functional tests."""

import pytest

from clients import KeycloakAdminClient


@pytest.mark.auth
def test_keycloak_admin_connection(auth_client: KeycloakAdminClient):
    """Test Keycloak admin API connection."""
    # Connect to Keycloak
    auth_client.connect()

    # Verify connection
    success = auth_client.verify_connection()

    assert success, "Admin connection should succeed"

    print(f"✓ Keycloak admin connection test passed")
    print(f"  Connected to realm: {auth_client.realm_name}")


@pytest.mark.auth
def test_keycloak_realm_info(auth_client: KeycloakAdminClient, config):
    """Test getting realm information."""
    auth_client.connect()

    realm_info = auth_client.get_realm_info()

    # Verify realm info
    assert realm_info is not None, "Realm info should not be None"
    assert realm_info.get("realm") == config.keycloak_realm, "Realm name should match"
    assert realm_info.get("enabled") is True, "Realm should be enabled"

    print(f"✓ Keycloak realm info test passed")
    print(f"  Realm: {realm_info.get('realm')}")
    print(f"  Display Name: {realm_info.get('displayName', 'N/A')}")
    print(f"  Enabled: {realm_info.get('enabled')}")


@pytest.mark.auth
def test_keycloak_functional_tests_client(auth_client: KeycloakAdminClient, config):
    """Test that functional-tests client exists and is configured."""
    auth_client.connect()

    # Check if client exists
    client_exists = auth_client.verify_client_exists(config.functional_tests_client_id)

    assert client_exists, f"Client '{config.functional_tests_client_id}' should exist in Keycloak"

    # Get client details
    client = auth_client.get_client_by_client_id(config.functional_tests_client_id)

    assert client is not None, "Client should not be None"
    assert client.get("enabled") is True, "Client should be enabled"
    assert client.get("publicClient") is False, "Client should be confidential (not public)"

    print(f"✓ Functional tests client configuration test passed")
    print(f"  Client ID: {client.get('clientId')}")
    print(f"  Enabled: {client.get('enabled')}")
    print(f"  Public: {client.get('publicClient')}")


@pytest.mark.auth
def test_keycloak_test_user_exists(auth_client: KeycloakAdminClient, config):
    """Test that functional test user exists."""
    auth_client.connect()

    # Check if user exists
    user_exists = auth_client.verify_user_exists(config.functional_test_user_email)

    assert user_exists, f"Test user '{config.functional_test_user_email}' should exist in Keycloak"

    # Get user details
    user = auth_client.get_user_by_username(config.functional_test_user_email)

    assert user is not None, "User should not be None"
    assert user.get("enabled") is True, "User should be enabled"
    assert user.get("email") == config.functional_test_user_email, "Email should match"

    print(f"✓ Test user existence test passed")
    print(f"  Username: {user.get('username')}")
    print(f"  Email: {user.get('email')}")
    print(f"  Enabled: {user.get('enabled')}")


@pytest.mark.auth
def test_keycloak_list_clients(auth_client: KeycloakAdminClient):
    """Test listing all clients in realm."""
    auth_client.connect()

    clients = auth_client.list_clients()

    # Verify response
    assert isinstance(clients, list), "Clients should be a list"
    assert len(clients) > 0, "Should have at least one client"

    # Find standard clients
    client_ids = [c.get("clientId") for c in clients]
    assert "account" in client_ids, "Should have default 'account' client"
    assert "admin-cli" in client_ids, "Should have default 'admin-cli' client"

    print(f"✓ Keycloak list clients test passed")
    print(f"  Total clients: {len(clients)}")
    print(f"  Client IDs: {', '.join(client_ids[:5])}...")


@pytest.mark.auth
def test_keycloak_list_users(auth_client: KeycloakAdminClient):
    """Test listing users in realm."""
    auth_client.connect()

    users = auth_client.list_users(max_users=10)

    # Verify response
    assert isinstance(users, list), "Users should be a list"

    # We should have at least the test user
    assert len(users) > 0, "Should have at least one user"

    print(f"✓ Keycloak list users test passed")
    print(f"  Total users (max 10): {len(users)}")
    if users:
        print(f"  Sample user: {users[0].get('username', 'N/A')}")
