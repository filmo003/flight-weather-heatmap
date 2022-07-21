# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /flight-weather-heatmap
COPY requirements.txt /flight-weather-heatmap/
RUN pip install -r requirements.txt
COPY . /flight-weather-heatmap/