"""
Repositorio para equipos de carguío minero y sensores asociados.
"""
from typing import Optional, List, Dict, Any
from database.connection import execute_query, get_db_cursor

class EquipmentRepository:
    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        sql = """
            SELECT id, codigo_tag, tipo_equipo, marca_modelo, anio_fabricacion,
                   capacidad_carga_tn, ubicacion_tajo, estado_operativo,
                   horas_acumuladas, ultimo_mantenimiento, created_at
            FROM equipos
            ORDER BY id ASC;
        """
        return execute_query(sql, fetch="all")

    @staticmethod
    def get_by_id(equipment_id: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT id, codigo_tag, tipo_equipo, marca_modelo, anio_fabricacion,
                   capacidad_carga_tn, ubicacion_tajo, estado_operativo,
                   horas_acumuladas, ultimo_mantenimiento, created_at
            FROM equipos
            WHERE id = %s;
        """
        return execute_query(sql, (equipment_id,), fetch="one")

    @staticmethod
    def get_by_tag(codigo_tag: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT id, codigo_tag, tipo_equipo, marca_modelo, anio_fabricacion,
                   capacidad_carga_tn, ubicacion_tajo, estado_operativo,
                   horas_acumuladas, ultimo_mantenimiento, created_at
            FROM equipos
            WHERE codigo_tag = %s;
        """
        return execute_query(sql, (codigo_tag,), fetch="one")

    @staticmethod
    def create(codigo_tag: str, tipo_equipo: str, marca_modelo: str, anio_fabricacion: int,
               capacidad_carga_tn: float, ubicacion_tajo: str, estado_operativo: str = "OPERATIVO") -> int:
        sql = """
            INSERT INTO equipos (codigo_tag, tipo_equipo, marca_modelo, anio_fabricacion,
                                 capacidad_carga_tn, ubicacion_tajo, estado_operativo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (codigo_tag, tipo_equipo, marca_modelo, anio_fabricacion,
                                 capacidad_carga_tn, ubicacion_tajo, estado_operativo))
            return cursor.fetchone()["id"]

    @staticmethod
    def update_status(equipment_id: int, nuevo_estado: str):
        sql = "UPDATE equipos SET estado_operativo = %s WHERE id = %s;"
        execute_query(sql, (nuevo_estado, equipment_id), commit=True, fetch="none")

    @staticmethod
    def update_operating_hours(equipment_id: int, additional_hours: float):
        sql = "UPDATE equipos SET horas_acumuladas = horas_acumuladas + %s WHERE id = %s;"
        execute_query(sql, (additional_hours, equipment_id), commit=True, fetch="none")

    @staticmethod
    def list_sensors(equipment_id: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT id, equipo_id, tipo_sensor, codigo_sensor, unidad_medida,
                   rango_min_normal, rango_max_normal, umbral_critico
            FROM sensores
            WHERE equipo_id = %s
            ORDER BY id ASC;
        """
        return execute_query(sql, (equipment_id,), fetch="all")

    @staticmethod
    def create_sensor(equipo_id: int, tipo_sensor: str, codigo_sensor: str, unidad_medida: str,
                      rango_min: float, rango_max: float, umbral_critico: float) -> int:
        sql = """
            INSERT INTO sensores (equipo_id, tipo_sensor, codigo_sensor, unidad_medida,
                                  rango_min_normal, rango_max_normal, umbral_critico)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (equipo_id, tipo_sensor, codigo_sensor, unidad_medida,
                                 rango_min, rango_max, umbral_critico))
            return cursor.fetchone()["id"]
