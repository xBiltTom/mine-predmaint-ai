"""
Repositorio para almacenamiento y consulta de predicciones de IA y modelos entrenados.
"""
import json
from typing import Optional, List, Dict, Any
from database.connection import execute_query, get_db_cursor

class PredictionRepository:
    @staticmethod
    def save_model(nombre: str, tipo_arq: str, version: str, metricas: dict,
                   hiperparametros: dict, ruta_archivo: str, usuario_id: Optional[int] = None,
                   es_activo: bool = True) -> int:
        if es_activo:
            # Desactivar todos los modelos anteriores para que solo haya uno activo globalmente
            execute_query("UPDATE modelos_entrenados SET es_activo = FALSE;", commit=True, fetch="none")
        
        sql = """
            INSERT INTO modelos_entrenados (
                nombre_algoritmo, tipo_arquitectura, version, metricas,
                hiperparametros, ruta_archivo, es_activo, usuario_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (
                nombre, tipo_arq, version, json.dumps(metricas),
                json.dumps(hiperparametros), ruta_archivo, es_activo, usuario_id
            ))
            return cursor.fetchone()["id"]

    @staticmethod
    def set_active_model(model_id: int):
        """Activa un modelo específico y desactiva todos los demás."""
        execute_query("UPDATE modelos_entrenados SET es_activo = FALSE;", commit=True, fetch="none")
        execute_query("UPDATE modelos_entrenados SET es_activo = TRUE WHERE id = %s;", (model_id,), commit=True, fetch="none")

    @staticmethod
    def list_models() -> List[Dict[str, Any]]:
        sql = """
            SELECT m.*, u.nombre_completo AS entrenador_por
            FROM modelos_entrenados m
            LEFT JOIN usuarios u ON m.usuario_id = u.id
            ORDER BY m.created_at DESC;
        """
        return execute_query(sql, fetch="all")

    @staticmethod
    def get_active_model() -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM modelos_entrenados WHERE es_activo = TRUE ORDER BY created_at DESC LIMIT 1;"
        return execute_query(sql, fetch="one")

    @staticmethod
    def insert_prediction(equipo_id: int, modelo_id: Optional[int], prob_falla: float,
                          estado_predicho: str, tipo_falla_estimada: str, nivel_criticidad: str,
                          rtv_horas: Optional[float], factores_riesgo: dict, recomendacion: str) -> int:
        sql = """
            INSERT INTO predicciones_mantenimiento (
                equipo_id, modelo_id, prob_falla, estado_predicho, tipo_falla_estimada,
                nivel_criticidad, rtv_horas_estimadas, factores_riesgo, recomendacion_tecnica
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (
                equipo_id, modelo_id, prob_falla, estado_predicho, tipo_falla_estimada,
                nivel_criticidad, rtv_horas, json.dumps(factores_riesgo), recomendacion
            ))
            return cursor.fetchone()["id"]

    @staticmethod
    def get_recent_predictions(limit: int = 50) -> List[Dict[str, Any]]:
        sql = """
            SELECT p.*, e.codigo_tag, e.marca_modelo, e.ubicacion_tajo,
                   m.nombre_algoritmo
            FROM predicciones_mantenimiento p
            JOIN equipos e ON p.equipo_id = e.id
            LEFT JOIN modelos_entrenados m ON p.modelo_id = m.id
            ORDER BY p.fecha_hora DESC
            LIMIT %s;
        """
        return execute_query(sql, (limit,), fetch="all")

    @staticmethod
    def get_critical_alerts_count() -> int:
        sql = """
            SELECT COUNT(*) FROM predicciones_mantenimiento
            WHERE nivel_criticidad IN ('ALTO', 'CRITICO')
              AND fecha_hora >= CURRENT_TIMESTAMP - INTERVAL '7 days';
        """
        return execute_query(sql, fetch="val") or 0
