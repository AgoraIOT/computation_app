FROM eclipse-mosquitto:2.0.20

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

USER appuser

COPY mosquitto.conf /mosquitto/config