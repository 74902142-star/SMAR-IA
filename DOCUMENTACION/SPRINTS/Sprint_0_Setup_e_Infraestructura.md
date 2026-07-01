# 📋 Sprint 0: Setup e Infraestructura del Sistema

## 1. Objetivos del Sprint
* Configurar el entorno de desarrollo local y de producción para el sistema **SMAR-IA**.
* Diseñar la infraestructura de datos para entrenar el motor de clasificación heurística (Random Forest + XGBoost).
* Empaquetar y contenerizar los microservicios mediante Docker y Docker Compose.

---

## 2. Alineación con el Estado del Arte
Basado en los retos metodológicos de los artículos analizados (por ejemplo, el uso de conjuntos de datos estandarizados como *CIC-DDoS2019* para garantizar la reproducibilidad científica), estructuramos el pipeline de ingesta de datos:
* **Preprocesamiento Científico:** Conversión de tipos de datos categóricos usando `LabelEncoder` y normalización de características con `StandardScaler`.
* **Desacoplamiento de Servicios:** Separación del motor de inferencia de aprendizaje automático y los servidores web en contenedores independientes para evitar cuellos de botella de CPU.

---

## 3. Guía de Instalación del Entorno
1. Clonar el repositorio y configurar el directorio de trabajo:
   ```bash
   git clone https://github.com/74902142-star/SMAR-IA.git
   cd SMAR-IA/ml_pipeline
   ```
2. Inicializar el entorno virtual de Python 3.12+ e instalar dependencias de ML:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 4. Estructura de Contenerización (Docker Compose)
Se define un archivo `docker-compose.yml` en la raíz del proyecto para empaquetar la base de datos, el backend de FastAPI y la interfaz web:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: smaria_backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - SMAR_IA_DRY_RUN=false
    restart: always

  frontend:
    build: ./frontend
    container_name: smaria_frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: always
```

---

## 5. Criterios de Aceptación
* El pipeline de Docker compila y expone los puertos `8000` (FastAPI) y `80` (Nginx/React) correctamente.
* Los archivos `.pkl` del modelo entrenado se exportan y cargan en memoria en menos de 5 segundos.
