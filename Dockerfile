FROM python:3.13-slim

WORKDIR /

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

ENV PYTHONPATH=/app

CMD ["uvicorn", "src.app.main:main_api_router", "--host", "0.0.0.0"]
