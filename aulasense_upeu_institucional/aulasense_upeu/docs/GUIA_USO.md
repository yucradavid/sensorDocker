# Guía de uso AulaSense UPeU

## 1. Ejecutar Unidad 2

Genera o consume eventos IoT y guarda Parquet:

```text
/opt/data/calidad_aire/eventos_limpios
/opt/data/calidad_aire/metricas_ventana
```

## 2. Ejecutar Unidad 3

Entrena el modelo y genera predicciones:

```text
15 min
30 min
1 hora
```

## 3. Exportar resultados

Al final del notebook de Unidad 3 ejecuta:

```python
exec(open("scripts/export_unidad3_para_dashboard.py", encoding="utf-8").read())
```

O pega directamente el contenido del archivo.

## 4. Abrir dashboard

```bash
streamlit run app/dashboard_streamlit.py
```

## 5. API local

```bash
uvicorn app.api_fastapi:app --reload --port 8000
```

## 6. Mensaje para exposición

El dashboard permite pasar del resultado técnico del modelo ML a una vista institucional de apoyo a decisiones. Muestra IAQ actual, IAQ predicho y acciones recomendadas para prevenir baja calidad de aire en aulas con alta afluencia.
