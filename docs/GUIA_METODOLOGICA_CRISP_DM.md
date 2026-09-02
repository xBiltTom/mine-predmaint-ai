# 🔬 Guía Metodológica CRISP-DM y Fundamentación de IA

**Sistema Web de Mantenimiento Predictivo con Inteligencia Artificial para Equipos de Carguío Minero**  
*Universidad Nacional de Trujillo — Ingeniería de Software II (IS-402)*  

---

## 📋 ¿Qué es CRISP-DM y cómo se aplica en este proyecto?

**CRISP-DM** (*Cross-Industry Standard Process for Data Mining*) es el estándar industrial más utilizado para estructurar proyectos de ciencia de datos e inteligencia artificial. En este proyecto, cada fase está directamente reflejada en el código:

```
[1. Comprensión del Negocio]  ---> Definición de KPIs mineros (MTBF, MTTR, Disponibilidad OEE)
          ↓
[2. Comprensión de los Datos] ---> data/dataset_generator.py (Telemetría de sensores y 5 modos de fallo)
          ↓
[3. Preparación de Datos]     ---> data/preprocessor.py (Escalado robusto, ventanas y balanceo SMOTE)
          ↓
[4. Modelado]                 ---> models/traditional/ y models/hybrid/ (5 algoritmos ML y DL)
          ↓
[5. Evaluación]               ---> models/evaluation.py y models/statistical_tests.py (CV y Wilcoxon)
          ↓
[6. Despliegue]               ---> app.py y views/ (Streamlit Web, PostgreSQL y Reportes multiformato)
```

---

## 1. Fase 1: Comprensión del Negocio (Business Understanding)

### El Problema en Minería:
En operaciones a tajo abierto, una parada no programada de una pala de 100 toneladas (como la Komatsu P&H 4100XPC o la CAT 7495) paraliza una flota de 6 a 8 camiones mineros de acarreo de 240 a 400 toneladas. Cada hora de inactividad imprevista puede costar decenas de miles de dólares en producción perdida.

### Objetivos de Negocio:
1. **Maximizar Disponibilidad OEE:** Mantener la flota disponible por encima del 90%.
2. **Elevar el MTBF (Mean Time Between Failures):** Alargar los ciclos continuos de operación sin averías.
3. **Reducir el MTTR (Mean Time To Repair):** Saber con exactitud qué componente va a fallar antes de que se rompa catastróficamente, reduciendo el tiempo de desarme y cambio de repuesto.

---

## 2. Fase 2: Comprensión de los Datos (Data Understanding)

### Variables de Telemetría Industrial:
El sistema monitorea 9 variables críticas en cada ciclo de carga:

| Variable en Código | Nombre del Sensor | Unidad | Rango Normal | Comportamiento en Fallo |
| :--- | :--- | :---: | :---: | :--- |
| `temp_motor_c` | Temperatura de Motor | °C | 60 - 95 | Sube drásticamente (> 105 °C) en fallos de refrigeración. |
| `presion_hidraulica_psi`| Presión Hidráulica Principal | PSI | 2500 - 3800 | Cae (< 2000 PSI) por fugas o sube (> 4200 PSI) por atascamiento. |
| `vibracion_rodamientos_mm_s` | Vibración RMS de Rodamientos | mm/s | 0.5 - 4.5 | Picos altos (> 7.0 mm/s) por picadura de pistas o desalineación. |
| `presion_aceite_psi` | Presión de Aceite Lubricante | PSI | 35 - 75 | Cae críticamente (< 25 PSI) por pérdida de viscosidad o bomba dañada. |
| `temp_refrigerante_c` | Temperatura de Refrigerante | °C | 70 - 92 | Sube (> 100 °C) en sobrecalentamiento térmico. |
| `rpm_motor` | Velocidad de Rotación | RPM | 1200 - 2100 | Fluctuaciones por inestabilidad de combustión o carga irregular. |
| `voltaje_sistema_v` | Voltaje del Sistema Eléctrico | V | 23.5 - 28.5 | Cae (< 21 V) por fallo de alternador o descarga de baterías. |
| `corriente_a` | Corriente Demandada | A | 50 - 280 | Picos excesivos (> 340 A) por sobreesfuerzo del balde en roca dura. |
| `desgaste_componente_hrs`| Horas Acumuladas de Fatiga | hrs | 0 - 3500 | Mientras más horas acumula un componente, mayor probabilidad de avería. |

### Los 5 Modos de Falla Industriales:
1. **HDF (Heat Dissipation Failure / Falla Térmica):** Sobrecalentamiento conjunto de refrigerante y motor.
2. **PWF (Power Failure / Falla de Presión o Potencia):** Caída de presión hidráulica o pérdida de torque motriz.
3. **TWF (Tool/Bearing Wear Failure / Desgaste de Rodamientos):** Altas vibraciones combinadas con elevado número de horas de fatiga.
4. **OSF (Overstrain Failure / Sobreesfuerzo Mecánico):** Balde atascado con corriente y presión simultáneamente elevadas.
5. **RNF (Random Failure / Falla Fortuita):** Caídas de voltaje o anomalías electromecánicas aleatorias.

---

## 3. Fase 3: Preparación de los Datos (Data Preparation)

Implementada en `data/preprocessor.py`:
1. **Escalado Robusto (`RobustScaler`):**  
   A diferencia de `StandardScaler` (que usa media y varianza), `RobustScaler` utiliza la **mediana** y el **rango intercuartílico (IQR)**. Esto es crucial en sensores mineros porque evita que los valores atípicos de fallas extremas distorsionen la normalización.
