"""Full integration test suite."""

import time
import pytest

from clients import (
    DataKwipAPIClient,
    DataKwipMCPClient,
    DataKwipUIClient,
    KeycloakAdminClient,
    UITestError,
)


@pytest.mark.integration
@pytest.mark.slow
def test_full_integration_suite(
    api_client: DataKwipAPIClient,
    mcp_client: DataKwipMCPClient,
    ui_client: DataKwipUIClient,
    auth_client: KeycloakAdminClient,
    config,
):
    """Run complete integration test suite in sequence.

    Tests all major components:
    1. Keycloak authentication
    2. API endpoints
    3. MCP tools
    4. UI automation

    This test provides a comprehensive validation of the entire platform.
    """
    print("\n" + "=" * 80)
    print("DATAKWIP PLATFORM FUNCTIONAL TEST SUITE")
    print("=" * 80)

    overall_start = time.time()
    stage_results = []

    # =========================================================================
    # STAGE 1: Keycloak Authentication
    # =========================================================================
    print("\n[1/4] Testing Keycloak Authentication...")
    stage_start = time.time()

    try:
        # Connect to Keycloak admin API
        auth_client.connect()
        assert auth_client.verify_connection(), "Keycloak connection failed"

        # Verify realm configuration
        realm_info = auth_client.get_realm_info()
        assert realm_info.get("realm") == config.keycloak_realm
        assert realm_info.get("enabled") is True

        # Verify functional-tests client exists
        assert auth_client.verify_client_exists(config.functional_tests_client_id), \
            "functional-tests client not found"

        # Verify test user exists
        assert auth_client.verify_user_exists(config.functional_test_user_email), \
            "Test user not found"

        stage_duration = time.time() - stage_start
        stage_results.append(("Keycloak Auth", True, stage_duration))
        print(f"✓ Keycloak authentication tests passed ({stage_duration:.2f}s)")

    except Exception as e:
        stage_duration = time.time() - stage_start
        stage_results.append(("Keycloak Auth", False, stage_duration))
        print(f"✗ Keycloak authentication tests failed: {e}")
        pytest.fail(f"Stage 1 failed: {e}")

    # =========================================================================
    # STAGE 2: API Endpoints
    # =========================================================================
    print("\n[2/4] Testing API Endpoints...")
    stage_start = time.time()

    try:
        # Test database health (no auth)
        health = api_client.get_database_health()
        assert isinstance(health, dict), "Invalid health response"

        # Test entity listing (OAuth2 required)
        entities = api_client.list_entities(org_id=config.test_org_id, limit=5)
        assert isinstance(entities, list), "Invalid entities response"

        # Test entity tag listing (OAuth2 required)
        tags = api_client.list_entity_tags(org_id=config.test_org_id, limit=10)
        assert isinstance(tags, list), "Invalid tags response"

        stage_duration = time.time() - stage_start
        stage_results.append(("API Endpoints", True, stage_duration))
        print(f"✓ API endpoint tests passed ({stage_duration:.2f}s)")
        print(f"  - Retrieved {len(entities)} entities")
        print(f"  - Retrieved {len(tags)} tags")

    except Exception as e:
        stage_duration = time.time() - stage_start
        stage_results.append(("API Endpoints", False, stage_duration))
        print(f"✗ API endpoint tests failed: {e}")
        pytest.fail(f"Stage 2 failed: {e}")

    # =========================================================================
    # STAGE 3: MCP Tools
    # =========================================================================
    print("\n[3/4] Testing MCP Tools...")
    stage_start = time.time()

    try:
        # List available tools
        tools = mcp_client.list_tools()
        assert isinstance(tools, list), "Invalid tools response"
        assert len(tools) > 0, "No tools available"

        tool_names = [t.get("name") for t in tools]
        assert "query_entities" in tool_names, "query_entities tool not found"

        # Test query_entities tool
        mcp_entities = mcp_client.query_entities(org_id=config.test_org_id, limit=5)
        assert isinstance(mcp_entities, list), "Invalid MCP entities response"

        # Test get_current_values tool (if we have entities)
        if mcp_entities:
            entity_ids = [e["id"] for e in mcp_entities if "id" in e][:3]
            if entity_ids:
                values = mcp_client.get_current_values(
                    entity_ids=entity_ids,
                    org_id=config.test_org_id
                )
                assert isinstance(values, list), "Invalid MCP values response"

        stage_duration = time.time() - stage_start
        stage_results.append(("MCP Tools", True, stage_duration))
        print(f"✓ MCP tool tests passed ({stage_duration:.2f}s)")
        print(f"  - Available tools: {len(tools)}")
        print(f"  - Retrieved {len(mcp_entities)} entities via MCP")

    except Exception as e:
        stage_duration = time.time() - stage_start
        stage_results.append(("MCP Tools", False, stage_duration))
        print(f"✗ MCP tool tests failed: {e}")
        pytest.fail(f"Stage 3 failed: {e}")

    # =========================================================================
    # STAGE 4: UI Automation
    # =========================================================================
    print("\n[4/4] Testing UI Automation...")
    stage_start = time.time()

    try:
        # Start browser
        ui_client.start()

        # Test login
        login_success = ui_client.login()
        assert login_success, "UI login failed"

        # Verify we're logged in
        current_url = ui_client.get_current_url()
        assert "realms/datakwip" not in current_url, "Still on login page"

        # Get page title
        title = ui_client.get_page_title()
        assert title and len(title) > 0, "Page title is empty"

        # Try to navigate to Data Explorer (optional)
        try:
            ui_client.navigate_to_data_explorer()
            data_explorer_available = True
        except UITestError:
            data_explorer_available = False

        stage_duration = time.time() - stage_start
        stage_results.append(("UI Automation", True, stage_duration))
        print(f"✓ UI automation tests passed ({stage_duration:.2f}s)")
        print(f"  - Login: ✓")
        print(f"  - Page title: {title}")
        print(f"  - Data Explorer: {'✓' if data_explorer_available else 'Not available'}")

    except Exception as e:
        stage_duration = time.time() - stage_start
        stage_results.append(("UI Automation", False, stage_duration))
        print(f"✗ UI automation tests failed: {e}")
        pytest.fail(f"Stage 4 failed: {e}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    overall_duration = time.time() - overall_start

    print("\n" + "=" * 80)
    print("TEST SUITE SUMMARY")
    print("=" * 80)

    for stage_name, success, duration in stage_results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:<8} {stage_name:<20} {duration:>6.2f}s")

    print("-" * 80)
    print(f"Total execution time: {overall_duration:.2f}s")

    # All stages must pass
    all_passed = all(result[1] for result in stage_results)
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")

    print("=" * 80 + "\n")

    assert all_passed, "Not all stages passed"


