
import os
import sys
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google.auth import exceptions as auth_exceptions
import google.auth
import google.auth.transport.requests
import json
import base64

def _get_id_token(target_audience: str) -> str:
    try:
        credentials, project = google.auth.default()
        if hasattr(credentials, "refresh"):
            auth_req = google.auth.transport.requests.Request()
            credentials.refresh(auth_req)
            if hasattr(credentials, "id_token"):
                return str(credentials.id_token)
        token = id_token.fetch_id_token(Request(), target_audience)
        return str(token) if token else ""
    except Exception as e:
        print(f"Error: {e}")
        return ""

def decode_token(token):
    _, payload_b64, _ = token.split('.')
    payload_b64 += '=' * (-len(payload_b64) % 4)
    payload_json = base64.b64decode(payload_b64).decode('utf-8')
    return json.loads(payload_json)

URL = "https://benchhub-orchestrator-byngbk6kwa-uc.a.run.app"
token = _get_id_token(URL)
if not token:
    print("No token fetched.")
    sys.exit(1)

print("Token fetched successfully.")
decoded = decode_token(token)
print(f"Issuer: {decoded.get('iss')}")
print(f"Audience: {decoded.get('aud')}")
print(f"Email: {decoded.get('email')}")
print(f"Sub: {decoded.get('sub')}")
