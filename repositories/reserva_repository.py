class ReservaRepository:
    
    def __init__(self, connection):
        self.connection = connection

    def obtener_pasajero_id_por_usuario(self, usuario_id):
        cursor = self.connection.cursor()
        try:
            sql = "SELECT id FROM pasajero WHERE usuario_id = %s"
            cursor.execute(sql, (usuario_id,))
            fila = cursor.fetchone()
            return fila["id"] if fila else None
        finally:
            cursor.close()

    def obtener_viaje_para_actualizar(self, viaje_id):
        cursor = self.connection.cursor()
        try:
            sql = """
                SELECT
                    v.id, v.fecha, v.hora, v.cupos, v.estado,
                    c.usuario_id AS conductor_usuario_id
                FROM viaje v
                INNER JOIN conductor c ON c.id = v.conductor_id
                WHERE v.id = %s
                FOR UPDATE
            """
            cursor.execute(sql, (viaje_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def crear_reserva(self, pasajero_id):
        cursor = self.connection.cursor()
        try:
            sql = """
                INSERT INTO reserva (pasajero_id, estado)
                VALUES (%s, 'CONFIRMADA')
            """
            cursor.execute(sql, (pasajero_id,))
            return cursor.lastrowid
        finally:
            cursor.close()

    def crear_detalle(self, reserva_id, viaje_id, cantidad, tipo_tramo, orden):
        cursor = self.connection.cursor()
        try:
            sql = """
                INSERT INTO reserva_viaje (
                    reserva_id, viaje_id, cantidad,
                    tipo_tramo, orden_tramo, estado
                )
                VALUES (%s, %s, %s, %s, %s, 'CONFIRMADA')
            """
            cursor.execute(sql, (
                reserva_id, viaje_id, cantidad,
                tipo_tramo, orden
            ))
        finally:
            cursor.close()
            
    def descontar_cupos(self, viaje_id, cantidad):
        cursor = self.connection.cursor()
        try:
            sql = """
                UPDATE viaje
                SET cupos = cupos - %s,
                    estado = CASE
                        WHEN cupos - %s = 0 THEN 'COMPLETO'
                        ELSE estado
                    END
                WHERE id = %s
            """
            cursor.execute(sql, (
                cantidad,
                cantidad,
                viaje_id
            ))
        finally:
            cursor.close()

    def obtener_tokens_conductores_por_viajes(self, viaje_ids):
        if not viaje_ids:
            return []

        cursor = self.connection.cursor()
        try:
            placeholders = ", ".join(["%s"] * len(viaje_ids))
            sql = f"""
                SELECT DISTINCT ud.fcm_token
                FROM viaje AS v
                INNER JOIN conductor AS c
                    ON c.id = v.conductor_id
                INNER JOIN usuario_dispositivo AS ud
                    ON ud.usuario_id = c.usuario_id
                WHERE v.id IN ({placeholders})
                  AND ud.activo = 1
                  AND ud.fcm_token IS NOT NULL
                  AND TRIM(ud.fcm_token) <> ''
            """
            cursor.execute(sql, tuple(viaje_ids))
            return [fila["fcm_token"] for fila in cursor.fetchall()]
        finally:
            cursor.close()
