# Pipeline IoT/Simulado de calidad de aire: Kafka + Spark Structured Streaming

Este paquete está actualizado para dos escenarios:

1. **Modo contingencia recomendado ahora:** simulador Python de sensor BME680 -> Kafka -> Spark.
2. **Modo final cuando llegue el sensor:** ESP32 + BME680 -> API local FastAPI -> Kafka -> Spark.

El objetivo es cumplir el entregable de Unidad 2: pipeline streaming funcional con Kafka, Spark Structured Streaming, contrato de evento, ventanas, watermarking, métricas, observabilidad y evidencias.

## Recomendación para presentar

Como el sensor físico no llegó, usa el **modo contingencia**. El simulador Python genera eventos cada 3 segundos con el mismo contrato que usará el ESP32. Cuando llegue el sensor, solo reemplazas el productor simulado por el ESP32 + API local. Kafka y Spark no cambian.

## Arquitectura modo contingencia

```text
air-quality-simulator-py
    ↓ genera eventos cada 3 segundos
Kafka topic: calidad-aire-eventos
    ↓
bigdata-lab / Spark Structured Streaming
    ↓
ventanas, watermarking, métricas, dataset limpio
```

## Arquitectura modo final con sensor

```text
ESP32 + BME680
    ↓ HTTP POST
air-ingest-api FastAPI
    ↓ Kafka Producer
Kafka topic: calidad-aire-eventos
    ↓
bigdata-lab / Spark Structured Streaming
```

## Carpetas incluidas

```text
air-quality-simulator-py/   # Recomendado ahora: genera data simulada de calidad de aire
air-ingest-api/             # Para cuando llegue el sensor: API local que recibe ESP32 y publica en Kafka
arduino/                    # Sketch limpio para ESP32 + BME680 sin claves reales
bigdata-lab/                # Scripts/notebooks para Spark Structured Streaming
scripts/                    # Comandos de ayuda para topic y consumidor Kafka
supabase-bridge/            # Alternativa opcional: Supabase -> Kafka
```

## Flujo de ejecución recomendado ahora

### 1. Levantar Kafka

```bash
cd ec-kafka
docker compose -f docker-compose-dev.yml up --build
```

### 2. Crear el topic

En otra terminal:

```bash
cd iot_air_kafka_updated/scripts
bash create_topic.sh
```

Si estás en Windows PowerShell y no tienes bash, entra al contenedor Kafka:

```bash
cd ec-kafka
docker compose -f docker-compose-dev.yml exec ec-kafka bash
/opt/kafka/bin/kafka-topics.sh --create --if-not-exists --topic calidad-aire-eventos --bootstrap-server ec-kafka:9092 --partitions 3 --replication-factor 1
```

### 3. Ejecutar simulador Python

Opción con Docker, recomendada:

```bash
cd iot_air_kafka_updated/air-quality-simulator-py
docker compose -f docker-compose-dev.yml up --build
```

Opción local con Python:

```bash
cd iot_air_kafka_updated/air-quality-simulator-py
pip install -r requirements.txt
python producer_air_quality.py
```

Si lo corres local, verifica que Kafka esté accesible en `localhost:49092`.

### 4. Ver eventos en Kafka

```bash
cd iot_air_kafka_updated/scripts
bash consume_topic.sh
```

También puedes usar Kafka UI desde el navegador si tu `ec-kafka` lo expone.

### 5. Levantar bigdata-lab

```bash
cd bigdata-lab/docker
docker compose -f docker-compose.yml -f docker-compose.kafka.yml up --build
```

Luego copia o abre los archivos de:

```text
iot_air_kafka_updated/bigdata-lab/notebooks/
```

## Qué evidencia tomar

1. Kafka levantado.
2. Topic `calidad-aire-eventos` creado.
3. Simulador Python enviando datos.
4. Kafka UI o consumidor mostrando JSON.
5. Spark leyendo desde Kafka.
6. Spark mostrando agregaciones por ventana.
7. Tabla de latencia, throughput, errores y lag.

## Nota para el informe

Usa esta explicación:

> Debido a que el sensor físico BME680 no llegó a tiempo, se implementó un modo de contingencia mediante un simulador IoT en Python. El simulador genera eventos con el mismo contrato que producirá el ESP32 + BME680. De esta forma, el pipeline Kafka + Spark Structured Streaming se mantiene funcional y preparado para reemplazar el simulador por el sensor real sin modificar el tópico, el contrato de evento ni el procesamiento streaming.

## Seguridad

No subas contraseñas WiFi, tokens de Supabase ni claves API a GitHub. El sketch Arduino incluido usa placeholders.

---

## Corrección importante para Spark + Kafka

Si aparece este error:

```txt
AnalysisException: Failed to find data source: kafka
```

usa el notebook corregido:

```txt
bigdata-lab/notebooks/09_streaming_calidad_aire_kafka_FIXED.ipynb
```

Ese notebook agrega automáticamente el paquete `spark-sql-kafka` según la versión de PySpark instalada.

## Si Kafka UI muestra Message Count = 0

Eso significa que el tópico existe, pero no hay productor generando datos. Ejecuta:

```bash
cd air-quality-simulator-py
docker compose -f docker-compose-dev.yml up --build
```
