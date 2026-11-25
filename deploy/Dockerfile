# syntax=docker/dockerfile:1
# The Strata Engine Book in a container: nginx serves an already built site under /strata-engine-docs/. It builds
# nothing. Build it in a folder that holds the unpacked release: strata-engine-docs/ (the site) and deploy/.
#
#     docker build -f deploy/Dockerfile -t strata-engine-docs:<tag> .
#     docker run -d --read-only --tmpfs /tmp --tmpfs /var/cache/nginx -p 127.0.0.1:8080:8080 strata-engine-docs:<tag>
#
# The image holds nginx's files and the built site, and nothing else: no node_modules, no tool that only builds or
# tests the book. nginx runs as the image's unprivileged user 101 and writes only into /tmp (its pid and temporary
# files) and /var/cache/nginx, so the container runs with a read-only file system.
FROM nginxinc/nginx-unprivileged:1.30.6-alpine
COPY deploy/nginx-http.conf /etc/nginx/conf.d/00-strata-engine-docs-http.conf
COPY deploy/nginx-container.conf /etc/nginx/conf.d/default.conf
COPY deploy/nginx.conf /etc/nginx/snippets/strata-engine-docs.conf
COPY deploy/nginx-csp.conf /etc/nginx/snippets/strata-engine-docs-csp.conf
COPY deploy/nginx-redirects.conf /etc/nginx/snippets/strata-engine-docs-redirects.conf
COPY --chown=101:101 strata-engine-docs/ /srv/www/strata-engine-docs/
RUN nginx -t
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q --spider http://127.0.0.1:8080/strata-engine-docs/ || exit 1
