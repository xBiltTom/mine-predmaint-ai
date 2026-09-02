"""
Matriz de permisos y definición de roles RBAC para el sistema.
"""

ROLES = {
    "ADMIN": "Administrador",
    "ING_MANTENIMIENTO": "Ingeniero de Mantenimiento",
    "OPERADOR": "Operador de Planta",
    "AUDITOR": "Auditor / Analista"
}

# Permisos específicos por módulo
PERMISSIONS = {
    # Módulo Usuarios y Sistema
    "USERS_MANAGE": "Gestionar usuarios, credenciales y asignación de roles",
    "AUDIT_VIEW": "Visualizar logs de auditoría del sistema",
    
    # Módulo Equipos y Sensores
    "EQUIPMENT_VIEW": "Visualizar catálogo de equipos y sensores",
    "EQUIPMENT_MANAGE": "Crear, editar o desactivar equipos y sensores",
    
    # Módulo Telemetría y Operación
    "TELEMETRY_VIEW": "Visualizar telemetría de sensores en tiempo real",
    "TELEMETRY_SIMULATE": "Registrar lecturas e inyectar telemetría simulada",
    
    # Módulo IA y Machine Learning
    "ML_VIEW_BENCHMARK": "Ver resultados de métricas y comparativa de modelos",
    "ML_TRAIN_EVALUATE": "Entrenar modelos, ejecutar validación cruzada y pruebas estadísticas",
    "ML_PREDICT": "Ejecutar diagnósticos predictivos bajo demanda",
    
    # Módulo Órdenes de Trabajo (OT)
    "WORK_ORDERS_VIEW": "Ver órdenes de trabajo y estado operativo",
    "WORK_ORDERS_MANAGE": "Crear, priorizar, reasignar y cerrar órdenes de trabajo",
    
    # Módulo Dashboard & EDA
    "DASHBOARD_VIEW": "Visualizar KPIs de confiabilidad (MTBF, MTTR, Disponibilidad)",
    "EDA_EXPLORE": "Explorar análisis estadístico multivariable y correlaciones",
    
    # Módulo Reportabilidad
    "REPORTS_EXPORT_PDF": "Generar y descargar reportes ejecutivos en PDF",
    "REPORTS_EXPORT_DOCX": "Generar y descargar informes técnicos en Word (.docx)",
    "REPORTS_EXPORT_EXCEL": "Exportar sábanas de datos y análisis en Excel (.xlsx)"
}

# Matriz de asignación de permisos por rol
ROLE_PERMISSIONS_MATRIX = {
    "Administrador": list(PERMISSIONS.keys()),  # Acceso total
    
    "Ingeniero de Mantenimiento": [
        "EQUIPMENT_VIEW",
        "EQUIPMENT_MANAGE",
        "TELEMETRY_VIEW",
        "ML_VIEW_BENCHMARK",
        "ML_TRAIN_EVALUATE",
        "ML_PREDICT",
        "WORK_ORDERS_VIEW",
        "WORK_ORDERS_MANAGE",
        "DASHBOARD_VIEW",
        "EDA_EXPLORE",
        "REPORTS_EXPORT_PDF",
        "REPORTS_EXPORT_DOCX",
        "REPORTS_EXPORT_EXCEL"
    ],
    
    "Operador de Planta": [
        "EQUIPMENT_VIEW",
        "TELEMETRY_VIEW",
        "TELEMETRY_SIMULATE",
        "ML_PREDICT",
        "WORK_ORDERS_VIEW",
        "DASHBOARD_VIEW"
    ],
    
    "Auditor / Analista": [
        "AUDIT_VIEW",
        "EQUIPMENT_VIEW",
        "TELEMETRY_VIEW",
        "ML_VIEW_BENCHMARK",
        "WORK_ORDERS_VIEW",
        "DASHBOARD_VIEW",
        "EDA_EXPLORE",
        "REPORTS_EXPORT_PDF",
        "REPORTS_EXPORT_DOCX",
        "REPORTS_EXPORT_EXCEL"
    ]
}

def has_permission(user_role: str, permission: str) -> bool:
    """Verifica si un rol tiene un permiso determinado."""
    allowed = ROLE_PERMISSIONS_MATRIX.get(user_role, [])
    return permission in allowed
