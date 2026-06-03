"""SMAR-IA — Gestor de conexiones WebSocket con seguridad de concurrencia."""

import json
import asyncio
import logging
from typing import List
from fastapi import WebSocket
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger("smar-ia-ws")


class ConnectionManager:
    """Gestiona conexiones WebSocket con protección de concurrencia."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Registra una nueva conexión WebSocket (ya aceptada)."""
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        """Elimina una conexión WebSocket de la lista activa."""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Envía un mensaje JSON a todas las conexiones activas."""
        text = json.dumps(message)
        async with self._lock:
            connections = list(self.active_connections)
        for connection in connections:
            try:
                await connection.send_text(text)
            except ConnectionClosed:
                await self.disconnect(connection)
            except Exception as exc:
                logger.warning("Error enviando mensaje WS: %s", exc)
                await self.disconnect(connection)


manager = ConnectionManager()
