# Arquitectura AulaSense UPeU

## Flujo técnico

```text
Sensor BME680 / simulador IoT
        ↓
Kafka topic calidad-aire-eventos
        ↓
Spark Structured Streaming
        ↓
Parquet eventos limpios / métricas ventana
        ↓
Spark MLlib RandomForestRegressor
        ↓
Predicción IAQ 15 min, 30 min y 1 hora
        ↓
CSV/Parquet de predicciones
        ↓
Dashboard Streamlit / API FastAPI / Grafana futuro
```

## Uso institucional

El sistema está orientado a aulas con alta afluencia de estudiantes. El objetivo no es solo observar el IAQ actual, sino anticipar el deterioro del aire y recomendar acciones preventivas:

- Ventilar el aula.
- Encender extractor.
- Encender purificador.
- Generar alerta operativa.

## Alcance realista

- Modelo principal: predicción a 15 y 30 minutos.
- Modelo complementario: predicción a 1 hora.
- No se recomienda usar 2h o 3h sin más historial real.

## Nota metodológica

El dashboard no entrena el modelo. El entrenamiento se realiza en el notebook de Unidad 3 con Spark MLlib. El dashboard consume los resultados exportados.
