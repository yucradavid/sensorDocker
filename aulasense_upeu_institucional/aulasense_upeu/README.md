# AulaSense UPeU

**Sistema institucional local para monitoreo predictivo de calidad del aire en aulas universitarias.**

Este proyecto complementa la Unidad 2 y Unidad 3 del pipeline Big Data:

```text
Sensor / simulador IoT → Kafka → Spark Streaming → Parquet → Spark MLlib → Predicciones → Dashboard
```

## Objetivo

Visualizar de forma clara el estado actual y predictivo de la calidad del aire en aulas UPeU con alta afluencia de estudiantes, usando IAQ, eCO2, VOC, temperatura y humedad. El sistema permite interpretar si se recomienda:

- Monitoreo normal.
- Ventilación preventiva.
- Encender purificador o extractor.
- Generar alerta operativa.

## Qué incluye

```text
app/dashboard_streamlit.py        Dashboard institucional local
app/api_fastapi.py                API REST para consultar predicciones
scripts/export_unidad3_para_dashboard.py  Celda/código para exportar resultados desde Unidad 3
data/demo/                       Datos de demostración para probar sin depender del notebook
docs/ARQUITECTURA.md             Arquitectura propuesta
docs/GUIA_USO.md                 Pasos de uso
requirements.txt                 Dependencias Python
docker-compose.yml               Ejecución opcional con Docker
```

## Instalación local rápida

Desde la carpeta del proyecto:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/dashboard_streamlit.py
```

En Linux/Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/dashboard_streamlit.py
```

Luego abre:

```text
http://localhost:8501
```

## Uso con resultados reales de Unidad 3

En tu notebook de Unidad 3, ejecuta el código de:

```text
scripts/export_unidad3_para_dashboard.py
```

Eso exportará los resultados a:

```text
/opt/data/calidad_aire/aulasense_dashboard_export
```

Luego en el dashboard cambia la ruta de datos en el panel lateral, o ejecuta:

```bash
set AULASENSE_DATA_DIR=C:\ruta\a\tu\export
streamlit run app/dashboard_streamlit.py
```

En Linux/Docker:

```bash
export AULASENSE_DATA_DIR=/opt/data/calidad_aire/aulasense_dashboard_export
streamlit run app/dashboard_streamlit.py
```

## API local opcional

```bash
uvicorn app.api_fastapi:app --reload --port 8000
```

Endpoints:

```text
GET http://localhost:8000/health
GET http://localhost:8000/predicciones/latest
GET http://localhost:8000/aulas/estado
```

## Explicación para exposición

Este dashboard no reemplaza a Kafka, Spark ni MLlib. Consume las predicciones generadas por la Unidad 3 y las presenta como un panel institucional para apoyar decisiones: ventilación, extractor o purificador.

