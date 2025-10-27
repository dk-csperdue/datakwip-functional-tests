# Keycloak Manual Setup Instructions

These instructions guide you through manually creating the `functional-tests` OAuth2 client and `functional-test-user` in Keycloak Admin Console.

## Prerequisites

- Keycloak admin credentials:
  - **Username**: `admin`
  - **Password**: `D@taKw!P@dm1nK3cl0@k` (from Railway)
- Keycloak URL: https://datakwip-ai.up.railway.app

---

## Part 1: Create OAuth2 Client (`functional-tests`)

### Step 1: Login to Keycloak Admin Console

1. Navigate to: **https://datakwip-ai.up.railway.app**
2. Click **Administration Console**
3. Login:
   - Username: `admin`
   - Password: `D@taKw!P@dm1nK3cl0@k`

### Step 2: Select Realm

1. In top-left dropdown, select realm: **datakwip** (if not already selected)

### Step 3: Create Client

1. In left sidebar, click **Clients**
2. Click **Create client** button (top-right)
3. **General Settings** tab:
   - Client type: **OpenID Connect**
   - Client ID: `functional-tests`
   - Name: `Functional Tests Client`
   - Description: `OAuth2 client for automated functional testing`
   - Click **Next**

4. **Capability config** tab:
   - ✅ Client authentication: **ON** (makes it confidential)
   - ✅ Authorization: **OFF**
   - Authentication flow:
     - ✅ Standard flow: **ON**
     - ✅ Direct access grants: **ON**
     - ✅ Service accounts roles: **ON**
     - ❌ Implicit flow: **OFF**
     - ❌ OAuth 2.0 Device Authorization Grant: **OFF**
     - ❌ OIDC CIBA Grant: **OFF**
   - Click **Next**

5. **Login settings** tab:
   - Root URL: *(leave empty)*
   - Home URL: *(leave empty)*
   - Valid redirect URIs:
     - `http://localhost:*`
     - `http://127.0.0.1:*`
   - Valid post logout redirect URIs: `+` (auto-inherit from redirect URIs)
   - Web origins:
     - `http://localhost`
     - `http://127.0.0.1`
   - Click **Save**

### Step 4: Set Client Secret

1. After saving, you'll be on the client details page
2. Click **Credentials** tab (top menu)
3. You'll see **Client secret** field
4. Click the **Regenerate** button
5. **IMPORTANT**: Set the secret to: `functional-tests-secret-2025`
   - *Note: Keycloak may not allow you to set a custom secret directly. If not:*
     - Copy the generated secret
     - Update your `.env` file with the generated secret instead
     - OR use the Keycloak REST API to set it (see Option B below)

Client Secret: CwYxoBl0GQnaGnbJAArMk88tNnWJ6cuB     

### Step 5: Configure Client Scopes

1. Click **Client scopes** tab (top menu)
2. Click **Add client scope** button (in "Assigned client scopes" section)
3. Search for and add each of these scopes (select "Default" for each):
   - `datakwip:access`
   - `datakwip:entity:list`
   - `datakwip:entity:read`
   - `datakwip:entity:search`
   - `datakwip:entity:tag:list`
   - `datakwip:entity:tag:read`
   - `datakwip:entitytag:list`
   - `datakwip:tag:list`
   - `datakwip:tag:read`
   - `datakwip:tagdef:list`
   - `datakwip:tagdef:read`
   - `datakwip:value:read`
   - `datakwip:value:read:historical`
   - `datakwip:value:aggregate`
   - `datakwip:value:analyze`
   - `datakwip:filter:execute`
   - `datakwip:export:execute`
   - `datakwip:system:health:read`

   *If any scope doesn't exist, skip it - the test may work without it*

### Step 6: Add Audience Mapper

1. Still in **Client scopes** tab
2. Click on the **functional-tests-dedicated** scope (in assigned scopes list)
3. Click **Add mapper** → **By configuration**
4. Select **Audience**
5. Configure:
   - Name: `datakwip-api-audience`
   - Included Client Audience: `datakwip-api`
   - Add to ID token: **ON**
   - Add to access token: **ON**
6. Click **Save**

### Step 7: Verify Client Configuration

1. Go back to **Settings** tab
2. Verify these settings:
   - Access Type: **confidential** ✅
   - Standard Flow Enabled: **ON** ✅
   - Direct Access Grants Enabled: **ON** ✅
   - Service Accounts Enabled: **ON** ✅

---

## Part 2: Create Test User (`functional-test-user`)

### Step 1: Create User

1. In left sidebar, click **Users**
2. Click **Add user** button (top-right)
3. **Create user** form:
   - Username: `functional-test-user@datakwip.local`
   - Email: `functional-test-user@datakwip.local`
   - Email verified: **ON** ✅
   - First name: `Functional`
   - Last name: `Test User`
   - Enabled: **ON** ✅
4. Click **Create**

### Step 2: Set Password

1. After creation, click **Credentials** tab
2. Click **Set password** button
3. Set password form:
   - Password: `FunctionalTest2025!`
   - Password confirmation: `FunctionalTest2025!`
   - Temporary: **OFF** ❌ (important!)
4. Click **Save**
5. Confirm by clicking **Save password** in the dialog

### Step 3: Assign Roles

1. Click **Role mapping** tab
2. Click **Assign role** button
3. Filter dropdown: Select **Filter by clients**
4. Search for and add these roles:
   - `analyst` (from datakwip-api client)
   - `user` (from datakwip-api client)
   - `offline_access` (from realm roles)
5. Click **Assign**

### Step 4: Verify User

1. Go back to **Details** tab
2. Verify:
   - Username: `functional-test-user@datakwip.local` ✅
   - Email verified: **ON** ✅
   - Enabled: **ON** ✅

---

