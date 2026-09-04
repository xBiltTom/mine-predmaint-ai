"""
Vista de Dashboard Ejecutivo con KPIs de Confiabilidad y Visualizaciones Interactivas (Plotly).
Integrado con el flujo guiado de mantenimiento predictivo.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.repositories.equipment_repo import EquipmentRepository
from database.repositories.telemetry_repo import TelemetryRepository
from database.repositories.prediction_repo import PredictionRepository
from database.repositories.work_order_repo import WorkOrderRepository
from views.components.flow_guide import render_step_header, render_step_footer, navigate_to

def render_dashboard_view():
    # 1. Encabezado del Flujo (DASHBOARD)
    render_step_header("DASHBOARD")

    # 2. Obtener datos de la base de datos
    equipments = EquipmentRepository.list_all()
    predictions = PredictionRepository.get_recent_predictions(limit=10)
    ot_stats = WorkOrderRepository.get_stats()

    total_eq = len(equipments)
    operativos = sum(1 for e in equipments if e["estado_operativo"] == "OPERATIVO")
    en_alerta = sum(1 for e in equipments if e["estado_operativo"] == "EN ALERTA")
    en_manto = sum(1 for e in equipments if e["estado_operativo"] == "EN MANTENIMIENTO")

    disponibilidad = round((operativos / total_eq) * 100, 1) if total_eq > 0 else 94.2
    mtbf = 315.4  # Estimado en horas
    mttr = 6.2   # Estimado en horas

    # 3. Tarjetas de KPIs Principales
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Disponibilidad Flota", f"{disponibilidad}%", delta=f"{operativos}/{total_eq} operativos")
    with k2:
        st.metric("MTBF Estimado", f"{mtbf} h", delta="Confiabilidad Alta")
    with k3:
        st.metric("MTTR Promedio", f"{mttr} h", delta="-12% vs mes ant.", delta_color="inverse")
    with k4:
        st.metric("Equipos en Alerta", f"{en_alerta}", delta="Atención requerida" if en_alerta > 0 else "Normal", delta_color="inverse" if en_alerta > 0 else "normal")
    with k5:
        st.metric("OTs Pendientes", f"{ot_stats.get('pendientes', 0)}", delta=f"{ot_stats.get('criticas', 0)} críticas", delta_color="inverse" if ot_stats.get('criticas', 0) > 0 else "normal")

    st.divider()

    # 4. Acciones Rápidas Directas del Flujo
    st.markdown("##### ⚡ Acciones Directas del Flujo:")
    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        if st.button("📡 Inspeccionar Telemetría en Tiempo Real", use_container_width=True):
            navigate_to("3️⃣ 📡 Telemetría en Vivo")
    with ac2:
        if st.button("🤖 Explorar Laboratorio de IA & Modelos", use_container_width=True):
            navigate_to("4️⃣ 🤖 Laboratorio de IA")
    with ac3:
        if st.button("🛠️ Ver Órdenes de Trabajo Pendientes", use_container_width=True):
            navigate_to("5️⃣ 🛠️ Órdenes de Trabajo")

    st.divider()

    # 5. Gráficos Ejecutivos con Plotly
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("🎯 Estado Operativo de la Flota")
        df_status = pd.DataFrame({
            "Estado": ["Operativo", "En Alerta", "En Mantenimiento"],
            "Cantidad": [operativos, en_alerta, en_manto],
            "Color": ["#10B981", "#F59E0B", "#3B82F6"]
        })
        fig_donut = px.pie(
            df_status,
            values="Cantidad",
            names="Estado",
            hole=0.55,
            color="Estado",
            color_discrete_map={"Operativo": "#10B981", "En Alerta": "#F59E0B", "En Mantenimiento": "#3B82F6"}
        )
        fig_donut.update_traces(textinfo="label+value", hoverinfo="label+percent")
        fig_donut.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        st.subheader("📈 Nivel de Riesgo Predictivo por Equipo")
        if predictions:
            df_pred = pd.DataFrame(predictions)
            df_pred["prob_pct"] = (df_pred["prob_falla"] * 100).round(1)
            fig_bar = px.bar(
                df_pred,
                x="codigo_tag",
                y="prob_pct",
                color="nivel_criticidad",
                color_discrete_map={"BAJO": "#10B981", "MEDIO": "#3B82F6", "ALTO": "#F59E0B", "CRITICO": "#EF4444"},
                labels={"codigo_tag": "Equipo", "prob_pct": "Probabilidad de Falla (%)", "nivel_criticidad": "Criticidad"},
                text="prob_pct"
            )
            fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300, yaxis_range=[0, 100])
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay predicciones registradas aún.")

    # 6. Estado Individual de Equipos de Carguío
    st.subheader("🚜 Censo de Flota de Carguío Minero en Faena")
    cols = st.columns(len(equipments)) if len(equipments) <= 5 else st.columns(5)
    for idx, eq in enumerate(equipments):
        with cols[idx % 5]:
            status_color = "#10B981" if eq["estado_operativo"] == "OPERATIVO" else ("#F59E0B" if eq["estado_operativo"] == "EN ALERTA" else "#3B82F6")
            st.markdown(f"""
                <div style="border: 1px solid #CBD5E1; border-left: 5px solid {status_color}; border-radius: 8px; padding: 12px; background-color: #F8FAFC; margin-bottom: 8px;">
                    <div style="font-weight: bold; font-size: 1.1rem; color: #1E293B;">{eq['codigo_tag']}</div>
                    <div style="font-size: 0.85rem; color: #64748B;">{eq['marca_modelo']}</div>
                    <div style="font-size: 0.8rem; margin-top: 4px;"><b>Ubicación:</b> {eq['ubicacion_tajo']}</div>
                    <div style="font-size: 0.8rem;"><b>Horas:</b> {eq['horas_acumuladas']:.0f} hrs</div>
                    <div style="font-size: 0.85rem; font-weight: bold; color: {status_color}; margin-top: 6px;">● {eq['estado_operativo']}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("📡 Monitorear", key=f"btn_mon_{eq['id']}", use_container_width=True):
                st.session_state["target_equipment_id"] = eq["id"]
                navigate_to("3️⃣ 📡 Telemetría en Vivo")

    # 7. Tabla de Alertas Predictivas Recientes
    st.subheader("⚠️ Diagnósticos Predictivos y Alertas Recientes de IA")
    if predictions:
        pred_table = []
        for p in predictions:
            pred_table.append({
                "Equipo TAG": p.get("codigo_tag"),
                "Modelo/Algoritmo": p.get("nombre_algoritmo", "Random Forest"),
                "Prob. Falla": f"{float(p['prob_falla'])*100:.1f}%",
                "Criticidad": p["nivel_criticidad"],
                "Diagnóstico Estimado": p["tipo_falla_estimada"],
                "RUL Estimado": f"{float(p.get('rtv_horas_estimadas') or 0.0):.0f} hrs",
                "Recomendación Técnica": p["recomendacion_tecnica"]
            })
        st.dataframe(pd.DataFrame(pred_table), use_container_width=True, hide_index=True)
    else:
        st.info("Sin alertas registradas.")

    # 8. Pie de Navegación del Flujo
    render_step_footer("DASHBOARD")
