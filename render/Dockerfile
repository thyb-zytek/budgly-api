FROM python:3.12

WORKDIR /app/

ARG ENV

# Env setup
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONPATH=/app

# Update and install usefull package
RUN pip install --no-cache-dir  poetry

# Setup app environment
COPY . .
RUN poetry install --no-root
RUN chmod +x ./scripts/start.sh

# Launch app
CMD poetry run ./scripts/start.sh
