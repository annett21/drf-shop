FROM python:3.10-slim-buster

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app
COPY pyproject.toml /app

WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
