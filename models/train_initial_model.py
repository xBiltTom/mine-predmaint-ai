"""
Script para entrenar y registrar un modelo base inicial en PostgreSQL.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
from config.settings import DATASETS_DIR
from data.preprocessor import DataPreprocessor
from models.traditional.random_forest import RandomForestModel
from models.traditional.xgboost_model import XGBoostModel
from models.model_registry import ModelRegistry
from database.repositories.user_repo import UserRepository
from database.repositories.equipment_repo import EquipmentRepository
from database.repositories.telemetry_repo import TelemetryRepository
from database.repositories.prediction_repo import PredictionRepository

def train_and_seed_model():
    print("🤖 Entrenando modelo predictivo base...")
    csv_path = DATASETS_DIR / "carguio_minero_telemetria.csv"
    df = pd.read_csv(csv_path)

    preprocessor = DataPreprocessor()
    X_train, X_test, y_train, y_test = preprocessor.prepare_train_test(df, apply_smote=True)

    rf = RandomForestModel(n_estimators=100, max_depth=8, random_state=42)
    rf.fit(X_train, y_train)
    metrics = rf.evaluate(X_test, y_test)
    print(f"   Accuracy: {metrics['accuracy']:.4f} | F1: {metrics['f1_score']:.4f} | ROC-AUC: {metrics['roc_auc']:.4f}")

    # Obtener usuario ingeniero
    user = UserRepository.get_by_username("ingeniero")
    user_id = user["id"] if user else None

    # Registrar en base de datos
    model_id = ModelRegistry.register_and_save(rf, version="v1.0", usuario_id=user_id, set_as_active=True)
    print(f"✅ Modelo guardado y registrado en PostgreSQL con ID: {model_id}")

    # Generar predicciones iniciales para los equipos usando sus últimas lecturas
    print("🔮 Generando diagnósticos predictivos iniciales para la flota...")
    equipments = EquipmentRepository.list_all()
    for eq in equipments:
        latest = TelemetryRepository.get_latest_by_equipment(eq["id"])
        if latest:
            diag = ModelRegistry.generate_diagnostic(rf, latest)
            PredictionRepository.insert_prediction(
                equipo_id=eq["id"],
                modelo_id=model_id,
                prob_falla=diag["prob_falla"],
                estado_predicho=diag["estado_predicho"],
                tipo_falla_estimada=diag["tipo_falla_estimada"],
                nivel_criticidad=diag["nivel_criticidad"],
                rtv_horas=diag["rtv_horas_estimadas"],
                factores_riesgo=diag["factores_riesgo"],
                recomendacion=diag["recomendacion_tecnica"]
            )
    print("✅ Predicciones iniciales registradas en PostgreSQL.")

if __name__ == "__main__":
    train_and_seed_model()
