"""
Componente de Guía de Flujo y Navegación Secuencial para MinePredMaint AI.
Proporciona indicadores de progreso dinámicos según los permisos del usuario activo (RBAC),
acordeón explicativo '¿Qué hacer aquí?' y botones de navegación rápida con redirección garantizada.
"""
import streamlit as st
from auth.session import user_has_permission

# Catálogo completo de pasos del ciclo de vida predictivo
ALL_STEPS = [
    {
        "id": "DASHBOARD",
        "menu_name": "1️⃣ 📊 Dashboard Ejecutivo",
        "title": "Panel Ejecutivo de Monitoreo & Confiabilidad",
        "desc": "Visión global del estado de salud de la flota de carguío minero y KPIs de confiabilidad operativa.",
        "icon": "📊",
        "required_permission": "DASHBOARD_VIEW",
        "help_tips": [
            "🎯 **Objetivo:** Monitorear disponibilidad de flota (MTBF, MTTR), identificar equipos en alerta y revisar OTs pendientes.",
            "⚙️ **Acción Clave:** Revisa el censo de flota y las alertas predictivas automáticas generadas por el motor de IA.",
            "⏭️ **Siguiente Paso:** Ve al Análisis Exploratorio (EDA) o inspecciona directamente un equipo en Telemetría en Vivo."
        ]
    },
    {
        "id": "EDA",
        "menu_name": "2️⃣ 🔬 EDA Sensores Mineros",
        "title": "Análisis Exploratorio de Datos (EDA) - Sensores Mineros",
        "desc": "Fases 2 y 3 CRISP-DM: Distribuciones multivariables, correlaciones térmicas-mecánicas y fronteras de fallo.",
        "icon": "🔬",
        "required_permission": "EDA_EXPLORE",
        "help_tips": [
            "🎯 **Objetivo:** Comprender las correlaciones entre temperatura, presión hidráulica, vibraciones y desgaste de componentes.",
            "⚙️ **Acción Clave:** Explora los boxplots comparativos y diagramas de dispersión para observar cómo se separan las clases de falla.",
            "⏭️ **Siguiente Paso:** Monitorea las lecturas en tiempo real en Telemetría en Vivo o entrena modelos en el Laboratorio de IA."
        ]
    },
    {
        "id": "TELEMETRY",
        "menu_name": "3️⃣ 📡 Telemetría en Vivo",
        "title": "Monitoreo en Tiempo Real & Simulador de Faena",
        "desc": "Supervisión de sensores industriales en streaming e inyección interactiva de anomalías y modos de falla a PostgreSQL.",
        "icon": "📡",
        "required_permission": "TELEMETRY_VIEW",
        "help_tips": [
            "🎯 **Objetivo:** Simular la telemetría enviada por los sensores IoT de palas y cargadores hacia la base de datos.",
            "⚙️ **Acción Clave:** Inyecta una lectura normal o simula un modo de falla específico para ver la respuesta del modelo de IA en tiempo real.",
            "⏭️ **Siguiente Paso:** Tras detectar una anomalía crítica, el sistema genera una Orden de Trabajo automática."
        ]
    },
    {
        "id": "ML_LAB",
        "menu_name": "4️⃣ 🤖 Laboratorio de IA",
        "title": "Laboratorio de Inteligencia Artificial & Benchmarking",
        "desc": "Fases 4 y 5 CRISP-DM: Comparativa de 5 algoritmos (Tradicionales vs Híbridos), validación cruzada y rigor estadístico.",
        "icon": "🤖",
        "required_permission": lambda: user_has_permission("ML_VIEW_BENCHMARK") or user_has_permission("ML_TRAIN_EVALUATE"),
        "help_tips": [
            "🎯 **Objetivo:** Evaluar el desempeño de 3 modelos tradicionales y 2 híbridos.",
            "⚙️ **Acción Clave:** Revisa curvas ROC/PR, ejecuta pruebas estadísticas (Wilcoxon) y activa el modelo óptimo en producción.",
            "⏭️ **Siguiente Paso:** Utiliza el modelo activo para diagnósticos en faena y verifica las OTs."
        ]
    },
    {
        "id": "WORK_ORDERS",
        "menu_name": "5️⃣ 🛠️ Órdenes de Trabajo",
        "title": "Gestión de Órdenes de Trabajo (OT)",
        "desc": "Ciclo de mantenimiento: Asignación, ejecución técnica y cierre de intervenciones con trazabilidad.",
        "icon": "🛠️",
        "required_permission": "WORK_ORDERS_VIEW",
        "help_tips": [
            "🎯 **Objetivo:** Administrar las intervenciones técnicas recomendadas por los diagnósticos predictivos de la IA.",
            "⚙️ **Acción Clave:** Revisa las OTs automáticas, asigna personal, inicia la labor y ciérralas registrando las acciones tomadas.",
            "⏭️ **Siguiente Paso:** Genera los reportes ejecutivos para documentar la gestión."
        ]
    },
    {
        "id": "REPORTS",
        "menu_name": "6️⃣ 📑 Generador de Reportes",
        "title": "Generador de Reportes Ejecutivos & Informes Técnicos",
        "desc": "Exportación multiformato: PDF ejecutivo formal con membrete UNT, Word (.docx) técnico completo y Excel (.xlsx) analítico.",
        "icon": "📑",
        "required_permission": "REPORTS_EXPORT_PDF",
        "help_tips": [
            "🎯 **Objetivo:** Exportar la evidencia documental de confiabilidad de flota, algoritmos de IA y órdenes de trabajo.",
            "⚙️ **Acción Clave:** Descarga los reportes en PDF, Word o Excel generados con un solo clic con datos actualizados de PostgreSQL.",
            "⏭️ **Siguiente Paso:** Revisa la trazabilidad de seguridad o vuelve al Dashboard."
        ]
    },
    {
        "id": "ADMIN",
        "menu_name": "7️⃣ ⚙️ Administración & Auditoría",
        "title": "Administración del Sistema, RBAC y Auditoría",
        "desc": "Gestión de usuarios, perfiles jerárquicos (RBAC) y bitácora inmutable de auditoría para trazabilidad.",
        "icon": "⚙️",
        "required_permission": lambda: user_has_permission("USERS_MANAGE") or user_has_permission("AUDIT_VIEW"),
        "help_tips": [
            "🎯 **Objetivo:** Administrar el control de acceso basado en roles y auditar las operaciones realizadas.",
            "⚙️ **Acción Clave:** Consulta la matriz de permisos por rol o revisa los logs de auditoría.",
            "⏭️ **Siguiente Paso:** Cambia de perfil en el login o regresa al Dashboard Principal."
        ]
    }
]

