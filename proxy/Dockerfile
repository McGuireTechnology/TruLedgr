# Dockerfile for Traefik on Fly.io
FROM traefik:3.0

# Copy static configuration
COPY traefik.yml /etc/traefik/traefik.yml

# Set the default command to run Traefik with the config file
CMD ["traefik", "--configFile=/etc/traefik/traefik.yml"]
