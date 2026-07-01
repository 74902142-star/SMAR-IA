import pytest
from fastapi.testclient import TestClient
from main import app, evaluate_condition

client = TestClient(app)

# =====================================================================
# ⚙️ PRUEBAS DE CAJA NEGRA (Black-Box Testing)
# =====================================================================

def test_login_blackbox_success():
    """CB-01 (Caso 2): Inicio de sesión exitoso con credenciales correctas."""
    # Obtenemos token con credenciales por defecto (admin / admin123)
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

def test_login_blackbox_failure():
    """CB-01 (Caso 1): Rechazo de inicio de sesión con credenciales incorrectas."""
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "incorrect_password"}
    )
    assert response.status_code == 401  # FastAPI OAuth2 form returns 401 for bad credentials
    assert "detail" in response.json()


# =====================================================================
# 🔍 PRUEBAS DE CAJA BLANCA (White-Box Testing)
# =====================================================================

def test_condition_evaluation_whitebox_valid():
    """CC-01: Verificación de evaluación correcta de sintaxis válida."""
    context = {
        "attack_type": "Brute Force",
        "confidence": 0.85,
        "ip": "192.168.1.105"
    }
    
    # Condición simple válida
    cond_1 = "attack_type == 'Brute Force' and confidence > 0.8"
    assert evaluate_condition(cond_1, context) is True
    
    # Condición falsa pero con sintaxis correcta
    cond_2 = "confidence < 0.5"
    assert evaluate_condition(cond_2, context) is False

def test_condition_evaluation_whitebox_injection_security():
    """CC-01: Verificación de seguridad ante intentos de inyección de código exec/eval."""
    context = {
        "attack_type": "DDoS",
        "confidence": 0.99,
        "ip": "10.0.0.1"
    }
    
    # Intentos de inyección maliciosa
    unsafe_cond_1 = "__import__('os').system('id')"
    unsafe_cond_2 = "eval('1+1')"
    unsafe_cond_3 = "import sys"
    
    # El evaluador AST debe atrapar el error interno y retornar False de forma segura
    assert evaluate_condition(unsafe_cond_1, context) is False
    assert evaluate_condition(unsafe_cond_2, context) is False
    assert evaluate_condition(unsafe_cond_3, context) is False

def test_condition_evaluation_whitebox_unknown_variables():
    """CC-01: Verificación de que variables no autorizadas no se evalúan."""
    context = {
        "attack_type": "DDoS",
        "confidence": 0.99,
        "ip": "10.0.0.1"
    }
    
    # Variable no declarada en el esquema permitido
    invalid_cond = "latency > 50"
    assert evaluate_condition(invalid_cond, context) is False
