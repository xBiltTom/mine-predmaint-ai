# ⛏️ MinePredMaint AI: Sistema Web de Mantenimiento Predictivo con IA para Carguío Minero

**Universidad Nacional de Trujillo**  
**Facultad de Ciencias Físicas y Matemáticas**  
**Escuela Profesional de Ingeniería de Sistemas**  
**Curso:** Ingeniería de Software II (IS-402) — Semestre 2026 - II  
**Práctica de Laboratorio N° 02**  

---

## 📖 Descripción General
**MinePredMaint AI** es una solución web empresarial desarrollada bajo principios de arquitectura limpia y la metodología **CRISP-DM** (*Cross-Industry Standard Process for Data Mining*), diseñada para optimizar la confiabilidad operacional y predecir fallas críticas en equipos pesados de carguío minero a tajo abierto (**Palas Eléctricas de Cable Komatsu P&H 4100XPC / CAT 7495**, **Palas Hidráulicas Hitachi EX5600** y **Cargadores Frontales CAT 994K / Komatsu WA1200**).

El sistema procesa telemetría continua de sensores industriales (temperaturas térmicas, presiones hidráulicas, vibraciones mecánicas triaxiales, presión de aceite, régimen de RPM y corrientes eléctricas), ejecuta diagnósticos predictivos con estimación de **RUL (Remaining Useful Life)** y gestiona automáticamente el ciclo de vida de **Órdenes de Trabajo (OT)** de mantenimiento preventivo.

---

## 🏛️ Arquitectura del Sistema

```
mine-predmaint-ai/
├── app.py                          # Punto de entrada principal y enrutador RBAC en Streamlit
├── config/
│   ├── settings.py                 # Parámetros de PostgreSQL, JWT, umbrales de sensores mineros
│   └── permissions.py              # Matriz de permisos RBAC para los 4 roles requeridos
├── database/
│   ├── schema.sql                  # DDL de PostgreSQL con 11 tablas relacionales normalizadas
│   ├── connection.py               # Pool de conexiones psycopg2 resiliente y transaccional
│   ├── seed.py                     # Script de población (roles, permisos, usuarios, flota, sensores, OTs)
│   ├── populate_telemetry.py       # Carga de telemetría histórica inicial en PostgreSQL
│   └── repositories/               # Capa de Acceso a Datos (DAL / Repository Pattern)
│       ├── user_repo.py            # CRUD de usuarios, roles y autenticación
│       ├── equipment_repo.py       # Gestión de flota de carguío y catálogo de sensores
│       ├── telemetry_repo.py       # Almacenamiento y consulta de series de tiempo de sensores
│       ├── prediction_repo.py      # Registro de modelos serializados y predicciones IA
│       ├── work_order_repo.py      # Ciclo de vida de Órdenes de Trabajo (OT)
│       └── audit_repo.py           # Trazabilidad y logs de auditoría de seguridad
├── auth/
│   ├── security.py                 # Hashing de contraseñas con bcrypt (salteado) y tokens PyJWT
│   └── session.py                  # Manejo de estado de sesión y guards de navegación en Streamlit
├── data/
│   ├── dataset_generator.py        # Generador industrial hiperrealista (benchmark UCI AI4I enriquecido)
│   ├── preprocessor.py             # CRISP-DM Data Prep: escalado robusto, ventanas y SMOTE
│   └── datasets/                   # CSV de telemetría minera (10,000 registros, 9 variables)
├── models/
│   ├── base_model.py               # Clase base abstracta BasePredictiveModel y cálculo de métricas
│   ├── traditional/                # 3 Algoritmos Tradicionales de Machine Learning
│   │   ├── random_forest.py        # Random Forest Classifier
│   │   ├── xgboost_model.py        # XGBoost Classifier
│   │   └── svm_model.py            # Support Vector Machine con kernel RBF y calibración
│   ├── hybrid/                     # 2 Arquitecturas Híbridas de Deep Learning
│   │   ├── cnn_lstm.py             # 1D-CNN + LSTM para series temporales de sensores
│   │   └── lstm_ae_rf.py           # LSTM-Autoencoder no supervisado + Random Forest
│   ├── evaluation.py               # Stratified K-Fold (5 folds), curvas ROC y Precision-Recall
│   ├── statistical_tests.py        # Pruebas de hipótesis: Wilcoxon Signed-Rank y Paired t-Test
│   └── model_registry.py          # Serialización (.joblib/.pt), inferencia y cálculo de RUL
├── reports/
│   ├── pdf_generator.py            # Reporte Ejecutivo formal con ReportLab (membrete UNT, tablas)
│   ├── docx_generator.py           # Informe Técnico editable en Microsoft Word (.docx) con python-docx
│   └── excel_generator.py          # Sábana analítica multihistorial en Excel (.xlsx) con openpyxl
├── views/                          # Vistas interactivas modulares de Streamlit
│   ├── login_view.py               # Login seguro con accesos rápidos demo para los 4 roles
│   ├── dashboard_view.py           # KPIs ejecutivos (OEE, MTBF, MTTR, Alertas) y gráficos Plotly
│   ├── eda_view.py                 # CRISP-DM EDA: correlaciones, histogramas, boxplots y outliers
│   ├── telemetry_view.py           # Monitoreo en vivo y Simulador de Streaming a PostgreSQL
│   ├── ml_lab_view.py              # Laboratorio IA: comparación de 5 modelos y pruebas estadísticas
│   ├── work_orders_view.py         # Tablero y flujo de estados de Órdenes de Trabajo
│   ├── reports_view.py             # Generación y descarga directa en PDF, Word y Excel
│   └── admin_view.py               # Gestión de usuarios, matriz RBAC y visor de auditoría
├── docs/                           # Documentación completa de usuario y metodológica
│   ├── MANUAL_DE_USUARIO.md        # Guía detallada: qué hace cada botón, métrica y acción
│   ├── GUIA_METODOLOGICA_CRISP_DM.md # Fundamentación de IA, matemáticas y metodología CRISP-DM
│   └── ROLES_Y_PERMISOS.md         # Matriz RBAC, credenciales y flujo de trabajo entre roles
├── train_colab_pipeline.py         # Script autónomo optimizado para GPU CUDA (Google Colab)
├── tests/                          # Suite de pruebas automatizadas con pytest (15 tests)
└── requirements.txt                # Especificación de dependencias del proyecto
```

