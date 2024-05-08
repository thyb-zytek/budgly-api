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
RUN poetry config virtualenvs.create false  # Needed to Github Actions

# Setup app environment
COPY ../app .
RUN poetry install --no-root
RUN chmod +x ./scripts/setup_database.sh
RUN ./scripts/setup_database.sh

# Launch app
CMD fastapi run --workers 4
