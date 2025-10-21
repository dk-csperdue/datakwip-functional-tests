# DataKwip Functional Tests

Comprehensive functional test suite for the DataKwip platform deployed on Railway. Tests all major components including API endpoints, MCP tools, UI automation, and Keycloak authentication.

## Overview

This test suite validates the complete DataKwip platform stack:

- **Keycloak Authentication**: OAuth2 flows, realm configuration, client/user management
- **DataKwip API**: REST endpoints with OAuth2 authentication, database health
- **MCP Tools**: JSON-RPC 2.0 protocol, query_entities, get_current_values
- **Admin UI**: Playwright browser automation, login flows, navigation

## Prerequisites

### Required Software

- **Python 3.11+**: Download from [python.org](https://www.python.org/downloads/)
- **Playwright Browsers**: Installed separately (see Installation section)
- **Git**: For version control

### Railway Services

All tests require the following Railway services to be running:

- **datakwip-auth-service** (Keycloak): `https://datakwip-ai.up.railway.app`
- **datakwip-api**: `https://datakwip-api-dev.up.railway.app`
- **datakwip-mcp-connector**: `https://datakwip-mcp-connector-dev.up.railway.app`
- **datakwip-ai-ui**: `https://datakwip-ai-ui-dev.up.railway.app`

### Test Data

Tests assume the simulator has seeded test data:

- Organization ID: `1`
- Test entities and tags in TimescaleDB
- Functional test user created in Keycloak

## Installation

### 1. Clone Repository

```bash
cd C:\Users\csper\datakwip-projects\datakwip-platform
# Repository is already in datakwip-functional-tests/
```

### 2. Create Virtual Environment

```bash
cd datakwip-functional-tests
python -m venv .venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install -e .
```

This installs:
- pytest (testing framework)
- pytest-asyncio (async test support)
- httpx (HTTP client)
- playwright (browser automation)
- python-keycloak (Keycloak admin API)
- python-dotenv (environment variables)
- pydantic (configuration validation)

### 5. Install Playwright Browsers

**IMPORTANT**: This is a **separate step** and must be run manually:

```bash
playwright install chromium
```

For other browsers:
```bash
playwright install firefox
playwright install webkit
```

To install all browsers:
```bash
playwright install
```

**Note**: Browser installation is ~300MB per browser. Chromium is recommended for fastest tests.

## Configuration

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Edit `.env` File

Update the following values if different from defaults:

```env
# Railway URLs (should match your Railway deployment)
RAILWAY_API_URL=https://datakwip-api-dev.up.railway.app
RAILWAY_MCP_URL=https://datakwip-mcp-connector-dev.up.railway.app
RAILWAY_UI_URL=https://datakwip-ai-ui-dev.up.railway.app
RAILWAY_AUTH_URL=https://datakwip-ai.up.railway.app

# OAuth2 Client (must match Keycloak configuration)
FUNCTIONAL_TESTS_CLIENT_ID=functional-tests
FUNCTIONAL_TESTS_CLIENT_SECRET=functional-tests-secret-2025

# Test User (must exist in Keycloak)
FUNCTIONAL_TEST_USER_EMAIL=functional-test-user@datakwip.local
FUNCTIONAL_TEST_USER_PASSWORD=FunctionalTest2025!

# Keycloak Admin (for admin API tests)
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123
```

**Security Note**: Never commit `.env` to version control. It contains secrets.

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# API tests only
pytest -m api

# MCP tests only
pytest -m mcp

# UI tests only (requires Playwright browsers)
pytest -m ui

# Authentication tests only
pytest -m auth

# Integration tests only
pytest -m integration
```

### Run Specific Test File

```bash
pytest tests/test_api.py
pytest tests/test_mcp.py
pytest tests/test_ui.py
pytest tests/test_auth.py
pytest tests/test_integration.py
```

### Run Specific Test Function

```bash
pytest tests/test_api.py::test_database_health
pytest tests/test_integration.py::test_full_integration_suite
```

### Verbose Output

```bash
pytest -v
pytest -vv  # Extra verbose
```

### Show Print Statements

```bash
pytest -s
```

### Run Tests in Parallel

```bash
pip install pytest-xdist
pytest -n auto  # Use all CPU cores
```

### Skip Slow Tests

```bash
pytest -m "not slow"
```

### Run Only Integration Suite

```bash
pytest -m integration -v -s
```

This runs the comprehensive integration test that validates all components in sequence.

## Test Output

### Successful Test Run

```
========== test session starts ==========
platform win32 -- Python 3.11.0
collected 25 items

tests/test_api.py::test_database_health PASSED        [ 4%]
tests/test_api.py::test_list_entities PASSED          [ 8%]
tests/test_api.py::test_list_entity_tags PASSED       [12%]
...
tests/test_integration.py::test_full_integration_suite PASSED [100%]

========== 25 passed in 45.32s ==========
```

### Failed Test

```
tests/test_api.py::test_database_health FAILED

FAILED tests/test_api.py::test_database_health - httpx.ConnectError: Connection refused
```

### Integration Suite Output

```
================================================================================
DATAKWIP PLATFORM FUNCTIONAL TEST SUITE
================================================================================

[1/4] Testing Keycloak Authentication...
✓ Keycloak authentication tests passed (2.34s)

[2/4] Testing API Endpoints...
✓ API endpoint tests passed (1.87s)
  - Retrieved 10 entities
  - Retrieved 20 tags

[3/4] Testing MCP Tools...
✓ MCP tool tests passed (1.52s)
  - Available tools: 5
  - Retrieved 10 entities via MCP

[4/4] Testing UI Automation...
✓ UI automation tests passed (8.21s)
  - Login: ✓
  - Page title: DataKwip Admin
  - Data Explorer: Not available

================================================================================
TEST SUITE SUMMARY
================================================================================
✓ PASS   Keycloak Auth          2.34s
✓ PASS   API Endpoints          1.87s
✓ PASS   MCP Tools              1.52s
✓ PASS   UI Automation          8.21s
--------------------------------------------------------------------------------
Total execution time: 13.94s

🎉 ALL TESTS PASSED!
================================================================================
```

## Test Coverage

### API Tests (`tests/test_api.py`)

- ✅ Database health check (no auth required)
- ✅ Entity listing with OAuth2 authentication
- ✅ Entity tag listing with OAuth2 authentication
- ✅ OAuth2 token caching verification
- ✅ API stress test (10 rapid requests)

**Expected Response Times:**
- Database health: < 1s
- Entity list: < 500ms
- Tag list: < 800ms

### MCP Tests (`tests/test_mcp.py`)

- ✅ List available MCP tools
- ✅ query_entities tool
- ✅ get_current_values tool
- ✅ Query with filters
- ✅ MCP error handling
- ✅ Pagination with offset

**Expected Response Times:**
- Tool listing: < 1s
- Query entities: < 500ms
- Get current values: < 1s

### UI Tests (`tests/test_ui.py`)

- ✅ Login flow via Keycloak OAuth2
- ✅ Navigation to Data Explorer
- ✅ Query execution (if Data Explorer exists)
- ✅ Page title verification
- ✅ Invalid login rejection

**Expected Response Times:**
- Full login flow: < 10s
- Navigation: < 5s

### Auth Tests (`tests/test_auth.py`)

- ✅ Keycloak admin API connection
- ✅ Realm configuration verification
- ✅ functional-tests client existence and configuration
- ✅ Test user existence and status
- ✅ List all clients in realm
- ✅ List all users in realm

### Integration Tests (`tests/test_integration.py`)

- ✅ Full integration suite (all components)
- ✅ API/MCP data consistency
- ✅ End-to-end data flow (Database → API → MCP)

**Expected Total Time:**
- Complete integration suite: < 3 minutes

## Interpreting Results

### All Tests Pass

✅ **Platform is healthy**. All services are running and properly configured.

### Some Tests Fail

#### API Tests Fail

**Possible causes:**
- Railway API service is down
- OAuth2 configuration is incorrect
- Test user doesn't have required scopes
- Database connection issues

**Debug steps:**
1. Check Railway API logs: `railway logs -s datakwip-api`
2. Verify test user in Keycloak has scopes: `datakwip:entity:list`, `datakwip:entity:tag:list`
3. Test API manually: `curl https://datakwip-api-dev.up.railway.app/health/databases`

#### MCP Tests Fail

**Possible causes:**
- Railway MCP service is down
- MCP server not configured correctly
- Internal API calls failing

**Debug steps:**
1. Check Railway MCP logs: `railway logs -s datakwip-mcp-connector`
2. Test MCP manually: `curl https://datakwip-mcp-connector-dev.up.railway.app/health`
3. Verify MCP can reach API (check network configuration)

#### UI Tests Fail

**Possible causes:**
- Playwright browsers not installed
- UI service is down
- Login flow has changed
- Keycloak redirect configuration incorrect

**Debug steps:**
1. Install Playwright browsers: `playwright install chromium`
2. Run UI tests with screenshots: `pytest -m ui -s`
3. Check `screenshots/` directory for failure screenshots
4. Verify NEXTAUTH configuration in UI service

#### Auth Tests Fail

**Possible causes:**
- Keycloak service is down
- Admin credentials are incorrect
- Realm not imported correctly
- functional-tests client not created

**Debug steps:**
1. Check Railway auth service logs: `railway logs -s datakwip-auth-service`
2. Access Keycloak admin console: `https://datakwip-ai.up.railway.app`
3. Verify realm exists and is enabled
4. Verify functional-tests client exists with correct secret

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'playwright'`

**Solution**: Install dependencies:
```bash
pip install -e .
```

### Error: `playwright._impl._api_types.Error: Executable doesn't exist`

**Solution**: Install Playwright browsers:
```bash
playwright install chromium
```

### Error: `httpx.ConnectError: Connection refused`

**Solution**: Verify Railway services are running:
```bash
railway status
```

### Error: `MCPError: -32601: Method not found`

**Solution**: MCP server may not have the tool. Check available tools:
```python
from clients import DataKwipMCPClient
client = DataKwipMCPClient("https://datakwip-mcp-connector-dev.up.railway.app")
tools = client.list_tools()
print([t["name"] for t in tools])
```

### Error: `KeycloakConnectionError: Unable to connect to Keycloak`

**Solution**: Verify Keycloak URL and admin credentials:
```bash
curl https://datakwip-ai.up.railway.app/health
```

### Error: `UITestError: Login failed`

**Solution**:
1. Run with visible browser: Set `HEADLESS_BROWSER=false` in `.env`
2. Check screenshots in `screenshots/` directory
3. Verify test user credentials in Keycloak

### Tests Are Very Slow

**Solutions:**
- Use headless browser: `HEADLESS_BROWSER=true` in `.env`
- Skip UI tests: `pytest -m "not ui"`
- Skip slow tests: `pytest -m "not slow"`
- Run in parallel: `pytest -n auto` (requires pytest-xdist)

### Screenshot Not Saving

**Solution**: Enable screenshots in `.env`:
```env
SCREENSHOT_ON_FAILURE=true
```

## Development

### Adding New Tests

1. Create test file in `tests/` directory
2. Import fixtures from `conftest.py`
3. Mark tests with appropriate markers (@pytest.mark.api, @pytest.mark.mcp, etc.)
4. Use descriptive test names: `test_<feature>_<scenario>`

Example:
```python
import pytest

@pytest.mark.api
def test_new_endpoint(api_client, config):
    """Test description."""
    result = api_client.some_method()
    assert result is not None
```

### Adding New Fixtures

Edit `conftest.py`:
```python
@pytest.fixture(scope="session")
def my_fixture(config):
    """Fixture description."""
    # Setup
    resource = create_resource(config)
    yield resource
    # Teardown
    resource.close()
```

### Running Tests Locally

You can also test against local services by updating `.env`:

```env
RAILWAY_API_URL=http://localhost:8000
RAILWAY_MCP_URL=http://localhost:9090
RAILWAY_UI_URL=http://localhost:3000
RAILWAY_AUTH_URL=http://localhost:8081
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Functional Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e .
          playwright install chromium
      - name: Run tests
        env:
          RAILWAY_API_URL: ${{ secrets.RAILWAY_API_URL }}
          FUNCTIONAL_TESTS_CLIENT_SECRET: ${{ secrets.CLIENT_SECRET }}
        run: pytest -v
```

## Best Practices

1. **Always use .env file**: Never hardcode credentials
2. **Run integration suite before deployment**: Validates entire platform
3. **Check screenshots on UI failures**: Visual debugging is invaluable
4. **Use markers to organize tests**: Run subsets during development
5. **Keep tests idempotent**: Tests should not depend on order or state
6. **Use descriptive assertions**: Make failures easy to understand
7. **Update .env.example**: When adding new configuration

## Project Structure

```
datakwip-functional-tests/
├── clients/                    # API client implementations
│   ├── __init__.py
│   ├── api_client.py          # DataKwip API client (OAuth2)
│   ├── mcp_client.py          # MCP JSON-RPC 2.0 client
│   ├── ui_client.py           # Playwright automation client
│   └── auth_client.py         # Keycloak admin client
├── tests/                     # Test modules
│   ├── __init__.py
│   ├── test_api.py           # API endpoint tests
│   ├── test_mcp.py           # MCP tool tests
│   ├── test_ui.py            # UI automation tests
│   ├── test_auth.py          # Keycloak auth tests
│   └── test_integration.py   # Full integration suite
├── fixtures/                  # Test fixtures and helpers
│   └── __init__.py
├── screenshots/               # Playwright screenshots (on failure)
├── conftest.py               # Pytest configuration and fixtures
├── pyproject.toml            # Python dependencies and config
├── .env.example              # Environment variable template
├── .env                      # Local configuration (DO NOT COMMIT)
├── .gitignore               # Git ignore patterns
└── README.md                # This file
```

## Known Limitations

1. **Playwright Browser Installation**: Requires separate manual installation step (~300MB)
2. **Railway Services Must Be Running**: Tests will fail if any Railway service is down
3. **Test Data Dependency**: Tests assume simulator has seeded organization ID 1 with test data
4. **UI Test Fragility**: UI tests depend on DOM structure and may break with UI changes
5. **Network Latency**: Railway response times may vary; adjust timeouts in `.env` if needed

## Next Steps

After functional tests pass:

1. **GitHub Repository**: Main agent will create GitHub repository
2. **Keycloak Production Deployment**: Main agent will deploy Keycloak to Railway
3. **CI/CD Integration**: Add GitHub Actions workflow for automated testing
4. **Production Tests**: Create separate test suite for production environment
5. **Performance Testing**: Add load tests using locust or k6
6. **Monitoring**: Integrate test results with monitoring dashboard

## Support

For issues or questions:

1. Check Railway service logs
2. Review Keycloak configuration
3. Verify test user and client exist
4. Check screenshots for UI test failures
5. Run tests with `-v -s` for detailed output

## License

This test suite is part of the DataKwip platform project.

---

**Last Updated**: 2025-10-21
**Version**: 0.1.0
**Python**: 3.11+
**Pytest**: 8.0+
