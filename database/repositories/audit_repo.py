"""
Repositorio para trazabilidad y auditoría de eventos del sistema.
"""
import json
from typing import Optional, List, Dict, Any
from database.connection import execute_query, get_db_cursor

class AuditRepository:
    @staticmethod
    def log(usuario_id: Optional[int], accion: str, tabla_afectada: str,
            registro_id: Optional[int] = None, detalles: Optional[dict] = None,
            ip_origen: str = "127.0.0.1"):
        sql = """
            INSERT INTO auditoria_logs (
                usuario_id, accion, tabla_afectada, registro_id, detalles, ip_origen
            ) VALUES (%s, %s, %s, %s, %s, %s);
        """
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute(sql, (
                    usuario_id, accion, tabla_afectada, registro_id,
                    json.dumps(detalles or {}), ip_origen
                ))
        except Exception:
            # Nunca bloquear la aplicación por fallo en log de auditoría
            pass

    @staticmethod
    def list_recent(limit: int = 100) -> List[Dict[str, Any]]:
        sql = """
            SELECT a.*, u.username, u.nombre_completo, r.nombre AS rol
            FROM auditoria_logs a
            LEFT JOIN usuarios u ON a.usuario_id = u.id
            LEFT JOIN roles r ON u.rol_id = r.id
            ORDER BY a.created_at DESC
            LIMIT %s;
        """
        return execute_query(sql, (limit,), fetch="all")
