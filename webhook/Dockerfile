FROM python:3.10-alpine


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV FLASK_APP=webhook.py

EXPOSE 5000
CMD flask run --host=0.0.0.0 --port=5000