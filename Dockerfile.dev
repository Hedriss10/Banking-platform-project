FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev gcc make build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV FLASK_ENV=development
ENV FLASK_APP=src.app:create_app 

COPY requirements/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY . /src

WORKDIR /src

EXPOSE 8080

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "src.app:create_app()"]