## Part 3: Test Configuration

### Test OAuth2 Password Grant Flow

Open a terminal and run this curl command:

```bash
curl -X POST "https://datakwip-ai.up.railway.app/realms/datakwip/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=functional-tests" \
  -d "client_secret=functional-tests-secret-2025" \
  -d "grant_type=password" \
  -d "username=functional-test-user@datakwip.local" \
  -d "password=FunctionalTest2025!" \
  -d "scope=openid email profile datakwip:access"
```

**Expected Result**: JSON response with `access_token`, `refresh_token`, and `expires_in` fields.

**Example successful response**:
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI...",
  "expires_in": 300,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
  "token_type": "Bearer",
  "not-before-policy": 0,
  "session_state": "...",
  "scope": "openid email profile datakwip:access"
}
```

**If you get an error**:
- `invalid_client`: Client not found or secret is wrong
- `invalid_grant`: Username/password incorrect
- `invalid_scope`: Scope not assigned to client

---

## Part 4: Update Functional Tests .env File

After successful test, create `.env` file in the functional-tests directory:

```bash
cd C:\Users\csper\datakwip-projects\datakwip-platform\datakwip-functional-tests
cp .env.example .env
```

Edit `.env` and update these values:

```env
# Railway Service URLs
RAILWAY_API_URL=https://datakwip-api-dev.up.railway.app
RAILWAY_MCP_URL=https://datakwip-mcp-connector-dev.up.railway.app
RAILWAY_UI_URL=https://datakwip-ai-ui-dev.up.railway.app
RAILWAY_AUTH_URL=https://datakwip-ai.up.railway.app

# Keycloak OAuth2 Configuration
KEYCLOAK_BASE_URL=https://datakwip-ai.up.railway.app
KEYCLOAK_REALM=datakwip
OAUTH2_ISSUER_URL=https://datakwip-ai.up.railway.app/realms/datakwip
OAUTH2_TOKEN_URL=https://datakwip-ai.up.railway.app/realms/datakwip/protocol/openid-connect/token
OAUTH2_AUTH_URL=https://datakwip-ai.up.railway.app/realms/datakwip/protocol/openid-connect/auth
OAUTH2_JWKS_URL=https://datakwip-ai.up.railway.app/realms/datakwip/protocol/openid-connect/certs

# Functional Test User Credentials
FUNCTIONAL_TEST_USER_EMAIL=functional-test-user@datakwip.local
FUNCTIONAL_TEST_USER_PASSWORD=FunctionalTest2025!

# Functional Test OAuth2 Client
FUNCTIONAL_TESTS_CLIENT_ID=functional-tests
FUNCTIONAL_TESTS_CLIENT_SECRET=functional-tests-secret-2025
# ☝️ UPDATE THIS if Keycloak generated a different secret

# Keycloak Admin Credentials
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=D@taKw!P@dm1nK3cl0@k

# Organization ID for testing (simulator creates org_id=1)
TEST_ORG_ID=1
```

---

## Option B: Set Custom Client Secret via API (Advanced)

If Keycloak doesn't allow you to set a custom secret in the UI, use this method:

### Step 1: Get Admin Access Token

```bash
curl -X POST "https://datakwip-ai.up.railway.app/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=admin-cli" \
  -d "username=admin" \
  -d "password=D@taKw!P@dm1nK3cl0@k" \
  -d "grant_type=password"
```

Copy the `access_token` from the response.

### Step 2: Get Client UUID

```bash
curl -X GET "https://datakwip-ai.up.railway.app/admin/realms/datakwip/clients?clientId=functional-tests" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Copy the `id` field (UUID) from the response.

### Step 3: Set Client Secret

```bash
curl -X POST "https://datakwip-ai.up.railway.app/admin/realms/datakwip/clients/CLIENT_UUID/client-secret" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type": "secret", "value": "functional-tests-secret-2025"}'
```

Replace `CLIENT_UUID` with the ID from step 2.

---

## Next Steps

After completing this setup:

1. ✅ Verify OAuth2 token test passes (Part 3)
2. ✅ Update `.env` file (Part 4)
3. ✅ Run functional tests:

```bash
cd C:\Users\csper\datakwip-projects\datakwip-platform\datakwip-functional-tests

# Install dependencies if not done
pip install -e .

# Install Playwright browsers
playwright install chromium

# Run tests
pytest -m integration -v -s
```

---

## Troubleshooting

### Problem: Can't login to Keycloak admin console

**Solution**: Verify password from Railway:
```bash
cd C:\Users\csper\datakwip-projects\datakwip-platform\datakwip-auth-service
railway variables | findstr KEYCLOAK_ADMIN
```

### Problem: Client scopes not available

**Solution**: The datakwip realm may not have all custom scopes created yet. Contact the auth-service team to create missing scopes.

### Problem: User can't login (invalid_grant)

**Solution**:
- Verify password was set correctly (case-sensitive)
- Check "Temporary" is OFF
- Verify user is Enabled

### Problem: Token missing scopes

**Solution**:
- Go to Client → Client scopes
- Ensure scopes are in "Assigned default client scopes" (not optional)
- Ensure audience mapper includes `datakwip-api`

---

## Summary Checklist

- [ ] Created `functional-tests` client
- [ ] Set client secret to `functional-tests-secret-2025`
- [ ] Enabled Direct Access Grants and Service Accounts
- [ ] Added all datakwip scopes to client
- [ ] Added audience mapper for datakwip-api
- [ ] Created `functional-test-user@datakwip.local` user
- [ ] Set password to `FunctionalTest2025!` (temporary: OFF)
- [ ] Assigned analyst and user roles
- [ ] Tested OAuth2 token endpoint successfully
- [ ] Created `.env` file in functional-tests directory
- [ ] Ready to run functional tests!
