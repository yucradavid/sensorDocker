#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE=${COMPOSE_FILE:-docker-compose-dev.yml}
KAFKA_DIR=${KAFKA_DIR:-../../ec-kafka}
TOPIC=${TOPIC:-calidad-aire-eventos}

cd "$KAFKA_DIR"

docker compose -f "$COMPOSE_FILE" exec ec-kafka bash -lc "
/opt/kafka/bin/kafka-console-consumer.sh \
  --topic '$TOPIC' \
  --bootstrap-server ec-kafka:9092 \
  --from-beginning \
  --property print.key=true \
  --property key.separator=' | '
"
