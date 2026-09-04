"""
Vista de Gestión de Órdenes de Trabajo (OT) de Mantenimiento Predictivo / Correctivo.
Integrada con el flujo secuencial y exportación de reportes técnicos.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from database.repositories.work_order_repo import WorkOrderRepository
from database.repositories.equipment_repo import EquipmentRepository
from database.repositories.prediction_repo import PredictionRepository
from database.repositories.user_repo import UserRepository
from auth.session import user_has_permission
from views.components.flow_guide import render_step_header, render_step_footer, navigate_to

def render_work_orders_view():
    # 1. Encabezado del Flujo (WORK_ORDERS)
    render_step_header("WORK_ORDERS")

    # 2. KPIs de Órdenes de Trabajo
    stats = WorkOrderRepository.get_stats()
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total Órdenes", f"{stats.get('total_ots', 0)}")
    with c2:
        st.metric("Pendientes", f"{stats.get('pendientes', 0)}", delta="Requieren atención", delta_color="inverse" if stats.get('pendientes', 0) > 0 else "normal")
    with c3:
        st.metric("En Progreso", f"{stats.get('en_progreso', 0)}")
    with c4:
        st.metric("Completadas", f"{stats.get('completadas', 0)}")
    with c5:
        st.metric("Prioridad Crítica / Alta", f"{stats.get('criticas', 0)}", delta="Atención urgente", delta_color="inverse" if stats.get('criticas', 0) > 0 else "normal")

    st.divider()

    # 3. Acciones Rápidas del Flujo
    st.markdown("##### ⚡ Acciones Directas del Flujo:")
    wo_c1, wo_c2 = st.columns(2)
    with wo_c1:
        if st.button("📡 Volver a Telemetría / Inyectar Nueva Falla (Paso 3)", use_container_width=True):
            navigate_to("3️⃣ 📡 Telemetría en Vivo")
    with wo_c2:
        if st.button("📑 Generar Reporte Formal con estas OTs (Paso 6)", use_container_width=True, type="primary"):
            navigate_to("6️⃣ 📑 Generador de Reportes")

    st.divider()

    # 4. Formulario para Crear Nueva OT
    if user_has_permission("WORK_ORDERS_MANAGE"):
        with st.expander("➕ Emitir Nueva Orden de Trabajo Manual"):
            equipments = EquipmentRepository.list_all()
            users = UserRepository.list_all()
            
            eq_map = {f"{e['codigo_tag']} - {e['marca_modelo']}": e["id"] for e in equipments}
            u_map = {f"{u['nombre_completo']} ({u['rol']})": u["id"] for u in users}

            with st.form("form_nueva_ot"):
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    eq_choice = st.selectbox("Equipo Afectado:", list(eq_map.keys()))
                    prio_choice = st.selectbox("Nivel de Prioridad:", ["BAJA", "MEDIA", "ALTA", "CRITICA"], index=2)
                    codigo_ot = st.text_input("Código OT:", value=f"OT-2026-{datetime.now().strftime('%m%d%H%M')}")
                with f_col2:
                    asig_choice = st.selectbox("Técnico / Ingeniero Asignado:", list(u_map.keys()))
                    titulo = st.text_input("Título de la Intervención:", placeholder="ej. Recambio de manguera hidráulica y purga")
                
                desc = st.text_area("Descripción detallada del trabajo a realizar:", placeholder="Indique síntomas detectados, repuestos requeridos y medidas de seguridad...")
                
                submitted = st.form_submit_button("Crear Orden de Trabajo", type="primary")
                if submitted:
                    if not titulo or not desc:
                        st.warning("Por favor complete el título y la descripción.")
                    else:
                        ot_id = WorkOrderRepository.create(
                            codigo_ot=codigo_ot,
                            equipo_id=eq_map[eq_choice],
                            prediccion_id=None,
                            prioridad=prio_choice,
                            titulo=titulo,
                            descripcion=desc,
                            asignado_a=u_map[asig_choice]
                        )
                        st.success(f"Orden de trabajo creada con éxito (ID: {ot_id})!")
                        st.rerun()

    # 5. Filtro y Listado de Órdenes de Trabajo
    st.subheader("📋 Padrón de Órdenes de Trabajo Registradas en PostgreSQL")
    filtro_estado = st.selectbox("Filtrar por Estado:", ["TODAS", "PENDIENTE", "EN_PROGRESO", "COMPLETADA"])
    
    ots = WorkOrderRepository.list_all(estado=None if filtro_estado == "TODAS" else filtro_estado)

    if ots:
        for ot in ots:
            prio_color = "#EF4444" if ot["prioridad"] == "CRITICA" else ("#F59E0B" if ot["prioridad"] == "ALTA" else "#10B981")
            status_badge = "🟡 Pendiente" if ot["estado"] == "PENDIENTE" else ("🔵 En Progreso" if ot["estado"] == "EN_PROGRESO" else "🟢 Completada")

            with st.container(border=True):
                oc1, oc2 = st.columns([3, 1])
                with oc1:
                    st.markdown(f"#### {ot['codigo_ot']} — {ot['titulo']}")
                    st.markdown(f"**Equipo:** `{ot.get('codigo_tag')}` ({ot.get('marca_modelo')}) | **Ubicación:** {ot.get('ubicacion_tajo')}")
                    st.markdown(f"**Prioridad:** <span style='color:{prio_color}; font-weight:bold;'>{ot['prioridad']}</span> | **Asignado a:** {ot.get('asignado_nombre', 'Sin Asignar')} | **Fecha:** {str(ot.get('fecha_creacion'))[:16]}", unsafe_allow_html=True)
                    st.markdown(f"*{ot['descripcion']}*")
                    if ot.get("acciones_tomadas"):
                        st.markdown(f"**Acciones de Cierre:** `{ot['acciones_tomadas']}`")
                
                with oc2:
                    st.markdown(f"**Estado:** {status_badge}")
                    if user_has_permission("WORK_ORDERS_MANAGE"):
                        if ot["estado"] == "PENDIENTE":
                            if st.button("▶️ Iniciar Trabajo", key=f"btn_init_{ot['id']}", use_container_width=True):
                                WorkOrderRepository.update_status(ot["id"], "EN_PROGRESO")
                                st.rerun()
                        elif ot["estado"] == "EN_PROGRESO":
                            acciones = st.text_input("Acciones tomadas:", key=f"acc_{ot['id']}", placeholder="Detalle el trabajo realizado...")
                            if st.button("✅ Cerrar OT", key=f"btn_close_{ot['id']}", use_container_width=True, type="primary"):
                                WorkOrderRepository.update_status(ot["id"], "COMPLETADA", acciones_tomadas=acciones)
                                st.rerun()
    else:
        st.info("No se encontraron órdenes de trabajo para este criterio.")

    # 6. Pie de Navegación del Flujo
    render_step_footer("WORK_ORDERS")
