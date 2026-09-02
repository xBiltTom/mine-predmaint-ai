"""
Generador de Datasets de Mantenimiento Predictivo para Equipos de Carguío Minero.
Combina la estructura del benchmark industrial UCI AI4I 2020 con dinámica física de minería.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd
from typing import Optional, Tuple, Dict, Any
from config.settings import DATASETS_DIR, SENSOR_THRESHOLDS, FAULT_MODES

def generate_base_dataset(n_samples: int = 10000, random_state: int = 42, save: bool = True) -> pd.DataFrame:
    """
    Genera un conjunto de datos industrial hiperrealista para carguío minero (palas y cargadores).
    Contempla ~6.5% de fallas distribuidas en 5 modos de fallo industriales.
    """
    np.random.seed(random_state)
    
    equipos = ["PALA-01", "PALA-02", "PALA-03", "CARG-01", "CARG-02"]
    equipo_probs = [0.25, 0.25, 0.20, 0.15, 0.15]
    tags = np.random.choice(equipos, size=n_samples, p=equipo_probs)

    # Variables base en rangos operacionales normales
    # 1. Temperatura de motor diésel / transmisión (°C): media 82°C, std 4.5°C
    temp_motor = np.random.normal(loc=82.0, scale=4.5, size=n_samples)
    
    # 2. Presión hidráulica principal (PSI): media 3250 PSI, std 180 PSI
    presion_hidraulica = np.random.normal(loc=3250.0, scale=180.0, size=n_samples)
    
    # 3. Vibración de rodamientos y tren de potencia (mm/s RMS): media 2.2, std 0.6
    vibracion = np.random.gamma(shape=4.0, scale=0.55, size=n_samples)
    
    # 4. Presión de aceite lubricante (PSI): media 54.0, std 5.0
    presion_aceite = np.random.normal(loc=54.0, scale=5.0, size=n_samples)
    
    # 5. Temperatura refrigerante (°C): media 81.0, std 4.0
    temp_refrigerante = np.random.normal(loc=81.0, scale=4.0, size=n_samples)
    
    # 6. RPM de motor: régimen entre 1400 y 1950 RPM
    rpm = np.random.normal(loc=1720.0, scale=120.0, size=n_samples)
    
    # 7. Voltaje sistema (V): 24V nominal, alternador ~26.5V
    voltaje = np.random.normal(loc=26.4, scale=0.8, size=n_samples)
    
    # 8. Corriente eléctrica demandada (A): media 160A, std 35A
    corriente = np.random.normal(loc=160.0, scale=35.0, size=n_samples)
    
    # 9. Horas acumuladas de fatiga en componente crítico (0 a 3500 hrs)
    desgaste_hrs = np.random.uniform(50.0, 3500.0, size=n_samples)

    # Inyección sistemática de anomalías y patrones de fallo industriales
    falla_maquina = np.zeros(n_samples, dtype=int)
    tipo_falla = np.array(["NORMAL"] * n_samples, dtype=object)

    # Modo 1: Falla Térmica / Refrigeración (HDF) ~1.8%
    # Ocurre cuando se combinan alta temp refrigerante y temp motor con sobrecalentamiento
    idx_hdf = np.random.choice(n_samples, size=int(n_samples * 0.018), replace=False)
    temp_motor[idx_hdf] += np.random.uniform(18.0, 35.0, size=len(idx_hdf))
    temp_refrigerante[idx_hdf] += np.random.uniform(16.0, 28.0, size=len(idx_hdf))
    falla_maquina[idx_hdf] = 1
    tipo_falla[idx_hdf] = "FALLA_TERMICA"

    # Modo 2: Pérdida de Presión / Potencia Hidráulica (PWF) ~1.5%
    # Ocurre por fuga interna en bomba o rotura de manguera de alta presión
    disponibles = np.where(falla_maquina == 0)[0]
    idx_pwf = np.random.choice(disponibles, size=int(n_samples * 0.015), replace=False)
    presion_hidraulica[idx_pwf] -= np.random.uniform(900.0, 1600.0, size=len(idx_pwf))
    presion_aceite[idx_pwf] -= np.random.uniform(18.0, 32.0, size=len(idx_pwf))
    falla_maquina[idx_pwf] = 1
    tipo_falla[idx_pwf] = "FALLA_PRESION_HIDRAULICA"

    # Modo 3: Desgaste Crítico en Rodamientos / Fatiga de Tren (TWF) ~1.6%
    # Vibraciones mecánicas muy elevadas asociadas a horas altas de operación
    disponibles = np.where(falla_maquina == 0)[0]
    idx_twf = np.random.choice(disponibles, size=int(n_samples * 0.016), replace=False)
    vibracion[idx_twf] += np.random.uniform(4.5, 9.5, size=len(idx_twf))
    desgaste_hrs[idx_twf] = np.random.uniform(2800.0, 4200.0, size=len(idx_twf))
    falla_maquina[idx_twf] = 1
    tipo_falla[idx_twf] = "FALLA_DESGASTE_RODAMIENTOS"

    # Modo 4: Sobreesfuerzo Mecánico / Carga Extrema de Balde (OSF) ~1.2%
    # Ocurre cuando el operador clava el balde en roca viva con exceso de corriente y torque
    disponibles = np.where(falla_maquina == 0)[0]
    idx_osf = np.random.choice(disponibles, size=int(n_samples * 0.012), replace=False)
    presion_hidraulica[idx_osf] += np.random.uniform(700.0, 1200.0, size=len(idx_osf))
    corriente[idx_osf] += np.random.uniform(120.0, 200.0, size=len(idx_osf))
    falla_maquina[idx_osf] = 1
    tipo_falla[idx_osf] = "FALLA_SOBRECARGA"

    # Modo 5: Falla Eléctrica / Aleatoria (RNF) ~0.6%
    disponibles = np.where(falla_maquina == 0)[0]
    idx_rnf = np.random.choice(disponibles, size=int(n_samples * 0.006), replace=False)
    voltaje[idx_rnf] -= np.random.uniform(5.0, 10.0, size=len(idx_rnf))
    falla_maquina[idx_rnf] = 1
    tipo_falla[idx_rnf] = "FALLA_ELECTRICA"

    df = pd.DataFrame({
        "equipo_tag": tags,
        "temp_motor_c": np.round(temp_motor, 2),
        "presion_hidraulica_psi": np.round(presion_hidraulica, 2),
        "vibracion_rodamientos_mm_s": np.round(vibracion, 2),
        "presion_aceite_psi": np.round(presion_aceite, 2),
        "temp_refrigerante_c": np.round(temp_refrigerante, 2),
        "rpm_motor": np.round(rpm, 1),
        "voltaje_sistema_v": np.round(voltaje, 2),
        "corriente_a": np.round(corriente, 2),
        "desgaste_componente_hrs": np.round(desgaste_hrs, 1),
        "falla_maquina": falla_maquina,
        "tipo_falla": tipo_falla
    })

    if save:
        output_file = DATASETS_DIR / "carguio_minero_telemetria.csv"
        df.to_csv(output_file, index=False)
        print(f"📁 Dataset generado exitosamente en: {output_file}")
        print(f"   Total registros: {len(df)} | Fallas: {df['falla_maquina'].sum()} ({df['falla_maquina'].mean()*100:.2f}%)")

    return df

def generate_live_telemetry_reading(equipo_id: int, simulate_failure: bool = False, failure_type: str = "NORMAL") -> Dict[str, Any]:
    """Genera una lectura de telemetría puntual para streaming / simulación."""
    base = {
        "equipo_id": equipo_id,
        "temp_motor_c": float(np.round(np.random.normal(82.0, 3.5), 2)),
        "presion_hidraulica_psi": float(np.round(np.random.normal(3250.0, 120.0), 2)),
        "vibracion_rodamientos_mm_s": float(np.round(np.random.gamma(4.0, 0.55), 2)),
        "presion_aceite_psi": float(np.round(np.random.normal(54.0, 4.0), 2)),
        "temp_refrigerante_c": float(np.round(np.random.normal(81.0, 3.0), 2)),
        "rpm_motor": float(np.round(np.random.normal(1720.0, 80.0), 1)),
        "voltaje_sistema_v": float(np.round(np.random.normal(26.4, 0.6), 2)),
        "corriente_a": float(np.round(np.random.normal(160.0, 25.0), 2)),
        "desgaste_componente_hrs": float(np.round(np.random.uniform(500.0, 2500.0), 1)),
        "falla_registrada": False,
        "tipo_falla_real": "NORMAL"
    }

    if simulate_failure:
        base["falla_registrada"] = True
        base["tipo_falla_real"] = failure_type
        if failure_type == "FALLA_TERMICA":
            base["temp_motor_c"] += np.random.uniform(22.0, 35.0)
            base["temp_refrigerante_c"] += np.random.uniform(18.0, 28.0)
        elif failure_type == "FALLA_PRESION_HIDRAULICA":
            base["presion_hidraulica_psi"] -= np.random.uniform(1100.0, 1600.0)
            base["presion_aceite_psi"] -= np.random.uniform(20.0, 30.0)
        elif failure_type == "FALLA_DESGASTE_RODAMIENTOS":
            base["vibracion_rodamientos_mm_s"] += np.random.uniform(5.0, 9.0)
            base["desgaste_componente_hrs"] = 3800.0
        elif failure_type == "FALLA_SOBRECARGA":
            base["presion_hidraulica_psi"] += np.random.uniform(800.0, 1200.0)
            base["corriente_a"] += np.random.uniform(140.0, 220.0)
        elif failure_type == "FALLA_ELECTRICA":
            base["voltaje_sistema_v"] -= np.random.uniform(6.0, 9.0)

    return base

if __name__ == "__main__":
    generate_base_dataset(n_samples=10000)
