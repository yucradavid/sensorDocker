# air-quality-simulator-py

Simulador de sensor BME680 para contingencia. Genera eventos cada 3 segundos y los publica en Kafka.

## Docker

```bash
docker compose -f docker-compose-dev.yml up --build
```

## Python local

```bash
pip install -r requirements.txt
set KAFKA_BOOTSTRAP_SERVERS=localhost:49092
python producer_air_quality.py
```

En Linux/Mac:

```bash
export KAFKA_BOOTSTRAP_SERVERS=localhost:49092
python producer_air_quality.py
```
