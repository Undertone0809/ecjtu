FROM python:3.14-slim

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=2.2.1

WORKDIR /app

RUN pip install "poetry==${POETRY_VERSION}" && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-interaction --no-ansi

COPY ecjtu ./ecjtu

EXPOSE 8080

CMD ["python", "-m", "ecjtu", "--port", "8080"]
