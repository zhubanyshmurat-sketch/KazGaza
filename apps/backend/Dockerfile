FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY packages/shared/python /packages/shared/python
COPY apps/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/backend .
# Normalize line endings in case this was checked out on Windows with
# CRLF (git core.autocrlf) — a \r before the shebang makes the kernel
# unable to find the interpreter ("no such file or directory").
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

RUN mkdir -p /app/storage/uploads

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
