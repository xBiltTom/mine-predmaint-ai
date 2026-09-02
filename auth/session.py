"""
Gestor de sesiones de usuario y control de acceso en Streamlit.
"""
import streamlit as st
from typing import Optional, Dict, Any
from auth.security import create_access_token, decode_access_token
from config.permissions import has_permission, ROLE_PERMISSIONS_MATRIX
from database.repositories.audit_repo import AuditRepository

def init_session():
    """Inicializa las variables de estado de sesión si no existen."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "jwt_token" not in st.session_state:
        st.session_state.jwt_token = None
    if "active_page" not in st.session_state:
        st.session_state.active_page = "dashboard"

def login_user(user_data: Dict[str, Any]):
    """Registra la sesión de un usuario autenticado y genera su JWT."""
    token = create_access_token({
        "sub": user_data["username"],
        "user_id": user_data["id"],
        "rol": user_data["rol"],
        "nombre": user_data["nombre_completo"]
    })
    st.session_state.authenticated = True
    st.session_state.user = user_data
    st.session_state.jwt_token = token
    AuditRepository.log(
        usuario_id=user_data["id"],
        accion="INICIO_SESION",
        tabla_afectada="usuarios",
        registro_id=user_data["id"],
        detalles={"username": user_data["username"], "rol": user_data["rol"]}
    )

def logout_user():
    """Cierra la sesión del usuario actual."""
    if st.session_state.get("user"):
        user = st.session_state.user
        AuditRepository.log(
            usuario_id=user.get("id"),
            accion="CIERRE_SESION",
            tabla_afectada="usuarios",
            registro_id=user.get("id")
        )
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.jwt_token = None
    st.session_state.active_page = "login"

def is_authenticated() -> bool:
    """Verifica si la sesión actual es válida y el JWT no ha expirado."""
    if not st.session_state.get("authenticated") or not st.session_state.get("jwt_token"):
        return False
    payload = decode_access_token(st.session_state.jwt_token)
    if not payload:
        logout_user()
        return False
    return True

def get_current_user() -> Optional[Dict[str, Any]]:
    """Retorna los datos del usuario logueado en la sesión."""
    return st.session_state.get("user")

def get_current_role() -> Optional[str]:
    """Retorna el rol del usuario logueado."""
    user = get_current_user()
    return user.get("rol") if user else None

def user_has_permission(permission: str) -> bool:
    """Verifica si el usuario actual posee el permiso requerido."""
    role = get_current_role()
    if not role:
        return False
    return has_permission(role, permission)
