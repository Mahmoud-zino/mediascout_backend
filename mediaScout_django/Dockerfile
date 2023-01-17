# Base image
FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1
# Create folder code
RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/
EXPOSE 8000
