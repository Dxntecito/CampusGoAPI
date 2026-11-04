import requests
import json
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import os
import datetime


def notificar(device_token, title, body):

    # Ruta al JSON de la cuenta de servicio local
    SERVICE_ACCOUNT_FILE = (
        "camposgoad-firebase-adminsdk-fbsvc-8c7ec329c9.json"
    )

    # Construir la ruta absoluta al archivo JSON
    service_account_path = os.path.join(
        os.path.dirname(__file__),
        SERVICE_ACCOUNT_FILE
    )

    # Verificar si el archivo existe en la ruta especificada
    if not os.path.isfile(service_account_path):
        raise FileNotFoundError(
            f"El archivo {service_account_path} no se encuentra. "
            "Verifica la ruta."
        )

    # Definir el scope para la API de FCM
    SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

    # Autenticación y obtención del token de acceso
    credentials = service_account.Credentials.from_service_account_file(
        service_account_path,
        scopes=SCOPES
    )
    credentials.refresh(Request())

    # URL de la API FCM V1 del proyecto CamposGOAD
    FCM_URL = (
        "https://fcm.googleapis.com/v1/projects/camposgoad/messages:send"
    )

    # Encabezados de la solicitud
    headers = {
        "Authorization": "Bearer " + credentials.token,
        "Content-Type": "application/json; UTF-8",
    }

    # Datos del mensaje
    message = {
        "message": {
            "token": device_token,
            "notification": {
                "title": title,
                "body": body,
            },
            "data": {
                "timestamp": str(datetime.datetime.utcnow()),
                "key1": "valor1",
                "key2": "valor2",
            }
        }
    }

    # Enviar la solicitud POST a la API de FCM
    response = requests.post(
        FCM_URL,
        headers=headers,
        data=json.dumps(message),
        timeout=10
    )

    # Mostrar errores de FCM explícitamente
    response.raise_for_status()
    return response.json()
