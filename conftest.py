"""Pytest configuration and fixtures."""

import os
from pathlib import Path
from typing import Generator

import pytest
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from clients import (
    DataKwipAPIClient,
    DataKwipMCPClient,
    DataKwipUIClient,
    KeycloakAdminClient,
)


class TestConfig(BaseSettings):
    """Test configuration from environment variables."""

    # Railway URLs
    railway_api_url: str
    railway_mcp_url: str
    railway_ui_url: str
    railway_auth_url: str

    # OAuth2
    oauth2_token_url: str
    oauth2_issuer_url: str

    # Keycloak
    keycloak_base_url: str
    keycloak_realm: str
    keycloak_admin: str
    keycloak_admin_password: str

    # Functional tests client
    functional_tests_client_id: str
    functional_tests_client_secret: str

    # Test user
    functional_test_user_email: str
    functional_test_user_password: str

    # Test data
    test_org_id: int = 1
    test_entity_limit: int = 10
    test_tag_limit: int = 20

    # Timeouts
    api_timeout: int = 30
    mcp_timeout: int = 30
    ui_timeout: int = 60
    auth_timeout: int = 30

    # UI config
    headless_browser: bool = True
    browser_type: str = "chromium"
    screenshot_on_failure: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


@pytest.fixture(scope="session")
def config() -> TestConfig:
    """Load test configuration from environment."""
    # Load .env file
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try .env.example as fallback
        env_example = Path(__file__).parent / ".env.example"
        if env_example.exists():
            print("Warning: .env not found, loading .env.example")
            load_dotenv(env_example)

    return TestConfig()


@pytest.fixture(scope="session")
def api_client(config: TestConfig) -> Generator[DataKwipAPIClient, None, None]:
    """Create DataKwip API client."""
    client = DataKwipAPIClient(
        base_url=config.railway_api_url,
        token_url=config.oauth2_token_url,
        client_id=config.functional_tests_client_id,
        client_secret=config.functional_tests_client_secret,
        username=config.functional_test_user_email,
        password=config.functional_test_user_password,
        timeout=config.api_timeout,
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
def mcp_client(config: TestConfig) -> Generator[DataKwipMCPClient, None, None]:
    """Create DataKwip MCP client."""
    client = DataKwipMCPClient(
        base_url=config.railway_mcp_url,
        timeout=config.mcp_timeout,
    )
    yield client
    client.close()


@pytest.fixture(scope="function")
def ui_client(config: TestConfig) -> Generator[DataKwipUIClient, None, None]:
    """Create DataKwip UI client (function-scoped for isolation)."""
    screenshot_dir = None
    if config.screenshot_on_failure:
        screenshot_dir = str(Path(__file__).parent / "screenshots")

    client = DataKwipUIClient(
        base_url=config.railway_ui_url,
        username=config.functional_test_user_email,
        password=config.functional_test_user_password,
        headless=config.headless_browser,
        browser_type=config.browser_type,
        timeout=config.ui_timeout * 1000,  # Convert to milliseconds
        screenshot_dir=screenshot_dir,
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
def auth_client(config: TestConfig) -> Generator[KeycloakAdminClient, None, None]:
    """Create Keycloak admin client."""
    client = KeycloakAdminClient(
        server_url=config.keycloak_base_url,
        realm_name=config.keycloak_realm,
        admin_username=config.keycloak_admin,
        admin_password=config.keycloak_admin_password,
        verify=False,  # Allow self-signed certs in dev
    )
    yield client
    client.close()
