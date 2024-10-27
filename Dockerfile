FROM python:3.10 as build-python

ENV PYTHONUNBUFFERED 1

RUN apt-get -y update \
    && apt-get install -y --no-install-recommends \
        postgresql-client ffmpeg\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["bash", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
