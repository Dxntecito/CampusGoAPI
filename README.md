# CampusGo API REST - Proyecto base de laboratorio

Esta versión permite implementar con los estudiantes, paso a paso, la arquitectura:

Route -> Service -> Repository -> MySQL

Las carpetas `repositories`, `routes` y `services` se entregan sin implementación funcional.
   
## Orden sugerido del laboratorio

1. Crear `repositories/usuario_repository.py`
2. Crear `services/auth_service.py`
3. Crear `routes/auth_routes.py`
4. Implementar Login + JWT
5. Crear `services/usuario_service.py`
6. Crear `routes/usuario_routes.py`
7. Implementar Perfil protegido con JWT

## Preparación

1. `python -m venv .venv`
2. `.\.venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. Copiar `.env.example` como `.env`
5. Ejecutar `sql/campusgo.sql`
6. Ejecutar desde la raíz:
   `python -m scripts.create_demo_users`
7. Ejecutar:
   `python app.py`

## Regla arquitectónica

- Route recibe y responde.
- Service decide.
- Repository consulta.

## Registro de dispositivos y notificaciones

La API registra el token de Firebase Cloud Messaging con `PUT /api/dispositivo`
(requiere JWT). El JSON acepta `fcm_token`, `plataforma` y, opcionalmente,
`nombre_dispositivo`. Cuando se crea una reserva, se notifica a los conductores
con dispositivos activos registrados.

Para una base ya creada, ejecuta una vez
`sql/migrations/20261104_add_usuario_dispositivo.sql`; no vuelvas a ejecutar
`sql/campusgo.sql` sobre una base con datos porque ese script recrea la base.
En Render configura `FIREBASE_PROJECT_ID` y `FIREBASE_SERVICE_ACCOUNT_JSON`
con los valores de la cuenta de servicio de Firebase. No subas el JSON de
credenciales al repositorio.
