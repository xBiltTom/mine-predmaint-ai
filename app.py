"""
Aplicación Principal Streamlit: MinePredMaint AI.
Punto de entrada, enrutamiento modular y control de acceso basado en roles (RBAC)
con navegación guiada del ciclo de mantenimiento predictivo (CRISP-DM).
Universidad Nacional de Trujillo - IS-402 Ingeniería de Software II
"""
import sys
import streamlit as st

# Forzar recarga limpia de módulos de vistas para desarrollo ágil en Streamlit
for mod in list(sys.modules.keys()):
    if mod.startswith("views.components") or mod.startswith("views."):
        sys.modules.pop(mod, None)

st.set_page_config(
    page_title="MinePredMaint AI - Mantenimiento Predictivo",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from auth.session import (
    init_session, is_authenticated, get_current_user, get_current_role,
    logout_user
)
from views.components.flow_guide import get_allowed_steps
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
            if "selected_page" in st.session_state:
                del st.session_state["selected_page"]
            st.rerun()

        st.divider()
        st.markdown("### 🧭 Flujo del Ciclo Predictivo")

        # Construir menú dinámico basado en los pasos permitidos para el rol
        allowed_steps = get_allowed_steps()
        menu_options = [s["menu_name"] for s in allowed_steps]

        if not menu_options:
            st.warning("Su usuario no posee módulos permitidos en este momento.")
            return

        # Sincronización robusta basada en st.session_state["selected_page"]
        if "selected_page" not in st.session_state or st.session_state["selected_page"] not in menu_options:
            st.session_state["selected_page"] = menu_options[0]

        selected_idx = menu_options.index(st.session_state["selected_page"])

        # Renderizar radio widget utilizando index sin clave fija para permitir cambios programáticos
        chosen_page = st.radio(
            "Navegación:",
            menu_options,
            index=selected_idx,
            label_visibility="collapsed"
        )
        
        # Si el usuario hace clic manual en el radio button de la barra lateral
        if chosen_page != st.session_state["selected_page"]:
            st.session_state["selected_page"] = chosen_page
            st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.caption("UNT - Ingeniería de Sistemas<br/>Curso: IS-402 Ing. Software II (2026)", unsafe_allow_html=True)

    selected_page = st.session_state["selected_page"]

    # Renderizar la vista seleccionada
    if "Dashboard Ejecutivo" in selected_page:
        render_dashboard_view()
    elif "EDA Sensores Mineros" in selected_page:
        render_eda_view()
    elif "Telemetría en Vivo" in selected_page:
        render_telemetry_view()
    elif "Laboratorio de IA" in selected_page:
        render_ml_lab_view()
    elif "Órdenes de Trabajo" in selected_page:
        render_work_orders_view()
    elif "Generador de Reportes" in selected_page:
        render_reports_view()
    elif "Administración & Auditoría" in selected_page:
        render_admin_view()

if __name__ == "__main__":
    main()
