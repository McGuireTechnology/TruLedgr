# Dockerfile for Traefik on Fly.io
FROM traefik:3.0

# Copy static configuration
COPY traefik.yml /etc/traefik/traefik.yml
