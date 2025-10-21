"""API endpoint functional tests."""

import time
import pytest

from clients import DataKwipAPIClient


@pytest.mark.api
def test_database_health(api_client: DataKwipAPIClient):
    """Test database health endpoint (no auth required)."""
    start_time = time.time()
    health = api_client.get_database_health()
    duration = time.time() - start_time

    # Verify response structure
    assert isinstance(health, dict), "Health response should be a dictionary"
    assert "timescaledb" in health or "status" in health, "Health should include database status"

    # Verify response time
    assert duration < 1.0, f"Database health check should be < 1s, got {duration:.2f}s"

    print(f"✓ Database health check passed ({duration*1000:.0f}ms)")
    print(f"  Response: {health}")


@pytest.mark.api
def test_list_entities(api_client: DataKwipAPIClient, config):
    """Test entity listing endpoint (requires datakwip:entity:list scope)."""
    start_time = time.time()
    entities = api_client.list_entities(org_id=config.test_org_id, limit=config.test_entity_limit)
    duration = time.time() - start_time

    # Verify response structure
    assert isinstance(entities, list), "Entities response should be a list"
    assert len(entities) <= config.test_entity_limit, "Should respect limit parameter"

    # Verify response time
    assert duration < 0.5, f"Entity list should be < 500ms, got {duration*1000:.0f}ms"

    # Verify entity structure (if data exists)
    if entities:
        entity = entities[0]
        assert "id" in entity, "Entity should have id"
        assert "org_id" in entity, "Entity should have org_id"
        assert entity["org_id"] == config.test_org_id, "Entity org_id should match request"

    print(f"✓ Entity listing passed ({duration*1000:.0f}ms)")
    print(f"  Retrieved {len(entities)} entities")
    if entities:
        print(f"  First entity: {entities[0].get('key', 'N/A')} - {entities[0].get('name', 'N/A')}")


@pytest.mark.api
def test_list_entity_tags(api_client: DataKwipAPIClient, config):
    """Test entity tag listing endpoint (requires datakwip:entity:tag:list scope)."""
    start_time = time.time()
    tags = api_client.list_entity_tags(org_id=config.test_org_id, limit=config.test_tag_limit)
    duration = time.time() - start_time

    # Verify response structure
    assert isinstance(tags, list), "Tags response should be a list"
    assert len(tags) <= config.test_tag_limit, "Should respect limit parameter"

    # Verify response time
    assert duration < 0.8, f"Tag list should be < 800ms, got {duration*1000:.0f}ms"

    # Verify tag structure (if data exists)
    if tags:
        tag = tags[0]
        assert "id" in tag or "tag_key" in tag, "Tag should have id or tag_key"
        assert "entity_id" in tag, "Tag should have entity_id"

    print(f"✓ Entity tag listing passed ({duration*1000:.0f}ms)")
    print(f"  Retrieved {len(tags)} tags")
    if tags:
        print(f"  First tag: {tag.get('tag_key', 'N/A')} = {tag.get('tag_value', 'N/A')}")


@pytest.mark.api
def test_oauth2_token_caching(api_client: DataKwipAPIClient):
    """Test that OAuth2 tokens are cached properly."""
    # First request - fetches token
    start1 = time.time()
    entities1 = api_client.list_entities(org_id=1, limit=1)
    duration1 = time.time() - start1

    # Second request - uses cached token
    start2 = time.time()
    entities2 = api_client.list_entities(org_id=1, limit=1)
    duration2 = time.time() - start2

    # Second request should be faster (no token fetch)
    # Allow some variance, but should be noticeably faster
    assert duration2 < duration1 * 0.8 or duration2 < 0.3, \
        f"Cached request should be faster: {duration1:.3f}s vs {duration2:.3f}s"

    print(f"✓ Token caching works")
    print(f"  First request: {duration1*1000:.0f}ms (with token fetch)")
    print(f"  Second request: {duration2*1000:.0f}ms (cached token)")


@pytest.mark.api
@pytest.mark.slow
def test_api_stress(api_client: DataKwipAPIClient, config):
    """Stress test: Make multiple API calls rapidly."""
    num_requests = 10
    results = []

    start_time = time.time()
    for i in range(num_requests):
        request_start = time.time()
        entities = api_client.list_entities(org_id=config.test_org_id, limit=5)
        request_duration = time.time() - request_start
        results.append(request_duration)

    total_duration = time.time() - start_time

    # Calculate stats
    avg_duration = sum(results) / len(results)
    max_duration = max(results)
    min_duration = min(results)

    # All requests should succeed
    assert len(results) == num_requests, "All requests should succeed"

    # Average should be reasonable
    assert avg_duration < 1.0, f"Average request time should be < 1s, got {avg_duration:.2f}s"

    print(f"✓ API stress test passed")
    print(f"  {num_requests} requests in {total_duration:.2f}s")
    print(f"  Avg: {avg_duration*1000:.0f}ms, Min: {min_duration*1000:.0f}ms, Max: {max_duration*1000:.0f}ms")
