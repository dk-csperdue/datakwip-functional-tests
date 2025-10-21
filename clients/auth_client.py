"""Keycloak admin client for authentication tests."""

from typing import Any, Dict, List, Optional

from keycloak import KeycloakAdmin, KeycloakOpenIDConnection


class KeycloakAdminClient:
    """Client for Keycloak admin console operations."""

    def __init__(
        self,
        server_url: str,
        realm_name: str,
        admin_username: str,
        admin_password: str,
        verify: bool = True,
    ):
        """Initialize Keycloak admin client.

        Args:
            server_url: Keycloak server URL (e.g., https://auth.example.com)
            realm_name: Realm name (e.g., 'datakwip')
            admin_username: Admin username
            admin_password: Admin password
            verify: Verify SSL certificates
        """
        self.server_url = server_url.rstrip("/")
        self.realm_name = realm_name
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.verify = verify

        self._admin: Optional[KeycloakAdmin] = None

    def connect(self):
        """Connect to Keycloak admin API."""
        # Create connection
        connection = KeycloakOpenIDConnection(
            server_url=self.server_url,
            realm_name="master",  # Admin login uses master realm
            username=self.admin_username,
            password=self.admin_password,
            verify=self.verify,
        )

        # Create admin client
        self._admin = KeycloakAdmin(connection=connection)

        # Switch to target realm
        self._admin.realm_name = self.realm_name

    def verify_connection(self) -> bool:
        """Verify admin connection is working.

        Returns:
            True if connection successful

        Raises:
            Exception: On connection failure
        """
        if not self._admin:
            raise RuntimeError("Not connected. Call connect() first.")

        # Try to get realm info
        realm_info = self._admin.get_realm(self.realm_name)

        return realm_info is not None and realm_info.get("realm") == self.realm_name

    def get_realm_info(self) -> Dict[str, Any]:
        """Get realm information.

        Returns:
            Realm configuration

        Example:
            {
                "realm": "datakwip",
                "enabled": true,
                "displayName": "DataKwip",
                ...
            }
        """
        if not self._admin:
            raise RuntimeError("Not connected. Call connect() first.")

        return self._admin.get_realm(self.realm_name)

    def list_clients(self) -> List[Dict[str, Any]]:
        """List all clients in realm.

        Returns:
            List of client configurations

        Example:
            [
                {
                    "clientId": "functional-tests",
                    "enabled": true,
                    "publicClient": false,
                    ...
                }
            ]
        """
        if not self._admin:
            raise RuntimeError("Not connected. Call connect() first.")

        return self._admin.get_clients()

    def get_client_by_client_id(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client configuration by client ID.

        Args:
            client_id: Client ID (e.g., 'functional-tests')

        Returns:
            Client configuration or None if not found
        """
        if not self._admin:
            raise RuntimeError("Not connected. Call connect() first.")

        clients = self._admin.get_clients()
        for client in clients:
            if client.get("clientId") == client_id:
                return client

        return None

    def verify_client_exists(self, client_id: str) -> bool:
        """Verify that a client exists.

        Args:
            client_id: Client ID to check

        Returns:
            True if client exists
        """
        return self.get_client_by_client_id(client_id) is not None

    def list_users(self, max_users: int = 100) -> List[Dict[str, Any]]:
        """List users in realm.

        Args:
            max_users: Maximum number of users to return

        Returns:
            List of user objects

        Example:
            [
                {
                    "id": "user-uuid",
                    "username": "testuser",
                    "email": "test@example.com",
                    "enabled": true,
                    ...
                }
            ]
        """
        if not self._admin:
            raise RuntimeError("Not connected. Call connect() first.")

        return self._admin.get_users({"max": max_users})

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username.

        Args:
            username: Username or email to search for

        Returns:
            User object or None if not found
        """
        if not self._admin:
            raise RuntimeError("Not connected. Call connect() first.")

        users = self._admin.get_users({"username": username, "exact": True})

        return users[0] if users else None

    def verify_user_exists(self, username: str) -> bool:
        """Verify that a user exists.

        Args:
            username: Username or email to check

        Returns:
            True if user exists
        """
        return self.get_user_by_username(username) is not None

    def close(self):
        """Close admin connection."""
        # python-keycloak doesn't require explicit close
        self._admin = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
