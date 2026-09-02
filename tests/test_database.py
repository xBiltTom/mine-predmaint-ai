"""
Pruebas automatizadas de Base de Datos y Persistencia PostgreSQL.
"""
import pytest
from database.connection import get_db_connection, execute_query
from database.repositories.user_repo import UserRepository
from database.repositories.equipment_repo import EquipmentRepository
from database.repositories.telemetry_repo import TelemetryRepository

def test_database_connection():
    """Valida la conectividad exitosa al pool de PostgreSQL."""
    with get_db_connection() as conn:
        assert conn is not None
        assert not conn.closed

def test_database_tables_exist():
    """Verifica que las 11 tablas relacionales estén creadas en la base de datos."""
    expected_tables = [
        "roles", "permisos", "rol_permisos", "usuarios", "equipos",
        "sensores", "telemetria_lecturas", "modelos_entrenados",
        "predicciones_mantenimiento", "ordenes_trabajo", "auditoria_logs"
    ]
    sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    """
    rows = execute_query(sql, fetch="all")
    actual_tables = [r["table_name"] for r in rows]
    for table in expected_tables:
        assert table in actual_tables, f"La tabla {table} no existe en la base de datos."

def test_seeded_users():
    """Verifica que los 4 usuarios de prueba para los 4 roles existan."""
    users = UserRepository.list_all()
    usernames = [u["username"] for u in users]
    assert "admin" in usernames
    assert "ingeniero" in usernames
    assert "operador" in usernames
    assert "auditor" in usernames

def test_seeded_equipments_and_sensors():
    """Verifica la carga de equipos de carguío minero y sus sensores asociados."""
    equipments = EquipmentRepository.list_all()
    assert len(equipments) >= 5
    tags = [e["codigo_tag"] for e in equipments]
    assert "PALA-01" in tags
    assert "CARG-01" in tags

    sensors = EquipmentRepository.list_sensors(equipments[0]["id"])
    assert len(sensors) >= 5
