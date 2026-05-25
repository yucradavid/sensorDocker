#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE=${COMPOSE_FILE:-docker-compose-dev.yml}
KAFKA_DIR=${KAFKA_DIR:-../../ec-kafka}
TOPIC=${TOPIC:-calidad-aire-eventos}
PARTITIONS=${PARTITIONS:-3}
REPLICATION_FACTOR=${REPLICATION_FACTOR:-1}

cd "$KAFKA_DIR"

docker compose -f "$COMPOSE_FILE" exec ec-kafka bash -lc "
/opt/kafka/bin/kafka-topics.sh --create --if-not-exists \
  --topic '$TOPIC' \
  --bootstrap-server ec-kafka:9092 \
  --partitions '$PARTITIONS' \
  --replication-factor '$REPLICATION_FACTOR'

/opt/kafka/bin/kafka-topics.sh --describe \
  --topic '$TOPIC' \
  --bootstrap-server ec-kafka:9092
"
