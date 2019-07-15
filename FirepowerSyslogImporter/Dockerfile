FROM python:3

COPY . /app
COPY ../.env /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "syslog_event_importer.py"]