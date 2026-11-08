FROM cgr.dev/chainguard/python:latest-dev AS build

WORKDIR /app

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:${PATH}"

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY --chown=65532:65532 . /app
RUN mkdir -p /app/logs && chown 65532:65532 /app/logs

FROM cgr.dev/chainguard/python:latest

WORKDIR /app

COPY --from=build --chown=65532:65532 /app /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8080

ENTRYPOINT ["/app/venv/bin/gunicorn"]
CMD ["--bind", "0.0.0.0:8080", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
