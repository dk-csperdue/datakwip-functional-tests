"""MCP tool functional tests."""

import time
import pytest

from clients import DataKwipMCPClient, MCPError


@pytest.mark.mcp
def test_list_mcp_tools(mcp_client: DataKwipMCPClient):
    """Test listing available MCP tools."""
    start_time = time.time()
    tools = mcp_client.list_tools()
    duration = time.time() - start_time

    # Verify response structure
    assert isinstance(tools, list), "Tools response should be a list"
    assert len(tools) > 0, "Should have at least one tool"

    # Verify tool structure
    tool_names = [t.get("name") for t in tools]
    assert "query_entities" in tool_names, "Should have query_entities tool"
    assert "get_current_values" in tool_names, "Should have get_current_values tool"

    # Verify response time
    assert duration < 1.0, f"Tool listing should be < 1s, got {duration:.2f}s"

    print(f"✓ MCP tool listing passed ({duration*1000:.0f}ms)")
    print(f"  Available tools: {', '.join(tool_names)}")


@pytest.mark.mcp
def test_query_entities_mcp(mcp_client: DataKwipMCPClient, config):
    """Test query_entities MCP tool."""
    start_time = time.time()
    entities = mcp_client.query_entities(
        org_id=config.test_org_id,
        limit=config.test_entity_limit,
    )
    duration = time.time() - start_time

    # Verify response structure
    assert isinstance(entities, list), "Entities response should be a list"
    assert len(entities) <= config.test_entity_limit, "Should respect limit parameter"

    # Verify response time
    assert duration < 0.5, f"Query entities should be < 500ms, got {duration*1000:.0f}ms"

    # Verify entity structure (if data exists)
    if entities:
        entity = entities[0]
        assert "id" in entity or "key" in entity, "Entity should have id or key"

    print(f"✓ Query entities MCP tool passed ({duration*1000:.0f}ms)")
    print(f"  Retrieved {len(entities)} entities via MCP")
    if entities:
        print(f"  First entity: {entity.get('key', 'N/A')} - {entity.get('name', 'N/A')}")


@pytest.mark.mcp
def test_get_current_values_mcp(mcp_client: DataKwipMCPClient, config):
    """Test get_current_values MCP tool."""
    # First get some entities to query values for
    entities = mcp_client.query_entities(org_id=config.test_org_id, limit=3)

    if not entities:
        pytest.skip("No entities available for value query test")

    entity_ids = [e["id"] for e in entities if "id" in e][:3]

    if not entity_ids:
        pytest.skip("No entity IDs found for value query test")

    start_time = time.time()
    values = mcp_client.get_current_values(entity_ids=entity_ids, org_id=config.test_org_id)
    duration = time.time() - start_time

    # Verify response structure
    assert isinstance(values, list), "Values response should be a list"

    # Verify response time
    assert duration < 1.0, f"Get current values should be < 1s, got {duration:.2f}s"

    print(f"✓ Get current values MCP tool passed ({duration*1000:.0f}ms)")
    print(f"  Queried {len(entity_ids)} entities")
    print(f"  Retrieved {len(values)} current values")
    if values:
        print(f"  Sample value: entity_id={values[0].get('entity_id', 'N/A')}")


@pytest.mark.mcp
def test_mcp_query_with_filters(mcp_client: DataKwipMCPClient, config):
    """Test query_entities with filters."""
    start_time = time.time()
    entities = mcp_client.query_entities(
        org_id=config.test_org_id,
        limit=5,
        filters={"type": "AHU"},  # Example filter
    )
    duration = time.time() - start_time

    # Verify response (even if empty due to filter)
    assert isinstance(entities, list), "Filtered entities response should be a list"
    assert len(entities) <= 5, "Should respect limit parameter"

    print(f"✓ Query entities with filters passed ({duration*1000:.0f}ms)")
    print(f"  Retrieved {len(entities)} filtered entities")


@pytest.mark.mcp
def test_mcp_error_handling(mcp_client: DataKwipMCPClient):
    """Test MCP error handling with invalid parameters."""
    # Test with invalid org_id (should either error or return empty)
    try:
        entities = mcp_client.query_entities(org_id=99999, limit=10)
        # If no error, should at least return empty list
        assert isinstance(entities, list), "Should return list even for invalid org"
        print(f"✓ MCP error handling: Invalid org_id returned empty list")
    except MCPError as e:
        # If MCP returns error, that's also acceptable
        print(f"✓ MCP error handling: Invalid org_id raised MCPError({e.code})")
        assert e.code != 0, "Error code should be set"
    except Exception as e:
        pytest.fail(f"Unexpected error type: {type(e).__name__}: {e}")


@pytest.mark.mcp
@pytest.mark.slow
def test_mcp_pagination(mcp_client: DataKwipMCPClient, config):
    """Test MCP pagination with offset parameter."""
    # Get first page
    page1 = mcp_client.query_entities(org_id=config.test_org_id, limit=5, offset=0)

    # Get second page
    page2 = mcp_client.query_entities(org_id=config.test_org_id, limit=5, offset=5)

    # Verify both are lists
    assert isinstance(page1, list), "Page 1 should be a list"
    assert isinstance(page2, list), "Page 2 should be a list"

    # If we have data, verify pages are different
    if page1 and page2:
        page1_ids = [e.get("id") for e in page1]
        page2_ids = [e.get("id") for e in page2]

        # Pages should not have overlapping IDs
        overlap = set(page1_ids) & set(page2_ids)
        assert len(overlap) == 0, f"Pages should not overlap, but found {len(overlap)} common IDs"

    print(f"✓ MCP pagination test passed")
    print(f"  Page 1: {len(page1)} entities")
    print(f"  Page 2: {len(page2)} entities")
