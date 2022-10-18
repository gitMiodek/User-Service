FROM python:latest

WORKDIR /app

COPY poetry.lock .
COPY pyproject.toml .


COPY /app .


RUN rm -r tests/

RUN pip install poetry


RUN poetry config virtualenvs.create false && poetry install



CMD ["uvicorn", "main:app","--reload", "--host", "0.0.0.0", "--port", "80"]
