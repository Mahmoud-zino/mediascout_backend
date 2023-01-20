# Base image
FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1

# Liebherr certificate (important for pip)
COPY ./cacert.crt /usr/local/share/ca-certificates/cacert.crt

ENV PIP_CERT /usr/local/share/ca-certificates/cacert.crt

RUN apk --no-cache add ca-certificates \
  && update-ca-certificates

RUN mkdir /code
WORKDIR /code

RUN /usr/local/bin/python -m pip install --upgrade pip

COPY requirements.txt /code/
RUN pip install --trusted-host pypi.org --no-cache-dir -r requirements.txt

COPY . /code/
EXPOSE 8000
