# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /flight-weather-heatmap/wasp
COPY requirements.txt /flight-weather-heatmap/wasp
RUN pip install -r requirements.txt
COPY . /flight-weather-heatmap/