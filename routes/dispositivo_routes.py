from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from services.dispositivo_service import DispositivoService
from utils.response import error_response, success_response


dispositivo_bp = Blueprint("dispositivos", __name__)


@dispositivo_bp.route("/api/dispositivo", methods=["PUT"])
@jwt_required()
def actualizar_dispositivo():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return error_response("Debe enviar los datos en formato JSON", 400)

    data, message, http_code = DispositivoService().actualizar(
        get_jwt_identity(),
        datos
    )
    if data is None:
        return error_response(message, http_code)

    return success_response(data, message, http_code)
