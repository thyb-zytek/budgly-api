FROM python:latest

WORKDIR /app/

ARG ENV

# Env setup
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONPATH=/app

# Update and install usefull package
RUN apt update && apt upgrade -qy
RUN pip install --upgrade pip
RUN pip install poetry

# Setup app environment
COPY app/pyproject.toml app/poetry.lock ./
RUN poetry install
COPY app .

# Launch server
CMD bash -c "poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