def get_allowed_steps():
    """Retorna únicamente los pasos a los que tiene acceso el rol del usuario conectado."""
    allowed = []
    for step in ALL_STEPS:
        req = step["required_permission"]
        if callable(req):
            if req():
                allowed.append(step)
        elif isinstance(req, str):
            if user_has_permission(req):
                allowed.append(step)
    return allowed

def navigate_to(step_menu_name: str):
    """
    Cambia de página programáticamente en la sesión de Streamlit
    actualizando la variable de estado seleccionada y disparando rerun.
    """
    st.session_state["selected_page"] = step_menu_name
    st.rerun()

def render_step_header(step_id: str):
    """
    Renderiza el encabezado del paso, barra de progreso del flujo de trabajo,
    título, subtítulo y acordeón explicativo '¿Qué hacer aquí?'.
    """
    allowed_steps = get_allowed_steps()
    step_info = next((s for s in ALL_STEPS if s["id"] == step_id), ALL_STEPS[0])
    
    current_index = 1
    for idx, s in enumerate(allowed_steps):
        if s["id"] == step_id:
            current_index = idx + 1
            break
            
    total_steps = len(allowed_steps)
    progress_pct = current_index / total_steps if total_steps > 0 else 1.0

    st.markdown(f"""
        <div style="background-color: #F1F5F9; border-radius: 8px; padding: 10px 14px; margin-bottom: 15px; border-left: 5px solid #0F766E;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: 700; color: #0F766E; font-size: 0.9rem;">
                    🔄 FLUJO GUIADO DE MANTENIMIENTO PREDICTIVO (CRISP-DM)
                </span>
                <span style="font-size: 0.85rem; font-weight: 600; color: #475569; background-color: #E2E8F0; padding: 2px 8px; border-radius: 10px;">
                    Paso {current_index} de {total_steps}
                </span>
            </div>
            <div style="background-color: #CBD5E1; border-radius: 6px; height: 7px; overflow: hidden;">
                <div style="background-color: #0F766E; width: {int(progress_pct * 100)}%; height: 100%; border-radius: 6px; transition: width 0.3s ease;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.title(f"{step_info['icon']} {step_info['title']}")
    st.caption(step_info['desc'])

    with st.expander("💡 **Guía Rápida del Flujo: ¿Qué hacer en este paso?**", expanded=False):
        for tip in step_info["help_tips"]:
            st.markdown(f"- {tip}")

def render_step_footer(step_id: str):
    """
    Renderiza los botones de navegación inferior dinámicamente según los pasos permitidos para el usuario.
    """
    allowed_steps = get_allowed_steps()
    total_steps = len(allowed_steps)
    if total_steps == 0:
        return
        
    current_idx = 0
    for idx, s in enumerate(allowed_steps):
        if s["id"] == step_id:
            current_idx = idx
            break

    st.divider()
    col_prev, col_center, col_next = st.columns([1.5, 1, 1.5])

    with col_prev:
        if current_idx > 0:
            prev_step = allowed_steps[current_idx - 1]
            if st.button(f"⬅️ Anterior: {prev_step['menu_name']}", use_container_width=True, key=f"btn_prev_{step_id}"):
                navigate_to(prev_step["menu_name"])

    with col_center:
        st.markdown(
            f"<div style='text-align: center; color: #64748B; font-weight: 600; padding-top: 8px;'>Paso {current_idx + 1} / {total_steps}</div>",
            unsafe_allow_html=True
        )

    with col_next:
        if current_idx < total_steps - 1:
            next_step = allowed_steps[current_idx + 1]
            if st.button(f"➡️ Siguiente: {next_step['menu_name']}", type="primary", use_container_width=True, key=f"btn_next_{step_id}"):
                navigate_to(next_step["menu_name"])
        else:
            first_step = allowed_steps[0]
            if st.button(f"🔄 Volver al Inicio ({first_step['menu_name']})", type="primary", use_container_width=True, key=f"btn_restart_{step_id}"):
                navigate_to(first_step["menu_name"])
