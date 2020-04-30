FROM python:3.7-alpine

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY umbrella_event_importer.py /app

CMD ["python", "-u", "umbrella_event_importer.py"]
