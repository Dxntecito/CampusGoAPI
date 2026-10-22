class ViajeRepository:
    
    def __init__(self, connection):
        self.connection = connection

    def obtener_conductor_id_por_usuario(self, usuario_id):
        cursor = self.connection.cursor()
        try:
            sql = "SELECT id FROM conductor WHERE usuario_id = %s"
            cursor.execute(sql, (usuario_id,))
            fila = cursor.fetchone()
            return fila["id"] if fila else None
        finally:
            cursor.close()

    def crear(self, conductor_id, datos):
        cursor = self.connection.cursor()
        try:
            sql = """
                INSERT INTO viaje (
                    conductor_id, origen, destino, fecha,
                    hora, cupos, precio, estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'DISPONIBLE')
            """
            cursor.execute(sql, (
                conductor_id,
                datos["origen"],
                datos["destino"],
                datos["fecha"],
                datos["hora"],
                datos["cupos"],
                datos["precio"]
            ))
            return cursor.lastrowid
        finally:
            cursor.close()

    def listar(self, origen=None, destino=None, fecha=None, estado=None):
        cursor = self.connection.cursor()
        try:
            sql = """
                SELECT
                    v.id, v.origen, v.destino, v.fecha, v.hora,
                    v.cupos, v.precio, v.estado,
                    CONCAT(u.nombres, ' ', u.apellidos) AS conductor
                FROM viaje v
                INNER JOIN conductor c ON c.id = v.conductor_id
                INNER JOIN usuario u ON u.id = c.usuario_id
                WHERE 1 = 1
            """
            params = []

            if origen:
                sql += " AND v.origen LIKE %s"
                params.append(f"%{origen}%")

            if destino:
                sql += " AND v.destino LIKE %s"
                params.append(f"%{destino}%")

            if fecha:
                sql += " AND v.fecha = %s"
                params.append(fecha)

            if estado:
                sql += " AND v.estado = %s"
                params.append(estado)

            sql += " ORDER BY v.fecha, v.hora"

            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()

    def obtener_por_id(self, viaje_id):
        cursor = self.connection.cursor()
        try:
            sql = """
                SELECT
                    v.*, c.usuario_id AS conductor_usuario_id
                FROM viaje v
                INNER JOIN conductor c ON c.id = v.conductor_id
                WHERE v.id = %s
            """
            cursor.execute(sql, (viaje_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def obtener_detalle(self, viaje_id):
        cursor = self.connection.cursor()
        try:
            sql_viaje = """
                SELECT
                    v.id,
                    v.origen,
                    v.destino,
                    v.fecha,
                    v.hora,
                    v.precio,
                    v.estado,
                    v.cupos,
                    CONCAT(uu.nombres, ' ', uu.apellidos) AS conductor_nombre,
                    c.foto_conductor AS conductor_foto,
                    ve.modelo AS vehiculo_modelo,
                    ve.placa AS vehiculo_placa,
                    ve.color AS vehiculo_color
                FROM viaje AS v
                INNER JOIN conductor AS c ON c.id = v.conductor_id
                INNER JOIN usuario AS uu ON uu.id = c.usuario_id
                LEFT JOIN vehiculo AS ve ON ve.conductor_id = c.id
                WHERE v.id = %s
                LIMIT 1
            """
            cursor.execute(sql_viaje, (viaje_id,))
            viaje = cursor.fetchone()

            if viaje is None:
                return None

            sql_pasajeros = """
                SELECT DISTINCT
                    up.id,
                    CONCAT(up.nombres, ' ', up.apellidos) AS nombre
                FROM reserva_viaje AS rv
                INNER JOIN reserva AS r ON r.id = rv.reserva_id
                INNER JOIN pasajero AS p ON p.id = r.pasajero_id
                INNER JOIN usuario AS up ON up.id = p.usuario_id
                WHERE rv.viaje_id = %s
                  AND rv.estado = 'CONFIRMADA'
                  AND r.estado = 'CONFIRMADA'
                ORDER BY up.id
            """
            cursor.execute(sql_pasajeros, (viaje_id,))
            pasajeros = cursor.fetchall()

            viaje["pasajeros"] = pasajeros
            return viaje
        finally:
            cursor.close()

    def actualizar(self, viaje_id, datos):
        cursor = self.connection.cursor()
        try:
            sql = """
                UPDATE viaje
                SET origen = %s,
                    destino = %s,
                    fecha = %s,
                    hora = %s,
                    cupos = %s,
                    precio = %s
                WHERE id = %s
            """
            cursor.execute(sql, (
                datos["origen"], datos["destino"],
                datos["fecha"], datos["hora"],
                datos["cupos"], datos["precio"],
                viaje_id
            ))
            return cursor.rowcount
        finally:
            cursor.close()

    def cancelar(self, viaje_id):
        cursor = self.connection.cursor()
        try:
            sql = """
                UPDATE viaje
                SET estado = 'CANCELADO'
                WHERE id = %s
            """
            cursor.execute(sql, (viaje_id,))
            return cursor.rowcount
        finally:
            cursor.close()
