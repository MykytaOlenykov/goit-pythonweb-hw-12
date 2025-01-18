FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry

ENV PYTHONPATH=/app

COPY ./src ./src
COPY pyproject.toml poetry.lock alembic.ini ./

RUN poetry config virtualenvs.create false 
RUN poetry install --only=main --no-root

EXPOSE 8000

CMD ["poetry", "run", "python", "src/main.py"]
