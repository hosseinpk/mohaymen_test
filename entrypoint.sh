#!/bin/sh
set -e

alembic upgrade head

exec uvicorn main:app --host 0.0.0.0 --port 8000


# exec gunicorn main:app \
#     --workers ${GUNICORN_WORKERS:-5} \
#     --worker-class uvicorn.workers.UvicornWorker \
#     --bind 0.0.0.0:8000
