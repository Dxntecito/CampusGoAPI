import mimetypes
import os

from config import Config
from database import get_connection
from repositories.usuario_repository import UsuarioRepository

class UsuarioService:
    def obtener_perfil(self, usuario_id):
        connection = get_connection()
        try:
            repository = UsuarioRepository(connection)
            usuario = repository.buscar_por_id(usuario_id)

            if usuario is None:
                return None, "Usuario no encontrado", 404
            if usuario["estado"] != "ACTIVO":
                return None, "El usuario se encuentra inactivo", 403

            data = {
                "id": usuario["id"],
                "email": usuario["email"],
                "nombres": usuario["nombres"],
                "apellidos": usuario["apellidos"],
                "foto": usuario["foto"],
                "rol": usuario["rol"],
                "estado": usuario["estado"],
                "fecha_registro": (
                usuario["fecha_registro"].strftime("%Y-%m-%d %H:%M:%S")
                if usuario["fecha_registro"] is not None
                else None
                )
            }

            return data, "Perfil obtenido correctamente", 200
        finally:
            connection.close()

    def obtener_foto_perfil(self, usuario_id):
        return self.obtener_foto_usuario(usuario_id)

    def obtener_foto_usuario(self, usuario_id):
        """
        Obtiene la ruta privada de la foto de un usuario.

        Retorna:
            ruta_archivo, mimetype, mensaje, http_code
        """
        connection = get_connection()

        try:
            repository = UsuarioRepository(connection)
            usuario = repository.obtener_foto_por_usuario(usuario_id)

            if usuario is None:
                return None, None, "Usuario no encontrado", 404

            if usuario["estado"] != "ACTIVO":
                return None, None, "El usuario se encuentra inactivo", 403

            ruta_base = os.path.realpath(Config.PROFILE_PHOTO_DIR)
            os.makedirs(ruta_base, exist_ok=True)

            nombre_foto = "default.png"
            if "foto" in usuario and usuario.get("foto"):
                nombre_foto = usuario.get("foto")

            nombre_seguro = os.path.basename(nombre_foto)
            ruta_archivo = os.path.realpath(
                os.path.join(ruta_base, nombre_seguro)
            )

            if os.path.commonpath([ruta_base, ruta_archivo]) != ruta_base:
                return None, None, "Ruta de foto no válida", 400

            if not os.path.isfile(ruta_archivo):
                return None, None, "Archivo de foto no encontrado", 404

            mimetype, _ = mimetypes.guess_type(ruta_archivo)

            if mimetype is None or not mimetype.startswith("image/"):
                return None, None, "El archivo almacenado no es una imagen válida", 415

            return (
                ruta_archivo,
                mimetype,
                "Foto de perfil obtenida correctamente",
                200
            )
        finally:
            connection.close()
