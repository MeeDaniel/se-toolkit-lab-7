# Serve the React frontend with Caddy
# NOTE: Build locally first with `npm run build`, then docker build copies the dist/ folder

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}caddy:2.11-alpine

COPY --chown=caddy:caddy dist /srv