# Guía rápida corregida

## Estado correcto esperado

- `ec-kafka`: Running
- `calidad-aire-eventos`: creado con 3 particiones
- `Message Count`: debe ser mayor que 0 cuando el simulador está corriendo
- Spark: debe abrir el notebook FIX sin error `Failed to find data source: kafka`

## 1. Levantar Kafka

```bash
cd ec-kafka
docker compose -f docker-compose-dev.yml up --build -d
```

## 2. Crear tópico

```bash
cd ../iot_air_kafka_updated_v2/scripts
bash create_topic.sh
```

## 3. Levantar simulador

```bash
cd ../air-quality-simulator-py
docker compose -f docker-compose-dev.yml up --build
```

Verás mensajes JSON cada 3 segundos.

## 4. Comprobar mensajes

```bash
cd ../scripts
bash consume_topic.sh
```

## 5. Ejecutar Spark

Copia el notebook:

```txt
iot_air_kafka_updated_v2/bigdata-lab/notebooks/09_streaming_calidad_aire_kafka_FIXED.ipynb
```

a:

```txt
bigdata-lab/notebooks/
```

Luego abre Jupyter y ejecuta ese notebook. Si ya habías ejecutado el notebook anterior, reinicia el kernel antes.