@pytest.mark.integration
def test_api_mcp_consistency(
    api_client: DataKwipAPIClient,
    mcp_client: DataKwipMCPClient,
    config,
):
    """Test that API and MCP return consistent data."""
    # Get entities from API
    api_entities = api_client.list_entities(org_id=config.test_org_id, limit=10)

    # Get entities from MCP
    mcp_entities = mcp_client.query_entities(org_id=config.test_org_id, limit=10)

    # Both should return lists
    assert isinstance(api_entities, list), "API should return list"
    assert isinstance(mcp_entities, list), "MCP should return list"

    # If data exists, counts should be similar (allowing for timing differences)
    if api_entities and mcp_entities:
        # Allow 10% variance due to timing
        max_diff = max(len(api_entities), len(mcp_entities)) * 0.1
        diff = abs(len(api_entities) - len(mcp_entities))

        assert diff <= max_diff, \
            f"API and MCP entity counts differ significantly: {len(api_entities)} vs {len(mcp_entities)}"

    print(f"✓ API/MCP consistency test passed")
    print(f"  API entities: {len(api_entities)}")
    print(f"  MCP entities: {len(mcp_entities)}")


@pytest.mark.integration
def test_end_to_end_data_flow(
    api_client: DataKwipAPIClient,
    mcp_client: DataKwipMCPClient,
    config,
):
    """Test complete data flow: Database → API → MCP."""
    print("\nTesting end-to-end data flow...")

    # Step 1: Verify database is healthy
    health = api_client.get_database_health()
    assert "timescaledb" in health or "status" in health, "Database health check failed"
    print("  ✓ Database is healthy")

    # Step 2: Fetch entities via API
    api_entities = api_client.list_entities(org_id=config.test_org_id, limit=5)
    assert isinstance(api_entities, list), "API entity fetch failed"
    print(f"  ✓ API returned {len(api_entities)} entities")

    # Step 3: Fetch same entities via MCP
    mcp_entities = mcp_client.query_entities(org_id=config.test_org_id, limit=5)
    assert isinstance(mcp_entities, list), "MCP entity fetch failed"
    print(f"  ✓ MCP returned {len(mcp_entities)} entities")

    # Step 4: If we have entities, verify structure
    if api_entities:
        entity = api_entities[0]
        assert "id" in entity, "Entity missing ID"
        assert "org_id" in entity, "Entity missing org_id"
        print(f"  ✓ Entity structure is valid")

    print("✓ End-to-end data flow test passed")
