-- =============================================================================
-- BASE DE DATOS: mine_predmaint_db
-- Sistema de Mantenimiento Predictivo con IA para Equipos de Carguío Minero
-- Universidad Nacional de Trujillo - Ingeniería de Software II (IS-402)
-- =============================================================================

-- 1. TABLA ROLES
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    nivel_jerarquia INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA PERMISOS
CREATE TABLE IF NOT EXISTS permisos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    descripcion TEXT
);

-- 3. TABLA ROL_PERMISOS (Relación N:M)
CREATE TABLE IF NOT EXISTS rol_permisos (
    rol_id INT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permiso_id INT NOT NULL REFERENCES permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id)
);

-- 4. TABLA USUARIOS
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    nombre_completo VARCHAR(120) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol_id INT NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    ultimo_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. TABLA EQUIPOS (Carguío Minero: Palas y Cargadores)
CREATE TABLE IF NOT EXISTS equipos (
    id SERIAL PRIMARY KEY,
    codigo_tag VARCHAR(50) UNIQUE NOT NULL,
    tipo_equipo VARCHAR(60) NOT NULL,
    marca_modelo VARCHAR(80) NOT NULL,
    anio_fabricacion INT NOT NULL,
    capacidad_carga_tn NUMERIC(6, 2) NOT NULL,
    ubicacion_tajo VARCHAR(80) NOT NULL,
    estado_operativo VARCHAR(30) NOT NULL DEFAULT 'OPERATIVO',
    horas_acumuladas NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    ultimo_mantenimiento TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_estado_equipo CHECK (estado_operativo IN ('OPERATIVO', 'EN ALERTA', 'EN MANTENIMIENTO', 'FUERA DE SERVICIO'))
);

-- 6. TABLA SENSORES
CREATE TABLE IF NOT EXISTS sensores (
    id SERIAL PRIMARY KEY,
    equipo_id INT NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
    tipo_sensor VARCHAR(80) NOT NULL,
    codigo_sensor VARCHAR(50) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL,
    rango_min_normal NUMERIC(10, 2) NOT NULL,
    rango_max_normal NUMERIC(10, 2) NOT NULL,
    umbral_critico NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_equipo_codigo_sensor UNIQUE (equipo_id, codigo_sensor)
);

-- 7. TABLA TELEMETRIA_LECTURAS (Series de Tiempo Industriales)
CREATE TABLE IF NOT EXISTS telemetria_lecturas (
    id BIGSERIAL PRIMARY KEY,
    equipo_id INT NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
    fecha_hora TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    temp_motor_c NUMERIC(8, 2) NOT NULL,
    presion_hidraulica_psi NUMERIC(8, 2) NOT NULL,
    vibracion_rodamientos_mm_s NUMERIC(8, 2) NOT NULL,
    presion_aceite_psi NUMERIC(8, 2) NOT NULL,
    temp_refrigerante_c NUMERIC(8, 2) NOT NULL,
    rpm_motor NUMERIC(8, 2) NOT NULL,
    voltaje_sistema_v NUMERIC(8, 2) NOT NULL,
    corriente_a NUMERIC(8, 2) NOT NULL,
    desgaste_componente_hrs NUMERIC(8, 2) NOT NULL DEFAULT 0.0,
    falla_registrada BOOLEAN NOT NULL DEFAULT FALSE,
    tipo_falla_real VARCHAR(60) NOT NULL DEFAULT 'NORMAL'
);

-- 8. TABLA MODELOS_ENTRENADOS (Metadatos y Versionado CRISP-DM)
CREATE TABLE IF NOT EXISTS modelos_entrenados (
    id SERIAL PRIMARY KEY,
    nombre_algoritmo VARCHAR(80) NOT NULL,
    tipo_arquitectura VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    metricas JSONB NOT NULL DEFAULT '{}',
    hiperparametros JSONB NOT NULL DEFAULT '{}',
    ruta_archivo VARCHAR(255),
    es_activo BOOLEAN NOT NULL DEFAULT FALSE,
    usuario_id INT REFERENCES usuarios(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_tipo_arq CHECK (tipo_arquitectura IN ('TRADICIONAL', 'HIBRIDO'))
);

-- 9. TABLA PREDICCIONES_MANTENIMIENTO (Inferencia IA)
CREATE TABLE IF NOT EXISTS predicciones_mantenimiento (
    id BIGSERIAL PRIMARY KEY,
    equipo_id INT NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
    modelo_id INT REFERENCES modelos_entrenados(id) ON DELETE SET NULL,
    fecha_hora TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    prob_falla NUMERIC(5, 4) NOT NULL,
    estado_predicho VARCHAR(30) NOT NULL,
    tipo_falla_estimada VARCHAR(80) NOT NULL,
    nivel_criticidad VARCHAR(20) NOT NULL,
    rtv_horas_estimadas NUMERIC(8, 2),
    factores_riesgo JSONB DEFAULT '{}',
    recomendacion_tecnica TEXT,
    CONSTRAINT chk_criticidad CHECK (nivel_criticidad IN ('BAJO', 'MEDIO', 'ALTO', 'CRITICO'))
);

-- 10. TABLA ORDENES_TRABAJO (Gestión de Mantenimiento Preventivo / Correctivo)
CREATE TABLE IF NOT EXISTS ordenes_trabajo (
    id SERIAL PRIMARY KEY,
    codigo_ot VARCHAR(40) UNIQUE NOT NULL,
    equipo_id INT NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
    prediccion_id BIGINT REFERENCES predicciones_mantenimiento(id) ON DELETE SET NULL,
    prioridad VARCHAR(20) NOT NULL,
    titulo VARCHAR(160) NOT NULL,
    descripcion TEXT NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    asignado_a INT REFERENCES usuarios(id) ON DELETE SET NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_programada TIMESTAMP WITH TIME ZONE,
    fecha_cierre TIMESTAMP WITH TIME ZONE,
    acciones_tomadas TEXT,
    CONSTRAINT chk_prioridad CHECK (prioridad IN ('BAJA', 'MEDIA', 'ALTA', 'CRITICA', 'BAJO', 'MEDIO', 'ALTO', 'CRITICO')),
    CONSTRAINT chk_estado_ot CHECK (estado IN ('PENDIENTE', 'EN_PROGRESO', 'COMPLETADA', 'CANCELADA'))
);

-- 11. TABLA AUDITORIA_LOGS (Trazabilidad y Seguridad)
CREATE TABLE IF NOT EXISTS auditoria_logs (
    id BIGSERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id) ON DELETE SET NULL,
    accion VARCHAR(80) NOT NULL,
    tabla_afectada VARCHAR(80) NOT NULL,
    registro_id BIGINT,
    detalles JSONB DEFAULT '{}',
    ip_origen VARCHAR(45) DEFAULT '127.0.0.1',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDICES PARA ALTO RENDIMIENTO
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_telemetria_equipo_fecha ON telemetria_lecturas(equipo_id, fecha_hora DESC);
CREATE INDEX IF NOT EXISTS idx_telemetria_falla ON telemetria_lecturas(falla_registrada);
CREATE INDEX IF NOT EXISTS idx_predicciones_equipo_fecha ON predicciones_mantenimiento(equipo_id, fecha_hora DESC);
CREATE INDEX IF NOT EXISTS idx_ordenes_estado_prioridad ON ordenes_trabajo(estado, prioridad);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
