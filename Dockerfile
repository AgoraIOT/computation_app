# Pin Alpine minor so OpenSSL package floors resolve consistently with apk repos.
FROM python:3.13-alpine3.23

# Fix zlib CVE (https://nvd.nist.gov/vuln/detail/CVE-2023-45853)is not in latest alpine (as of 2026-03-17)
# This command will be need to be removed once alpine includes the fixed version
# Fix OpenSSL CVE-2026-28390 (https://nvd.nist.gov/vuln/detail/CVE-2026-28390) - fixed in 3.5.6-r0
# These commands will need to be removed once alpine includes the fixed version
RUN apk update && apk add --no-cache 'libcrypto3>=3.5.6-r0' 'libssl3>=3.5.6-r0' 'zlib>=1.3.2-r0' && rm -rf /var/cache/apk/*

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

