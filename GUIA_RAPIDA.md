# Guía rápida de exposición y ejecución

## Qué opción recomiendo

Usa el **simulador Python**. Es lo más seguro porque el sensor físico no llegó, pero la arquitectura se mantiene válida.

## Cómo defenderlo ante el docente

> El pipeline se implementó con un simulador IoT porque el sensor físico BME680 no llegó a tiempo. El simulador emite eventos cada 3 segundos con el mismo contrato que usará el ESP32. Por tanto, Kafka, Spark, ventanas, watermarking, métricas y observabilidad se prueban de manera completa. Cuando el sensor llegue, solo se cambia la fuente de datos; el topic y Spark quedan iguales.

## Comandos resumen

```bash
# 1. Kafka
cd ec-kafka
docker compose -f docker-compose-dev.yml up --build

# 2. Topic
cd ../iot_air_kafka_updated/scripts
bash create_topic.sh

# 3. Simulador
cd ../air-quality-simulator-py
docker compose -f docker-compose-dev.yml up --build

# 4. Consumer opcional
cd ../scripts
bash consume_topic.sh

# 5. bigdata-lab
cd ../../bigdata-lab/docker
docker compose -f docker-compose.yml -f docker-compose.kafka.yml up --build
```
