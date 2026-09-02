"""
Vista de Autenticación y Login con soporte RBAC.
"""
import streamlit as st
from database.repositories.user_repo import UserRepository
from auth.security import verify_password
from auth.session import login_user

def render_login_view():
    st.markdown("""
        <style>
        .login-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 2rem;
            margin-top: 1rem;
        }
        .main-header {
            text-align: center;
            color: #0F766E;
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            text-align: center;
            color: #64748B;
            font-size: 1rem;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='main-header'>⛏️ MinePredMaint AI</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-header'>Gestión de Mantenimiento Predictivo para Equipos de Carguío Minero<br/><b>Universidad Nacional de Trujillo — Ingeniería de Software II</b></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.subheader("🔐 Iniciar Sesión en el Sistema")
            username = st.text_input("Usuario", placeholder="ej. admin, ingeniero, operador, auditor")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")

            if st.button("Ingresar", type="primary", use_container_width=True):
                if not username or not password:
                    st.warning("Por favor ingrese su usuario y contraseña.")
                else:
                    user = UserRepository.get_by_username(username.strip())
                    if user and user["activo"] and verify_password(password, user["password_hash"]):
                        UserRepository.update_last_login(user["id"])
                        login_user(user)
                        st.success(f"¡Bienvenido, {user['nombre_completo']} ({user['rol']})!")
                        st.rerun()
                    else:
                        st.error("Credenciales inválidas o cuenta desactivada. Intente de nuevo.")

            st.divider()
            st.markdown("##### ⚡ Acceso Rápido Demo (4 Roles Requeridos):")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("👑 Administrador", use_container_width=True):
                    user = UserRepository.get_by_username("admin")
                    if user:
                        login_user(user)
                        st.rerun()
                if st.button("👷 Ing. Mantenimiento", use_container_width=True):
                    user = UserRepository.get_by_username("ingeniero")
                    if user:
                        login_user(user)
                        st.rerun()
            with c2:
                if st.button("🕹️ Operador de Planta", use_container_width=True):
                    user = UserRepository.get_by_username("operador")
                    if user:
                        login_user(user)
                        st.rerun()
                if st.button("🔍 Auditor / Analista", use_container_width=True):
                    user = UserRepository.get_by_username("auditor")
                    if user:
                        login_user(user)
                        st.rerun()
