from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils_data import get_data_dir, read_csv_logical, parse_datetime_columns, classify_iaq, recommend_action

st.set_page_config(
    page_title="AulaSense UPeU",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

UP_BLUE = "#0088CB"
UP_RED = "#ED1C24"
UP_YELLOW = "#FFCB05"
UP_GRAY = "#4A4A4A"

st.markdown(
    f"""
    <style>
    .main-header {{
        padding: 1rem 1.25rem;
        border-radius: 18px;
        background: linear-gradient(90deg, {UP_BLUE} 0%, #0b4f7a 100%);
        color: white;
        margin-bottom: 1rem;
    }}
    .main-header h1 {{ margin: 0; font-size: 2rem; }}
    .main-header p {{ margin: 0.25rem 0 0 0; font-size: 1rem; }}
    .metric-card {{
        padding: 1rem;
        border-radius: 16px;
        border: 1px solid #e8e8e8;
        background: #ffffff;
        min-height: 110px;
    }}
    .section-title {{
        font-weight: 700;
        font-size: 1.15rem;
        margin-top: 1.2rem;
        margin-bottom: 0.4rem;
        color: {UP_GRAY};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="main-header">
        <h1>AulaSense UPeU</h1>
        <p>Sistema local de monitoreo predictivo de calidad del aire para aulas universitarias</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header("Configuración")
default_dir = get_data_dir()
data_dir_input = st.sidebar.text_input("Ruta de datos exportados", value=str(default_dir))
data_dir = Path(data_dir_input).expanduser().resolve()
st.sidebar.caption("Usa la carpeta exportada desde Unidad 3 o los datos demo incluidos.")

serie = read_csv_logical("serie_temporal", data_dir)
metricas = read_csv_logical("metricas_modelo", data_dir)
predicciones = read_csv_logical("predicciones_batch", data_dir)
acciones = read_csv_logical("acciones_ultima_ventana", data_dir)
importancia = read_csv_logical("importancia_variables", data_dir)

serie = parse_datetime_columns(serie, ["minuto", "inicio_ventana", "fin_ventana"])
predicciones = parse_datetime_columns(predicciones, ["minuto"])

if serie.empty and metricas.empty and predicciones.empty and acciones.empty:
    st.error("No se encontraron datos. Verifica la ruta o ejecuta scripts/export_unidad3_para_dashboard.py en tu notebook de Unidad 3.")
    st.stop()

st.sidebar.success("Datos cargados")
st.sidebar.write("Carpeta:", str(data_dir))

# =========================
# KPIs principales
# =========================
latest_iaq = None
latest_ec02 = None
latest_voc = None
latest_station = "Aula UPeU"

if not serie.empty:
    serie = serie.sort_values("minuto") if "minuto" in serie.columns else serie
    last_row = serie.tail(1).iloc[0]
    latest_station = str(last_row.get("estacion", latest_station))
    latest_iaq = last_row.get("iaq_promedio", last_row.get("iaq", None))
    latest_ec02 = last_row.get("eco2_promedio", last_row.get("eco2", None))
    latest_voc = last_row.get("voc_promedio", last_row.get("voc", None))

st.markdown(f"### Estado institucional del aula: **{latest_station}**")

col1, col2, col3, col4 = st.columns(4)
col1.metric("IAQ actual", "Sin dato" if pd.isna(latest_iaq) else f"{float(latest_iaq):.2f}", classify_iaq(latest_iaq))
col2.metric("eCO₂ actual", "Sin dato" if pd.isna(latest_ec02) else f"{float(latest_ec02):.0f} ppm")
col3.metric("VOC actual", "Sin dato" if pd.isna(latest_voc) else f"{float(latest_voc):.3f}")
col4.metric("Acción actual", recommend_action(latest_iaq))

# =========================
# Acción predictiva
# =========================
if not acciones.empty:
    st.markdown('<div class="section-title">Decisión operativa predictiva</div>', unsafe_allow_html=True)
    acciones_show = acciones.copy()
    preferred_cols = [c for c in ["horizonte_texto", "iaq_actual", "iaq_predicho", "estado_iaq_predicho", "accion_recomendada"] if c in acciones_show.columns]
    st.dataframe(acciones_show[preferred_cols] if preferred_cols else acciones_show, use_container_width=True)

    if {"horizonte_texto", "iaq_predicho"}.issubset(acciones_show.columns):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=acciones_show["horizonte_texto"],
            y=acciones_show["iaq_predicho"],
            mode="lines+markers",
            name="IAQ predicho",
        ))
        fig.add_hline(y=50, line_dash="dash", annotation_text="Bueno / moderado")
        fig.add_hline(y=100, line_dash="dash", annotation_text="Moderado / riesgo")
        fig.add_hline(y=150, line_dash="dash", annotation_text="Riesgo alto")
        fig.update_layout(title="IAQ predicho por horizonte", xaxis_title="Horizonte", yaxis_title="IAQ")
        st.plotly_chart(fig, use_container_width=True)

# =========================
# Serie temporal
# =========================
if not serie.empty:
    st.markdown('<div class="section-title">Serie temporal del aula</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["IAQ", "eCO₂", "VOC"])

    with tab1:
        if {"minuto", "iaq_promedio"}.issubset(serie.columns):
            fig = px.line(serie, x="minuto", y="iaq_promedio", title="IAQ promedio por minuto")
            fig.add_hline(y=50, line_dash="dash")
            fig.add_hline(y=100, line_dash="dash")
            fig.add_hline(y=150, line_dash="dash")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No se encontró columna minuto/iaq_promedio.")

    with tab2:
        if {"minuto", "eco2_promedio"}.issubset(serie.columns):
            fig = px.line(serie, x="minuto", y="eco2_promedio", title="eCO₂ promedio por minuto")
            fig.add_hline(y=1000, line_dash="dash")
            fig.add_hline(y=1500, line_dash="dash")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No se encontró columna minuto/eco2_promedio.")

    with tab3:
        if {"minuto", "voc_promedio"}.issubset(serie.columns):
            fig = px.line(serie, x="minuto", y="voc_promedio", title="VOC promedio por minuto")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No se encontró columna minuto/voc_promedio.")

# =========================
# Métricas de modelo
# =========================
if not metricas.empty:
    st.markdown('<div class="section-title">Evaluación del modelo Spark MLlib</div>', unsafe_allow_html=True)
    metricas_show = metricas.copy().sort_values("horizonte_minutos") if "horizonte_minutos" in metricas.columns else metricas
    st.dataframe(metricas_show, use_container_width=True)

    if {"horizonte_texto", "r2"}.issubset(metricas_show.columns):
        fig = px.bar(metricas_show, x="horizonte_texto", y="r2", title="R² por horizonte")
        fig.add_hline(y=0.75, line_dash="dash")
        st.plotly_chart(fig, use_container_width=True)

    if {"horizonte_texto", "rmse", "mae"}.issubset(metricas_show.columns):
        m_long = metricas_show.melt(id_vars=["horizonte_texto"], value_vars=["rmse", "mae"], var_name="métrica", value_name="valor")
        fig = px.bar(m_long, x="horizonte_texto", y="valor", color="métrica", barmode="group", title="RMSE y MAE por horizonte")
        st.plotly_chart(fig, use_container_width=True)

# =========================
# Real vs predicho
# =========================
if not predicciones.empty:
    st.markdown('<div class="section-title">IAQ real futuro vs IAQ predicho</div>', unsafe_allow_html=True)
    if "horizonte_texto" in predicciones.columns:
        horizontes = list(predicciones["horizonte_texto"].dropna().unique())
        selected = st.selectbox("Horizonte", horizontes)
        pred_h = predicciones[predicciones["horizonte_texto"] == selected].copy()
    else:
        pred_h = predicciones.copy()

    if {"minuto", "iaq_real_futuro", "iaq_predicho"}.issubset(pred_h.columns):
        pred_h = pred_h.sort_values("minuto").tail(80)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=pred_h["minuto"], y=pred_h["iaq_real_futuro"], mode="lines", name="IAQ real futuro"))
        fig.add_trace(go.Scatter(x=pred_h["minuto"], y=pred_h["iaq_predicho"], mode="lines", name="IAQ predicho"))
        fig.update_layout(title="Comparación IAQ real futuro vs predicho", xaxis_title="Tiempo", yaxis_title="IAQ")
        st.plotly_chart(fig, use_container_width=True)

    if {"minuto", "error_abs"}.issubset(pred_h.columns):
        fig = px.line(pred_h.sort_values("minuto").tail(80), x="minuto", y="error_abs", title="Error absoluto del modelo")
        st.plotly_chart(fig, use_container_width=True)

# =========================
# Importancia de variables
# =========================
if not importancia.empty:
    st.markdown('<div class="section-title">Importancia de variables</div>', unsafe_allow_html=True)
    imp = importancia.copy()
    if "horizonte_texto" in imp.columns:
        selected_imp = st.selectbox("Horizonte para importancia", list(imp["horizonte_texto"].dropna().unique()))
        imp = imp[imp["horizonte_texto"] == selected_imp]
    if {"variable", "importancia"}.issubset(imp.columns):
        imp = imp.sort_values("importancia", ascending=False).head(10)
        fig = px.bar(imp.sort_values("importancia"), x="importancia", y="variable", orientation="h", title="Top variables del modelo")
        st.plotly_chart(fig, use_container_width=True)

st.caption("AulaSense UPeU · Dashboard institucional local basado en resultados de Kafka, Spark Streaming y Spark MLlib.")
