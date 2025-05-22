FROM python:3.13-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

COPY ./bot .


CMD ["sh", "-c", "python main.py"]
