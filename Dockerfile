# syntax=docker/dockerfile:1

FROM node:22-bookworm-slim AS frontend
WORKDIR /build/http/frontend
COPY http/frontend/package.json http/frontend/package-lock.json ./
RUN npm ci
COPY http/frontend/ ./
RUN npm run build

FROM python:3.13-slim-bookworm AS dependencies
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git libffi-dev \
    && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt /build/requirements.txt
RUN pip install -r /build/requirements.txt

FROM python:3.13-slim-bookworm AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    WEB_HOST=0.0.0.0 \
    WEB_PORT=8000 \
    SQL_LOG_FILE=/app/storages/sql.log
RUN apt-get update \
    && apt-get install -y --no-install-recommends libopus0 libffi8 ca-certificates ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 hydromel \
    && useradd --uid 10001 --gid hydromel --no-create-home hydromel
WORKDIR /app
COPY --from=dependencies /opt/venv /opt/venv
COPY --from=frontend /usr/local/bin/node /usr/local/bin/node
COPY bot.py requirements.txt LICENSE ./
COPY commands/ commands/
COPY cogs/ cogs/
COPY libs/ libs/
COPY assets/ assets/
COPY tests/ tests/
COPY http/bootstrap.py http/bootstrap.py
COPY http/controllers/ http/controllers/
COPY http/middlewares/ http/middlewares/
COPY --from=frontend /build/http/public/ http/public/
RUN mkdir -p storages/locals storages/caches \
    && touch log.txt \
    && chown -R hydromel:hydromel storages log.txt
USER hydromel
EXPOSE 8000
ENTRYPOINT ["python3", "bot.py"]
CMD ["webserver"]
