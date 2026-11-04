class DispositivoRepository:

    def __init__(self, connection):
        self.connection = connection

    def actualizar_dispositivo(
        self,
        usuario_id,
        fcm_token,
        plataforma,
        nombre_dispositivo
    ):
        cursor = self.connection.cursor()
        try:
            sql = """
                INSERT INTO usuario_dispositivo (
                    usuario_id,
                    fcm_token,
                    plataforma,
                    nombre_dispositivo,
                    activo
                )
                VALUES (%s, %s, %s, %s, 1)
                ON DUPLICATE KEY UPDATE
                    usuario_id = VALUES(usuario_id),
                    plataforma = VALUES(plataforma),
                    nombre_dispositivo = VALUES(nombre_dispositivo),
                    activo = 1,
                    fecha_actualizacion = CURRENT_TIMESTAMP
            """
            cursor.execute(sql, (
                usuario_id,
                fcm_token,
                plataforma,
                nombre_dispositivo
            ))
            return cursor.rowcount
        finally:
            cursor.close()
