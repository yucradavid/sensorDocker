import json
import os
import time
from typing import Set

import requests
from dotenv import load_dotenv
from kafka import KafkaProducer

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:49092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "calidad-aire-eventos")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "3"))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Configura SUPABASE_URL y SUPABASE_KEY en .env")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda value: json.dumps(value, ensure_ascii=False).encode("utf-8"),
    key_serializer=lambda key: str(key).encode("utf-8"),
)

seen: Set[str] = set()
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

while True:
    try:
        url = f"{SUPABASE_URL}?select=*&order=id.desc&limit=20"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        rows = response.json()

        for row in reversed(rows):
            row_id = str(row.get("id") or row.get("created_at") or hash(json.dumps(row, sort_keys=True)))
            if row_id in seen:
                continue
            seen.add(row_id)

            event = dict(row)
            event["tipoEvento"] = "calidad_aire.actualizada"
            event["origen"] = "supabase-bridge"
            event["ingestTimestamp"] = int(time.time() * 1000)
            event.setdefault("id_sensor", "esp32-bme680-grupo-2")

            producer.send(KAFKA_TOPIC, key=event.get("id_sensor", "sensor"), value=event)
            producer.flush()
            print(json.dumps({"sent": True, "event": event}, ensure_ascii=False))
    except Exception as exc:
        print(f"ERROR: {exc}")

    time.sleep(POLL_SECONDS)