2. **Ventanas Deslizantes Secuenciales (`create_sliding_sequences`):**  
   Para los modelos de Deep Learning (CNN-LSTM y Autoencoders), los datos se estructuran en tensores tridimensionales `(muestras, timesteps=5, características=9)`. Esto permite que la red aprenda la trayectoria temporal de la degradación a lo largo del tiempo.
3. **Manejo de Desbalance Severo con SMOTE:**  
   En la industria real, las fallas son raras (~5-8% de los datos). Si entrenamos un modelo sin balancear, la IA predecirá siempre "Normal" con un 93% de exactitud aparente, pero no detectará ninguna falla.  
   **SMOTE** (*Synthetic Minority Over-sampling Technique*) genera ejemplos sintéticos matemáticamente consistentes de la clase minoritaria (Falla), aplicado **estrictamente en los folds de entrenamiento** para evitar fugas de información (*Data Leakage*).

---

## 4. Fase 4: Modelado (Modeling) - Los 5 Algoritmos

### Algoritmos Tradicionales:
1. **Random Forest Classifier (`models/traditional/random_forest.py`):**
   * *¿Cómo funciona?* Construye un conjunto (*ensemble*) de múltiples árboles de decisión entrenados con diferentes subconjuntos de datos y características.
   * *Ventaja:* No sobreajusta con facilidad, es robusto al ruido y calcula la importancia de cada sensor en el diagnóstico.
2. **XGBoost Classifier (`models/traditional/xgboost_model.py`):**
   * *¿Cómo funciona?* Construye árboles de forma secuencial donde cada nuevo árbol corrige los errores del árbol anterior mediante optimización por gradiente con regularización L1 y L2.
   * *Ventaja:* Es el algoritmo tabular más rápido y preciso en competiciones mundiales de ciencia de datos.
3. **Support Vector Machine - SVM RBF (`models/traditional/svm_model.py`):**
   * *¿Cómo funciona?* Proyecta los datos de los sensores a un espacio de mayor dimensionalidad usando una función de base radial gaussiana (*RBF Kernel*) para encontrar un hiperplano óptimo de máxima separación.
   * *Ventaja:* Excelente fundamentación matemática para detectar fronteras no lineales complejas.

### Algoritmos Híbridos:
4. **CNN-LSTM (`models/hybrid/cnn_lstm.py`):**
   * *¿Cómo funciona?*
     * **Capa Convolucional 1D:** Funciona como un filtro digital que extrae patrones espectrales de alta frecuencia (firmas de vibración y picos de presión).
     * **Capa LSTM (Long Short-Term Memory):** Una red neuronal recurrente con compuertas de olvido, entrada y salida que recuerda la secuencia temporal de la degradación.
   * *Ventaja:* Capta simultáneamente los transitorios repentinos y el deterioro progresivo en el tiempo.
5. **LSTM-Autoencoder + Random Forest (`models/hybrid/lstm_ae_rf.py`):**
   * *¿Cómo funciona?*
     * **Etapa 1 (No supervisada):** Un Autoencoder LSTM aprende a reconstruir exclusivamente ciclos de operación normales. Cuando entra una señal anómala, no sabe reconstruirla bien y el **error de reconstrucción** se dispara.
     * **Etapa 2 (Supervisada):** El vector latente comprimido (cuello de botella) más el error de reconstrucción se entregan a un Random Forest para emitir la clasificación final.
   * *Ventaja:* Combina la capacidad de compresión no lineal del Deep Learning con la solidez de clasificación de los ensambles de árboles.

---

## 5. Fase 5: Evaluación y Rigor Estadístico (Evaluation)

### Validación Cruzada Estratificada (5 Folds):
El dataset se divide en 5 particiones con igual proporción de fallas. El modelo se entrena 5 veces alternando 4 particiones para entrenamiento y 1 para validación.

### Pruebas de Hipótesis para Comparación Científica:
Para demostrar que el mejor modelo híbrido supera al mejor modelo tradicional:
1. **Test de Shapiro-Wilk:** Verifica si las diferencias de F1-Score en los 5 folds provienen de una distribución normal.
2. **Paired t-Test (t-Student Pareado):** Si las diferencias son normales, evalúa si la diferencia media de rendimiento es significativamente distinta de cero.
3. **Wilcoxon Signed-Rank Test:** Si las diferencias no son normales, aplica una prueba no paramétrica basada en los rangos de las diferencias con signo.
4. **Criterio de Aceptación:** Si el **p-value es menor a 0.05**, se concluye con un 95% de nivel de confianza que el modelo híbrido es genuinamente superior.

---

## 6. Fase 6: Despliegue (Deployment)

El despliegue productivo se consolida mediante:
* **Aplicación Web Interactiva:** Interfaz Streamlit modular con rutas protegidas por JWT y RBAC.
* **Persistencia Transaccional:** Base de datos relacional PostgreSQL con registro continuo de lecturas, modelos e inferencias.
* **Cálculo de RUL (Remaining Useful Life):** Estimación automática de horas restantes de vida antes de la rotura para programar la intervención antes del fallo.
* **Emisión Automática de Órdenes de Trabajo:** Las alertas críticas generan automáticamente una OT con prioridad y recomendación de reparación para la cuadrilla de mecánicos.
* **Reportabilidad Multiformato:** Exportación en un clic a PDF formal, informe editable en Word y sábanas analíticas en Excel.
