from database import get_connection
from repositories.viaje_repository import ViajeRepository
from datetime import date, time, timedelta
from decimal import Decimal

class ViajeService:

    def crear(self, usuario_id, datos):
        obligatorios = ["origen", "destino", "fecha", "hora", "cupos", "precio"]

        if any(campo not in datos for campo in obligatorios):
            return None, "Faltan datos obligatorios", 400

        if int(datos["cupos"]) <= 0:
            return None, "Los cupos deben ser mayores que cero", 400

        if float(datos["precio"]) < 0:
            return None, "El precio no puede ser negativo", 400

        connection = get_connection()

        try:
            print(usuario_id)
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

            for viaje in viajes:
                if isinstance(viaje.get("fecha"), date):
                    viaje["fecha"] = viaje["fecha"].strftime("%d-%m-%Y")

                hora = viaje.get("hora")
                if isinstance(hora, timedelta):
                    total_segundos = int(hora.total_seconds())
                    horas, resto = divmod(total_segundos, 3600)
                    minutos, segundos = divmod(resto, 60)
                    viaje["hora"] = (
                        f"{horas:02d}:{minutos:02d}:{segundos:02d}"
                    )
                elif isinstance(hora, time):
                    viaje["hora"] = hora.strftime("%H:%M:%S")

                if isinstance(viaje.get("precio"), Decimal):
                    viaje["precio"] = float(viaje["precio"])

            return viajes, "Viajes obtenidos correctamente", 200
        finally:
            connection.close()

    def obtener(self, viaje_id):
        connection = get_connection()
        try:
            repository = ViajeRepository(connection)
            viaje = repository.obtener_detalle(viaje_id)
            if viaje is None:
                return None, "Viaje no encontrado", 404

            if isinstance(viaje.get("fecha"), date):
                viaje["fecha"] = viaje["fecha"].strftime("%d-%m-%Y")

            hora = viaje.get("hora")
            if isinstance(hora, timedelta):
                total_segundos = int(hora.total_seconds())
                horas, resto = divmod(total_segundos, 3600)
                minutos, segundos = divmod(resto, 60)
                viaje["hora"] = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
            elif isinstance(hora, time):
                viaje["hora"] = hora.strftime("%H:%M:%S")

            if isinstance(viaje.get("precio"), Decimal):
                viaje["precio"] = float(viaje["precio"])

            detalle = {
                "id": viaje["id"],
                "origen": viaje["origen"],
                "destino": viaje["destino"],
                "fecha": viaje["fecha"],
                "hora": viaje["hora"],
                "precio": viaje["precio"],
                "estado": viaje["estado"],
                "cupos": viaje["cupos"],
                "conductor": {
                    "nombre": viaje["conductor_nombre"],
                    "foto": (
                        f"/api/usuarios/{viaje['conductor_usuario_id']}/foto"
                        if viaje.get("conductor_foto")
                        else None
                    ),
                    "vehiculo": {
                        "modelo": viaje["vehiculo_modelo"],
                        "placa": viaje["vehiculo_placa"],
                        "color": viaje["vehiculo_color"],
                    },
                },
                "pasajeros": viaje["pasajeros"],
            }

            return detalle, "Detalle del viaje obtenido", 200
        finally:
            connection.close()

    def actualizar(self, usuario_id, viaje_id, datos):
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
