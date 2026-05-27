# Backend SMAR-IA

## Configuración y ejecución

1. Crear/activar entorno virtual en `backend/`:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Inicializar bases de datos y migrar esquemas:
   ```bash
   python manage.py migrate
   ```

3. Crear usuario administrador (por defecto `admin/admin123`):
   ```bash
   python manage.py seed-admin
   ```

4. Generar tráfico de prueba:
   ```bash
   python manage.py seed-traffic --count 400
   ```

5. Iniciar la API:
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

## Uso del simulador de tráfico

También hay un simulador de tráfico en `simulation.py` que inserta paquetes de red continuos en `traffic.db`.

```bash
python simulation.py
```

## Endpoints clave

- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/logs`
- `GET /api/stats`
- `GET /api/stats/alerts-count`
- `GET /api/stats/active-threats`
- `GET /api/mitigation/suspicious`
- `GET /api/mitigation/blocked`
- `GET /api/mitigation/active`
- `POST /api/mitigation/block`

## Troubleshooting

- Si la API no arranca, asegúrate de usar `python3` y activar el entorno virtual.
- Si no hay datos en el dashboard, genera tráfico con `python manage.py seed-traffic` o `python simulation.py`.
- Comprueba que `security_logs.db` y `traffic.db` existen en `backend/`.
- Si el login falla, revisa las credenciales y que el usuario está activo en la tabla `users`.
