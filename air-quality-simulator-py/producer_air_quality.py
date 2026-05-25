import json
import math
import os
import random
import signal
import sys
import time
from datetime import datetime
from typing import Dict

from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:49092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "calidad-aire-eventos")
SENSOR_ID = os.getenv("SENSOR_ID", "sensor-simulado-bme680")
ESTACION = os.getenv("ESTACION", "Grupo 2 - Sensor Simulado")
INTERVAL_SECONDS = float(os.getenv("INTERVAL_SECONDS", "3"))

running = True

def stop_handler(signum, frame):
    global running
    running = False

signal.signal(signal.SIGINT, stop_handler)
signal.signal(signal.SIGTERM, stop_handler)

def clasificar_calidad(iaq: float) -> str:
    if iaq < 100:
        return "Excelente"
    if iaq < 200:
        return "Buena"
    return "Pobre"

def clasificar_riesgo(iaq: float, eco2: float, voc: float) -> str:
    if iaq >= 200 or eco2 >= 800 or voc >= 15:
        return "ALTO"
    if iaq >= 100 or eco2 >= 600 or voc >= 10:
        return "MEDIO"
    return "BAJO"

def generar_lectura(contador: int) -> Dict:
    # Señales suaves para parecer sensor real, no valores totalmente aleatorios.
    fase = contador / 20.0
    temperatura = 20 + 2.5 * math.sin(fase) + random.uniform(-0.6, 0.6)
    humedad = 45 + 8 * math.sin(fase / 1.7) + random.uniform(-2.0, 2.0)
    presion = 1012 + 3 * math.sin(fase / 2.0) + random.uniform(-0.8, 0.8)
    altura = 3825 + random.uniform(-5, 5)

    # Simular episodios de mala ventilación cada cierto tiempo.
    episodio = (contador // 25) % 4 == 2
    base_iaq = 70 + 45 * math.sin(fase / 1.3) + random.uniform(-12, 12)
    if episodio:
        base_iaq += random.uniform(90, 160)

    iaq = max(0, min(500, base_iaq))
    eco2 = 400 + iaq * 1.8 + random.uniform(-15, 15)
    voc = max(1, iaq / 18 + random.uniform(-1.5, 1.5))
    gas = max(5, 80 - iaq / 5 + random.uniform(-4, 4))

    calidad = clasificar_calidad(iaq)
    riesgo = clasificar_riesgo(iaq, eco2, voc)
    now_ms = int(time.time() * 1000)

    return {
        "tipoEvento": "calidad_aire.actualizada",
        "idLectura": contador,
        "id_sensor": SENSOR_ID,
        "estacion": ESTACION,
        "temperatura": round(temperatura, 2),
        "humedad": round(humedad, 2),
        "presion": round(presion, 2),
        "altura": round(altura, 2),
        "gas": round(gas, 2),
        "iaq": round(iaq, 2),
        "eco2": round(eco2, 2),
        "voc": round(voc, 2),
        "calidad_aire": calidad,
        "riesgo_aire": riesgo,
        "origen": "python-sensor-simulator",
        "fechaHora": datetime.now().isoformat(timespec="seconds"),
        "timestamp": now_ms,
    }

def main() -> int:
    print("Iniciando simulador IoT de calidad de aire")
    print(f"Kafka bootstrap: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {KAFKA_TOPIC}")
    print(f"Sensor: {SENSOR_ID}")
    print(f"Intervalo: {INTERVAL_SECONDS} segundos")

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(value, ensure_ascii=False).encode("utf-8"),
        key_serializer=lambda key: str(key).encode("utf-8"),
        retries=5,
        linger_ms=50,
    )

    contador = 1
    while running:
        evento = generar_lectura(contador)
        producer.send(KAFKA_TOPIC, key=evento["id_sensor"], value=evento)
        producer.flush()
        print(json.dumps(evento, ensure_ascii=False))
        contador += 1
        time.sleep(INTERVAL_SECONDS)

    print("Deteniendo simulador...")
    producer.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
