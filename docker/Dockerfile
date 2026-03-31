FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y build-essential libpq-dev \
    && apt-get clean

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y gettext

RUN chmod +x /app/docker/entrypoint.sh

RUN django-admin compilemessages

ENTRYPOINT ["/app/docker/entrypoint.sh"]