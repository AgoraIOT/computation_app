FROM python:3.13-alpine

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

COPY requirements.txt ./requirements.txt
COPY entrypoint.sh ./entrypoint.sh
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app
COPY AEA.json /app/AEA.json

RUN find /app -type d -exec chmod 0555 {} \; \
 && find /app -type f -exec chmod 0444 {} \; \
 && chmod 0555 /app/entrypoint.sh

USER appuser

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

ENTRYPOINT [ "/app/entrypoint.sh" ]

