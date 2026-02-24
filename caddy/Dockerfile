FROM caddy:2.9.1

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

USER appuser

COPY Caddyfile /etc/caddy
