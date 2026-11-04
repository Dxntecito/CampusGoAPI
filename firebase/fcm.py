import json
import os

import google.auth
import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account


SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def notificar(device_token, title, body):
    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    project_id = os.getenv("FIREBASE_PROJECT_ID")

    if service_account_json:
        service_account_info = json.loads(service_account_json)
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES
        )
        project_id = project_id or service_account_info.get("project_id")
    else:
        credentials, default_project_id = google.auth.default(scopes=SCOPES)
        project_id = project_id or default_project_id

    if not project_id:
        raise RuntimeError(
            "Configura FIREBASE_PROJECT_ID o las credenciales de Firebase"
        )

    credentials.refresh(Request())
    response = requests.post(
        f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send",
        headers={
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json; UTF-8",
        },
        json={
            "message": {
                "token": device_token,
                "notification": {
                    "title": title,
                    "body": body,
                },
            }
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
