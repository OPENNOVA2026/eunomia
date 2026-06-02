FROM python:3.10.16-slim-bullseye AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.5

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev

FROM python:3.10.16-slim-bullseye AS prod

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin/celery /usr/local/bin/celery

COPY src src

RUN useradd -m nova
USER nova

CMD ["celery", "-A", "src.celery.celery", "worker", "--loglevel=INFO"]

FROM builder AS dev

RUN poetry install

COPY . .

RUN useradd -m nova
USER nova

CMD ["watchmedo", "auto-restart", "--directory=./", "--pattern=*.py", "--recursive", "--", "celery", "-A", "src.celery.celery", "worker", "--loglevel=INFO"]
