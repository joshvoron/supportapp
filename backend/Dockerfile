FROM python:3.13-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

COPY ./app .


CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py create_records && python manage.py runserver 0.0.0.0:8000"]
