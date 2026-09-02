# 📘 Manual de Usuario Integral: MinePredMaint AI

**Sistema Web de Mantenimiento Predictivo con Inteligencia Artificial para Equipos de Carguío Minero**  
*Universidad Nacional de Trujillo — Ingeniería de Software II (IS-402)*  

---

## 📑 Tabla de Contenidos
1. [Acceso al Sistema y Roles Demo](#1-acceso-al-sistema-y-roles-demo)
2. [Barra Lateral y Navegación según Rol (RBAC)](#2-barra-lateral-y-navegación-según-rol-rbac)
3. [Módulo: Dashboard Ejecutivo](#3-módulo-dashboard-ejecutivo)
4. [Módulo: EDA (Análisis Exploratorio de Datos)](#4-módulo-eda-análisis-exploratorio-de-datos)
5. [Módulo: Telemetría en Vivo y Simulador de Faena](#5-módulo-telemetría-en-vivo-y-simulador-de-faena)
6. [Módulo: Laboratorio de IA & Benchmarking](#6-módulo-laboratorio-de-ia--benchmarking)
7. [Módulo: Gestión de Órdenes de Trabajo (OT)](#7-módulo-gestión-de-órdenes-de-trabajo-ot)
8. [Módulo: Generador de Reportes (PDF, Word, Excel)](#8-módulo-generador-de-reportes-pdf-word-excel)
9. [Módulo: Administración & Auditoría](#9-módulo-administración--auditoría)

---

## 1. Acceso al Sistema y Roles Demo

Al abrir la aplicación en tu navegador (`http://localhost:8501`), lo primero que verás es la pantalla de **Inicio de Sesión**:

### ¿Qué elementos hay y qué hace cada uno?
* **Cajas de texto Usuario y Contraseña:** Permiten ingresar credenciales manuales registradas en la base de datos PostgreSQL (verificadas con cifrado `bcrypt`).
* **Botón "Ingresar":** Valida las credenciales, genera un token criptográfico de sesión (`PyJWT`) y te redirige a los módulos según tu rol.
* **Sección "⚡ Acceso Rápido Demo":** Cuatro botones diseñados para cambiar de rol con un solo clic durante exposiciones o pruebas:
  1. **👑 Administrador (`admin`):** Acceso total al sistema, auditoría y creación de usuarios.
  2. **👷 Ing. Mantenimiento (`ingeniero`):** Responsable técnico: puede entrenar modelos de IA, crear y cerrar órdenes de trabajo y generar reportes.
  3. **🕹️ Operador de Planta (`operador`):** Vista operativa: supervisa telemetría en vivo, inyecta eventos simulados y ve alertas.
  4. **🔍 Auditor / Analista (`auditor`):** Consulta dashboards, realiza análisis exploratorio (EDA), revisa logs forenses y exporta informes.

---

## 2. Barra Lateral y Navegación según Rol (RBAC)

Ubicada en el lateral izquierdo de la pantalla:

### Elementos presentes:
* **Insignia y Nombre del Usuario Activo:** Muestra quién está conectado y qué rol posee.
* **Botón "🚪 Cerrar Sesión":** Destruye el token JWT activo, limpia la memoria de sesión y te regresa al login.
* **Menú "🧭 Módulos Disponibles":** Cambia automáticamente según los permisos de tu rol:
  * Si eres **Operador**, solo verás *Dashboard*, *Telemetría* y *Órdenes de Trabajo*.
  * Si eres **Administrador**, verás los 7 módulos incluyendo *Administración & Auditoría*.

---

## 3. Módulo: Dashboard Ejecutivo

Es el centro de control principal para supervisar la salud de la flota minera de carguío (palas y cargadores).

### A. Tarjetas de Indicadores Clave (KPIs):
1. **Disponibilidad Flota (%):**
   * *¿Qué es?* Porcentaje de equipos que están actualmente en condición `OPERATIVO` frente al total de la flota.
   * *Meta:* Superior al 90%. Si cae, significa que hay equipos parados o en mantenimiento.
2. **MTBF Estimado (Mean Time Between Failures - Tiempo Medio Entre Fallas):**
   * *¿Qué es?* Promedio de horas que un equipo opera de manera continua antes de sufrir una parada no programada.
   * *Interpretación:* Mientras más alto el valor (ej. > 300 hrs), mayor es la confiabilidad del carguío.
3. **MTTR Promedio (Mean Time To Repair - Tiempo Medio de Reparación):**
   * *¿Qué es?* Promedio de horas requeridas por el equipo de mecánicos/electricistas para reparar una falla y devolver el equipo a producción.
   * *Interpretación:* Mientras más bajo sea el valor (ej. < 8 hrs), más ágil es la respuesta técnica.
4. **Equipos en Alerta:**
   * *¿Qué es?* Cantidad de palas o cargadores cuyos sensores o predicción de IA indican un riesgo inminente.
5. **OTs Pendientes:**
   * *¿Qué es?* Cantidad de órdenes de trabajo de mantenimiento abiertas que aún no han sido atendidas.

### B. Gráficos Ejecutivos:
* **Donut "Estado Operativo de la Flota":** Muestra la proporción visual de equipos en faena:
  * 🟢 **Verde (Operativo):** Trabajando con normalidad en el tajo.
  * 🟡 **Amarillo (En Alerta):** Parámetros anómalos detectados por IA; requiere inspección.
  * 🔵 **Azul (En Mantenimiento):** En taller o bahía de parada programada.
* **Barras "Nivel de Riesgo Predictivo por Equipo":**
  * Presenta el porcentaje de probabilidad de falla estimado por la IA para cada pala/cargador.
  * Colores por criticidad: Verde (Bajo: 0-20%), Azul (Medio: 21-45%), Naranja (Alto: 46-74%), Rojo (Crítico: ≥ 75%).

### C. Censo de Flota en Faena:
Tarjetas individuales de los 5 equipos mineros simulados:
* `PALA-01`: Pala Eléctrica Komatsu P&H 4100XPC (105 Ton).
* `PALA-02`: Pala Eléctrica CAT 7495 HD (118 Ton).
* `PALA-03`: Pala Hidráulica Hitachi EX5600-7 (85 Ton).
* `CARG-01`: Cargador Frontal CAT 994K (45 Ton).
* `CARG-02`: Cargador Frontal Komatsu WA1200-6 (40 Ton).
Cada tarjeta indica su ubicación en el tajo minero, horas acumuladas y estado actual.

### D. Tabla de Diagnósticos Predictivos Recientes:
Lista detallada de las últimas predicciones emitidas por el modelo de IA:
* **Prob. Falla (%):** Certeza matemática del algoritmo sobre una avería inminente.
* **Criticidad:** Grado de urgencia (`BAJO`, `MEDIO`, `ALTO`, `CRITICO`).
* **Diagnóstico Estimado:** Causa raíz identificada (ej. Falla Térmica, Pérdida de Presión Hidráulica, Desgaste de Rodamientos, Sobrecarga).
* **RUL Estimado (Remaining Useful Life):** Horas estimadas de vida útil que le quedan al componente antes de romperse definitivamente.
* **Recomendación Técnica:** Acción correctiva precisa que debe realizar el mecánico.

---

## 4. Módulo: EDA (Análisis Exploratorio de Datos)

Permite a los analistas de datos e ingenieros explorar el comportamiento estadístico de las 9 variables de sensores (CRISP-DM Fase 2 y 3).

### ¿Qué elementos contiene y qué significan?
1. **Resumen de Muestras:** Informa el tamaño del dataset (10,000 lecturas históricas) y la tasa real de fallas industriales (~6.7%).
2. **Tabla de Estadísticas Descriptivas (Desplegable):**
   * `mean` (Media): Valor promedio de operación normal del sensor.
   * `std` (Desviación Estándar): Qué tanto fluctúa el sensor en condiciones habituales.
   * `min` / `max`: Valores extremos registrados en la historia de la mina.
   * `skewness` (Asimetría): Si los datos tienen colas alargadas hacia la derecha o izquierda.
3. **Matriz de Correlación de Sensores (Heatmap Interactivo):**
   * Muestra el coeficiente de correlación de Pearson entre pares de variables (-1 a +1).
   * Un valor cercano a **+1.0 (amarillo/verde claro)** indica que cuando una variable sube, la otra también (ej. Temperatura de Motor con Temperatura de Refrigerante).
   * Ayuda a identificar qué sensores se disparan simultáneamente cuando ocurre un fallo.
4. **Distribución de Variables (Normal vs Falla):**
   * Permite elegir un sensor (ej. `vibracion_rodamientos_mm_s`) y comparar:
     * **Boxplot Comparativo:** Muestra la mediana, cuartiles y los "outliers" (puntos aislados) en color rojo para equipos que fallaron.
     * **Histograma de Distribución:** Curvas de frecuencia sobrepuestas para ver cómo se separan las lecturas sanas de las defectuosas.
5. **Diagrama de Dispersión Multivariable (Scatter Plot):**
   * Permite cruzar 2 variables cualesquiera (ej. Eje X = `desgaste_componente_hrs`, Eje Y = `vibracion_rodamientos_mm_s`).
   * Colorea los puntos según el modo de falla para visualizar las fronteras de decisión que aprende la IA.

---

## 5. Módulo: Telemetría en Vivo y Simulador de Faena

Diseñado para el **Operador de Planta / Sala de Control** para vigilar lecturas instantáneas e interactuar con la faena minera.

### A. Selector de Equipo:
Un menú desplegable para elegir qué pala o cargador frontal inspeccionar.

### B. Panel de Sensores en Tiempo Real:
Muestra las 8 lecturas del equipo seleccionado:
* **Temp. Motor (°C):** Temperatura del bloque y transmisión. Normal: 60 - 95 °C. Si pasa de 95 °C muestra alerta roja.
* **Temp. Refrigerante (°C):** Sistema de refrigeración. Normal: 70 - 92 °C.
* **Presión Hidráulica (PSI):** Circuito principal de levante y empuje de balde. Normal: 2500 - 3800 PSI.
* **Presión de Aceite (PSI):** Lubricación de motor. Si cae de 25 PSI se considera fallo crítico.
* **Vibración Rodamientos (mm/s):** Aceleración RMS en tren de rodaje y rodamientos de giro. Normal: 0.5 - 4.5 mm/s. Si sube de 7.0 mm/s indica fatiga destructiva.
* **Desgaste Balde/Pista (hrs):** Horas de servicio del componente actual.
* **Voltaje Sistema (V) y Corriente (A):** Alimentación eléctrica de motores de tracción y generador.

### C. Simulador de Telemetría Streaming a PostgreSQL:
* **Botón "🟢 Inyectar Lectura Normal":** Genera valores dentro del rango seguro, los guarda en la tabla `telemetria_lecturas` de PostgreSQL y refresca la pantalla.
* **Selector "Modo de Falla a Simular":** Permite escoger qué tipo de avería inducir:
  1. `FALLA_TERMICA`: Provoca recalentamiento de refrigerante y motor.
  2. `FALLA_PRESION_HIDRAULICA`: Simula reventón de manguera o falla de bomba hidráulica (caída drástica de PSI).
  3. `FALLA_DESGASTE_RODAMIENTOS`: Dispara vibraciones violentas (> 7 mm/s).
  4. `FALLA_SOBRECARGA`: Simula bloqueo de balde en roca viva con exceso de corriente y presión.
  5. `FALLA_ELECTRICA`: Caída de tensión por falla de alternador.
* **Botón "🚨 Inyectar Anomalía de Falla":**
  * Guarda la lectura anómala en PostgreSQL.
  * Invoca inmediatamente al modelo de IA activo para calcular el diagnóstico.
  * Si la criticidad es **ALTA o CRÍTICA**:
    * Cambia el estado del equipo a `EN ALERTA`.
    * **Emite automáticamente una nueva Orden de Trabajo (OT)** en la base de datos con prioridad `CRITICA` o `ALTA` y la recomendación técnica sugerida por la IA.
    * Despliega un mensaje rojo de alerta en pantalla.

### D. Gráfico de Tendencias Temporales:
Grafica las últimas 60 lecturas del equipo en tiempo real, permitiendo observar visualmente los picos de temperatura o vibración cuando se inyecta una anomalía.

---

## 6. Módulo: Laboratorio de IA & Benchmarking

Es el motor analítico de CRISP-DM (Fase 4 y 5), pensado para que el **Ingeniero de Mantenimiento** evalúe y compare algoritmos con rigor científico.

Tiene 4 pestañas:

### Pestaña 1: Benchmarking de 5 Algoritmos
Presenta la tabla comparativa de los 5 modelos entrenados bajo Validación Cruzada Estratificada (5 Folds):
1. **Random Forest Classifier (Tradicional):** Ensemble de árboles de decisión. Rápido, interpretable y robusto.
2. **XGBoost Classifier (Tradicional):** Gradient boosting de alto rendimiento con regularización L1/L2.
3. **Support Vector Machine - SVM RBF (Tradicional):** Clasificador de hiperplanos con kernel gaussiano.
4. **Híbrido CNN-LSTM (Deep Learning):** Combina Convolución 1D (para capturar firmas de frecuencia en vibración y presión) + Red Recurrente LSTM (para recordar la degradación temporal).
5. **Híbrido LSTM-Autoencoder + Random Forest (Deep Learning + ML):** Un Autoencoder aprende a comprimir y reconstruir ciclos de trabajo normales; el error de reconstrucción y el vector latente se entregan a un Random Forest para detectar fallas incipientes.

#### ¿Qué significa cada métrica de la tabla?
* **Accuracy (%):** Porcentaje total de diagnósticos correctos (sano vs falla).
* **Precision (%):** De todos los casos que la IA marcó como "Falla", cuántos realmente fallaron (evita falsas alarmas).
* **Recall / Sensibilidad (%):** De todas las fallas reales que ocurrieron en la mina, cuántas logró detectar la IA. **¡Es la métrica más importante en minería!** Un recall alto (ej. 96%) evita que una pala sufra una parada catastrófica en tajo.
* **F1-Score:** Media armónica entre Precision y Recall (el indicador de balance global).
* **ROC-AUC:** Capacidad de la IA de separar equipos sanos de averiados en cualquier umbral (1.00 es la perfección).
* **Inferencia (ms):** Tiempo en milisegundos que tarda la IA en procesar una lectura.
* **Botón "🚀 Entrenar y Poner en Activo":** Permite reentrenar cualquier modelo con el dataset y dejarlo como el clasificador oficial en producción en PostgreSQL.

### Pestaña 2: Curvas ROC, PR & Matriz de Confusión
* **Curvas ROC Comparativas:** Grafica la tasa de verdaderos positivos contra falsos positivos para los modelos. La curva más pegada a la esquina superior izquierda es la mejor.
* **Matriz de Confusión:** Tabla 2x2 que desglosa:
  * Verdaderos Negativos (Equipos sanos predichos como sanos).
  * Falsos Positivos (Falsas alarmas: predijo falla pero estaba sano).
  * Falsos Negativos (Fallas no vistas: ¡lo más peligroso!).
  * Verdaderos Positivos (Fallas detectadas a tiempo con éxito).

### Pestaña 3: Pruebas Estadísticas Robustas
Responde con evidencia matemática a la pregunta: *¿La ventaja del modelo híbrido sobre el tradicional es real o fue casualidad estadística?*
* **Test de Normalidad Shapiro-Wilk:** Evalúa si las diferencias entre los folds siguen una distribución gaussiana.
* **Wilcoxon Signed-Rank Test / Paired t-Test:** Pruebas pareadas de hipótesis.
* **Valor p (p-value):** Si $p < 0.05$, se rechaza la hipótesis nula H0 con un 95% de confianza estadística y se certifica científicamente que la arquitectura híbrida es superior.

### Pestaña 4: Entrenamiento GPU en Google Colab
* **Botón "📥 Descargar Script train_colab_pipeline.py":** Descarga un script autónomo optimizado para GPU NVIDIA CUDA.
* **Instrucciones:** Pasos para abrir Google Colab, habilitar GPU T4 gratuita y ejecutar el entrenamiento masivo en la nube.

---

## 7. Módulo: Gestión de Órdenes de Trabajo (OT)

Permite gestionar el ciclo de vida de mantenimiento derivado de las alertas de la IA.

### A. Resumen de OTs:
Muestra cuántas órdenes existen en total, cuántas están `PENDIENTE`, `EN PROGRESO`, `COMPLETADA` y cuántas son de prioridad `CRITICA`.

### B. Formulario "➕ Emitir Nueva Orden de Trabajo":
Permite a ingenieros crear órdenes manuales:
* **Equipo Afectado:** Menú para seleccionar el TAG del equipo.
* **Nivel de Prioridad:** `BAJA`, `MEDIA`, `ALTA` o `CRITICA`.
* **Técnico / Ingeniero Asignado:** Menú desplegable con los usuarios del sistema.
* **Título y Descripción:** Síntomas detectados, repuestos necesarios y pautas de seguridad.

### C. Padrón y Acciones de Flujo de Trabajo:
Cada orden aparece en una tarjeta con su código (ej. `OT-2026-001` o `OT-AUTO-PALA-01-4` generada automáticamente por IA).
* Si la OT está **Pendiente**, aparece el botón **"▶️ Iniciar"**: cambia su estado a `EN PROGRESO`.
* Si la OT está **En Progreso**, aparece un campo de texto y el botón **"✅ Cerrar OT"**: permite escribir qué reparación se hizo (ej. *"Se cambió filtro hidráulico y válvula de alivio"*) y la marca como `COMPLETADA` con fecha y hora de cierre.

---

## 8. Módulo: Generador de Reportes (PDF, Word, Excel)

Genera reportes corporativos listos para presentar a jefaturas y auditorías:

### 1. 📄 Reporte Ejecutivo en PDF (ReportLab)
* **¿Qué contiene?**
  * Membrete institucional de la UNT y Minera San Cristóbal.
  * Resumen de confiabilidad (Disponibilidad, MTBF, MTTR, Alertas).
  * Censo completo de la flota de carguío minero.
  * Lista de diagnósticos críticos con recomendación técnica y RUL.
  * Espacio de firma formal para el Ingeniero y la Superintendencia de Mantenimiento.
* **¿Para qué sirve?** Presentaciones ejecutivas a gerencia y firmas de conformidad.

### 2. 📝 Informe Técnico en Word (.docx con python-docx)
* **¿Qué contiene?**
  * Documento editable con formato corporativo.
  * Explicación de la metodología CRISP-DM.
  * Tablas de especificaciones de los 5 modelos de IA y benchmarking de métricas.
  * Resultado formal de las pruebas estadísticas (Wilcoxon p-value).
  * Padrón de órdenes de trabajo activas.
* **¿Para qué sirve?** Entregar como informe técnico editable de laboratorio o tesis universitaria.

### 3. 📊 Sábana Analítica en Excel (.xlsx con openpyxl)
* **¿Qué contiene?**
  * Un libro con **6 hojas estructuradas**:
    1. `Resumen Ejecutivo`: Métricas clave y estado de flota.
    2. `Flota Equipos`: TAGs, capacidades en toneladas, ubicaciones y horas.
    3. `Telemetria Sensores`: Últimas 200 lecturas con temperaturas, presiones y vibraciones.
    4. `Diagnosticos IA`: Historial de predicciones con probabilidades y criticidad.
    5. `Ordenes Trabajo`: Estado, responsable y prioridad de cada OT.
    6. `Auditoria`: Trazabilidad de accesos y modificaciones.
* **¿Para qué sirve?** Análisis en tablas dinámicas, auditorías contables y control operativo.

---

## 9. Módulo: Administración & Auditoría

Solo accesible por usuarios con rol **Administrador** (`admin`):

### Pestaña 1: Usuarios y Credenciales
* Visualiza la lista de todos los usuarios registrados con su correo, rol y fecha de último login.
* **Formulario "➕ Crear Nuevo Usuario":** Permite dar de alta a nuevos ingenieros, operadores o auditores, hasheando su contraseña con `bcrypt` y guardándolo en la base de datos PostgreSQL.

### Pestaña 2: Matriz de Permisos RBAC
* Muestra una tabla comparativa con los 4 roles en columnas y todos los permisos del sistema en filas con checks (✅ o ❌).
* Permite auditar qué puede y qué no puede hacer cada perfil.

### Pestaña 3: Logs de Auditoría del Sistema
* Registro forense inmutable de todas las acciones importantes (inicios de sesión, cierres de sesión, inyección de anomalías, emisión de OTs, creación de usuarios).
* Muestra: ID, fecha/hora exacta, usuario que lo hizo, rol, tabla afectada, detalles en JSON e IP de origen (`127.0.0.1`).
