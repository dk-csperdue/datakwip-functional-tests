# OAuth2 Troubleshooting Checklist

**Current Error**: `unauthorized_client - Invalid client or Invalid client credentials`

## Quick Checklist

### 1. Verify Client Configuration in Keycloak

Go to: https://datakwip-ai.up.railway.app → Admin Console → Clients → functional-tests

#### Settings Tab:
- [ ] **Client authentication**: ON (confidential client)
- [ ] **Authorization**: OFF
- [ ] **Standard flow**: ON
- [ ] **Direct access grants**: ON ⚠️ **CRITICAL!**
- [ ] **Implicit flow**: OFF
- [ ] **Service accounts roles**: ON

**If "Direct access grants" is OFF, this is your problem!**

#### Credentials Tab:
- [ ] Client secret matches what's in `.env` file
- [ ] No extra spaces before/after the secret

### 2. Verify Client Secret

**Copy the secret from Keycloak again**:
1. Go to Credentials tab
2. Click the eye icon to show the secret
3. Copy it carefully (no extra spaces!)
4. Paste it into `.env` file

**Current secret in .env**: `abc123xyz789wYxoBl0GQnaGnbJAArMk88tNnWJ6cuB`

Does this exactly match what's in Keycloak?

### 3. Test with Client Credentials Flow First

If Direct Access Grants is causing issues, try the simpler client credentials flow:

```bash
curl -X POST "https://datakwip-ai.up.railway.app/realms/datakwip/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=functional-tests" \
  -d "client_secret=abc123xyz789wYxoBl0GQnaGnbJAArMk88tNnWJ6cuB"
```

**If this works**: Client secret is correct, but Direct Access Grants might be disabled
**If this fails**: Client secret is wrong or client doesn't exist

### 4. Verify User Credentials

Go to: Keycloak → Users → functional-test-user@datakwip.local

- [ ] User exists
- [ ] User is **Enabled**
- [ ] Email verified: ON
- [ ] Password is set (Credentials tab)
- [ ] Password temporary: OFF

### 5. Common Keycloak Issues

#### Issue: "Direct Access Grants" not enabled

**Solution**:
1. Clients → functional-tests → Settings
2. Scroll to "Capability config" section
3. Turn ON "Direct access grants enabled"
4. Click Save
5. Try authentication again

#### Issue: Client secret has spaces

**Solution**:
1. Regenerate the secret in Keycloak
2. Copy it carefully
3. Update `.env` file
4. No quotes, no spaces

#### Issue: Wrong Grant Type

The password grant flow requires these Keycloak settings:
- Client authentication: ON
- Direct access grants: ON

### 6. Alternative: Use Standard Flow Instead

If Direct Access Grants keeps failing, modify the test to use authorization code flow instead (more complex but more standard).

## Next Steps

1. Check "Direct access grants" in Keycloak ⚠️
2. Verify client secret matches exactly
3. Test with client credentials flow first
4. Then try password grant flow again

## Need More Help?

Check Railway logs for Keycloak errors:
```bash
cd C:\Users\csper\datakwip-projects\datakwip-platform\datakwip-auth-service
railway logs --service datakwip-auth-service --tail 50
```

Look for:
- LOGIN_ERROR events
- invalid_client_credentials
- Client not found errors
