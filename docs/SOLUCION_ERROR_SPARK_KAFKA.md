# Solución: AnalysisException Failed to find data source: kafka

## Qué pasó

Kafka está bien levantado y el tópico `calidad-aire-eventos` fue creado correctamente. El error aparece en Spark porque el contenedor de bigdata-lab no tiene cargado el conector `spark-sql-kafka` cuando se crea la `SparkSession`.

Error típico:

```txt
AnalysisException: Failed to find data source: kafka.
Please deploy the application as per the deployment section of Structured Streaming + Kafka Integration Guide.
```

## Solución en Jupyter

1. Detén el notebook.
2. Kernel → Restart Kernel.
3. Usa el notebook corregido:

```txt
bigdata-lab/notebooks/09_streaming_calidad_aire_kafka_FIXED.ipynb
```

El fix está en estas líneas, que deben ejecutarse antes de crear SparkSession:

```python
import os
import pyspark

spark_version = pyspark.__version__
scala_suffix = "2.13" if spark_version.startswith("4.") else "2.12"
kafka_package = f"org.apache.spark:spark-sql-kafka-0-10_{scala_suffix}:{spark_version}"
os.environ["PYSPARK_SUBMIT_ARGS"] = f"--packages {kafka_package} pyspark-shell"
```

## También falta generar datos

Si Kafka UI muestra `Message Count = 0`, todavía no está corriendo el productor/simulador.

Ejecuta:

```bash
cd iot_air_kafka_updated_v2/air-quality-simulator-py
docker compose -f docker-compose-dev.yml up --build
```

Si quieres correrlo sin Docker desde Windows:

```cmd
cd iot_air_kafka_updated_v2\air-quality-simulator-py
pip install -r requirements.txt
set KAFKA_BOOTSTRAP_SERVERS=localhost:49092
python producer_air_quality.py
```

Luego revisa Kafka UI. El `Message Count` debe subir.

## Orden correcto

```bash
# 1. Kafka
cd ec-kafka
docker compose -f docker-compose-dev.yml up --build -d

# 2. Crear tópico
cd ../iot_air_kafka_updated_v2/scripts
bash create_topic.sh

# 3. Generar datos
cd ../air-quality-simulator-py
docker compose -f docker-compose-dev.yml up --build

# 4. Spark
cd ../../bigdata-lab/docker
docker compose -f docker-compose.yml -f docker-compose.kafka.yml up --build

# 5. En Jupyter
Abrir: notebooks/09_streaming_calidad_aire_kafka_FIXED.ipynb
```
