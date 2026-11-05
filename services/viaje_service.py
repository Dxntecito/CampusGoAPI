from database import get_connection
from repositories.viaje_repository import ViajeRepository
from datetime import date, timedelta


class ViajeService:

    def validar_datos_viaje(self, datos):
        obligatorios = [
            "origen",
            "origen_latitud",
            "origen_longitud",
            "destino",
            "destino_latitud",
            "destino_longitud",
            "fecha",
            "hora",
            "cupos",
            "precio"
        ]

        if any(campo not in datos for campo in obligatorios):
            return "Faltan datos obligatorios", 400

        # -----------------------------------------
        # VALIDAR COORDENADAS
        # -----------------------------------------
        try:
            origen_latitud = float(datos["origen_latitud"])
            origen_longitud = float(datos["origen_longitud"])
            destino_latitud = float(datos["destino_latitud"])
            destino_longitud = float(datos["destino_longitud"])
        except (TypeError, ValueError):
            return "Las coordenadas no son válidas", 400

        if not (-90 <= origen_latitud <= 90):
            return "La latitud de origen no es válida", 400

        if not (-90 <= destino_latitud <= 90):
            return "La latitud de destino no es válida", 400

        if not (-180 <= origen_longitud <= 180):
            return "La longitud de origen no es válida", 400

        if not (-180 <= destino_longitud <= 180):
            return "La longitud de destino no es válida", 400

        # -----------------------------------------
        # VALIDAR CUPOS
        # -----------------------------------------
        try:
            cupos = int(datos["cupos"])
        except (TypeError, ValueError):
            return "Los cupos no son válidos", 400

        if cupos <= 0:
            return "Los cupos deben ser mayores que cero", 400

        # -----------------------------------------
        # VALIDAR PRECIO
        # -----------------------------------------
        try:
            precio = float(datos["precio"])
        except (TypeError, ValueError):
            return "El precio no es válido", 400

        if precio < 0:
            return "El precio no puede ser negativo", 400

        # Guardar los valores ya convertidos
        datos["origen_latitud"] = origen_latitud
        datos["origen_longitud"] = origen_longitud
        datos["destino_latitud"] = destino_latitud
        datos["destino_longitud"] = destino_longitud
        datos["cupos"] = cupos
        datos["precio"] = precio

        return None

    # =====================================================
    # CREAR VIAJE
    # =====================================================
    def crear(self, usuario_id, datos):
        error = self.validar_datos_viaje(datos)
        if error is not None:
            mensaje, codigo = error
            return None, mensaje, codigo

        connection = get_connection()
        try:
            repository = ViajeRepository(connection)
            conductor_id = repository.obtener_conductor_id_por_usuario(usuario_id)

            if conductor_id is None:
                return None, "El usuario no posee perfil de conductor", 403

            viaje_id = repository.crear(conductor_id, datos)
            connection.commit()

            return {"viaje_id": viaje_id}, "Viaje creado correctamente", 201

        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    # =====================================================
    # LISTAR VIAJES
    # =====================================================
    def listar(self, filtros):
        connection = get_connection()
        try:
            repository = ViajeRepository(connection)
            viajes = repository.listar(
                filtros.get("origen"),
                filtros.get("destino"),
                filtros.get("fecha"),
                filtros.get("estado")
            )
            return viajes, "Viajes obtenidos correctamente", 200
        finally:
            connection.close()

    # =====================================================
    # OBTENER VIAJE
    # =====================================================
    def obtener(self, viaje_id):
        connection = get_connection()
        try:
            repository = ViajeRepository(connection)
            viaje = repository.obtener_por_id(viaje_id)

            if viaje is None:
                return None, "Viaje no encontrado", 404

            if isinstance(viaje.get("hora"), timedelta):
                viaje["hora"] = str(viaje["hora"])

            if isinstance(viaje.get("fecha"), date):
                viaje["fecha"] = viaje["fecha"].isoformat()

            return viaje, "Viaje obtenido correctamente", 200
        finally:
            connection.close()

    # =====================================================
    # ACTUALIZAR VIAJE
    # =====================================================
    def actualizar(self, usuario_id, viaje_id, datos):
        error = self.validar_datos_viaje(datos)
        if error is not None:
            mensaje, codigo = error
            return None, mensaje, codigo

        connection = get_connection()
        try:
            repository = ViajeRepository(connection)
            viaje = repository.obtener_por_id(viaje_id)

            if viaje is None:
                return None, "Viaje no encontrado", 404

            if str(viaje["conductor_usuario_id"]) != str(usuario_id):
                return None, "No puede modificar un viaje de otro conductor", 403

            if viaje["estado"] in ("FINALIZADO", "CANCELADO"):
                return None, "El estado actual no permite modificar el viaje", 409

            repository.actualizar(viaje_id, datos)
            connection.commit()

            return {"viaje_id": viaje_id}, "Viaje actualizado correctamente", 200

        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    # =====================================================
    # CANCELAR VIAJE
    # =====================================================
    def cancelar(self, usuario_id, viaje_id):
        connection = get_connection()
        try:
            repository = ViajeRepository(connection)
            viaje = repository.obtener_por_id(viaje_id)

            if viaje is None:
                return None, "Viaje no encontrado", 404

            if str(viaje["conductor_usuario_id"]) != str(usuario_id):
                return None, "No puede cancelar un viaje de otro conductor", 403

            if viaje["estado"] == "CANCELADO":
                return None, "El viaje ya se encuentra cancelado", 409

            repository.cancelar(viaje_id)
            connection.commit()

            return {"viaje_id": viaje_id}, "Viaje cancelado correctamente", 200

        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()