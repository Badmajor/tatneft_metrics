FROM python:3.12-slim


WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN pip install gunicorn==24.0.0

COPY . .
