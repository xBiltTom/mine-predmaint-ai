"""
Repositorio para telemetría de sensores industriales en tiempo real e histórica.
"""
from typing import Optional, List, Dict, Any
from database.connection import execute_query, get_db_cursor

class TelemetryRepository:
    @staticmethod
    def insert(record: Dict[str, Any]) -> int:
        sql = """
            INSERT INTO telemetria_lecturas (
                equipo_id, temp_motor_c, presion_hidraulica_psi, vibracion_rodamientos_mm_s,
                presion_aceite_psi, temp_refrigerante_c, rpm_motor, voltaje_sistema_v,
                corriente_a, desgaste_componente_hrs, falla_registrada, tipo_falla_real
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (
                record["equipo_id"],
                record["temp_motor_c"],
                record["presion_hidraulica_psi"],
                record["vibracion_rodamientos_mm_s"],
                record["presion_aceite_psi"],
                record["temp_refrigerante_c"],
                record["rpm_motor"],
                record["voltaje_sistema_v"],
                record["corriente_a"],
                record.get("desgaste_componente_hrs", 0.0),
                record.get("falla_registrada", False),
                record.get("tipo_falla_real", "NORMAL")
            ))
            return cursor.fetchone()["id"]

    @staticmethod
    def insert_batch(records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        sql = """
            INSERT INTO telemetria_lecturas (
                equipo_id, temp_motor_c, presion_hidraulica_psi, vibracion_rodamientos_mm_s,
                presion_aceite_psi, temp_refrigerante_c, rpm_motor, voltaje_sistema_v,
                corriente_a, desgaste_componente_hrs, falla_registrada, tipo_falla_real
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        data = [
            (
                r["equipo_id"],
                r["temp_motor_c"],
                r["presion_hidraulica_psi"],
                r["vibracion_rodamientos_mm_s"],
                r["presion_aceite_psi"],
                r["temp_refrigerante_c"],
                r["rpm_motor"],
                r["voltaje_sistema_v"],
                r["corriente_a"],
                r.get("desgaste_componente_hrs", 0.0),
                r.get("falla_registrada", False),
                r.get("tipo_falla_real", "NORMAL")
            )
            for r in records
        ]
        with get_db_cursor(commit=True) as cursor:
            cursor.executemany(sql, data)
            return len(data)

    @staticmethod
    def get_latest_by_equipment(equipment_id: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT t.*, e.codigo_tag, e.marca_modelo
            FROM telemetria_lecturas t
            JOIN equipos e ON t.equipo_id = e.id
            WHERE t.equipo_id = %s
            ORDER BY t.fecha_hora DESC
            LIMIT 1;
        """
        return execute_query(sql, (equipment_id,), fetch="one")

    @staticmethod
    def get_recent_history(equipment_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        if equipment_id:
            sql = """
                SELECT t.*, e.codigo_tag, e.marca_modelo
                FROM telemetria_lecturas t
                JOIN equipos e ON t.equipo_id = e.id
                WHERE t.equipo_id = %s
                ORDER BY t.fecha_hora DESC
                LIMIT %s;
            """
            return execute_query(sql, (equipment_id, limit), fetch="all")
        else:
            sql = """
                SELECT t.*, e.codigo_tag, e.marca_modelo
                FROM telemetria_lecturas t
                JOIN equipos e ON t.equipo_id = e.id
                ORDER BY t.fecha_hora DESC
                LIMIT %s;
            """
            return execute_query(sql, (limit,), fetch="all")

    @staticmethod
    def get_overall_stats() -> Dict[str, Any]:
        sql = """
            SELECT 
                COUNT(*) AS total_lecturas,
                COUNT(CASE WHEN falla_registrada = TRUE THEN 1 END) AS total_fallas,
                AVG(temp_motor_c) AS avg_temp_motor,
                AVG(presion_hidraulica_psi) AS avg_presion_hidraulica,
                AVG(vibracion_rodamientos_mm_s) AS avg_vibracion,
                AVG(presion_aceite_psi) AS avg_presion_aceite
            FROM telemetria_lecturas;
        """
        return execute_query(sql, fetch="one") or {}
