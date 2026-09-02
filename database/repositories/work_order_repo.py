"""
Repositorio para la gestión de órdenes de trabajo (OT) derivadas de predicciones de IA.
"""
from typing import Optional, List, Dict, Any
from database.connection import execute_query, get_db_cursor

class WorkOrderRepository:
    @staticmethod
    def create(codigo_ot: str, equipo_id: int, prediccion_id: Optional[int],
               prioridad: str, titulo: str, descripcion: str, asignado_a: Optional[int],
               fecha_programada: Optional[str] = None) -> int:
        sql = """
            INSERT INTO ordenes_trabajo (
                codigo_ot, equipo_id, prediccion_id, prioridad, titulo,
                descripcion, asignado_a, fecha_programada
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        prio_norm = str(prioridad).upper().strip()
        if prio_norm in ["CRITICO", "CRÍTICO", "CRITICA", "CRÍTICA"]:
            prio_norm = "CRITICA"
        elif prio_norm in ["ALTO", "ALTA"]:
            prio_norm = "ALTA"
        elif prio_norm in ["MEDIO", "MEDIA"]:
            prio_norm = "MEDIA"
        elif prio_norm in ["BAJO", "BAJA"]:
            prio_norm = "BAJA"
        else:
            prio_norm = "MEDIA"

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (
                codigo_ot, equipo_id, prediccion_id, prio_norm, titulo,
                descripcion, asignado_a, fecha_programada
            ))
            return cursor.fetchone()["id"]

    @staticmethod
    def list_all(estado: Optional[str] = None) -> List[Dict[str, Any]]:
        if estado:
            sql = """
                SELECT ot.*, e.codigo_tag, e.marca_modelo, e.ubicacion_tajo,
                       u.nombre_completo AS asignado_nombre
                FROM ordenes_trabajo ot
                JOIN equipos e ON ot.equipo_id = e.id
                LEFT JOIN usuarios u ON ot.asignado_a = u.id
                WHERE ot.estado = %s
                ORDER BY ot.fecha_creacion DESC;
            """
            return execute_query(sql, (estado,), fetch="all")
        else:
            sql = """
                SELECT ot.*, e.codigo_tag, e.marca_modelo, e.ubicacion_tajo,
                       u.nombre_completo AS asignado_nombre
                FROM ordenes_trabajo ot
                JOIN equipos e ON ot.equipo_id = e.id
                LEFT JOIN usuarios u ON ot.asignado_a = u.id
                ORDER BY ot.fecha_creacion DESC;
            """
            return execute_query(sql, fetch="all")

    @staticmethod
    def update_status(ot_id: int, nuevo_estado: str, acciones_tomadas: Optional[str] = None):
        if nuevo_estado == "COMPLETADA":
            sql = """
                UPDATE ordenes_trabajo
                SET estado = %s, fecha_cierre = CURRENT_TIMESTAMP, acciones_tomadas = COALESCE(%s, acciones_tomadas)
                WHERE id = %s;
            """
            execute_query(sql, (nuevo_estado, acciones_tomadas, ot_id), commit=True, fetch="none")
        else:
            sql = """
                UPDATE ordenes_trabajo
                SET estado = %s, acciones_tomadas = COALESCE(%s, acciones_tomadas)
                WHERE id = %s;
            """
            execute_query(sql, (nuevo_estado, acciones_tomadas, ot_id), commit=True, fetch="none")

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        sql = """
            SELECT 
                COUNT(*) AS total_ots,
                COUNT(CASE WHEN estado = 'PENDIENTE' THEN 1 END) AS pendientes,
                COUNT(CASE WHEN estado = 'EN_PROGRESO' THEN 1 END) AS en_progreso,
                COUNT(CASE WHEN estado = 'COMPLETADA' THEN 1 END) AS completadas,
                COUNT(CASE WHEN prioridad = 'CRITICA' THEN 1 END) AS criticas
            FROM ordenes_trabajo;
        """
        return execute_query(sql, fetch="one") or {}
