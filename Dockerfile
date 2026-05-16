FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GUNICORN_CMD_ARGS="--bind 0.0.0.0:5000 --workers 1 --threads 4 --timeout 180 --access-logfile -"

WORKDIR /app

COPY youtube_transcript_app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY youtube_transcript_app ./youtube_transcript_app
WORKDIR /app/youtube_transcript_app

EXPOSE 5000

CMD ["gunicorn", "app:app"]
