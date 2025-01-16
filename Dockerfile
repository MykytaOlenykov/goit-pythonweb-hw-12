FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry

COPY ./contacts-api ./contacts-api
COPY pyproject.toml poetry.lock alembic.ini ./

RUN poetry config virtualenvs.create false 
RUN poetry install --only=main --no-root

EXPOSE 8000

CMD ["poetry", "run", "python", "contacts-api/main.py"]
