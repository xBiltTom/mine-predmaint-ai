# 👥 Matriz de Roles, Permisos y Flujos de Trabajo (RBAC)

**Sistema Web de Mantenimiento Predictivo con Inteligencia Artificial para Equipos de Carguío Minero**  
*Universidad Nacional de Trujillo — Ingeniería de Software II (IS-402)*  

---

## 🎯 Resumen de los 4 Roles Requeridos

El sistema implementa **Control de Acceso Basado en Roles (RBAC)** con 4 perfiles claramente diferenciados:

```
                  ┌───────────────────────────────────┐
                  │          ADMINISTRADOR            │
                  │   (Acceso Total, Usuarios, Logs)  │
                  └─────────────────┬─────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
┌────────┴─────────────┐ ┌──────────┴──────────┐ ┌─────────────┴────────────┐
│ ING. DE MANTENIMIENTO│ │  OPERADOR DE PLANTA │ │    AUDITOR / ANALISTA    │
│  (Flota, IA, OTs,    │ │ (Telemetría en Vivo,│ │(Dashboards, EDA, Reportes│
│     Reportes)        │ │ Simulación de Faena)│ │      y Auditoría)        │
└──────────────────────┘ └─────────────────────┘ └──────────────────────────┘
```

---

## 🔑 Credenciales de Acceso Demo

Todas las cuentas se encuentran precargadas en la base de datos PostgreSQL con contraseñas hasheadas mediante `bcrypt`:

| Rol | Usuario | Contraseña | Nombre Completo | Correo Institucional |
| :--- | :---: | :---: | :--- | :--- |
| **Administrador** | `admin` | `admin123` | Ing. Administrador de Sistemas | `admin@mina-antamina.pe` |
| **Ingeniero de Mantenimiento** | `ingeniero` | `manto123` | Ing. Carlos Mendoza (Jefe Mantenimiento) | `carlos.mendoza@mina-antamina.pe` |
| **Operador de Planta** | `operador` | `planta123` | Tec. Jorge Huamán (Operador Sala Control) | `jorge.huaman@mina-antamina.pe` |
| **Auditor / Analista** | `auditor` | `auditor123` | Lic. María Fernandez (Auditora Operaciones) | `maria.fernandez@mina-antamina.pe` |

---

## 📋 Matriz Detallada de Permisos por Módulo

| Módulo / Funcionalidad | Código de Permiso | Administrador | Ing. Mantenimiento | Operador Planta | Auditor / Analista |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Gestión de Usuarios y Roles** | `USERS_MANAGE` | ✅ Total | ❌ Sin acceso | ❌ Sin acceso | ❌ Sin acceso |
| **Visor de Auditoría del Sistema** | `AUDIT_VIEW` | ✅ Total | ❌ Sin acceso | ❌ Sin acceso | ✅ Lectura |
| **Configuración de Flota y Sensores** | `EQUIPMENT_VIEW` / `MANAGE` | ✅ Total | ✅ Total | 👁️ Solo Lectura | 👁️ Solo Lectura |
| **Dashboard de KPIs (OEE, MTBF, MTTR)**| `DASHBOARD_VIEW` | ✅ Total | ✅ Total | 👁️ KPIs Básicos | ✅ Total |
| **Análisis Exploratorio de Datos (EDA)**| `EDA_EXPLORE` | ✅ Total | ✅ Total | ❌ Sin acceso | ✅ Total |
| **Telemetría en Tiempo Real** | `TELEMETRY_VIEW` | 👁️ Visualizar | 👁️ Visualizar | ✅ Monitoreo | 👁️ Visualizar |
| **Simulador de Inyección Streaming** | `TELEMETRY_SIMULATE` | ❌ | ❌ | ✅ Inyectar/Simular | ❌ |
| **Laboratorio IA (Comparar Modelos)** | `ML_VIEW_BENCHMARK` | 👁️ Visualizar | ✅ Total | ❌ Sin acceso | 👁️ Solo Lectura |
| **Entrenar y Calibrar Modelos IA** | `ML_TRAIN_EVALUATE` | ❌ | ✅ Ejecutar | ❌ Sin acceso | ❌ Sin acceso |
| **Gestión y Creación de OTs** | `WORK_ORDERS_MANAGE` | 👁️ Visualizar | ✅ Crear / Cerrar | 👁️ Ver asignadas | 👁️ Solo Lectura |
| **Exportación de Reportes PDF/Word/Excel**| `REPORTS_EXPORT_PDF` | ✅ Total | ✅ Total | ❌ Sin acceso | ✅ Total |

