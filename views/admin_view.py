"""
Vista de Administración del Sistema, Matriz de Permisos RBAC y Trazabilidad de Auditoría.
"""
import streamlit as st
import pandas as pd
from database.repositories.user_repo import UserRepository
from database.repositories.audit_repo import AuditRepository
from auth.security import hash_password
from config.permissions import ROLE_PERMISSIONS_MATRIX, PERMISSIONS

def render_admin_view():
    st.title("⚙️ Administración del Sistema y Auditoría de Seguridad")
    st.markdown("Gestión de credenciales, roles RBAC y trazabilidad de eventos del sistema.")

    adm_tab1, adm_tab2, adm_tab3 = st.tabs([
        "👥 Usuarios y Credenciales",
        "🔐 Matriz de Permisos RBAC",
        "📜 Logs de Auditoría del Sistema"
    ])

    # 1. Gestión de Usuarios
    with adm_tab1:
        st.subheader("Usuarios Registrados en el Sistema")
        users = UserRepository.list_all()
        if users:
            df_u = pd.DataFrame(users)
            df_u["activo_str"] = df_u["activo"].map({True: "🟢 Activo", False: "🔴 Inactivo"})
            st.dataframe(
                df_u[["id", "username", "nombre_completo", "email", "rol", "activo_str", "ultimo_login"]],
                use_container_width=True,
                hide_index=True
            )

        st.divider()
        with st.expander("➕ Crear Nuevo Usuario del Sistema"):
            roles = UserRepository.list_roles()
            role_map = {r["nombre"]: r["id"] for r in roles}

            with st.form("form_nuevo_usuario"):
                u_col1, u_col2 = st.columns(2)
                with u_col1:
                    new_user = st.text_input("Nombre de Usuario (Login):", placeholder="ej. rquispe")
                    new_nombre = st.text_input("Nombre Completo:", placeholder="ej. Ing. Roberto Quispe")
                    new_email = st.text_input("Correo Electrónico:", placeholder="rquispe@mina-antamina.pe")
                with u_col2:
                    new_pwd = st.text_input("Contraseña Temporal:", type="password", placeholder="••••••••")
                    new_rol = st.selectbox("Rol Asignado:", list(role_map.keys()), index=1)
                
                submitted = st.form_submit_button("Registrar Usuario", type="primary")
                if submitted:
                    if not new_user or not new_pwd or not new_email:
                        st.warning("Complete todos los campos obligatorios.")
                    else:
                        pwd_hash = hash_password(new_pwd)
                        try:
                            uid = UserRepository.create(
                                username=new_user.strip().lower(),
                                nombre_completo=new_nombre.strip(),
                                email=new_email.strip().lower(),
                                password_hash=pwd_hash,
                                rol_id=role_map[new_rol]
                            )
                            AuditRepository.log(
                                usuario_id=st.session_state.get("user", {}).get("id"),
                                accion="CREACION_USUARIO",
                                tabla_afectada="usuarios",
                                registro_id=uid,
                                detalles={"nuevo_usuario": new_user, "rol": new_rol}
                            )
                            st.success(f"Usuario '{new_user}' registrado exitosamente con ID {uid}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al registrar usuario (posible usuario duplicado): {e}")

    # 2. Matriz RBAC
    with adm_tab2:
        st.subheader("Matriz de Permisos por Rol (RBAC)")
        st.markdown("Configuración de acceso granular según los 4 perfiles de usuario del sistema.")
        
        roles_list = list(ROLE_PERMISSIONS_MATRIX.keys())
        matrix_data = []
        for perm_code, perm_desc in PERMISSIONS.items():
            row = {"Código de Permiso": perm_code, "Descripción de Funcionalidad": perm_desc}
            for r in roles_list:
                row[r] = "✅" if perm_code in ROLE_PERMISSIONS_MATRIX.get(r, []) else "❌"
            matrix_data.append(row)

        st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)

    # 3. Logs de Auditoría
    with adm_tab3:
        st.subheader("Logs de Auditoría y Trazabilidad")
        logs = AuditRepository.list_recent(limit=100)
        if logs:
            df_logs = pd.DataFrame(logs)
            df_logs["fecha"] = pd.to_datetime(df_logs["created_at"]).dt.strftime('%d/%m/%Y %H:%M:%S')
            st.dataframe(
                df_logs[["id", "fecha", "username", "rol", "accion", "tabla_afectada", "registro_id", "detalles", "ip_origen"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Sin registros de auditoría recientes.")
