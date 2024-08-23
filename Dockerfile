FROM python:3.12-slim
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app
COPY . .

RUN pip install poetry \
    && poetry config installer.max-workers 10\ 
    && poetry install --no-dev --no-interaction --no-ansi

EXPOSE 8000
