"""Test rapido de arranque del backend Sprint 0"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 50)
print("  SMAR-IA -- Test de Arranque Sprint 0")
print("=" * 50)

# 1. Config
print("\n[1] Probando config.py...")
from config import print_config_summary
print_config_summary()
print("   [OK] Config OK")

# 2. Database
print("\n[2] Probando database.py...")
from database import init_db, SecuritySessionLocal, TrafficSessionLocal
from database import SecurityLog, NetworkTraffic, User
from sqlalchemy import func

db_sec = SecuritySessionLocal()
count_logs = db_sec.query(func.count(SecurityLog.id)).scalar()
count_users = db_sec.query(func.count(User.id)).scalar()
db_sec.close()

db_traf = TrafficSessionLocal()
count_traffic = db_traf.query(func.count(NetworkTraffic.id)).scalar()
db_traf.close()

print(f"   Logs de seguridad: {count_logs}")
print(f"   Usuarios: {count_users}")
print(f"   Registros de trafico: {count_traffic}")
print("   [OK] Database OK")

# 3. ML Service
print("\n[3] Probando ml_service.py...")
from ml_service import ml_service
ml_service.load_models()
info = ml_service.get_model_info()
print(f"   Cargado: {info['is_loaded']}")
print(f"   Tipo: {info['model_type']}")
print(f"   Clases: {info['num_classes']}")
print(f"   Features: {info['num_features']}")

if info['is_loaded']:
    import numpy as np
    test_features = np.random.randn(80).tolist()
    pred, conf = ml_service.predict(test_features)
    print(f"   Test predict: {pred} ({conf:.1%})")
    print("   [OK] ML Service OK")
else:
    print("   [WARN] Modelos no cargados")

# 4. Auth
print("\n[4] Probando auth.py...")
from auth import create_access_token, get_password_hash
token = create_access_token(data={"sub": "test"})
print(f"   Token generado: {token[:30]}...")
print("   [OK] Auth OK")

# 5. System router imports
print("\n[5] Probando routers...")
from routers import auth, mitigation, system
print("   [OK] Routers importados OK")

print("\n" + "=" * 50)
print("  [OK] TODOS LOS MODULOS ARRANCAN CORRECTAMENTE")
print("=" * 50)
