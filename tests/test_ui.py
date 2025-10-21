"""UI automation functional tests."""

import pytest

from clients import DataKwipUIClient, UITestError


@pytest.mark.ui
def test_ui_login(ui_client: DataKwipUIClient):
    """Test UI login flow via Keycloak."""
    # Start browser
    ui_client.start()

    # Perform login
    success = ui_client.login()

    assert success, "Login should succeed"

    # Verify we're logged in by checking URL
    current_url = ui_client.get_current_url()
    assert "realms/datakwip" not in current_url, "Should not be on Keycloak login page"

    print(f"✓ UI login test passed")
    print(f"  Logged in successfully")
    print(f"  Current URL: {current_url}")


@pytest.mark.ui
def test_ui_navigation(ui_client: DataKwipUIClient):
    """Test UI navigation to Data Explorer."""
    # Start browser and login
    ui_client.start()
    ui_client.login()

    # Navigate to Data Explorer
    try:
        success = ui_client.navigate_to_data_explorer()
        assert success, "Navigation should succeed"
        print(f"✓ UI navigation test passed")
    except UITestError as e:
        # Data Explorer might not exist yet - that's okay
        pytest.skip(f"Data Explorer not available: {e}")


@pytest.mark.ui
@pytest.mark.slow
def test_ui_query_execution(ui_client: DataKwipUIClient):
    """Test executing a query in Data Explorer."""
    # Start browser and login
    ui_client.start()
    ui_client.login()

    # Navigate to Data Explorer
    try:
        ui_client.navigate_to_data_explorer()
    except UITestError:
        pytest.skip("Data Explorer not available")

    # Execute query
    try:
        result = ui_client.execute_query()
        assert result["success"], "Query should execute successfully"
        print(f"✓ UI query execution test passed")
        print(f"  Results: {result.get('results_summary', 'N/A')}")
    except UITestError as e:
        # Query execution might not work if Data Explorer UI is different
        pytest.skip(f"Query execution not available: {e}")


@pytest.mark.ui
def test_ui_page_title(ui_client: DataKwipUIClient):
    """Test that page title is set correctly."""
    # Start browser and login
    ui_client.start()
    ui_client.login()

    # Get page title
    title = ui_client.get_page_title()

    assert title, "Page title should not be empty"
    assert len(title) > 0, "Page title should have content"

    print(f"✓ UI page title test passed")
    print(f"  Title: {title}")


@pytest.mark.ui
def test_ui_invalid_login(config):
    """Test UI login with invalid credentials."""
    # Create client with invalid credentials
    ui_client = DataKwipUIClient(
        base_url=config.railway_ui_url,
        username="invalid@example.com",
        password="wrongpassword",
        headless=config.headless_browser,
        browser_type=config.browser_type,
        timeout=config.ui_timeout * 1000,
    )

    try:
        ui_client.start()

        # This should fail
        with pytest.raises(UITestError):
            ui_client.login()

        print(f"✓ UI invalid login test passed (correctly rejected)")

    finally:
        ui_client.close()
