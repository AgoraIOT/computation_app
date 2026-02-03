FROM python:3.13-alpine

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src app
WORKDIR /app

ENV PYTHONUNBUFFERED True
USER root
ENV PATH="${PATH}:/sbin"

RUN rm /app/AEA.json
COPY AEA.json /app/AEA.json

EXPOSE 5678

ENV PYTHONPATH=/app

CMD cd /app && sed -e "s/localhost/${MQTT_HOST}/g" AEA.json -e "s/\<1707\>/${MQTT_PORT}/g" --in-place && python -m debugpy --listen 0.0.0.0:5678 main.py

