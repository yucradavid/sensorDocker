import json
import os
import time
from typing import Optional

from fastapi import FastAPI, HTTPException
from kafka import KafkaProducer
from pydantic import BaseModel, Field

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "ec-kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "calidad-aire-eventos")
ESTACION_DEFAULT = os.getenv("ESTACION_DEFAULT", "Grupo 2 - Sensor")

app = FastAPI(title="Air Quality Ingest API", version="1.1.0")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda value: json.dumps(value, ensure_ascii=False).encode("utf-8"),
    key_serializer=lambda key: str(key).encode("utf-8"),
    retries=5,
)

class AirQualityReading(BaseModel):
    estacion: Optional[str] = Field(default=None)
    device_id: Optional[str] = Field(default="esp32-bme680-grupo-2")
    temperatura: float
    humedad: float
    presion: float
    altura: float
    gas: float
    iaq: float
    eco2: float
    voc: float
    calidad_aire: str
    riesgo_aire: Optional[str] = None
    timestamp_ms: Optional[int] = None


def clasificar_riesgo(iaq: float, eco2: float, voc: float) -> str:
    if iaq >= 200 or eco2 >= 800 or voc >= 15:
        return "ALTO"
    if iaq >= 100 or eco2 >= 600 or voc >= 10:
        return "MEDIO"
    return "BAJO"

@app.get("/health")
def health():
    return {
        "status": "ok",
        "kafka_bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
        "topic": KAFKA_TOPIC,
    }

@app.post("/api/air-quality")
def ingest_air_quality(reading: AirQualityReading):
    try:
        now_ms = int(time.time() * 1000)
        event = reading.model_dump()
        event["tipoEvento"] = "calidad_aire.actualizada"
        event["id_sensor"] = event.pop("device_id", None) or "esp32-bme680-grupo-2"
        event["estacion"] = event.get("estacion") or ESTACION_DEFAULT
        event["origen"] = "esp32-bme680"
        event["timestamp"] = event.pop("timestamp_ms", None) or now_ms
        event["ingestTimestamp"] = now_ms
        event["riesgo_aire"] = event.get("riesgo_aire") or clasificar_riesgo(event["iaq"], event["eco2"], event["voc"])

        producer.send(KAFKA_TOPIC, key=event["id_sensor"], value=event)
        producer.flush()

        print(json.dumps({"status": "sent", "topic": KAFKA_TOPIC, "event": event}, ensure_ascii=False))
        return {"status": "sent", "topic": KAFKA_TOPIC, "event": event}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
