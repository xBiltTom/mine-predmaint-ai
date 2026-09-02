"""
Script de población de datos iniciales (Seed) para PostgreSQL.
Crea roles, permisos, matriz RBAC, usuarios demo, equipos mineros, sensores y OTs.
"""
import sys
import os
from pathlib import Path

# Agregar raíz al sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database.connection import get_db_cursor
from auth.security import hash_password
from config.permissions import ROLES, PERMISSIONS, ROLE_PERMISSIONS_MATRIX

def seed_database():
    print("🌱 Iniciando población de datos iniciales en PostgreSQL...")
    with get_db_cursor(commit=True) as cursor:
        # 1. Poblar Roles
        print("  -> Creando roles...")
        roles_data = [
            ("Administrador", "Acceso total a configuración, usuarios y auditoría", 1),
            ("Ingeniero de Mantenimiento", "Gestión de flota, entrenamiento de IA y órdenes de trabajo", 2),
            ("Operador de Planta", "Monitoreo en vivo, reporte de telemetría y simulación", 3),
            ("Auditor / Analista", "Inspección de dashboards, reportabilidad y trazabilidad", 3)
        ]
        role_ids = {}
        for nombre, desc, nivel in roles_data:
            cursor.execute("""
                INSERT INTO roles (nombre, descripcion, nivel_jerarquia)
                VALUES (%s, %s, %s)
                ON CONFLICT (nombre) DO UPDATE SET descripcion = EXCLUDED.descripcion, nivel_jerarquia = EXCLUDED.nivel_jerarquia
                RETURNING id, nombre;
            """, (nombre, desc, nivel))
            row = cursor.fetchone()
            role_ids[row["nombre"]] = row["id"]

        # 2. Poblar Permisos
        print("  -> Creando catálogo de permisos...")
        perm_ids = {}
        for codigo, desc in PERMISSIONS.items():
            modulo = codigo.split("_")[0]
            cursor.execute("""
                INSERT INTO permisos (codigo, modulo, descripcion)
                VALUES (%s, %s, %s)
                ON CONFLICT (codigo) DO UPDATE SET descripcion = EXCLUDED.descripcion
                RETURNING id, codigo;
            """, (codigo, modulo, desc))
            row = cursor.fetchone()
            perm_ids[row["codigo"]] = row["id"]

        # 3. Asignar Permisos a Roles (Matriz RBAC)
        print("  -> Asignando matriz de permisos por rol...")
        for rol_nombre, perms in ROLE_PERMISSIONS_MATRIX.items():
            rol_id = role_ids.get(rol_nombre)
            if rol_id:
                for p_cod in perms:
                    p_id = perm_ids.get(p_cod)
                    if p_id:
                        cursor.execute("""
                            INSERT INTO rol_permisos (rol_id, permiso_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING;
                        """, (rol_id, p_id))

        # 4. Poblar Usuarios Demo
        print("  -> Creando usuarios para cada rol...")
        users_data = [
            ("admin", "Ing. Administrador de Sistemas", "admin@mina-antamina.pe", "admin123", role_ids["Administrador"]),
            ("ingeniero", "Ing. Carlos Mendoza (Jefe Mantenimiento)", "carlos.mendoza@mina-antamina.pe", "manto123", role_ids["Ingeniero de Mantenimiento"]),
            ("operador", "Tec. Jorge Huamán (Operador Sala Control)", "jorge.huaman@mina-antamina.pe", "planta123", role_ids["Operador de Planta"]),
            ("auditor", "Lic. María Fernandez (Auditora de Operaciones)", "maria.fernandez@mina-antamina.pe", "auditor123", role_ids["Auditor / Analista"])
        ]
        user_ids = {}
        for username, nombre, email, pwd, r_id in users_data:
            pwd_hash = hash_password(pwd)
            cursor.execute("""
                INSERT INTO usuarios (username, nombre_completo, email, password_hash, rol_id, activo)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                ON CONFLICT (username) DO UPDATE
                SET nombre_completo = EXCLUDED.nombre_completo,
                    password_hash = EXCLUDED.password_hash,
                    rol_id = EXCLUDED.rol_id
                RETURNING id, username;
            """, (username, nombre, email, pwd_hash, r_id))
            row = cursor.fetchone()
            user_ids[row["username"]] = row["id"]

        # 5. Poblar Flota de Equipos de Carguío Minero
        print("  -> Creando catálogo de flota de carguío minero...")
        equipos_data = [
            ("PALA-01", "Pala Eléctrica de Cable", "Komatsu P&H 4100XPC", 2021, 105.0, "Tajo Principal - Fase 4", "OPERATIVO", 8450.0),
            ("PALA-02", "Pala Eléctrica de Cable", "CAT 7495 HD", 2020, 118.0, "Tajo Sur - Banco 32", "OPERATIVO", 12300.0),
            ("PALA-03", "Pala Hidráulica", "Hitachi EX5600-7", 2022, 85.0, "Fase Este - Frente 2", "EN ALERTA", 6320.0),
            ("CARG-01", "Cargador Frontal de Ruedas", "CAT 994K", 2019, 45.0, "Stockpile Primario Chancado", "OPERATIVO", 14500.0),
            ("CARG-02", "Cargador Frontal de Ruedas", "Komatsu WA1200-6", 2021, 40.0, "Tajo Oeste - Nivel 2800", "EN MANTENIMIENTO", 9120.0)
        ]
        equipment_ids = {}
        for tag, tipo, mod, anio, cap, tajo, est, hrs in equipos_data:
            cursor.execute("""
                INSERT INTO equipos (codigo_tag, tipo_equipo, marca_modelo, anio_fabricacion, capacidad_carga_tn, ubicacion_tajo, estado_operativo, horas_acumuladas)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (codigo_tag) DO UPDATE
                SET estado_operativo = EXCLUDED.estado_operativo,
                    horas_acumuladas = EXCLUDED.horas_acumuladas,
                    ubicacion_tajo = EXCLUDED.ubicacion_tajo
                RETURNING id, codigo_tag;
            """, (tag, tipo, mod, anio, cap, tajo, est, hrs))
            row = cursor.fetchone()
            equipment_ids[row["codigo_tag"]] = row["id"]

        # 6. Sensores para cada equipo
        print("  -> Registrando sensores en equipos...")
        sensores_base = [
            ("Temperatura de Motor", "TEMP_MOT", "°C", 60.0, 95.0, 105.0),
            ("Presión Hidráulica Principal", "PRES_HID", "PSI", 2500.0, 3800.0, 4200.0),
            ("Vibración Rodamientos Tren Potencia", "VIB_ROD", "mm/s", 0.5, 4.5, 7.0),
            ("Presión de Aceite Lubricante", "PRES_ACE", "PSI", 35.0, 75.0, 25.0),
            ("Temperatura Refrigerante", "TEMP_REF", "°C", 70.0, 92.0, 102.0),
            ("Velocidad de Giro Motor", "RPM_MOT", "RPM", 1200.0, 2100.0, 2350.0),
            ("Voltaje del Sistema Eléctrico", "VOLT_SIS", "V", 23.5, 28.5, 21.0),
            ("Corriente Eléctrica Demandada", "CORR_AMP", "A", 50.0, 280.0, 340.0)
        ]
        for eq_id in equipment_ids.values():
            for t_sen, cod, un, r_min, r_max, crit in sensores_base:
                cursor.execute("""
                    INSERT INTO sensores (equipo_id, tipo_sensor, codigo_sensor, unidad_medida, rango_min_normal, rango_max_normal, umbral_critico)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (equipo_id, codigo_sensor) DO NOTHING;
                """, (eq_id, t_sen, cod, un, r_min, r_max, crit))

        # 7. Órdenes de Trabajo de Ejemplo
        print("  -> Creando órdenes de trabajo iniciales...")
        ots = [
            ("OT-2026-001", equipment_ids["PALA-03"], "ALTA", "Inspección de bomba hidráulica y sensor de presión",
             "Se detectó oscilación anormal de presión hidráulica (picos de 4050 PSI). Se requiere cambio de filtros y calibración de válvula de alivio.",
             "EN_PROGRESO", user_ids["ingeniero"]),
            ("OT-2026-002", equipment_ids["CARG-02"], "CRITICA", "Mantenimiento preventivo mayor a 9000 hrs y recambio de sellos",
             "Mantenimiento mayor programado según catálogo del fabricante. Desarme parcial de mandos finales y recambio de sellos.",
             "PENDIENTE", user_ids["ingeniero"]),
            ("OT-2026-003", equipment_ids["PALA-01"], "MEDIA", "Alineación de acoples y lubricación de rodamientos de giro",
             "Inspección preventiva de rutina en parada semanal de chancado.",
             "COMPLETADA", user_ids["ingeniero"])
        ]
        for cod_ot, eq_id, prio, tit, desc, est, asig in ots:
            cursor.execute("""
                INSERT INTO ordenes_trabajo (codigo_ot, equipo_id, prioridad, titulo, descripcion, estado, asignado_a)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (codigo_ot) DO NOTHING;
            """, (cod_ot, eq_id, prio, tit, desc, est, asig))

        print("✅ Base de datos inicializada y poblada exitosamente.")

if __name__ == "__main__":
    seed_database()