---

## 🔄 Flujo Operativo Completo entre Roles (Paso a Paso)

Para una demostración completa del sistema ante el docente o evaluadores, sigue este flujo natural de trabajo:

```
[1. Operador de Planta]             [2. Motor IA en Vivo]               [3. Ing. Mantenimiento]              [4. Auditor / Gerencia]
         │                                    │                                    │                                    │
   Inyecta anomalía                     Clasifica riesgo                      Revisa la OT generada                 Descarga Reporte PDF,
   de telemetría en                     y emite alerta                        automáticamente, inicia               Word o Excel con las
   'Telemetría en Vivo'  ───────────►   crítica a PostgreSQL   ───────────►   reparación y la cierra ───────────►   métricas actualizadas
                                                                              con acciones tomadas
```

### Paso 1: El Operador de Planta detecta o simula un fallo
1. Inicia sesión como **`operador`** (o pulsa el botón rápido *"🕹️ Operador de Planta"* en el login).
2. Ve al módulo **"📡 Telemetría en Vivo"**.
3. Selecciona la pala `PALA-01`.
4. En el simulador, escoge el modo `FALLA_DESGASTE_RODAMIENTOS` y presiona **"🚨 Inyectar Anomalía de Falla"**.
5. Verás cómo los sensores de vibración se disparan al rojo (> 7.0 mm/s) y en pantalla aparece un aviso de **¡ALERTA CRÍTICA GENERADA!** informando que se creó una orden de trabajo automática.

### Paso 2: El Ingeniero de Mantenimiento atiende la orden
1. Cierra sesión y entra como **`ingeniero`** (o botón *"👷 Ing. Mantenimiento"*).
2. Entra al módulo **"🛠️ Órdenes de Trabajo"**.
3. Observarás la orden automática recién creada (ej. `OT-AUTO-PALA-01-4`) con prioridad `CRITICA` y la recomendación técnica sugerida por la IA (*"Monitorear espectro FFT de rodamientos de giro..."*).
4. Pulsa **"▶️ Iniciar"** para cambiar su estado a `EN PROGRESO`.
5. Llena el campo de acciones tomadas (ej. *"Se aplicó grasa de litio sintética y se programó cambio de rodamientos"*) y presiona **"✅ Cerrar OT"** para dejarla `COMPLETADA`.

### Paso 3: El Ingeniero revisa el Laboratorio de IA
1. En el menú lateral, abre **"🤖 Laboratorio de IA"**.
2. Consulta la tabla comparativa de los 5 algoritmos.
3. Ve a la pestaña **"Pruebas Estadísticas Robustas"** para verificar el p-value de Wilcoxon ($p < 0.05$) que certifica la ventaja del modelo híbrido.

### Paso 4: El Auditor genera los informes ejecutivos
1. Cierra sesión y entra como **`auditor`** (o botón *"🔍 Auditor / Analista"*).
2. Entra al módulo **"📑 Generador de Reportes"**.
3. Haz clic en **"📥 Descargar Reporte PDF"**, **"📥 Descargar Informe Word"** o **"📥 Descargar Sábana Excel"**.
4. Abre los archivos generados para comprobar las tablas consolidadas con la flota, predicciones, OTs y firma de aprobación.

### Paso 5: El Administrador supervisa la auditoría
1. Inicia sesión como **`admin`** (botón *"👑 Administrador"*).
2. Entra a **"⚙️ Administración & Auditoría"**.
3. Revisa la pestaña **"Logs de Auditoría"**: verás el registro con fecha y hora de todos los inicios de sesión, cambios de órdenes de trabajo y accesos realizados en los pasos anteriores.
