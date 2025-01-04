# Ваш основной образ
FROM python:3.12

RUN apt-get update && apt-get install -y postgresql-client

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

CMD ["sh", "-c", "./wait-for-it.sh db:5432 -- python manage.py migrate && gunicorn --bind 0.0.0.0:8000 study_platform.wsgi:application"]
