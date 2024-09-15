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
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false  # Needed to Render

# Setup app environment
COPY . .
RUN poetry install --no-root --without dev

# Launch app
CMD ./scripts/start.sh