---

## 📚 Documentación de Usuario y Guías del Sistema

Para consultar el detalle de cada pantalla, botón, fórmula o flujo de trabajo, revisa los documentos en la carpeta `docs/`:

1. 📘 **[Manual de Usuario (MANUAL_DE_USUARIO.md)](file:///home/bilton/Universidad/CICLO-VIII/ING-SOFTWARE-II/SESION-02/mine-predmaint-ai/docs/MANUAL_DE_USUARIO.md):** Guía exhaustiva pantalla por pantalla. Explica qué es cada KPI (MTBF, MTTR, OEE), qué hacen los botones del simulador, cómo se interpretan los gráficos y cómo se cierran las órdenes de trabajo.
2. 🔬 **[Guía Metodológica CRISP-DM (GUIA_METODOLOGICA_CRISP_DM.md)](file:///home/bilton/Universidad/CICLO-VIII/ING-SOFTWARE-II/SESION-02/mine-predmaint-ai/docs/GUIA_METODOLOGICA_CRISP_DM.md):** Explicación de las 6 fases de CRISP-DM, arquitectura de los 5 modelos de IA (Random Forest, XGBoost, SVM, CNN-LSTM, Autoencoder) y pruebas estadísticas de Wilcoxon y t-Student.
3. 👥 **[Matriz de Roles y Permisos (ROLES_Y_PERMISOS.md)](file:///home/bilton/Universidad/CICLO-VIII/ING-SOFTWARE-II/SESION-02/mine-predmaint-ai/docs/ROLES_Y_PERMISOS.md):** Matriz RBAC completa, credenciales de los 4 perfiles y guía de flujo operativo paso a paso (desde que el operador detecta la anomalía hasta que el auditor descarga los reportes).

---

## 🗄️ Modelo Relacional de Base de Datos (PostgreSQL)

Se diseñaron e implementaron **11 tablas relacionales en 3FN** (superando el mínimo de 8 tablas exigido):

| N° | Tabla | Descripción |
| :---: | :--- | :--- |
| **1** | `roles` | Catálogo de perfiles jerárquicos (Administrador, Ing. Mantenimiento, Operador, Auditor). |
| **2** | `permisos` | Catálogo de permisos granulares por módulo funcional. |
| **3** | `rol_permisos` | Tabla puente N:M para la matriz de control de acceso RBAC. |
| **4** | `usuarios` | Cuentas de usuario con contraseña cifrada mediante `bcrypt` y flags de estado. |
| **5** | `equipos` | Catálogo de palas eléctricas, hidráulicas y cargadores (TAG, modelo, tajo, horas). |
| **6** | `sensores` | Instrumentación de sensores por equipo (unidad, rangos normales, umbral crítico). |
| **7** | `telemetria_lecturas` | Series temporales continuas de sensores (temp, presión, vibración, RPM, etc.). |
| **8** | `modelos_entrenados` | Registro de metadatos, hiperparámetros, métricas y versionado de modelos CRISP-DM. |
| **9** | `predicciones_mantenimiento` | Diagnósticos emitidos por la IA, probabilidades de falla, RUL estimado y criticidad. |
| **10** | `ordenes_trabajo` | Órdenes de trabajo preventivas y correctivas asociadas a predicciones de falla. |
| **11** | `auditoria_logs` | Trazabilidad forense de todas las acciones críticas ejecutadas en el sistema. |

---

## 🔐 Matriz de Control de Acceso RBAC (4 Roles)

El sistema incluye 4 cuentas de demostración preconfiguradas con contraseñas seguras hasheadas en `bcrypt`:

| Rol | Usuario | Contraseña | Alcance de Permisos |
| :--- | :---: | :---: | :--- |
| **Administrador** | `admin` | `admin123` | **Acceso Total:** Usuarios, roles, matriz RBAC, visor de auditoría y configuración. |
| **Ingeniero de Mantenimiento** | `ingeniero` | `manto123` | Flota, entrenamiento de IA, evaluación en ML Lab, emisión/cierre de OTs y reportes. |
| **Operador de Planta** | `operador` | `planta123` | Telemetría en vivo, inyector/simulador de lecturas a PostgreSQL y visualización de OTs. |
| **Auditor / Analista** | `auditor` | `auditor123` | Dashboards ejecutivos, análisis EDA, logs de auditoría y exportación de reportes. |

---

## 🧠 Metodología CRISP-DM & Motor de Inteligencia Artificial

### Benchmarking de los 5 Algoritmos Evaluados:
1. **Tradicional 1:** `Random Forest Classifier` (Ensemble de árboles con MDI).
2. **Tradicional 2:** `XGBoost Classifier` (Gradient Boosting regularizado).
3. **Tradicional 3:** `Support Vector Machine (SVM RBF)` (Vectores de soporte con kernel gaussiano y probabilidades calibradas).
4. **Híbrido 1:** `CNN-LSTM` (Convolución 1D para firmas espectrales de vibración + LSTM para secuencias temporales).
5. **Híbrido 2:** `LSTM-Autoencoder + Random Forest` (Autoencoder no supervisado para espacio latente y anomalía por reconstrucción + Random Forest para clasificación de falla).

### Rigor Estadístico y Pruebas de Hipótesis:
* Validación cruzada: `StratifiedKFold(n_splits=5)` con `SMOTE` en cada fold de entrenamiento.
* **Test de Normalidad Shapiro-Wilk** sobre las diferencias de rendimiento entre modelos.
* **Wilcoxon Signed-Rank Test** y **Paired t-Test** ($p < 0.05$): Demostración científica formal de la superioridad de los modelos híbridos frente a los tradicionales.

---

## 📑 Módulo de Reportes Multiformato
* **PDF Formal (`ReportLab`):** Membrete institucional UNT, tarjetas de confiabilidad, censo de equipos de carguío, diagnósticos críticos y espacio de firma técnica.
* **Word Técnico (`python-docx`):** Informe de ingeniería detallado editable con fundamentación CRISP-DM, tablas de modelos y plan de intervención.
* **Excel Analítico (`openpyxl`):** Libro con 6 hojas (`Resumen`, `Flota`, `Telemetría`, `Diagnósticos IA`, `OTs`, `Auditoría`) con estilos corporativos y anchos de columna autoajustados.

---

## 🚀 Puesta en Marcha e Instalación Local

### 1. Requisitos Previos
* Linux / Windows con **Python 3.12** instalado (mediante `pyenv` o nativo).
* Servicio **PostgreSQL 14+** activo localmente.

### 2. Configurar Base de Datos
```bash
# Crear base de datos (si aún no existe)
psql -U postgres -c "CREATE DATABASE mine_predmaint_db;"

# Ejecutar el esquema relacional DDL (11 tablas)
psql -U postgres -d mine_predmaint_db -f database/schema.sql

# Poblar datos iniciales (roles, permisos, usuarios demo, equipos, sensores, OTs)
.venv/bin/python database/seed.py

# Cargar telemetría histórica inicial
.venv/bin/python database/populate_telemetry.py

# Entrenar y registrar el modelo activo inicial
.venv/bin/python models/train_initial_model.py
```

### 3. Ejecutar las Pruebas Automatizadas
```bash
.venv/bin/pytest -v tests/
# Resultado: 15 passed, 0 failed
```

### 4. Iniciar la Aplicación Web en Streamlit
```bash
.venv/bin/streamlit run app.py
```
La aplicación se abrirá automáticamente en: `http://localhost:8501`.

---

## ☁️ Entrenamiento GPU en Google Colab

Si deseas entrenar las redes neuronales profundas con aceleración GPU (CUDA T4 / A100):
1. Abre [Google Colab](https://colab.research.google.com/).
2. Configura el entorno de ejecución en **GPU T4**.
3. Sube el archivo `train_colab_pipeline.py`.
4. Ejecuta:
   ```bash
   !pip install xgboost imbalanced-learn reportlab python-docx openpyxl
   !python train_colab_pipeline.py
   ```
5. El script ejecutará el entrenamiento completo en GPU, calculará los p-values de Wilcoxon/t-Student y exportará los resultados en `models_exported/`.
