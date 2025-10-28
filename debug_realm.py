from clients import KeycloakAdminClient
from dotenv import load_dotenv
import os

load_dotenv()

client = KeycloakAdminClient(
    server_url='https://datakwip-ai.up.railway.app',
    realm_name='datakwip',
    admin_username='admin',
    admin_password=os.getenv('KEYCLOAK_ADMIN_PASSWORD'),
    verify=False
)

client.connect()

print(f"Target realm_name: {client.realm_name}")

# Try getting clients
clients = client._admin.get_clients()
print(f"\nFound {len(clients)} clients")
print("First 10 clients:")
for c in clients[:10]:
    print(f"  - {c.get('clientId')}")

# Search for functional-tests
functional_test_client = [c for c in clients if c.get('clientId') == 'functional-tests']
if functional_test_client:
    print("\n✓ FOUND functional-tests client!")
else:
    print("\n✗ functional-tests client NOT FOUND")

# Try getting users
users = client._admin.get_users({"max": 10})
print(f"\nFound {len(users)} users")
for u in users[:10]:
    print(f"  - {u.get('username')} <{u.get('email', 'N/A')}>")

# Search for functional test user
test_user = [u for u in users if u.get('email') == 'functional-test-user@datakwip.local']
if test_user:
    print("\n✓ FOUND functional-test-user@datakwip.local!")
else:
    print("\n✗ functional-test-user@datakwip.local NOT FOUND")
