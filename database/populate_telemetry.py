"""
Inserta lecturas históricas iniciales en PostgreSQL desde el dataset generado.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
from config.settings import DATASETS_DIR
from database.repositories.equipment_repo import EquipmentRepository
from database.repositories.telemetry_repo import TelemetryRepository

def populate_initial_telemetry(limit_per_equipment: int = 150):
    csv_path = DATASETS_DIR / "carguio_minero_telemetria.csv"
    if not csv_path.exists():
        print("⚠️ Dataset no encontrado, generándolo...")
        from data.dataset_generator import generate_base_dataset
        generate_base_dataset(n_samples=10000)

    df = pd.read_csv(csv_path)
    equipments = EquipmentRepository.list_all()
    if not equipments:
        print("⚠️ No hay equipos en la base de datos. Ejecuta database/seed.py primero.")
        return

    eq_map = {eq["codigo_tag"]: eq["id"] for eq in equipments}
    records = []

    for tag, eq_id in eq_map.items():
        subset = df[df["equipo_tag"] == tag].head(limit_per_equipment)
        for _, row in subset.iterrows():
            records.append({
                "equipo_id": eq_id,
                "temp_motor_c": float(row["temp_motor_c"]),
                "presion_hidraulica_psi": float(row["presion_hidraulica_psi"]),
                "vibracion_rodamientos_mm_s": float(row["vibracion_rodamientos_mm_s"]),
                "presion_aceite_psi": float(row["presion_aceite_psi"]),
                "temp_refrigerante_c": float(row["temp_refrigerante_c"]),
                "rpm_motor": float(row["rpm_motor"]),
                "voltaje_sistema_v": float(row["voltaje_sistema_v"]),
                "corriente_a": float(row["corriente_a"]),
                "desgaste_componente_hrs": float(row["desgaste_componente_hrs"]),
                "falla_registrada": bool(row["falla_maquina"] == 1),
                "tipo_falla_real": str(row.get("tipo_falla", "NORMAL"))
            })

    total_inserted = TelemetryRepository.insert_batch(records)
    print(f"✅ Se insertaron {total_inserted} registros de telemetría inicial en PostgreSQL.")

if __name__ == "__main__":
    populate_initial_telemetry()
