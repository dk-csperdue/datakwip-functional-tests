import requests
import os
from dotenv import load_dotenv

load_dotenv()
admin_pwd = os.getenv('KEYCLOAK_ADMIN_PASSWORD')

token_url = 'https://datakwip-ai.up.railway.app/realms/master/protocol/openid-connect/token'
token_data = {
    'grant_type': 'password',
    'client_id': 'admin-cli',
    'username': 'admin',
    'password': admin_pwd
}

response = requests.post(token_url, data=token_data, verify=False)
token = response.json()['access_token']

headers = {'Authorization': 'Bearer ' + token}
users_url = 'https://datakwip-ai.up.railway.app/admin/realms/datakwip/users'
users_response = requests.get(users_url, headers=headers, verify=False)

users = users_response.json()
for user in users:
    username = user.get('username', '')
    email = user.get('email', '')
    if 'functional-test-user' in username.lower() or 'functional-test-user' in email.lower():
        print('Username:', username)
        print('Email:', email)
        print('ID:', user.get('id'))
        print('Enabled:', user.get('enabled'))
