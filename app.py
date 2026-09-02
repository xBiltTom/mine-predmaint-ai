"""
Aplicación Principal Streamlit: MinePredMaint AI.
Punto de entrada, enrutamiento modular y control de acceso basado en roles (RBAC).
Universidad Nacional de Trujillo - IS-402 Ingeniería de Software II
"""
import streamlit as st

st.set_page_config(
    page_title="MinePredMaint AI - Mantenimiento Predictivo",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from auth.session import (
    init_session, is_authenticated, get_current_user, get_current_role,
    logout_user, user_has_permission
)
from views.login_view import render_login_view
from views.dashboard_view import render_dashboard_view
from views.eda_view import render_eda_view
from views.telemetry_view import render_telemetry_view
from views.ml_lab_view import render_ml_lab_view
from views.work_orders_view import render_work_orders_view
from views.reports_view import render_reports_view
from views.admin_view import render_admin_view

def main():
    # Inicializar estado de sesión
    init_session()

    # Si no está autenticado, renderizar Login
    if not is_authenticated():
        render_login_view()
        return

    # Usuario y rol actual
    user = get_current_user()
    role = get_current_role()

    # Sidebar: Perfil de Usuario y Navegación RBAC
    with st.sidebar:
        st.markdown("## ⛏️ MinePredMaint AI")
        st.caption("Confiabilidad Operativa de Carguío Minero")
        st.divider()

        # Tarjeta de Usuario
        role_badges = {
            "Administrador": "👑 Administrador",
            "Ingeniero de Mantenimiento": "👷 Ing. Mantenimiento",
            "Operador de Planta": "🕹️ Operador Planta",
            "Auditor / Analista": "🔍 Auditor / Analista"
        }
        st.markdown(f"**Usuario:** {user.get('nombre_completo', 'Usuario')}")
        st.markdown(f"**Rol:** `{role_badges.get(role, role)}`")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout_user()
            st.rerun()

        st.divider()
        st.markdown("### 🧭 Módulos Disponibles")

        # Construir menú dinámico según permisos RBAC
        menu_options = []
        if user_has_permission("DASHBOARD_VIEW"):
            menu_options.append("📊 Dashboard Ejecutivo")
        if user_has_permission("EDA_EXPLORE"):
            menu_options.append("🔬 EDA Sensores Mineros")
        if user_has_permission("TELEMETRY_VIEW"):
            menu_options.append("📡 Telemetría en Vivo")
        if user_has_permission("ML_VIEW_BENCHMARK") or user_has_permission("ML_TRAIN_EVALUATE"):
            menu_options.append("🤖 Laboratorio de IA")
        if user_has_permission("WORK_ORDERS_VIEW"):
            menu_options.append("🛠️ Órdenes de Trabajo")
        if user_has_permission("REPORTS_EXPORT_PDF"):
            menu_options.append("📑 Generador de Reportes")
        if user_has_permission("USERS_MANAGE") or user_has_permission("AUDIT_VIEW"):
            menu_options.append("⚙️ Administración & Auditoría")

        selected_page = st.radio("Navegación:", menu_options, label_visibility="collapsed")

        st.sidebar.markdown("---")
        st.sidebar.caption("UNT - Ingeniería de Sistemas<br/>Curso: IS-402 Ing. Software II (2026)", unsafe_allow_html=True)

    # Renderizar la vista seleccionada
    if selected_page == "📊 Dashboard Ejecutivo":
        render_dashboard_view()
    elif selected_page == "🔬 EDA Sensores Mineros":
        render_eda_view()
    elif selected_page == "📡 Telemetría en Vivo":
        render_telemetry_view()
    elif selected_page == "🤖 Laboratorio de IA":
        render_ml_lab_view()
    elif selected_page == "🛠️ Órdenes de Trabajo":
        render_work_orders_view()
    elif selected_page == "📑 Generador de Reportes":
        render_reports_view()
    elif selected_page == "⚙️ Administración & Auditoría":
        render_admin_view()

if __name__ == "__main__":
    main()
