"""
Vista de Autenticación y Login con soporte RBAC y Acceso Guiado por Roles.
"""
import streamlit as st
from database.repositories.user_repo import UserRepository
from auth.security import verify_password
from auth.session import login_user

def render_login_view():
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            color: #0F766E;
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            text-align: center;
            color: #475569;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([0.8, 2.4, 0.8])
    with col2:
        st.markdown("<div class='main-header'>⛏️ MinePredMaint AI</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-header'>Sistema Inteligente de Mantenimiento Predictivo para Equipos de Carguío Minero<br/><b>Universidad Nacional de Trujillo — IS-402 Ingeniería de Software II</b></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.subheader("🔐 Iniciar Sesión en el Sistema")
            username = st.text_input("Usuario", placeholder="ej. admin, ingeniero, operador, auditor")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")

            if st.button("Ingresar al Sistema", type="primary", use_container_width=True):
                if not username or not password:
                    st.warning("Por favor ingrese su usuario y contraseña.")
                else:
                    user = UserRepository.get_by_username(username.strip())
                    if user and user["activo"] and verify_password(password, user["password_hash"]):
                        UserRepository.update_last_login(user["id"])
                        login_user(user)
                        st.session_state["selected_page"] = "1️⃣ 📊 Dashboard Ejecutivo"
                        st.success(f"¡Bienvenido, {user['nombre_completo']} ({user['rol']})!")
                        st.rerun()
                    else:
                        st.error("Credenciales inválidas o cuenta desactivada. Intente de nuevo.")

            st.divider()
            st.markdown("##### ⚡ Acceso Rápido Demo por Perfiles (1 Clic):")
            st.caption("Selecciona un rol para ingresar de inmediato y explorar su flujo de trabajo específico:")

            c1, c2 = st.columns(2)
            with c1:
                with st.container(border=True):
                    st.markdown("👑 **Administrador**<br/><small style='color:#64748B;'>Acceso total, gestión de usuarios, roles RBAC y auditoría.</small>", unsafe_allow_html=True)
                    if st.button("Entrar como Admin", use_container_width=True, key="btn_login_admin"):
                        user = UserRepository.get_by_username("admin")
                        if user:
                            login_user(user)
                            st.session_state["selected_page"] = "1️⃣ 📊 Dashboard Ejecutivo"
                            st.rerun()

                with st.container(border=True):
                    st.markdown("👷 **Ing. Mantenimiento**<br/><small style='color:#64748B;'>Flujo completo: Telemetría, IA, OTs y Reportes.</small>", unsafe_allow_html=True)
                    if st.button("Entrar como Ingeniero", type="primary", use_container_width=True, key="btn_login_ing"):
                        user = UserRepository.get_by_username("ingeniero")
                        if user:
                            login_user(user)
                            st.session_state["selected_page"] = "1️⃣ 📊 Dashboard Ejecutivo"
                            st.rerun()

            with c2:
                with st.container(border=True):
                    st.markdown("🕹️ **Operador de Planta**<br/><small style='color:#64748B;'>Monitoreo de sensores en vivo y simulación de fallas.</small>", unsafe_allow_html=True)
                    if st.button("Entrar como Operador", use_container_width=True, key="btn_login_op"):
                        user = UserRepository.get_by_username("operador")
                        if user:
                            login_user(user)
                            st.session_state["selected_page"] = "3️⃣ 📡 Telemetría en Vivo"
                            st.rerun()

                with st.container(border=True):
                    st.markdown("🔍 **Auditor / Analista**<br/><small style='color:#64748B;'>Dashboards ejecutivos, métricas y exportación de informes.</small>", unsafe_allow_html=True)
                    if st.button("Entrar como Auditor", use_container_width=True, key="btn_login_aud"):
                        user = UserRepository.get_by_username("auditor")
                        if user:
                            login_user(user)
                            st.session_state["selected_page"] = "1️⃣ 📊 Dashboard Ejecutivo"
                            st.rerun()
