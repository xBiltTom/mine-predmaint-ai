"""
Configuración global del sistema de mantenimiento predictivo para minería.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno si existe .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Configuración de Base de Datos PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "mine_predmaint_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Configuración de Seguridad y JWT
SECRET_KEY = os.getenv("SECRET_KEY", "unt-is402-mine-predmaint-secret-key-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 12

# Rutas de almacenamiento de artefactos y datasets
DATA_DIR = BASE_DIR / "data"
DATASETS_DIR = DATA_DIR / "datasets"
SAVED_MODELS_DIR = BASE_DIR / "models" / "saved"

DATASETS_DIR.mkdir(parents=True, exist_ok=True)
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Umbrales operativos estándar para sensores de equipos de carguío minero
SENSOR_THRESHOLDS = {
    "temp_motor_c": {"min": 60.0, "max": 95.0, "critico": 105.0, "unidad": "°C"},
    "presion_hidraulica_psi": {"min": 2500.0, "max": 3800.0, "critico": 4200.0, "unidad": "PSI"},
    "vibracion_rodamientos_mm_s": {"min": 0.5, "max": 4.5, "critico": 7.0, "unidad": "mm/s"},
    "presion_aceite_psi": {"min": 35.0, "max": 75.0, "critico": 25.0, "unidad": "PSI"},
    "temp_refrigerante_c": {"min": 70.0, "max": 92.0, "critico": 102.0, "unidad": "°C"},
    "rpm_motor": {"min": 1200.0, "max": 2100.0, "critico": 2350.0, "unidad": "RPM"},
    "voltaje_sistema_v": {"min": 23.5, "max": 28.5, "critico": 21.0, "unidad": "V"},
    "corriente_a": {"min": 50.0, "max": 280.0, "critico": 340.0, "unidad": "A"}
}

# Modos de falla industriales categorizados
FAULT_MODES = {
    0: "Operación Normal",
    1: "Falla Térmica / Refrigeración (HDF)",
    2: "Pérdida de Presión / Potencia (PWF)",
    3: "Sobreesfuerzo Mecánico / Carga Extrema (OSF)",
    4: "Desgaste Crítico Rodamientos / Tren (TWF)",
    5: "Falla Aleatoria / Eléctrica (RNF)"
}
