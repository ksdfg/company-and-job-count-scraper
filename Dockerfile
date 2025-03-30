FROM python:3.13.2

RUN pip install poetry==2.1.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

ENV PATH="/app/.venv/bin:$PATH"

RUN playwright install --with-deps chromium

COPY app ./app

ENTRYPOINT ["poetry", "run", "python", "-m", "app"]