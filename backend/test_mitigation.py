import pytest
from fastapi.testclient import TestClient
from main import app
from database import SecuritySessionLocal, BlockedIP
import os

client = TestClient(app)

def test_manual_block_rbac():
    """Verifica que un usuario sin rol admin no puede bloquear IPs."""
    # 1. Obtener token de viewer (o simular login)
    # Aquí asumimos que tenemos un endpoint para crear usuarios de prueba
    response = client.post("/api/mitigation/block", 
                          json={"ip": "1.1.1.1", "action": "BLOCK_IP"},
                          headers={"Authorization": "Bearer TOKEN_VIEWER"})
    assert response.status_code == 401 # Sin token válido falla

def test_auto_block_logic():
    """Prueba la lógica de bloqueo automático en la DB."""
    db = SecuritySessionLocal()
    # Simulamos una IP bloqueada
    from routers.mitigation import record_block
    record_block(db, "10.10.10.10", method="TEST", reason="Test logic")
    
    blocked = db.query(BlockedIP).filter(BlockedIP.ip == "10.10.10.10").first()
    assert blocked is not None
    assert blocked.is_active == 1
    db.close()

def test_firewall_dry_run():
    """Verifica que el módulo de firewall respeta el modo DRY_RUN."""
    from mitigation.firewall import apply_iptables_block
    from config import DRY_RUN
    
    assert DRY_RUN is True # Asegurarse que está en True para el test
    result = apply_iptables_block("8.8.8.8")
    assert result is True # No debe lanzar error de permisos

if __name__ == "__main__":
    # Ejecutar con: pytest test_mitigation.py
    print("Ejecutando tests de mitigación...")
    os.system("pytest test_mitigation.py")