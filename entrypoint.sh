#!/usr/bin/env sh
set -eu

: "${MQTT_HOST:?MQTT_HOST is required}"
: "${MQTT_PORT:?MQTT_PORT is required}"

cp /app/AEA.json /tmp/AEA.json
sed -i "s|localhost|${MQTT_HOST}|g; s|<1707>|${MQTT_PORT}|g" /tmp/AEA.json

cd /tmp

exec python -m debugpy --listen 0.0.0.0:5678 /app/main.py