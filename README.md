# SMAR-IA — Sistema de Detección y Mitigación de Intrusiones (IDS/IPS)

**SMAR-IA** es un sistema inteligente de detección y prevención de intrusiones (NIDS/NIPS) que utiliza **Random Forest + XGBoost** para clasificar tráfico de red en 8 categorías de ataque. Implementa bloqueo automático por iptables, panel web en tiempo real y cumple con **ISO/IEC 27001:2022**.

## Arquitectura

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Frontend    │────▶│   Backend    │────▶│   Modelo ML  │
│  React+Vite  │     │  FastAPI     │     │ RandomForest │
│  Bootstrap   │◀────│  SQLite      │◀────│   XGBoost    │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                     ┌──────▼───────┐
                     │   iptables   │
                     │  (firewall)  │
                     └──────────────┘
```

## Clasificación

| Clase | Descripción |
|-------|-------------|
| Normal | Tráfico benigno |
| DDoS SYN Flood | Ataque de inundación SYN |
| DDoS UDP Flood | Ataque de inundación UDP |
| Port Scanning | Escaneo de puertos |
| Brute Force | Ataque de fuerza bruta |
| DHCP Starvation | Agotamiento de DHCP |
| DHCP Spoofing | Suplantación de DHCP |
| Sniffing Pasivo | Monitorización pasiva |

## Stack Tecnológico

- **Backend:** Python 3.14, FastAPI, SQLAlchemy, SQLite, scikit-learn, XGBoost
- **Frontend:** React 19, Vite 8, Bootstrap 5, Recharts, Tailwind CSS 4, Lucide
- **ML Pipeline:** Random Forest (150 estimadores, 80 features), XGBoost
- **Firewall:** iptables (Linux), dry-run (macOS/desarrollo)
- **Calidad:** SonarCloud, pytest, bandit

## Requisitos

- Python 3.12+
- Node.js 20+
- (Opcional) `sudo` sin contraseña para iptables en Linux

## Instalación

```bash
git clone https://github.com/74902142-star/SMAR-IA.git
cd SMAR-IA
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Editar según entorno
python -m uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --port 5174
```

Acceder a `http://localhost:5174`

## Usuario por Defecto

- **Usuario:** `admin`
- **Contraseña:** `admin123` (configurable via `SMAR_IA_ADMIN_PASSWORD`)

## Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `SMAR_IA_SECRET_KEY` | Clave JWT (obligatoria en prod) | Auto-generada en dev |
| `SMAR_IA_ADMIN_PASSWORD` | Contraseña admin | `admin123` |
| `SMAR_IA_DRY_RUN` | Simular bloqueos sin iptables | `false` |
| `SMAR_IA_CORS_ORIGINS` | Orígenes CORS permitidos | `http://localhost:5174` |
| `VITE_API_BASE_URL` | URL base de la API (frontend) | `http://localhost:8000` |

## Despliegue

Ver `DOCUMENTACION/Sprint_6_Implementacion_Final.md` para guía completa de despliegue en servidor Linux.

## Licencia

Proyecto académico — Universidad Continental
