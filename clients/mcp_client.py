"""DataKwip MCP client with JSON-RPC 2.0 support."""

import json
from typing import Any, Dict, List, Optional

import httpx


class MCPError(Exception):
    """MCP protocol error."""

    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"MCP Error {code}: {message}")


class DataKwipMCPClient:
    """Client for DataKwip MCP server using JSON-RPC 2.0."""

    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize MCP client.

        Args:
            base_url: Base URL of MCP server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)
        self._request_id = 0

    def _get_next_id(self) -> int:
        """Get next JSON-RPC request ID."""
        self._request_id += 1
        return self._request_id

    def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call MCP tool using JSON-RPC 2.0.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result

        Raises:
            MCPError: On MCP protocol error
            httpx.HTTPStatusError: On HTTP error
        """
        request_payload = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        response = self._client.post(
            f"{self.base_url}/mcp",
            json=request_payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()

        result = response.json()

        # Check for JSON-RPC error
        if "error" in result:
            error = result["error"]
            raise MCPError(
                code=error.get("code", -1),
                message=error.get("message", "Unknown error"),
                data=error.get("data"),
            )

        return result.get("result")

    def query_entities(
        self,
        org_id: int = 1,
        limit: int = 10,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Query entities via MCP.

        Args:
            org_id: Organization ID (default: 1)
            limit: Maximum number of entities to return
            offset: Offset for pagination
            filters: Optional filters (e.g., {"type": "AHU"})

        Returns:
            List of entity objects

        Example:
            [
                {
                    "id": 1,
                    "org_id": 1,
                    "key": "building-1",
                    "name": "Building 1",
                    ...
                }
            ]
        """
        arguments = {
            "org_id": org_id,
            "limit": limit,
            "offset": offset,
        }

        if filters:
            arguments["filters"] = filters

        result = self._call_tool("query_entities", arguments)

        # MCP result format: {"content": [{"type": "text", "text": "<json>"}]}
        if isinstance(result, dict) and "content" in result:
            content = result["content"]
            if isinstance(content, list) and len(content) > 0:
                text_content = content[0].get("text", "[]")
                return json.loads(text_content)

        # Fallback: assume result is already the data
        return result if isinstance(result, list) else []

    def get_current_values(
        self, entity_ids: List[int], org_id: int = 1
    ) -> List[Dict[str, Any]]:
        """Get current time-series values for entities.

        Args:
            entity_ids: List of entity IDs
            org_id: Organization ID (default: 1)

        Returns:
            List of current value objects

        Example:
            [
                {
                    "entity_id": 1,
                    "timestamp": "2025-10-21T12:00:00Z",
                    "value": 72.5,
                    "unit": "°F"
                }
            ]
        """
        arguments = {
            "entity_ids": entity_ids,
            "org_id": org_id,
        }

        result = self._call_tool("get_current_values", arguments)

        # MCP result format: {"content": [{"type": "text", "text": "<json>"}]}
        if isinstance(result, dict) and "content" in result:
            content = result["content"]
            if isinstance(content, list) and len(content) > 0:
                text_content = content[0].get("text", "[]")
                return json.loads(text_content)

        # Fallback: assume result is already the data
        return result if isinstance(result, list) else []

    def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools.

        Returns:
            List of tool definitions

        Example:
            [
                {
                    "name": "query_entities",
                    "description": "Query entities from DataKwip",
                    "inputSchema": {...}
                }
            ]
        """
        request_payload = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/list",
        }

        response = self._client.post(
            f"{self.base_url}/mcp",
            json=request_payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()

        result = response.json()

        if "error" in result:
            error = result["error"]
            raise MCPError(
                code=error.get("code", -1),
                message=error.get("message", "Unknown error"),
                data=error.get("data"),
            )

        return result.get("result", {}).get("tools", [])

    def close(self):
        """Close HTTP client."""
        self._client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
