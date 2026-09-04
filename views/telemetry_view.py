"""
Vista de Telemetría y Monitoreo en Vivo con Simulador de Streaming a PostgreSQL.
Integrada con diagnóstico IA en tiempo real y generación automática de OTs.
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
from views.components.flow_guide import render_step_header, render_step_footer, navigate_to

def render_telemetry_view():
    # 1. Encabezado del Flujo (TELEMETRY)
    render_step_header("TELEMETRY")

    equipments = EquipmentRepository.list_all()
    if not equipments:
        st.warning("No hay equipos registrados en la base de datos.")
        return

    # Selección de equipo con soporte para pre-selección desde el Dashboard
    eq_options = {f"{e['codigo_tag']} - {e['marca_modelo']} ({e['ubicacion_tajo']})": e["id"] for e in equipments}
    target_id = st.session_state.get("target_equipment_id")
    
    default_idx = 0
    if target_id:
        for idx, (label, eq_id) in enumerate(eq_options.items()):
            if eq_id == target_id:
                default_idx = idx
                break

    selected_label = st.selectbox("Seleccione Equipo de Carguío para Monitoreo:", list(eq_options.keys()), index=default_idx)
    selected_id = eq_options[selected_label]
    st.session_state["target_equipment_id"] = selected_id
    selected_eq = next(e for e in equipments if e["id"] == selected_id)

    # 2. Obtener última lectura de telemetría
    latest = TelemetryRepository.get_latest_by_equipment(selected_id)

    # Panel de Sensores en Vivo
    st.subheader(f"⚡ Telemetría Actual en Faena: {selected_eq['codigo_tag']} ({selected_eq['tipo_equipo']})")
    
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
            st.metric("Desgaste Componente", f"{val:.0f} hrs", delta=f"{latest['rpm_motor']:.0f} RPM")

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
        st.info("Sin lecturas registradas para este equipo.")

    st.divider()

    # 3. Simulador de Telemetría Streaming e Inyección de Fallas
    st.subheader("🕹️ Simulador de Inyección de Eventos Industriales a PostgreSQL")
    st.caption("Prueba cómo reacciona el motor de IA en tiempo real al enviar telemetría normal o forzar un modo de falla específico.")
    
    with st.container(border=True):
        sim_col1, sim_col2, sim_col3 = st.columns([1.2, 1.4, 1.4])
        with sim_col1:
            st.markdown("<b>Lectura de Operación Continua:</b>", unsafe_allow_html=True)
            if st.button("🟢 Inyectar Lectura Normal", use_container_width=True):
                data = generate_live_telemetry_reading(selected_id, simulate_failure=False)
                new_id = TelemetryRepository.insert(data)
                st.session_state["last_sim_result"] = {
                    "type": "NORMAL",
                    "msg": f"Lectura normal registrada exitosamente en PostgreSQL (ID: {new_id}). Sensores dentro de parámetros nominales."
                }
                st.rerun()

        with sim_col2:
            st.markdown("<b>Seleccionar Modo de Fallo:</b>", unsafe_allow_html=True)
            fail_mode = st.selectbox(
                "Modo de Falla:",
                ["FALLA_TERMICA", "FALLA_PRESION_HIDRAULICA", "FALLA_DESGASTE_RODAMIENTOS", "FALLA_SOBRECARGA", "FALLA_ELECTRICA"],
                label_visibility="collapsed"
            )

        with sim_col3:
            st.markdown("<b>Inyectar Evento de Falla:</b>", unsafe_allow_html=True)
            if st.button("🚨 Inyectar Anomalía de Falla", type="primary", use_container_width=True):
                data = generate_live_telemetry_reading(selected_id, simulate_failure=True, failure_type=fail_mode)
                new_id = TelemetryRepository.insert(data)
                
                # Evaluar con IA usando el modelo activo en producción
                active_model, active_m = ModelRegistry.get_loaded_active_model()
                if active_model and active_m:
                    diag = ModelRegistry.generate_diagnostic(active_model, data)
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
                    
                    ot_cod = None
                    if diag["nivel_criticidad"] in ["ALTO", "CRITICO"]:
                        EquipmentRepository.update_status(selected_id, "EN ALERTA")
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

                    st.session_state["last_sim_result"] = {
                        "type": "ANOMALY",
                        "diag": diag,
                        "pred_id": pred_id,
                        "ot_cod": ot_cod,
                        "eq_tag": selected_eq["codigo_tag"]
                    }
                st.rerun()

    # 4. Banner de Resultado de la Inyección y Conexión con OTs
    if "last_sim_result" in st.session_state:
        res = st.session_state["last_sim_result"]
        if res.get("type") == "NORMAL":
            st.success(f"✅ {res['msg']}")
        elif res.get("type") == "ANOMALY":
            diag = res["diag"]
            crit_color = "#EF4444" if diag["nivel_criticidad"] == "CRITICO" else "#F59E0B"
            st.markdown(f"""
                <div style="border: 2px solid {crit_color}; border-radius: 8px; padding: 14px; background-color: #FFF5F5; margin: 12px 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:{crit_color};">🚨 DIAGNÓSTICO DE IA: {diag['tipo_falla_estimada'].upper()}</h4>
                        <span style="background-color:{crit_color}; color:white; padding:4px 10px; border-radius:12px; font-weight:bold; font-size:0.85rem;">
                            CRITICIDAD: {diag['nivel_criticidad']}
                        </span>
                    </div>
                    <p style="margin:8px 0 4px 0; color:#1E293B;">
                        <b>Probabilidad de Falla:</b> {diag['prob_falla']*100:.1f}% | <b>RUL (Vida Útil Remanente Estimada):</b> {diag['rtv_horas_estimadas']:.0f} horas
                    </p>
                    <p style="margin:0; color:#475569; font-size:0.9rem;">
                        <b>Recomendación Técnica:</b> {diag['recomendacion_tecnica']}
                    </p>
                    {f'<p style="margin:6px 0 0 0; color:#B91C1C; font-weight:bold;">🛠️ Se generó automáticamente la orden de trabajo: <code>{res["ot_cod"]}</code></p>' if res.get("ot_cod") else ''}
                </div>
            """, unsafe_allow_html=True)

            rc1, rc2 = st.columns(2)
            with rc1:
                if st.button("🛠️ Ir a Gestionar la Orden de Trabajo Generada (Paso 5)", type="primary", use_container_width=True):
                    navigate_to("5️⃣ 🛠️ Órdenes de Trabajo")
            with rc2:
                if st.button("🤖 Inspeccionar Algoritmos en Laboratorio IA (Paso 4)", use_container_width=True):
                    navigate_to("4️⃣ 🤖 Laboratorio de IA")

    # 5. Gráfico Histórico de Telemetría
    st.subheader(f"📈 Tendencias Temporales de Telemetría: {selected_eq['codigo_tag']} (Últimas 60 lecturas)")
    history = TelemetryRepository.get_recent_history(equipment_id=selected_id, limit=60)
    if history:
        df_hist = pd.DataFrame(history)
        df_hist["fecha_str"] = pd.to_datetime(df_hist["fecha_hora"]).dt.strftime('%H:%M:%S')
        df_hist = df_hist.sort_values(by="id", ascending=True)

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=df_hist["fecha_str"], y=df_hist["temp_motor_c"], name="Temp Motor (°C)", line=dict(color="#EF4444", width=2)))
        fig_trend.add_trace(go.Scatter(x=df_hist["fecha_str"], y=df_hist["vibracion_rodamientos_mm_s"] * 15, name="Vibración (x15 mm/s)", line=dict(color="#F59E0B", width=2)))
        fig_trend.add_trace(go.Scatter(x=df_hist["fecha_str"], y=df_hist["presion_hidraulica_psi"] / 40, name="Presión Hidr (/40 PSI)", line=dict(color="#3B82F6", width=2)))
        fig_trend.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20), xaxis_title="Hora de Muestreo", yaxis_title="Escala Normalizada")
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Sin historial suficiente para graficar.")

    # 6. Pie de Navegación del Flujo
    render_step_footer("TELEMETRY")
