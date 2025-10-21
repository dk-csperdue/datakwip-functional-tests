"""DataKwip API client with OAuth2 authentication."""

import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import httpx
from pydantic import BaseModel


class TokenCache(BaseModel):
    """OAuth2 token cache."""

    access_token: str
    expires_at: datetime
    token_type: str = "Bearer"

    def is_expired(self) -> bool:
        """Check if token is expired (with 30 second buffer)."""
        return datetime.now() >= (self.expires_at - timedelta(seconds=30))


class DataKwipAPIClient:
    """Client for DataKwip API with OAuth2 password grant authentication."""

    def __init__(
        self,
        base_url: str,
        token_url: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        timeout: int = 30,
    ):
        """Initialize API client.

        Args:
            base_url: Base URL of DataKwip API
            token_url: OAuth2 token endpoint URL
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            username: User email/username
            password: User password
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.timeout = timeout
        self._token_cache: Optional[TokenCache] = None
        self._client = httpx.Client(timeout=timeout)

    def _get_access_token(self) -> str:
        """Get valid access token (cached or fetch new)."""
        if self._token_cache and not self._token_cache.is_expired():
            return self._token_cache.access_token

        # Fetch new token using password grant
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
            "scope": "openid profile email datakwip:entity:list datakwip:entity:tag:list",
        }

        response = self._client.post(self.token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        expires_in = token_data.get("expires_in", 300)
        expires_at = datetime.now() + timedelta(seconds=expires_in)

        self._token_cache = TokenCache(
            access_token=token_data["access_token"],
            expires_at=expires_at,
            token_type=token_data.get("token_type", "Bearer"),
        )

        return self._token_cache.access_token

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
    ) -> httpx.Response:
        """Make authenticated API request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/entity')
            params: Query parameters
            json: JSON request body
            require_auth: Whether to include authentication header

        Returns:
            httpx.Response object

        Raises:
            httpx.HTTPStatusError: On HTTP error status
        """
        url = f"{self.base_url}{endpoint}"
        headers = {}

        if require_auth:
            access_token = self._get_access_token()
            headers["Authorization"] = f"Bearer {access_token}"

        response = self._client.request(
            method=method, url=url, params=params, json=json, headers=headers
        )
        response.raise_for_status()
        return response

    def get_database_health(self) -> Dict[str, Any]:
        """Get database health status.

        Returns:
            Database health information

        Example:
            {
                "timescaledb": {"status": "healthy", "latency_ms": 12},
                "statedb": {"status": "healthy", "latency_ms": 8}
            }
        """
        response = self._request("GET", "/health/databases", require_auth=False)
        return response.json()

    def list_entities(self, org_id: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """List entities from TimescaleDB.

        Args:
            org_id: Organization ID (default: 1)
            limit: Maximum number of entities to return

        Returns:
            List of entity objects

        Example:
            [
                {
                    "id": 1,
                    "org_id": 1,
                    "org_key": "test-org",
                    "key": "building-1",
                    "name": "Building 1",
                    ...
                }
            ]
        """
        params = {"org_id": org_id, "limit": limit}
        response = self._request("GET", "/entity", params=params)
        return response.json()

    def list_entity_tags(self, org_id: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """List entity tags (EAV model).

        Args:
            org_id: Organization ID (default: 1)
            limit: Maximum number of tags to return

        Returns:
            List of entity tag objects

        Example:
            [
                {
                    "id": 1,
                    "entity_id": 1,
                    "tag_key": "type",
                    "tag_value": "AHU",
                    ...
                }
            ]
        """
        params = {"org_id": org_id, "limit": limit}
        response = self._request("GET", "/entitytag", params=params)
        return response.json()

    def close(self):
        """Close HTTP client."""
        self._client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
