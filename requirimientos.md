# UNIVERSIDAD NACIONAL DE TRUJILLO
## VICERRECTORADO ACADÉMICO
### ESCUELA PROFESIONAL DE INGENIERÍA DE SISTEMAS

---

# 📘 GUÍA DE PRÁCTICA DE LABORATORIO N° 02
## DESARROLLO DE UNA APLICACIÓN WEB CON INTELIGENCIA ARTIFICIAL PARA GESTIÓN DE MANTENIMIENTO PREDICTIVO

---

## 📋 DATOS GENERALES

| Concepto | Detalle |
| :--- | :--- |
| **Curso** | Ingeniería de Software II |
| **Código** | IS-402 |
| **Semestre Académico** | 2026 - II |
| **Docente** | Ing. [Nombre del Docente] |
| **Duración** | 4 sesiones de 2 horas (8 horas cronológicas) |
| **Trabajo** | Grupos de 2 alumnos |
| **Semestre** | VIII |
| **Prerrequisitos** | Programación Orientada a Objetos, Bases de Datos I, Estructuras de Datos |
| **Fecha de entrega** | Sesión 2 de la práctica |

---

## 1. FUNDAMENTACIÓN TEÓRICA

### 1.1 Ingeniería de Software y Aplicaciones Empresariales
La ingeniería de software es una disciplina que aplica principios de ingeniería para desarrollar software de calidad. En la actualidad, las aplicaciones empresariales integran cada vez más componentes de inteligencia artificial para proporcionar valor agregado a los procesos de negocio.

En el contexto peruano, la industria minera representa uno de los pilares económicos más importantes, y la optimización de los procesos de mantenimiento de equipos de carguío mediante técnicas de IA puede generar ahorros significativos y reducir tiempos de inactividad.

### 1.2 Metodología CRISP-DM
CRISP-DM (*Cross-Industry Standard Process for Data Mining*) es la metodología estándar de la industria para proyectos de minería de datos y ciencia de datos. Consta de 6 fases:

1. **Comprensión del Negocio:** Definir objetivos y requisitos desde la perspectiva del negocio.
2. **Comprensión de los Datos:** Recolectar, explorar y familiarizarse con los datos iniciales.
3. **Preparación de los Datos:** Limpiar, transformar y construir el conjunto de datos final.
4. **Modelado:** Construir, entrenar y calibrar modelos de IA.
5. **Evaluación:** Medir el rendimiento y seleccionar el mejor modelo.
6. **Despliegue:** Integrar el modelo en la aplicación y ponerlo en producción.

### 1.3 Algoritmos de Inteligencia Artificial

#### Algoritmos Tradicionales (Machine Learning Clásico):
* **Random Forest:** Ensemble de múltiples árboles de decisión. Alta interpretabilidad, robusto al sobreajuste, maneja bien relaciones no lineales.
* **XGBoost:** Implementación optimizada de Gradient Boosting. Alto rendimiento predictivo, maneja regularización integrada.
* **SVM (Support Vector Machines):** Máquinas de Vectores de Soporte. Efectivo en espacios de alta dimensionalidad, sólida fundamentación matemática.

#### Algoritmos Híbridos (Deep Learning + ML):
* **CNN-LSTM:** Combina Redes Neuronales Convolucionales (CNN) para extracción automática de características locales + Redes LSTM para capturar dependencias temporales en series de datos.
* **LSTM-Autoencoder + RF:** Autoencoder LSTM para reducción no lineal de dimensionalidad + Random Forest para la clasificación final. Combina lo mejor de ambos mundos.

### 1.4 Tecnologías Web Modernas
* **Streamlit:** Framework Python de código abierto para crear aplicaciones web interactivas de manera rápida y sencilla, sin necesidad de conocimientos de frontend.
* **PostgreSQL:** Sistema de gestión de bases de datos relacional objeto-relacional, robusto, escalable y con características avanzadas.
* **JWT (JSON Web Tokens):** Estándar abierto para la transmisión segura de información entre partes como un objeto JSON.
* **bcrypt:** Biblioteca de hashing de contraseñas diseñada para ser segura y resistente a ataques de fuerza bruta.

---

## 2. OBJETIVOS

### 2.1 Objetivo General
Desarrollar una aplicación web completa usando **Python + Streamlit + PostgreSQL** que implemente un motor de inteligencia artificial para mantenimiento predictivo de equipos industriales, aplicando la metodología CRISP-DM y principios de ingeniería de software.

### 2.2 Objetivos Específicos
- ✅ Diseñar e implementar una base de datos relacional en PostgreSQL con al menos 8 tablas.
- ✅ Desarrollar un sistema de autenticación con 4 roles y matriz de permisos de usuario.
- ✅ Implementar un dashboard interactivo con KPIs y visualizaciones interactivas.
- ✅ Aplicar análisis exploratorio de datos (EDA) sobre datos de sensores industriales.
- ✅ Entrenar y evaluar comparativamente 3 algoritmos de IA tradicionales y 2 híbridos.
- ✅ Implementar validación cruzada, optimización de hiperparámetros y pruebas estadísticas robustas.
- ✅ Desarrollar módulo de generación de reportes en PDF, Word y Excel.
- ✅ Aplicar principios de modularidad, reutilización y documentación de código.

---

## 3. COMPETENCIAS A DESARROLLAR

| Competencia | Descriptor del Nivel de Logro |
| :--- | :--- |
| **Resuelve problemas** | Aplica conocimientos de ingeniería de software para resolver problemas complejos de la industria minera local. |
| **Diseña arquitecturas** | Diseña arquitecturas de software multicapa integrando componentes de inteligencia artificial. |
| **Implementa soluciones** | Desarrolla aplicaciones web modernas con persistencia en bases de datos relacionales. |
| **Evalúa modelos** | Aplica métodos estadísticos robustos para validar y comparar modelos de IA. |
| **Trabaja en equipo** | Colabora efectivamente en equipos de 3 personas, usando control de versiones. |
| **Documenta** | Elabora documentación técnica y reportes profesionales en múltiples formatos. |

---

## 4. EQUIPOS Y MATERIALES

### 4.1 Software Requerido

| Software | Versión Mínima | Enlace de Descarga |
| :--- | :---: | :--- |
| **Python** | 3.10 | [Descargar Python](https://www.python.org/downloads/) |
| **PostgreSQL** | 14 | [Descargar PostgreSQL](https://www.postgresql.org/download/) |
| **pgAdmin** | 4 | [Descargar pgAdmin](https://www.pgadmin.org/download/) |
| **Git** | 2.3 | [Descargar Git](https://git-scm.com/downloads) |
| **Visual Studio Code** | 1.80 | [Descargar VS Code](https://code.visualstudio.com/) |

### 4.2 Librerías Python Principales

```bash
# Instalación básica
pip install streamlit pandas numpy plotly

# Machine Learning
pip install scikit-learn xgboost imbalanced-learn

# Deep Learning (opcional pero recomendado)
pip install tensorflow

# Base de datos
pip install psycopg2-binary

# Reportes
pip install reportlab python-docx openpyxl

# Seguridad
pip install PyJWT bcrypt

# Estadística y visualización
pip install scipy seaborn