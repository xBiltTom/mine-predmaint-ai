"""
Vista de Análisis Exploratorio de Datos (CRISP-DM Fase 2 y 3).
Estadísticas descriptivas, correlaciones, distribuciones multivariables y detección de outliers.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
from config.settings import DATASETS_DIR
from data.preprocessor import FEATURE_COLS

def render_eda_view():
    st.title("🔬 Análisis Exploratorio de Datos (EDA) - Sensores Mineros")
    st.markdown("Exploración profunda de telemetría de sensores, correlaciones multivariables y patrones de fallo (CRISP-DM).")

    csv_path = DATASETS_DIR / "carguio_minero_telemetria.csv"
    if not csv_path.exists():
        st.warning("Dataset no encontrado. Se generará automáticamente...")
        from data.dataset_generator import generate_base_dataset
        df = generate_base_dataset(n_samples=10000)
    else:
        df = pd.read_csv(csv_path)

    # 1. Resumen Estadístico General
    st.subheader("📋 Resumen General del Dataset")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Muestras Telemetría", f"{len(df):,}")
    with m2:
        fallas = int(df["falla_maquina"].sum())
        st.metric("Eventos de Falla", f"{fallas}", f"{(fallas/len(df))*100:.2f}% del total")
    with m3:
        st.metric("Variables Sensadas", f"{len(FEATURE_COLS)}")
    with m4:
        st.metric("Equipos Monitoreados", f"{df['equipo_tag'].nunique()}")

    # 2. Tabla Descriptiva
    with st.expander("📊 Ver Estadísticas Descriptivas (Media, Desv. Est., Cuartiles, Asimetría)", expanded=True):
        desc = df[FEATURE_COLS].describe().T
        desc["skewness"] = df[FEATURE_COLS].skew()
        desc = desc.round(2)
        st.dataframe(desc, use_container_width=True)

    # 3. Matriz de Correlación
    st.subheader("🔥 Matriz de Correlación de Sensores")
    st.markdown("Identificación de relaciones lineales entre variables térmicas, dinámicas y de desgaste.")
    corr = df[FEATURE_COLS + ["falla_maquina"]].corr().round(3)
    fig_corr = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Viridis",
        labels=dict(color="Correlación Pearson")
    )
    fig_corr.update_layout(height=480, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_corr, use_container_width=True)

    # 4. Distribuciones y Separabilidad de Clases
    st.subheader("📈 Distribución de Variables: Operación Normal vs Falla")
    c1, c2 = st.columns(2)
    with c1:
        sensor_select = st.selectbox(
            "Seleccione Sensor para análisis de densidad / Boxplot:",
            FEATURE_COLS,
            index=2  # Vibración por defecto
        )
    with c2:
        plot_type = st.radio("Tipo de Gráfico:", ["Boxplot Comparativo", "Histograma de Distribución"], horizontal=True)

    df_plot = df.copy()
    df_plot["Estado"] = df_plot["falla_maquina"].map({0: "Normal", 1: "Falla"})

    if plot_type == "Boxplot Comparativo":
        fig_dist = px.box(
            df_plot,
            x="Estado",
            y=sensor_select,
            color="Estado",
            color_discrete_map={"Normal": "#10B981", "Falla": "#EF4444"},
            points="outliers",
            labels={sensor_select: f"Lectura de {sensor_select}", "Estado": "Condición del Equipo"}
        )
        fig_dist.update_layout(height=380, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        fig_hist = px.histogram(
            df_plot,
            x=sensor_select,
            color="Estado",
            barmode="overlay",
            nbins=60,
            opacity=0.75,
            color_discrete_map={"Normal": "#10B981", "Falla": "#EF4444"}
        )
        fig_hist.update_layout(height=380, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_hist, use_container_width=True)

    # 5. Diagrama de Dispersión Multivariable (Vibración vs Desgaste / Temperatura vs Presión)
    st.subheader("🎯 Dispersión Multivariable y Fronteras de Falla")
    sc1, sc2 = st.columns(2)
    with sc1:
        x_axis = st.selectbox("Eje X:", FEATURE_COLS, index=8)  # desgaste_componente_hrs
    with sc2:
        y_axis = st.selectbox("Eje Y:", FEATURE_COLS, index=2)  # vibracion_rodamientos_mm_s

    fig_scatter = px.scatter(
        df_plot.sample(min(2000, len(df_plot)), random_state=42),
        x=x_axis,
        y=y_axis,
        color="tipo_falla",
        hover_data=["equipo_tag", "temp_motor_c", "presion_hidraulica_psi"],
        title=f"Dispersión {y_axis} vs {x_axis} por Tipo de Falla (Muestra 2,000 pts)"
    )
    fig_scatter.update_layout(height=420, margin=dict(t=30, b=20, l=20, r=20))
    st.plotly_chart(fig_scatter, use_container_width=True)
