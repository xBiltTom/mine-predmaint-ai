"""
Vista de Telemetría y Monitoreo en Vivo con Simulador de Streaming a PostgreSQL.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.settings import SENSOR_THRESHOLDS, FAULT_MODES
from database.repositories.equipment_repo import EquipmentRepository
from database.repositories.telemetry_repo import TelemetryRepository
from database.repositories.prediction_repo import PredictionRepository
from database.repositories.work_order_repo import WorkOrderRepository
from data.dataset_generator import generate_live_telemetry_reading
from models.model_registry import ModelRegistry
from models.traditional.random_forest import RandomForestModel
from config.settings import SAVED_MODELS_DIR

def render_telemetry_view():
    st.title("📡 Monitoreo de Telemetría en Vivo & Simulador de Faena")
    st.markdown("Inspección de variables de sensores en tiempo real e inyección de eventos operativos simulados.")

    equipments = EquipmentRepository.list_all()
    if not equipments:
        st.warning("No hay equipos registrados.")
        return

    eq_options = {f"{e['codigo_tag']} - {e['marca_modelo']} ({e['ubicacion_tajo']})": e["id"] for e in equipments}
    selected_label = st.selectbox("Seleccione Equipo de Carguío:", list(eq_options.keys()))
    selected_id = eq_options[selected_label]
    selected_eq = next(e for e in equipments if e["id"] == selected_id)

    # 1. Obtener última lectura de telemetría
    latest = TelemetryRepository.get_latest_by_equipment(selected_id)

    # Panel de Sensores en Vivo
    st.subheader(f"⚡ Telemetría Actual: {selected_eq['codigo_tag']} ({selected_eq['tipo_equipo']})")
    
    if latest:
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            val = float(latest["temp_motor_c"])
            th = SENSOR_THRESHOLDS["temp_motor_c"]
            is_high = val > th["max"]
            st.metric("Temp. Motor", f"{val:.1f} °C", delta="Sobre umbral" if is_high else "Normal", delta_color="inverse" if is_high else "normal")
            
            val = float(latest["temp_refrigerante_c"])
            th = SENSOR_THRESHOLDS["temp_refrigerante_c"]
            is_high = val > th["max"]
            st.metric("Temp. Refrigerante", f"{val:.1f} °C", delta="Sobre umbral" if is_high else "Normal", delta_color="inverse" if is_high else "normal")

        with s2:
            val = float(latest["presion_hidraulica_psi"])
            th = SENSOR_THRESHOLDS["presion_hidraulica_psi"]
            is_abnormal = val < th["min"] or val > th["max"]
            st.metric("Presión Hidráulica", f"{val:.0f} PSI", delta="Falla Presión" if is_abnormal else "Normal", delta_color="inverse" if is_abnormal else "normal")

            val = float(latest["presion_aceite_psi"])
            th = SENSOR_THRESHOLDS["presion_aceite_psi"]
            is_low = val < th["critico"]
            st.metric("Presión Aceite", f"{val:.1f} PSI", delta="Presión Baja" if is_low else "Normal", delta_color="inverse" if is_low else "normal")

        with s3:
            val = float(latest["vibracion_rodamientos_mm_s"])
            th = SENSOR_THRESHOLDS["vibracion_rodamientos_mm_s"]
            is_high = val > th["max"]
            st.metric("Vibración Rodamientos", f"{val:.2f} mm/s", delta="Alerta Fatiga" if is_high else "Normal", delta_color="inverse" if is_high else "normal")

            val = float(latest["desgaste_componente_hrs"])
            st.metric("Desgaste Balde/Pista", f"{val:.0f} hrs", delta=f"{latest['rpm_motor']:.0f} RPM")

        with s4:
            val = float(latest["voltaje_sistema_v"])
            th = SENSOR_THRESHOLDS["voltaje_sistema_v"]
            is_low = val < th["min"]
            st.metric("Voltaje Sistema", f"{val:.1f} V", delta="Batería/Alternador" if is_low else "Normal", delta_color="inverse" if is_low else "normal")

            val = float(latest["corriente_a"])
            th = SENSOR_THRESHOLDS["corriente_a"]
            is_high = val > th["max"]
            st.metric("Corriente Demandada", f"{val:.0f} A", delta="Sobreesfuerzo" if is_high else "Normal", delta_color="inverse" if is_high else "normal")
    else:
        st.info("Sin lecturas recientes registradas para este equipo.")

    st.divider()

    # 2. Simulador de Telemetría Streaming
    st.subheader("🕹️ Inyector / Simulador de Telemetría de Mina a PostgreSQL")
    st.markdown("Permite inyectar lecturas directas a la base de datos simulando el trabajo en faena o forzando un modo de fallo específico.")
    
    sim_col1, sim_col2, sim_col3 = st.columns([1, 1, 1])
    with sim_col1:
        if st.button("🟢 Inyectar Lectura Normal", use_container_width=True):
            data = generate_live_telemetry_reading(selected_id, simulate_failure=False)
            new_id = TelemetryRepository.insert(data)
            st.success(f"Lectura normal registrada en PostgreSQL (ID: {new_id}).")
            st.rerun()

    with sim_col2:
        fail_mode = st.selectbox(
            "Modo de Falla a Simular:",
            ["FALLA_TERMICA", "FALLA_PRESION_HIDRAULICA", "FALLA_DESGASTE_RODAMIENTOS", "FALLA_SOBRECARGA", "FALLA_ELECTRICA"]
        )

    with sim_col3:
        if st.button("🚨 Inyectar Anomalía de Falla", type="primary", use_container_width=True):
            data = generate_live_telemetry_reading(selected_id, simulate_failure=True, failure_type=fail_mode)
            new_id = TelemetryRepository.insert(data)
            
            # Evaluar con IA de inmediato
            active_m = PredictionRepository.get_active_model()
            if active_m and active_m.get("ruta_archivo"):
                rf = RandomForestModel()
                rf.load(active_m["ruta_archivo"])
                diag = ModelRegistry.generate_diagnostic(rf, data)
                pred_id = PredictionRepository.insert_prediction(
                    equipo_id=selected_id,
                    modelo_id=active_m["id"],
                    prob_falla=diag["prob_falla"],
                    estado_predicho=diag["estado_predicho"],
                    tipo_falla_estimada=diag["tipo_falla_estimada"],
                    nivel_criticidad=diag["nivel_criticidad"],
                    rtv_horas=diag["rtv_horas_estimadas"],
                    factores_riesgo=diag["factores_riesgo"],
                    recomendacion=diag["recomendacion_tecnica"]
                )
                if diag["nivel_criticidad"] in ["ALTO", "CRITICO"]:
                    # Actualizar estado de equipo
                    EquipmentRepository.update_status(selected_id, "EN ALERTA")
                    # Crear OT automática sugerida
                    ot_cod = f"OT-AUTO-{selected_eq['codigo_tag']}-{pred_id}"
                    prio_ot = "CRITICA" if diag["nivel_criticidad"] == "CRITICO" else "ALTA"
                    WorkOrderRepository.create(
                        codigo_ot=ot_cod,
                        equipo_id=selected_id,
                        prediccion_id=pred_id,
                        prioridad=prio_ot,
                        titulo=f"Falla detectada por IA: {diag['tipo_falla_estimada']}",
                        descripcion=diag["recomendacion_tecnica"],
                        asignado_a=None
                    )
                    st.error(f"¡ALERTA CRÍTICA GENERADA! Se emitió orden de trabajo automática {ot_cod}.")
                else:
                    st.warning("Anomalía registrada pero nivel de riesgo evaluado en rango tolerable.")
            st.rerun()

    # 3. Gráfico Histórico de Telemetría
    st.subheader("📈 Tendencias Temporales de Telemetría (Últimas 60 lecturas)")
    history = TelemetryRepository.get_recent_history(equipment_id=selected_id, limit=60)
    if history:
        df_hist = pd.DataFrame(history)
        df_hist["fecha_str"] = pd.to_datetime(df_hist["fecha_hora"]).dt.strftime('%H:%M:%S')
        df_hist = df_hist.sort_values(by="id", ascending=True)

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=df_hist["fecha_str"], y=df_hist["temp_motor_c"], name="Temp Motor (°C)", line=dict(color="#EF4444", width=2)))
        fig_trend.add_trace(go.Scatter(x=df_hist["fecha_str"], y=df_hist["vibracion_rodamientos_mm_s"] * 15, name="Vibración (x15 mm/s)", line=dict(color="#F59E0B", width=2)))
        fig_trend.add_trace(go.Scatter(x=df_hist["fecha_str"], y=df_hist["presion_hidraulica_psi"] / 40, name="Presión Hidr (/40 PSI)", line=dict(color="#3B82F6", width=2)))
        fig_trend.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20), xaxis_title="Hora", yaxis_title="Escala Normalizada")
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Sin historial suficiente para graficar.")
