import datetime
import json
import os
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account


SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
SERVICE_ACCOUNT_FILE = (
    "camposgoad-firebase-adminsdk-fbsvc-8c7ec329c9.json"
)


def notificar(device_token, title, body):
    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if service_account_json:
        service_account_info = json.loads(service_account_json)
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES
        )
        credentials_project_id = service_account_info.get("project_id")
    else:
        service_account_path = Path(__file__).parent / SERVICE_ACCOUNT_FILE
        if not service_account_path.is_file():
            raise RuntimeError(
                "Configura FIREBASE_SERVICE_ACCOUNT_JSON en Render o coloca "
                "el JSON de servicio en la carpeta firebase local."
            )
        credentials = service_account.Credentials.from_service_account_file(
            str(service_account_path),
            scopes=SCOPES
        )
        credentials_project_id = credentials.project_id

    project_id = os.getenv("FIREBASE_PROJECT_ID") or credentials_project_id
    if not project_id:
        raise RuntimeError(
            "No se pudo determinar el proyecto Firebase; configura "
            "FIREBASE_PROJECT_ID."
        )
    if credentials_project_id and project_id != credentials_project_id:
        raise RuntimeError(
            "FIREBASE_PROJECT_ID no coincide con el proyecto de las credenciales"
        )

    credentials.refresh(Request())
    fcm_url = (
        f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    )
    headers = {
        "Authorization": "Bearer " + credentials.token,
        "Content-Type": "application/json; UTF-8",
    }
    message = {
        "message": {
            "token": device_token,
            "notification": {
                "title": title,
                "body": body,
            },
            "data": {
                "timestamp": str(
                    datetime.datetime.now(datetime.timezone.utc)
                ),
                "key1": "valor1",
                "key2": "valor2",
            }
        }
    }

    response = requests.post(
        fcm_url,
        headers=headers,
        json=message,
        timeout=10
    )
    response.raise_for_status()
    return response.json()
