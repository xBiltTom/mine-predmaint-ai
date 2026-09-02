"""
Repositorio para gestión de usuarios, roles y autenticación.
"""
from typing import Optional, List, Dict, Any
from database.connection import execute_query, get_db_cursor

class UserRepository:
    @staticmethod
    def get_by_username(username: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT u.id, u.username, u.nombre_completo, u.email, u.password_hash,
                   u.rol_id, r.nombre AS rol, u.activo, u.ultimo_login, u.created_at
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE u.username = %s;
        """
        return execute_query(sql, (username,), fetch="one")

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT u.id, u.username, u.nombre_completo, u.email,
                   u.rol_id, r.nombre AS rol, u.activo, u.ultimo_login, u.created_at
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE u.id = %s;
        """
        return execute_query(sql, (user_id,), fetch="one")

    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        sql = """
            SELECT u.id, u.username, u.nombre_completo, u.email,
                   r.nombre AS rol, u.activo, u.ultimo_login, u.created_at
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            ORDER BY u.id ASC;
        """
        return execute_query(sql, fetch="all")

    @staticmethod
    def create(username: str, nombre_completo: str, email: str, password_hash: str, rol_id: int) -> int:
        sql = """
            INSERT INTO usuarios (username, nombre_completo, email, password_hash, rol_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (username, nombre_completo, email, password_hash, rol_id))
            return cursor.fetchone()["id"]

    @staticmethod
    def update_last_login(user_id: int):
        sql = "UPDATE usuarios SET ultimo_login = CURRENT_TIMESTAMP WHERE id = %s;"
        execute_query(sql, (user_id,), commit=True, fetch="none")

    @staticmethod
    def update_status(user_id: int, activo: bool):
        sql = "UPDATE usuarios SET activo = %s WHERE id = %s;"
        execute_query(sql, (activo, user_id), commit=True, fetch="none")

    @staticmethod
    def list_roles() -> List[Dict[str, Any]]:
        sql = "SELECT id, nombre, descripcion, nivel_jerarquia FROM roles ORDER BY nivel_jerarquia ASC;"
        return execute_query(sql, fetch="all")

    @staticmethod
    def get_role_permissions(rol_nombre: str) -> List[str]:
        sql = """
            SELECT p.codigo
            FROM permisos p
            JOIN rol_permisos rp ON p.id = rp.permiso_id
            JOIN roles r ON rp.rol_id = r.id
            WHERE r.nombre = %s;
        """
        rows = execute_query(sql, (rol_nombre,), fetch="all")
        return [r["codigo"] for r in rows]
